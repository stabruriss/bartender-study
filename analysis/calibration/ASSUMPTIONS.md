# External range-positioning assumptions and hold points

Status: **HOLD pending second-eye review**. Workload derivation is complete.

This is **scenario-based range positioning**, not empirical calibration. The
output is an effective per-cross-unit collision probability (`p_eff`) under a
strong independence mapping; it must not be called the Bartender simulation's
`p`.

The positioning uses the independent-edit approximation

`q_pair = 1 - (1 - p_eff)^(m1*m2)`.

Here `p_eff` is the effective collision probability under this mapping and
`m1`, `m2` are
counts of editor units in the two sides. An editor unit would be a changed
hunk, because a hunk is closer to the model's line-range edit than a whole
file. The number of changed files would be only a sensitivity upper bound.
The cited [23] paper and replication package do not supply final-diff hunk
counts for the exact replay sample. We therefore derived them from the current
public PR heads for the exact 747 source row keys. The package lacks frozen
replay OIDs, so this is a current-retrievable-head sensitivity and not an exact
replay. Conflicted-file counts are outcome-conditioned and are not used as edit
counts.

The Xu et al. rates are kept separate: 19.8% is the same agent-type/model
PR-pair rate (119/601 evaluable pairs), and 41.7% is the cross-type/model
PR-pair rate (48/115). They are not pooled or averaged. These labels do not
mean that the two PRs share an individual authoring agent.

AgenticFlict [22] reports 29,609/107,026 (27.67%) textual conflict for a PR
replayed against its observed or reconstructed base. We report it as a
distinct PR-to-base quantity. Mapping it to the same formula requires an
explicit assumed effective `m2`, the number of base-side landed edits between
the merge base and that base revision; [22] does not report it. Until that
quantity is separately reconstructed or declared as a sensitivity scenario,
no `p_eff` is reported for this row.

The published rates are textual conflict rates, not semantic conflict rates.
[23] includes structural outcomes (modify/delete and add/add), so a hunk-based
mapping would need either a content-conflict-only outcome or an explicit
structural-inclusive label. The positioning does not validate the mechanism,
identify the synthetic parameter, or infer causality. Denominators and
numerators are retained where the source reports them. Missing source
summaries remain blank rather than being guessed.

## Sensitivity and decision gate

For each of the two Xu rates, `p_eff` is calculated independently at the
median, Q1 and Q3 positive hunk products, and separately at file-product values
as a sensitivity. The result is compared with the synthetic scan
`0.0034–0.0687`. Some scenarios are below the scan. This observation does not
authorize a rerun: a second reader must first approve the workload mapping and
decide whether any additional cells are scientifically useful; the owner must
then approve at most ten additional cells with 30 seeds each.

The hold is released only after: (1) source locations and denominators are
checked, (2) exact-row-key current-head final-diff hunk/file sensitivity values
are reviewed, (3) 佛印's four-point review passes, and (4) the coverage decision
is recorded in this file. The legacy scenario calculator remains blank and
points readers to `range-positioning.csv`.

## Execution gate

The bounded read-only extraction was approved on 16 September 2026 with these
conditions: public repositories only; pause below 500 remaining GitHub core API
requests; record current head/base/merge-base OIDs, retrieval time, Git version
and diff parameters; retain counts and OID metadata rather than diff contents;
keep the 31 source-unavailable rows separate; and obtain second-eye review
before pushing the result branch. The implementation follows the source
replay's depth-80 fetch with a depth-600 retry and fixes the diff algorithm and
rename setting explicitly. The output is still **HOLD** until the completed
validation record is reviewed.

## Completed extraction record

The extraction covers all 747 source keys one to one. It derived counts for
715 pairs, retained the source package's 25 `UNAVAIL_fetch` and 6
`UNAVAIL_nobase` rows, and records one additional current failure:
`kiwicom/orbit` PR 4567 returns 404. Its paired row is source-labeled clean, so
the published rate denominator and numerator are unchanged; only the observed
workload-product distribution loses that pair. No retrieved head differed
between its API OID and fetched OID. There were no fetch, merge-base, diff or
timeout failures among the other rows.

The hunk-product distributions contain 75 zero-product same-type/model pairs
and 5 zero-product cross-type/model pairs. They remain in the workload table,
but quantiles and inversion use positive products because
`q = 1 - (1 - p_eff)^N` cannot be inverted at `N = 0`. This handling is stated
in `VALIDATION.json`, `workload-summary.csv` and `RESULTS.md`.

Unresolved gate: 佛印 must review the 747-key mapping, the current-head scope,
the three conflict definitions and denominators, positive-product handling,
Wilson interval propagation, and the conclusion about scan coverage. No
additional simulation has been run or approved.
