"""Discrete-event replay of exogenous edit proposals.

The shared state is an append-only sequence of synthetic patches. A patch
conflicts with unseen, overlapping foreign patches, or a missing prerequisite.
This is a declared geometry model, not an implementation of Git cherry-pick.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import heapq
import json
import math
import random


@dataclass(frozen=True)
class Scenario:
    n: int = 4
    rate: float = 1.0
    files: int = 8
    lines: int = 256
    length: int = 16
    horizon: float = 256.0
    tau: float = 1.0
    dependency: float = 0.0
    avoidance: float = 0.0
    repair_time: float = 0.25
    context_weight: float = 0.05
    repair_clock: str = "fixed"
    refresh_at: str = "start"
    delta: float = 0.0
    policy: str = "clean_first"
    seed: int = 1000
    avoidance_trials: int = 4
    dependency_lookback: int = 32
    visibility_lookback: int = 32
    ejection_threshold: int = 5

    def validate(self) -> None:
        for key in ("n", "files", "lines", "length", "avoidance_trials",
                    "dependency_lookback", "visibility_lookback", "ejection_threshold"):
            value = getattr(self, key)
            if type(value) is not int or value < 1:
                raise ValueError(f"{key} must be a positive integer")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        for key in ("rate", "horizon", "tau", "repair_time", "delta",
                    "context_weight", "dependency", "avoidance"):
            value = getattr(self, key)
            if not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f"{key} must be finite")
        if self.length > self.lines:
            raise ValueError("edit length exceeds file length")
        if min(self.horizon, self.tau, self.repair_time) <= 0:
            raise ValueError("horizon, tau, and repair_time must be positive")
        if min(self.rate, self.delta, self.context_weight) < 0:
            raise ValueError("rate, delta, and context_weight must be nonnegative")
        if not 0 <= self.dependency <= 1 or not 0 <= self.avoidance <= 1:
            raise ValueError("dependency and avoidance must be in [0, 1]")
        if self.policy not in {"clean_first", "in_place", "kick_back"}:
            raise ValueError("unknown policy")
        if self.policy != "kick_back" and self.delta != 0:
            raise ValueError("only kick_back has an external response delay")
        if self.repair_clock not in {"fixed", "context"}:
            raise ValueError("unknown repair clock")
        if self.refresh_at not in {"dispatch", "start"}:
            raise ValueError("unknown repair baseline read time")


@dataclass(frozen=True)
class Proposal:
    id: str
    at: float
    agent: int
    file_u: float
    start_u: float
    avoidance_u: float = 1.0
    alternatives: tuple[tuple[float, float], ...] = ()
    dependency_u: float = 1.0
    dependency_candidate: str | None = None


def _rng(seed: int, agent: int, domain: str) -> random.Random:
    key = f"bartender-sim-v1:{seed}:{agent}:{domain}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(key).digest(), "big"))


def make_flow(s: Scenario) -> tuple[Proposal, ...]:
    """Independent actor arrival/mark streams; no policy draws during replay."""
    s.validate()
    if s.rate == 0:
        return ()
    raw = []
    for agent in range(s.n):
        arrival, marks = _rng(s.seed, agent, "arrival"), _rng(s.seed, agent, "marks")
        at, index = 0.0, 0
        while True:
            at += arrival.expovariate(s.rate)
            if at >= s.horizon:
                break
            raw.append((at, agent, index, [marks.random() for _ in range(6)],
                        tuple((marks.random(), marks.random())
                              for _ in range(s.avoidance_trials))))
            index += 1
    history: list[Proposal] = []
    for at, agent, index, u, alternatives in sorted(raw):
        candidates = [p.id for p in history[-s.dependency_lookback:] if p.agent != agent]
        dependency = candidates[int(u[5] * len(candidates))] if candidates else None
        history.append(Proposal(f"a{agent}:{index}", at, agent, u[0], u[1],
                                u[2], alternatives, u[3], dependency))
    return tuple(history)


def flow_digest(flow: tuple[Proposal, ...]) -> str:
    data = json.dumps([asdict(p) for p in flow], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class Patch:
    proposal: Proposal
    file: int
    start: int
    end: int
    base: int
    birth_base: int
    dependency: str | None
    predecessor: str | None
    avoided: bool = False
    first_failure: float | None = None
    landed_at: float | None = None
    revision: int | None = None
    application_attempts: int = 0
    failed_applications: int = 0
    dispatches: int = 0
    repair_starts: int = 0
    repair_completions: int = 0
    failed_repairs: int = 0
    ejections: int = 0
    concurrent_pairs: int = 0
    concurrent_lines: set[int] = field(default_factory=set)
    repair_blocked_time: float = 0.0
    first_failure_overlap_lines: int = 0
    first_failure_context_count: int = 0


@dataclass
class Repair:
    token: int
    patch_id: str
    dispatched_at: float
    dispatch_revision: int
    requested_start: float
    started_at: float | None = None
    read_revision: int | None = None
    read_at: float | None = None
    duration: float | None = None
    context_count: int = 0
    overlap_lines: int = 0
    effort: float = 0.0
    new_landings_before_start: int = 0


def overlap(a: Patch, b: Patch) -> bool:
    return a.file == b.file and max(a.start, b.start) < min(a.end, b.end)


class Simulator:
    def __init__(self, scenario: Scenario, flow: tuple[Proposal, ...]):
        scenario.validate()
        self.s = scenario
        self.flow = flow
        self.now = 0.0
        self.patches: dict[str, Patch] = {}
        self.start_buckets: dict[tuple[int, int], list[Patch]] = {}
        self.actor_queues: list[list[str]] = [[] for _ in range(scenario.n)]
        self.actor_positions = [0] * scenario.n
        self.landed: list[Patch] = []
        self.visible = [0] * scenario.n
        self.last_actor_patch: dict[int, str] = {}
        self.pending: set[str] = set()
        self.events: list[tuple[float, int, int, str, object]] = []
        self.sequence = 0
        self.repair: Repair | None = None
        self.repair_token = 0
        self.repair_log: list[dict] = []
        self.inline_batch: list[str] | None = None
        self.inline_position = 0
        self.sync_requests = 0
        self.sync_calls = 0
        self.passes = 0
        self.application_attempts = 0
        self.failed_applications = 0
        self.rescued = 0
        self.repair_busy_time = 0.0
        self.observed_repair_effort = 0.0

    def _event(self, at: float, priority: int, kind: str, payload: object) -> None:
        self.sequence += 1
        heapq.heappush(self.events, (at, priority, self.sequence, kind, payload))

    def _location(self, file_u: float, start_u: float) -> tuple[int, int, int]:
        start = int(start_u * (self.s.lines - self.s.length + 1))
        return int(file_u * self.s.files), start, start + self.s.length

    def _arrive(self, p: Proposal) -> None:
        location = self._location(p.file_u, p.start_u)
        view = self.visible[p.agent]

        def visible_overlap(loc: tuple[int, int, int]) -> bool:
            return any(q.revision is not None and max(0, view - self.s.visibility_lookback) < q.revision <= view
                       and q.proposal.agent != p.agent
                       and max(loc[1], q.start) < min(loc[2], q.end)
                       for q in self._neighbors(loc))

        avoided = False
        if p.avoidance_u < self.s.avoidance and visible_overlap(location):
            for alternate in p.alternatives[:self.s.avoidance_trials]:
                candidate = self._location(*alternate)
                if not visible_overlap(candidate):
                    location, avoided = candidate, True
                    break
        dependency = p.dependency_candidate if p.dependency_u < self.s.dependency else None
        patch = Patch(p, *location, view, view, dependency,
                      self.last_actor_patch.get(p.agent), avoided)
        for other in self._neighbors(location):
            if (other.proposal.agent != p.agent and overlap(patch, other)
                    and (other.revision is None or other.revision > view)):
                patch.concurrent_pairs += 1
                patch.concurrent_lines.update(range(max(patch.start, other.start),
                                                    min(patch.end, other.end)))
        self.patches[p.id] = patch
        self.start_buckets.setdefault((patch.file, patch.start // self.s.length), []).append(patch)
        self.actor_queues[p.agent].append(p.id)
        self.last_actor_patch[p.agent] = p.id
        self.pending.add(p.id)

    def _predecessor_landed(self, patch: Patch) -> bool:
        return patch.predecessor is None or patch.predecessor not in self.pending

    def _neighbors(self, location: tuple[int, int, int]):
        file, start, end = location
        low = max(0, start - self.s.length + 1) // self.s.length
        high = (end - 1) // self.s.length
        for bucket in range(low, high + 1):
            yield from self.start_buckets.get((file, bucket), ())

    def _head(self, agent: int) -> Patch | None:
        queue = self.actor_queues[agent]
        while self.actor_positions[agent] < len(queue):
            pid = queue[self.actor_positions[agent]]
            if pid in self.pending:
                return self.patches[pid]
            self.actor_positions[agent] += 1
        return None

    def _context(self, patch: Patch, revision: int) -> list[Patch]:
        return [q for q in self.landed[patch.base:revision]
                if q.proposal.agent != patch.proposal.agent]

    def _attempt(self, patch: Patch) -> bool:
        patch.application_attempts += 1
        self.application_attempts += 1
        missing = patch.dependency is not None and self.patches[patch.dependency].revision is None
        conflicts = [q for q in self._neighbors((patch.file, patch.start, patch.end))
                     if q.revision is not None and q.revision > patch.base
                     and q.proposal.agent != patch.proposal.agent and overlap(patch, q)]
        conflicting = bool(conflicts)
        if missing or conflicting:
            patch.failed_applications += 1
            self.failed_applications += 1
            if patch.first_failure is None:
                patch.first_failure = self.now
                patch.ejections += 1
                changed_lines = set()
                for q in conflicts:
                    changed_lines.update(range(max(patch.start, q.start), min(patch.end, q.end)))
                patch.first_failure_overlap_lines = len(changed_lines)
                patch.first_failure_context_count = len(self._context(patch, len(self.landed)))
            return False
        patch.landed_at = self.now
        patch.revision = len(self.landed) + 1
        self.landed.append(patch)
        self.pending.remove(patch.proposal.id)
        if patch.first_failure is not None and patch.repair_starts == 0:
            self.rescued += 1
        return True

    def _ordered_pending(self) -> list[str]:
        return sorted(self.pending, key=lambda pid: (self.patches[pid].proposal.agent,
                                                     self.patches[pid].proposal.at, pid))

    def _refresh_idle(self) -> None:
        for agent in range(self.s.n):
            if self._head(agent) is None:
                self.visible[agent] = len(self.landed)

    def _dispatch(self, patch: Patch) -> None:
        assert self.repair is None
        self.repair_token += 1
        delay = self.s.delta if self.s.policy == "kick_back" else 0.0
        self.repair = Repair(self.repair_token, patch.proposal.id, self.now,
                             len(self.landed), self.now + delay)
        patch.dispatches += 1
        self._event(self.now + delay, 3, "repair_start", self.repair.token)

    def _sync(self) -> None:
        if self.s.policy == "in_place" and self.repair is not None:
            return
        self.sync_calls += 1
        if self.s.policy == "in_place":
            self._inline_sync()
            return
        while True:
            self.passes += 1
            progress = False
            for agent in range(self.s.n):
                while (patch := self._head(agent)) is not None:
                    pid = patch.proposal.id
                    if self.repair and self.repair.patch_id == pid and self.repair.started_at is not None:
                        break
                    if not self._attempt(patch):
                        break
                    progress = True
                    if self.repair and self.repair.patch_id == pid:
                        self.repair_log.append({**asdict(self.repair),
                                                "outcome": "rescued_before_start",
                                                "observed_until": self.now})
                        self.repair = None
            if not progress or not self.pending:
                break
        self._refresh_idle()
        if self.repair is None:
            for agent in range(self.s.n):
                patch = self._head(agent)
                if patch is not None and patch.first_failure is not None:
                    self._dispatch(patch)
                    break

    def _inline_sync(self) -> None:
        if self.inline_batch is None:
            self.inline_batch = self._ordered_pending()
            self.inline_position = 0
            self.passes += 1
        while self.inline_position < len(self.inline_batch):
            pid = self.inline_batch[self.inline_position]
            if pid in self.pending:
                patch = self.patches[pid]
                if not self._predecessor_landed(patch):
                    raise RuntimeError("inline order violated actor commit order")
                if not self._attempt(patch):
                    self._dispatch(patch)
                    return
            self.inline_position += 1
        self.inline_batch = None
        self._refresh_idle()

    def _start_repair(self, token: int) -> None:
        r = self.repair
        if r is None or r.token != token:
            return
        patch = self.patches[r.patch_id]
        r.started_at = self.now
        r.read_revision = r.dispatch_revision if self.s.refresh_at == "dispatch" else len(self.landed)
        r.read_at = r.dispatched_at if self.s.refresh_at == "dispatch" else self.now
        context = self._context(patch, r.read_revision)
        r.context_count = len(context)
        changed_lines = set()
        for q in context:
            if overlap(patch, q):
                changed_lines.update(range(max(patch.start, q.start), min(patch.end, q.end)))
        r.overlap_lines = len(changed_lines)
        r.new_landings_before_start = len(self.landed) - r.dispatch_revision
        r.effort = 1 + self.s.context_weight * r.context_count + r.overlap_lines / self.s.length
        r.duration = self.s.repair_time * (r.effort if self.s.repair_clock == "context" else 1)
        patch.repair_starts += 1
        self._event(self.now + r.duration, 0, "repair_done", token)

    def _account_repair(self, r: Repair, until: float) -> None:
        if r.started_at is None:
            return
        duration = min(r.duration, max(0, until - r.started_at))
        self.repair_busy_time += duration
        self.observed_repair_effort += r.effort * duration / r.duration
        if self.s.policy == "in_place":
            for pid in self.pending:
                if pid != r.patch_id:
                    p = self.patches[pid]
                    p.repair_blocked_time += max(0, until - max(p.proposal.at, r.started_at))

    def _finish_repair(self, token: int) -> None:
        r = self.repair
        if r is None or r.token != token:
            return
        self._account_repair(r, self.now)
        patch = self.patches[r.patch_id]
        # The repair absorbs only the selected snapshot, not subsequent work.
        patch.base = r.read_revision
        patch.repair_completions += 1
        success = self._attempt(patch)
        if not success:
            patch.failed_repairs += 1
            patch.ejections += 1
        self.repair_log.append({**asdict(r), "outcome": "landed" if success else "failed",
                                "observed_until": self.now,
                                "stale_window": self.now - r.read_at})
        self.repair = None
        # A completed owner repair requests another sync in the analysis protocol.
        self._sync()

    def run(self) -> dict:
        seen = set()
        previous_time = -1.0
        for p in self.flow:
            if (p.id in seen or not 0 <= p.agent < self.s.n or
                    not 0 <= p.at < self.s.horizon or p.at < previous_time):
                raise ValueError("flow must have unique IDs and sorted arrivals within the window")
            if p.dependency_candidate is not None and p.dependency_candidate not in seen:
                raise ValueError("dependency must refer to an earlier proposal")
            marks = (p.file_u, p.start_u, *[v for pair in p.alternatives for v in pair])
            if any(not 0 <= u < 1 for u in marks):
                raise ValueError("location marks must be in [0, 1)")
            seen.add(p.id)
            previous_time = p.at
            self._event(p.at, 1, "arrival", p)
        # No extra drain period or forced final sync: all policies share a cutoff.
        for index in range(1, math.floor(self.s.horizon / self.s.tau) + 1):
            self._event(index * self.s.tau, 2, "sync", None)
        while self.events and self.events[0][0] <= self.s.horizon:
            self.now, _, _, kind, payload = heapq.heappop(self.events)
            if kind == "arrival":
                self._arrive(payload)
            elif kind == "sync":
                self.sync_requests += 1
                self._sync()
            elif kind == "repair_start":
                self._start_repair(payload)
            elif kind == "repair_done":
                self._finish_repair(payload)
        if self.repair is not None:
            self._account_repair(self.repair, self.s.horizon)
            self.repair_log.append({**asdict(self.repair), "outcome": "right_censored",
                                    "observed_until": self.s.horizon})
        return self._result()

    def _result(self) -> dict:
        rows = []
        for p in self.patches.values():
            end = p.landed_at if p.landed_at is not None else self.s.horizon
            rows.append({
                "id": p.proposal.id, "agent": p.proposal.agent,
                "arrived_at": p.proposal.at, "file": p.file,
                "start": p.start, "end": p.end, "birth_base": p.birth_base,
                "covered_revision": p.base, "dependency": p.dependency,
                "predecessor": p.predecessor, "avoided": p.avoided,
                "first_failure": p.first_failure, "landed_at": p.landed_at,
                "first_failure_overlap_lines": p.first_failure_overlap_lines,
                "first_failure_context_count": p.first_failure_context_count,
                "landed_revision": p.revision, "right_censored": p.landed_at is None,
                "observed_latency": end - p.proposal.at,
                "observed_conflict_age": None if p.first_failure is None else end - p.first_failure,
                "application_attempts": p.application_attempts,
                "failed_applications": p.failed_applications,
                "dispatches": p.dispatches, "repair_starts": p.repair_starts,
                "repair_completions": p.repair_completions,
                "failed_repairs": p.failed_repairs, "ejections": p.ejections,
                "concurrent_overlap_pairs": p.concurrent_pairs,
                "unique_concurrent_overlap_lines": len(p.concurrent_lines),
                "repair_blocked_time": p.repair_blocked_time,
            })
        conflicts = [r for r in rows if r["first_failure"] is not None]
        early = [r for r in conflicts if r["first_failure"] <= self.s.horizon / 2]

        def unresolved_many(group: list[dict]) -> int:
            return sum(r["right_censored"] and r["ejections"] > self.s.ejection_threshold for r in group)

        total = len(rows)
        completed_repairs = sum(r["repair_completions"] for r in rows)
        failed_repairs = sum(r["failed_repairs"] for r in rows)
        pairs = sum(r["concurrent_overlap_pairs"] for r in rows)
        metrics = {
            "generated_edits": total, "landed_edits": len(self.landed),
            "unresolved_edits": len(self.pending), "failed_edits": len(conflicts),
            "concurrent_overlap_pairs": pairs,
            "overlap_pairs_per_time": pairs / self.s.horizon,
            "overlap_pairs_per_generated_edit": pairs / total if total else None,
            "first_failures_per_time": len(conflicts) / self.s.horizon,
            "first_failures_per_generated_edit": len(conflicts) / total if total else None,
            "first_failures_per_sync_call": len(conflicts) / self.sync_calls if self.sync_calls else None,
            "overlap_pairs_per_scheduled_interval": pairs / self.sync_requests if self.sync_requests else None,
            "mean_first_failure_overlap_lines": sum(r["first_failure_overlap_lines"] for r in conflicts) / len(conflicts) if conflicts else None,
            "mean_first_failure_context_count": sum(r["first_failure_context_count"] for r in conflicts) / len(conflicts) if conflicts else None,
            "application_attempts": self.application_attempts,
            "failed_applications": self.failed_applications,
            "author_repair_starts": sum(r["repair_starts"] for r in rows),
            "author_repair_completions": completed_repairs,
            "failed_repair_completions": failed_repairs,
            "repair_failure_fraction": failed_repairs / completed_repairs if completed_repairs else None,
            "dispatches": sum(r["dispatches"] for r in rows),
            "dependency_rescues_without_repair": self.rescued,
            "avoided_proposals": sum(r["avoided"] for r in rows),
            "sync_requests": self.sync_requests, "sync_calls": self.sync_calls,
            "automatic_passes": self.passes,
            "observed_repair_busy_time": self.repair_busy_time,
            "observed_repair_effort": self.observed_repair_effort,
            "repair_effort_per_generated_edit": self.observed_repair_effort / total if total else None,
            "unresolved_fraction": len(self.pending) / total if total else None,
            "conflict_cohort_n": len(conflicts),
            "unresolved_over_threshold_n": unresolved_many(conflicts),
            "unresolved_over_threshold_fraction": unresolved_many(conflicts) / len(conflicts) if conflicts else None,
            "early_conflict_cohort_n": len(early),
            "early_unresolved_over_threshold_fraction": unresolved_many(early) / len(early) if early else None,
            "mean_observed_latency": sum(r["observed_latency"] for r in rows) / total if total else None,
        }
        return {"scenario": asdict(self.s), "flow_sha256": flow_digest(self.flow),
                "metrics": metrics, "patches": rows, "repairs": self.repair_log}


def simulate(scenario: Scenario, flow: tuple[Proposal, ...] | None = None) -> dict:
    return Simulator(scenario, make_flow(scenario) if flow is None else flow).run()
