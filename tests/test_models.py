from dataclasses import replace
import itertools
import math
import unittest

from bartender_sim.controls import fixed_batch, interval_overlap_probability, retry_reference
from bartender_sim.model import Proposal, Scenario, flow_digest, make_flow, simulate
from bartender_sim.report import kaplan_meier, summarize


def edit(name, at, agent, start=0, file=0, dependency=None, avoidance_u=1.0,
         alternatives=()):
    return Proposal(name, at, agent, (file + 0.1) / 2, (start + 0.1) / 9,
                    avoidance_u, alternatives, 0.0 if dependency else 1.0, dependency)


def scenario(**kwargs):
    values = dict(n=3, files=2, lines=10, length=2, horizon=4.0,
                  tau=1.0, repair_time=0.5, rate=0.0)
    values.update(kwargs)
    return Scenario(**values)


def by_id(result):
    return {p["id"]: p for p in result["patches"]}


class DynamicMechanismTests(unittest.TestCase):
    def test_clean_content_order_and_no_repairs(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1, file=1))
        a = simulate(scenario(), flow)
        b = simulate(scenario(policy="in_place"), flow)
        self.assertEqual(a["patches"], b["patches"])
        self.assertEqual(a["metrics"]["author_repair_starts"], 0)
        self.assertEqual(a["metrics"]["landed_edits"], 2)

    def test_clean_work_does_not_wait_for_another_repair(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1), edit("C", 0.3, 2, file=1))
        clean = by_id(simulate(scenario(), flow))
        inline = by_id(simulate(scenario(policy="in_place"), flow))
        self.assertEqual(clean["C"]["landed_at"], 1.0)
        self.assertEqual(clean["C"]["repair_blocked_time"], 0)
        self.assertEqual(inline["C"]["landed_at"], 1.5)
        self.assertEqual(inline["C"]["repair_blocked_time"], 0.5)

    def test_dependency_is_rescued_by_later_actor_in_next_pass(self):
        flow = (edit("C", 0.1, 1, file=1), edit("B", 0.2, 0, dependency="C"))
        result = simulate(scenario(dependency=1), flow)
        self.assertEqual(result["metrics"]["landed_edits"], 2)
        self.assertEqual(result["metrics"]["dependency_rescues_without_repair"], 1)
        self.assertEqual(result["metrics"]["author_repair_starts"], 0)
        self.assertEqual(by_id(result)["B"]["landed_revision"], 2)

    def test_inline_cannot_invent_a_missing_dependency(self):
        flow = (edit("C", 0.1, 1, file=1), edit("B", 0.2, 0, dependency="C"))
        result = simulate(scenario(policy="in_place", dependency=1), flow)
        self.assertEqual(result["metrics"]["landed_edits"], 0)
        self.assertGreater(result["metrics"]["failed_repair_completions"], 0)
        self.assertTrue(all(p["right_censored"] for p in result["patches"]))

    def test_zero_delay_kick_back_equals_clean_first(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1), edit("C", 0.3, 2, file=1),
                edit("D", 1.2, 0))
        for refresh in ("dispatch", "start"):
            for clock in ("fixed", "context"):
                s = scenario(refresh_at=refresh, repair_clock=clock)
                clean = simulate(s, flow)
                kick = simulate(replace(s, policy="kick_back"), flow)
                for field in ("metrics", "patches", "repairs", "flow_sha256"):
                    self.assertEqual(clean[field], kick[field])

    def test_refresh_at_start_absorbs_work_landed_during_wait(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1), edit("D", 1.2, 0))
        s = scenario(horizon=3.0, policy="kick_back", delta=1.0, repair_time=0.25)
        fresh = simulate(replace(s, refresh_at="start"), flow)
        stale = simulate(replace(s, refresh_at="dispatch"), flow)
        self.assertEqual(by_id(fresh)["B"]["landed_at"], 2.25)
        self.assertEqual(by_id(fresh)["B"]["failed_repairs"], 0)
        self.assertEqual(by_id(stale)["B"]["failed_repairs"], 1)
        self.assertTrue(by_id(stale)["B"]["right_censored"])
        self.assertEqual(fresh["repairs"][0]["stale_window"], 0.25)
        self.assertEqual(stale["repairs"][0]["stale_window"], 1.25)

    def test_new_work_during_nonzero_repair_can_cause_retry(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1), edit("D", 1.2, 0))
        result = simulate(scenario(repair_time=1.5, horizon=5.0), flow)
        self.assertEqual(by_id(result)["B"]["failed_repairs"], 1)
        self.assertEqual(by_id(result)["B"]["landed_at"], 4.0)

    def test_successful_commit_prefix_remains_landed(self):
        flow = (edit("A", 0.1, 0), edit("B1", 0.2, 1, start=5),
                edit("B2", 0.3, 1), edit("C", 0.4, 2, file=1))
        result = by_id(simulate(scenario(), flow))
        self.assertEqual(result["B1"]["landed_at"], 1.0)
        self.assertEqual(result["B1"]["landed_revision"], 2)
        self.assertEqual(result["B2"]["predecessor"], "B1")
        self.assertGreater(result["B2"]["landed_at"], result["C"]["landed_at"])

    def test_unfinished_repair_is_censored_and_partial_work_accounted(self):
        flow = (edit("A", 0.1, 0), edit("B", 0.2, 1))
        result = simulate(scenario(horizon=3, repair_time=10), flow)
        self.assertTrue(by_id(result)["B"]["right_censored"])
        self.assertEqual(by_id(result)["B"]["observed_conflict_age"], 2.0)
        self.assertEqual(result["metrics"]["observed_repair_busy_time"], 2.0)
        self.assertEqual(result["metrics"]["author_repair_completions"], 0)
        self.assertEqual(result["repairs"][-1]["outcome"], "right_censored")

    def test_pair_count_is_not_failure_or_repair_count(self):
        flow = (edit("A1", 0.1, 0), edit("A2", 0.2, 0), edit("B", 0.3, 1))
        result = simulate(scenario(), flow)
        self.assertEqual(result["metrics"]["concurrent_overlap_pairs"], 2)
        self.assertEqual(result["metrics"]["failed_edits"], 1)
        self.assertEqual(result["metrics"]["author_repair_starts"], 1)
        self.assertEqual(result["metrics"]["mean_first_failure_overlap_lines"], 2)

    def test_sync_makes_a_later_overlap_sequential(self):
        flow = (edit("A", 0.1, 0), edit("B", 1.2, 1))
        result = simulate(scenario(), flow)
        self.assertEqual(result["metrics"]["concurrent_overlap_pairs"], 0)
        self.assertEqual(result["metrics"]["failed_edits"], 0)

    def test_avoidance_changes_realized_location_not_proposal_stream(self):
        flow = (edit("A", 0.1, 0),
                edit("B", 1.2, 1, avoidance_u=0, alternatives=((0.9, 0.5),)))
        a = simulate(scenario(avoidance=0), flow)
        b = simulate(scenario(avoidance=1), flow)
        self.assertEqual(a["flow_sha256"], b["flow_sha256"])
        self.assertEqual(by_id(a)["B"]["file"], 0)
        self.assertEqual(by_id(b)["B"]["file"], 1)
        self.assertTrue(by_id(b)["B"]["avoided"])

    def test_flow_generation_is_policy_and_parameter_independent(self):
        s = scenario(rate=1, seed=7)
        a = make_flow(s)
        b = make_flow(replace(s, policy="kick_back", delta=3, tau=0.25,
                              dependency=0.3, avoidance=0.9, length=6))
        self.assertEqual(a, b)
        self.assertEqual(flow_digest(a), flow_digest(b))

    def test_no_arrivals_has_defined_empty_denominators(self):
        result = simulate(scenario())
        self.assertEqual(result["metrics"]["generated_edits"], 0)
        self.assertIsNone(result["metrics"]["unresolved_fraction"])
        self.assertIsNone(result["metrics"]["repair_failure_fraction"])

    def test_future_dependency_and_invalid_windows_rejected(self):
        with self.assertRaises(ValueError):
            simulate(scenario(), (edit("A", 0.1, 0, dependency="future"),))
        for value in (0, -1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                simulate(scenario(repair_time=value))


class ControlModelTests(unittest.TestCase):
    def test_overlap_probability_matches_finite_enumeration(self):
        for lines in range(1, 9):
            for length in range(1, lines + 1):
                starts = range(lines - length + 1)
                overlaps = sum(abs(a - b) < length for a in starts for b in starts)
                self.assertAlmostEqual(interval_overlap_probability(3, lines, length),
                                       overlaps / (3 * len(starts)**2))

    def test_fixed_graph_theorem_for_all_graphs_through_four_items(self):
        for n in range(1, 5):
            edges = list(itertools.combinations(range(n), 2))
            for mask in range(1 << len(edges)):
                footprints = [set() for _ in range(n)]
                for k, (a, b) in enumerate(edges):
                    if mask & (1 << k):
                        footprints[a].add(("edge", k))
                        footprints[b].add(("edge", k))
                for blocked in range(1 << n):
                    f = [x.copy() for x in footprints]
                    initial = set()
                    for i in range(n):
                        if blocked & (1 << i):
                            f[i].add(("initial", i))
                            initial.add(("initial", i))
                    clean = fixed_batch(tuple(map(frozenset, f)), frozenset(initial), "clean_first")
                    inline = fixed_batch(tuple(map(frozenset, f)), frozenset(initial), "in_place")
                    self.assertLessEqual(set(clean.repairs), set(inline.repairs))
                    for i in clean.repairs:
                        self.assertLessEqual(inline.contexts[i], clean.contexts[i])

    def test_shrinking_footprint_reverses_repair_count(self):
        f = tuple(map(frozenset, ({"x", "y"}, {"y", "z", "w"}, {"z"}, {"w"})))
        replacement = {1: frozenset({"y"})}
        clean = fixed_batch(f, frozenset({"x"}), "clean_first", replacement)
        inline = fixed_batch(f, frozenset({"x"}), "in_place", replacement)
        self.assertEqual(clean.repairs, (0, 2, 3))
        self.assertEqual(inline.repairs, (0, 1))

    def test_characteristic_time_is_finite(self):
        result = retry_reference(0.5, 2.0)
        self.assertAlmostEqual(result["expected_attempts"], math.e)
        self.assertAlmostEqual(result["retry_probability"], 1 - math.exp(-1))


class ReportingTests(unittest.TestCase):
    def test_censored_conflict_remains_at_risk(self):
        rows = kaplan_meier([(1, True), (1, False), (2, False)])
        self.assertAlmostEqual(rows[0]["survival"], 2 / 3)
        self.assertEqual(rows[1]["at_risk"], 1)
        self.assertAlmostEqual(rows[1]["survival"], 2 / 3)

    def test_paired_contrast_uses_seed_difference_and_keeps_nulls(self):
        records = []
        for seed in (0, 1):
            for policy, value in (("clean_first", 3 + seed), ("in_place", 5 + seed)):
                records.append({"suite": "test", "cell_id": policy,
                                "scenario": {"policy": policy, "seed": seed},
                                "status": "ok", "flow_sha256": str(seed),
                                "metrics": {"repairs": value, "undefined": None}})
        means, differences = summarize(records)
        self.assertEqual(differences[0]["mean"], -2)
        self.assertEqual(differences[0]["ci95_low"], -2)
        self.assertTrue(all(r["n"] == 0 for r in means if r["metric"] == "undefined"))
        records[0]["flow_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            summarize(records)


if __name__ == "__main__":
    unittest.main()
