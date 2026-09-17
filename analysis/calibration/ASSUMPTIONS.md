# External range-positioning assumptions and hold points

Status: **Scoped PASS for current-retrievable scenario positioning**. Full
current retrieval remains false because one source-clean pair now returns 404.
This status is bound to the reviewed source, count, cell and summary hashes in
`VALIDATION.json`; changed inputs automatically return to `UNREVIEWED/HOLD`.

This is **scenario-based range positioning**, not empirical calibration. The
output is an effective per-cross-unit collision probability (`p_eff`) under a
strong independence mapping; it must not be called the Bartender simulation's
`p`.

The positioning uses the independent-edit approximation

`q_pair = 1 - (1 - p_eff)^(m1*m2)`.

Here `p_eff` is the effective collision probability under this mapping and
`m1`, `m2` are
counts of edit units in the two sides. An edit unit would be a changed
hunk, because a hunk is closer to the model's line-range edit than a whole
file. Changed-file products provide a coarser alternative-unit sensitivity;
they are not an unconditional upper bound on edit counts or `p_eff`.
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

The rates are selected-repository-pair readings, not pair-weighted rates over
all 580,913 co-active pairs. The same-type/model stratum starts from 625 seeded
repositories; the cross-type/model stratum uses all 122 eligible repositories.
Each stratum takes the first qualifying co-active pair per repository. Wilson
intervals therefore describe only this selected sample and its sampling
convention.

AgenticFlict [22] reports 29,609/107,026 (27.67%) textual conflict for a PR
replayed against its observed or reconstructed base. We report it as a
distinct PR-to-base quantity. Mapping it to the same formula requires an
explicit assumed effective `m2`, the number of base-side landed edits between
the merge base and that base revision; [22] does not report it. Until that
quantity is separately reconstructed or declared as a sensitivity scenario,
no `p_eff` is reported for this row.

The published rates are textual conflict rates, not semantic conflict rates.
The structural-inclusive reading includes modify/delete and add/add events and
is the broad scope. “Conflict with any content component” is closest to the
simulation's at-least-one line-range overlap, though mixed structural/content
events and Git merge semantics still prevent equivalence. “Content-only” also
requires the PR pair to contain no structural conflicted file, so it is a
strict event-definition lower sensitivity rather than an exact line-overlap
counterpart. The positioning does not validate the mechanism, identify the
synthetic parameter, or infer causality. Denominators and numerators are
retained where the source reports them. Missing source summaries remain blank
rather than being guessed.

## Unit-free positioning

The per-hunk inversion depends strongly on the edit unit: the observed PRs
contain many more hunk pairs than one synthetic edit per agent per interval.
For each observed hunk-product Q1, median and Q3, we therefore report the
independent-Bernoulli expected overlap count
`E = N*p_eff = N*[1-(1-q)^(1/N)]`. Wilson intervals for `q` are propagated by
the same monotone transform and labeled transformed intervals.

The quantity `-ln(1-q) = -N*ln(1-p_eff)` is retained only as the
Poisson-equivalent hazard. It converges to `E` when `p_eff` is small; the output
reports their point difference rather than assuming equality. The first-order
synthetic counterpart per agent pair and synchronization interval is
`p*(lambda*tau)^2`. The numerical comparison uses the fixed-`N`
independent-Bernoulli mapping plus an event-definition and workload-scale
analogy. The Poisson/rare-event limit is used only to interpret `-ln(1-q)`, not
to compute `E` or target `tau`. The Figure 5 rate divides the model quantity by
`tau` and sums over the `C(n,2)` agent pairs.

This comparison removes the arbitrary hunk unit but not the independence,
event-definition analogy, textual-conflict, current-head or workload-selection
assumptions. It
also distinguishes the continuous parameter envelope from the 21 actually
sampled `(p,tau)` points. A target `tau` inside the envelope is not an observed
cell unless that exact `tau` occurs in `cells.json`; nearest and bracketing
cells are labeled as such and are never interpolated into a reported outcome.

## Sensitivity and decision gate

For each of the two Xu rates, `p_eff` is calculated independently at the
median, Q1 and Q3 hunk products across all currently retrievable pairs,
including zero products, and separately at file-product values as a
sensitivity. A selected zero quantile would be marked non-invertible; no
reported Q1, median or Q3 is zero here. The result is compared with the synthetic scan
`0.0034–0.0687`. Some scenarios are below the scan. This observation does not
authorize a rerun: a second reader must first approve the workload mapping and
decide whether any additional cells are scientifically useful; the owner must
then approve at most ten additional cells with 30 seeds each.

The scientific review gate is complete: source locations and denominators,
exact-row-key current-head final-diff hunk/file sensitivities, interval
transforms and accepted-grid lookups passed independent second-eye review. No
additional simulation cell is added because the existing grid already
separates continuous-envelope coverage, exact interval hits and bracketing;
post-hoc target-`tau` sampling would not turn this analogy into calibration or
validation. The legacy scenario calculator remains blank and points readers
to `range-positioning.csv`.

## Execution gate

The bounded read-only extraction was approved on 16 September 2026 with these
conditions: public repositories only; pause below 500 remaining GitHub core API
requests; record current head/base/merge-base OIDs, retrieval time, Git version
and diff parameters; retain counts and OID metadata rather than diff contents;
keep the 31 source-unavailable rows separate; and obtain second-eye review
before pushing the result branch. The implementation follows the source
replay's depth-80 fetch with a depth-600 retry and fixes the diff algorithm and
rename setting explicitly. The scientific review is complete; the mechanical
full-retrieval field remains false solely because of the recorded current 404.

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
and 5 zero-product cross-type/model pairs. They remain in both the workload
table and the full-distribution quantiles so that the `N` support matches the
published `q` denominator as closely as current retrieval permits. Only a
selected quantile that itself equals zero would be non-invertible. This
handling is stated in `VALIDATION.json`, `workload-summary.csv` and
`RESULTS.md`.

Review resolution: an independent second reviewer accepted the 747-key and
field mapping, current-head scope, three conflict definitions and denominators,
full-distribution quantiles, Wilson interval propagation, dimensionless
transformation, accepted-grid lookup and scan-coverage wording. No additional
simulation was run or approved.
