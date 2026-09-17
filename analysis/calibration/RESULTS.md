# External workload range-positioning result

Status: **Scoped PASS for current-retrievable scenario positioning**. Full
current retrieval remains false because one source-clean pair now returns 404.
Date: 2026-09-16/17 UTC.

This is a scenario-based range-positioning exercise. It is not an empirical
calibration or validation of the simulation, and `p_eff` below is not the
simulation parameter `p`.

## Extraction and identity

The input is the 747-row Xu et al. replay sample. Its SHA-256 is
`a6a3f3e88f6b8445a07d5b43bb8c6d4583cfffb33bd25f650a766a096baaef3c`.
The derived count table has the same 747 unique pair keys, with no missing,
extra or duplicate key. It contains 715 currently retrievable pairs, the 31
rows already unavailable in the source package, and one additional current
404: `kiwicom/orbit` PR 4567 in the clean same-type/model pair 4567/4572.
No API-head/fetched-head OID drift occurred among the 715 derived pairs.

The available pairs were retrieved between 2026-09-16 23:32:04 UTC and
2026-09-17 00:12:50 UTC with Apple Git 2.50.1. The table records the current
head and base OIDs, computed merge-base OID, retrieval time and fixed fetch and
diff settings for every derived pair. The source package does not contain the
frozen replay OIDs, so these counts describe the currently retrievable heads,
not an exact replay of the source study. The count-table SHA-256 is
`667db8c0c82776a6250a47ff9e58174e1a446eb3330992ff67dcebf81a9d95e8`.

## Source rates and workload sizes

The original denominators remain 601 evaluable same-type/model pairs and 115
evaluable cross-type/model pairs. Structural-inclusive conflict is 119/601
(19.80%, Wilson 95% interval 16.81%–23.17%) and 48/115 (41.74%,
33.14%–50.88%), respectively. Conflict with any content component is 107/601
(17.80%, 14.95%–21.06%) and 47/115 (40.87%, 32.32%–50.01%); this is the
closest available scope to at-least-one line-range overlap, but remains a Git
textual-conflict outcome. Content-only is the stricter event-definition lower
sensitivity at 88/601 (14.64%, 12.04%–17.69%) and 36/115 (31.30%,
23.55%–40.27%); it excludes mixed structural/content events.

These are selected-repository-pair rates. The same-type/model stratum begins
with 625 seeded repositories and the cross-type/model stratum uses all 122
eligible repositories, selecting the first qualifying co-active pair per
repository in each stratum. They are not pair-weighted rates over all 580,913
co-active pairs, and the Wilson intervals apply only to this selected sample.

For hunk products `N = m1*m2`, the all-pair Q1/median/Q3 values are
4/59/880 across 600 retrievable same-type/model pairs and
295/2,972/19,442 across 115 cross-type/model pairs. These quantiles include
the 75 and 5 zero-product pairs, respectively, so their support remains as
closely aligned with the published-rate population as current retrieval
permits. The same-type/model `q` denominator has 601 pairs while `N` has 600
because of the new 404, and the retrieved heads are not frozen source-study
OIDs. None of the selected quantiles is zero.
File-product sensitivity values are 2/12/91 and 31.5/252/1,661; files are a
coarser alternative unit, not an unconditional upper bound.

## Range position

Under `q = 1 - (1 - p_eff)^N`, the main hunk-product readings are:

| Stratum and outcome | N scenario | p_eff (Wilson-mapped interval) | Position vs scan 0.003435–0.06872 |
|---|---:|---:|---|
| same type/model, structural-inclusive | Q1 4 | 0.05367 (0.04497–0.06378) | inside |
| same type/model, structural-inclusive | median 59 | 0.003733 (0.003115–0.004458) | partly overlaps |
| same type/model, content-only | Q1 4 | 0.03881 (0.03156–0.04751) | inside |
| same type/model, content-only | median 59 | 0.002680 (0.002172–0.003295) | below |
| cross type/model, structural-inclusive | Q1 295 | 0.001830 (0.001364–0.002407) | below |
| cross type/model, structural-inclusive | median 2,972 | 0.0001818 (0.0001354–0.0002391) | below |
| cross type/model, content-only | Q1 295 | 0.001272 (0.0009098–0.001745) | below |
| cross type/model, content-only | median 2,972 | 0.0001263 (0.00009035–0.0001734) | below |

All hunk-product Q3 readings are below the scan. In the file-product
sensitivity, the same-type/model medians and cross-type/model Q1 readings are
inside; same-type/model Q1 is above or partly above, and the remaining medians
and Q3 readings are below. Thus, median-and-larger hunk scenarios lie at the
low end or below, while same-type/model Q1 scenarios lie inside the scanned
continuous `p` envelope. The envelope is not a claim that every `p` value was
sampled as a discrete cell. This statement positions ranges only;
clustered edits, structural conflicts, current rather than frozen heads, and
the unavailable rows prevent direct parameter identification.

## Expected overlap pairs per concurrent work-unit pair

To reduce dependence on the hunk unit, the second output uses the independent
Bernoulli expectation
`E = N*p_eff = N*[1-(1-q)^(1/N)]`. Wilson intervals for `q` are transformed
through the same monotone formula. The Poisson-equivalent hazard
`-ln(1-q)` is shown only as a small-`p_eff` limit. This compact table uses the
broad structural-inclusive scope:

| Stratum | N scenario | E (transformed 95% interval) | −ln(1−q) | E minus hazard |
|---|---:|---:|---:|---:|
| same type/model | Q1 4 | 0.214675 (0.179880–0.255124) | 0.220651 | −0.005975 |
| same type/model | median 59 | 0.220239 (0.183763–0.263035) | 0.220651 | −0.000412 |
| same type/model | Q3 880 | 0.220623 (0.184031–0.263584) | 0.220651 | −0.000028 |
| cross type/model | Q1 295 | 0.539745 (0.402238–0.709969) | 0.540240 | −0.000494 |
| cross type/model | median 2,972 | 0.540190 (0.402485–0.710740) | 0.540240 | −0.000049 |
| cross type/model | Q3 19,442 | 0.540232 (0.402508–0.710812) | 0.540240 | −0.000008 |

For the “any content component” scope, which is closer to the simulation
event, median-`N` `E` is 0.195734 (0.161740–0.236055) for same type/model and
0.525378 (0.390375–0.693225) for cross type/model. The stricter content-only
median readings are 0.158107 and 0.375461. All Q1/median/Q3 scopes and
transformed intervals remain in `dimensionless-positioning.csv`.

The numerical comparison of external `E` with the model quantity
`p*(lambda*tau)^2` uses the fixed-`N` independent-Bernoulli mapping plus an
event-definition and workload-scale analogy. The Poisson/rare-event limit is
used only to interpret `-ln(1-q)`, not to compute `E` or target `tau`. At median
`N`, the external point corresponds to
`tau` 8.01/3.76/1.79 for the three scanned `p` values in the same-type/model
stratum, and 12.54/5.89/2.80 in the cross-type/model stratum. All target values
are inside the study's continuous `tau` range, but the discrete grid contains
only 0.125, 0.25, 0.5, 1, 2, 8 and 32. It therefore has one exact interval hit
for the same-type/model structural reading (`p=0.003435`, `tau=8`) and no exact
hit for the cross-type/model structural reading. The latter is bracketed by
sampled cells; it must not be described as directly observed at the target.

Selected relevant accepted Figure 5 cells give these three observed means across
30 seeds; full intervals and all 21 cells are in `sync-grid-positioning.csv`:

| Cell | p | tau | p*(lambda*tau)^2 | Overlap pairs/time | First conflicts/time | Lines at first conflict |
|---|---:|---:|---:|---:|---:|---:|
| `cc3faf54a13c1e38` | 0.003435 | 8 | 0.219844 | 0.1500 | 0.1438 | 2.300 |
| `e2d2846d32941999` | 0.003435 | 32 | 3.517505 | 0.6014 | 0.4870 | 2.402 |
| `8e389ad71c19e48e` | 0.015562 | 2 | 0.062249 | 0.1833 | 0.1768 | 8.296 |
| `a7a47b831a79b459` | 0.015562 | 8 | 0.995988 | 0.6762 | 0.5760 | 8.672 |
| `0573c77147ccd4ce` | 0.068723 | 2 | 0.274893 | 0.8173 | 0.6698 | 36.684 |

Accordingly, median-and-larger per-hunk scenarios lie at the scan's low end or
below it, while same-type/model Q1 scenarios lie inside the continuous
envelope. The expected-overlap view places the external points inside
the continuous `(p,tau)` parameter envelope; the sampled grid exactly covers
the same-type/model broad and any-content intervals. For cross type/model it
brackets both the broad and the closest any-content intervals; only the strict
content-only sensitivity has an exact sampled-grid hit. Neither view is a
calibration or validation.

Result 1 fixes `tau=1` and has one expected edit per agent per interval. A
larger integration unit creates more cross-unit pair opportunities at the same
per-hunk probability. This unit dependence does not change any Result 1
number; it belongs in the threats-to-validity interpretation.

## Review status

No supplementary simulation cell was run. Independent second-eye review
accepted the row and field mapping, conflict scopes, full-distribution
quantiles, transformed intervals, modeled-count analogy, accepted-grid lookup
and stated current-head boundary. No target-`tau` cells are added: they would
be post-hoc samples and would not remove the mapping and selection limits.
