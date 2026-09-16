# External calibration assumptions and hold points

Status: **HOLD pending workload derivation and second-eye review**.

This is **scenario-based range positioning**, not empirical calibration. The
output is an effective per-cross-unit collision probability (`p_eff`) under a
strong independence mapping; it must not be called the Bartender simulation's
`p`.

The positioning uses the independent-edit approximation

`q_pair = 1 - (1 - p)^(m1*m2)`.

Here `p_eff` is the effective collision probability under this mapping and
`m1`, `m2` are
counts of editor units in the two sides. An editor unit would be a changed
hunk, because a hunk is closer to the model's line-range edit than a whole
file. The number of changed files would be only a sensitivity upper bound.
The cited [23] paper and replication package do not supply final-diff hunk
counts for the exact replay sample, so no hunk median or quartile is entered
yet. Conflicted-file counts are outcome-conditioned and cannot substitute for
edit counts.

The Xu et al. rates are kept separate: 19.8% is the same-agent PR-pair rate
(119/601 evaluable pairs), and 41.7% is the cross-agent PR-pair rate
(48/115). They are not pooled or averaged.

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

For each of the two Xu rates, calculate `p_eff` independently at the median, Q1
and Q3 hunk counts (and separately at file-count values as an upper-bound
sensitivity) only after those counts are derived from final diffs for the exact
sample. Compare the resulting interval with the synthetic scan
`0.0034–0.0687`. If every externally implied value is inside that scan, only
the existing aggregate cells are read and no simulation is rerun. If any
value is outside, a second reader must first approve the workload mapping and
the owner must approve at most ten additional cells with 30 seeds each.

The hold is released only after: (1) source locations and denominators are
checked, (2) exact-sample final-diff hunk/file sensitivity values are entered,
(3)佛印's four-point review passes, and (4) the coverage decision is recorded
in this file. Until then `calibration-results.csv` must report `pending
workload summary`.
