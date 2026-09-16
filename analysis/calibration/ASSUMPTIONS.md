# External calibration assumptions and hold points

Status: **HOLD pending second-eye review and workload transcription**.

The calibration uses the independent-edit approximation

`q_pair = 1 - (1 - p)^(m1*m2)`.

Here `p` is the model's independent overlap probability and `m1`, `m2` are
counts of editor units in the two sides. An editor unit is a changed hunk,
because a hunk is closer to the model's line-range edit than a whole file. The
number of changed files is retained only as a sensitivity upper bound. We will
transcribe the median, first quartile and third quartile of hunk counts from
Xu et al. [23], and record the exact table/figure location for each value.

The Xu et al. rates are kept separate: 19.8% is the same-agent PR-pair rate
(119/601 evaluable pairs), and 41.7% is the cross-agent PR-pair rate
(48/115). They are not pooled or averaged.

AgenticFlict [22] reports 27.7% textual conflict for a PR replayed against its
base. We report it as a distinct PR-to-base quantity. Mapping it to the same
formula requires an explicit estimate of `m2`, the number of concurrent edits
already landed in the base. Until that quantity is available, no p is
reported for this row.

The published rates are textual conflict rates, not semantic conflict rates;
the calibration therefore only positions the synthetic parameter against the
published textual workload. It does not validate the mechanism or infer
causality. Denominators and numerators are retained where the source reports
them. Missing source summaries remain blank rather than being guessed.

## Sensitivity and decision gate

For each of the two Xu rates, calculate p independently at the median, Q1 and
Q3 hunk counts (and separately at file-count values as an upper-bound
sensitivity). Compare the resulting interval with the synthetic scan
`0.0034–0.0687`. If every externally implied value is inside that scan, only
the existing aggregate cells are read and no simulation is rerun. If any
value is outside, a second reader must first approve the workload mapping and
the owner must approve at most ten additional cells with 30 seeds each.

The hold is released only after: (1) the source locations and denominators are
checked, (2) hunk/file sensitivity values are entered, (3)佛印's four-point
review passes, and (4) the coverage decision is recorded in this file. Until
then `calibration-results.csv` must report `pending workload summary`.
