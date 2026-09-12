# Analysis of the accepted study-01 delivery

Maintainer analysis, draft figures for manuscript Section 6.2. Execution and
fixed application conformance were accepted in `ANSWERS.md`; the evidence is
`validation/delivery-acceptance-m1.json`. This directory is outside the frozen
execution protocol. It changes no model, configuration, approval or original
delivery. The execution agent has no analysis task.

## Reproduce

Use CPython 3.12.4 and a separate analysis environment. Do not install plotting
dependencies into the study runtime environment.

```sh
.venv/bin/python -m venv local-logs/analysis-venv
local-logs/analysis-venv/bin/python -m pip install -r analysis/requirements.lock
local-logs/analysis-venv/bin/python analysis/make_figures.py
local-logs/analysis-venv/bin/python analysis/make_manuscript_figures.py
```

The script reads precisely three delivery inputs, checks their accepted hashes
before and after analysis, and imports no simulation module:

- `deliverables/study-01/summary.csv`: the 34,650 cell/metric aggregates.
- `deliverables/study-01/paired-differences.csv`: the 11,010 paired contrasts.
- `deliverables/study-01/cells.json`: approved coordinate metadata only.

The two CSVs are the only scientific observations. The grid supplies nominal p,
μ, times, policies and slice labels, and the unfit first-order curves. There is
no access to `outputs/`, individual run files, or diagnostic per-seed summaries.
The earlier acceptance review used the transferred summaries only to verify
the delivered CSVs; that is separate from these analyses.

## Current manuscript displays

`make_manuscript_figures.py` imports the accepted-input reader from
`make_figures.py` and writes a separate `manuscript/` directory. It does not
regenerate or alter the original full-scan outputs below. Its manifest records
both script hashes, the three accepted input hashes, and every new artifact.

| File | Content |
|---|---|
| `manuscript/fig4_repairs_overlap.pdf` / `.svg` | Both policies, all five agent/dependency slices. Logarithmic axes retain every positive mean and supplied interval. High-overlap labels divide the in-place mean by the Bartender mean. |
| `manuscript/fig5_sync_interval.pdf` / `.svg` | Relocation 0 only; three rows separate overlap pairs, first conflicts, and overlap size. The first-order prediction applies only to the overlap-pair row. |
| `manuscript/fig6_wait_resolved.pdf` / `.svg` | Initial conflicts resolved by the window end, two baseline timings. Immediate dispatch is labeled; the 64-line zero-wait value is 99.7622%, not exactly 100%. |
| `manuscript/fig7_wait_failures.pdf` / `.svg` | Failed completed attempts divided by completed attempts, with the two unfitted nominal failure probabilities. |
| `manuscript/repair-reference.csv` | Three overlap values, four agents, no dependency, both policies; means and original intervals. |
| `manuscript/repair-paper-table.csv` | The paper's seven repair comparison rows; original intervals and paired differences retained. |
| `manuscript/repair-all-five-slices.csv` | All fifteen reference combinations, including the five high-overlap ratios. |
| `manuscript/wait-reference.csv` | All 36 requested waiting combinations; ratios, nominal predictions and original component intervals. |
| `manuscript/table4-repair-rows.tex`, `manuscript/table5-wait-rows.tex` | Reproducible rounded rows for the two numerical manuscript tables. |
| `manuscript/NUMBERS.md` | Descriptive numbers, the three complete waiting tables, and interpretation limits. |

The relocation knob did not deliver a consistent reduction in conflicts in
this scan. Its three settings and their numerical differences remain in the
full tables and supplementary atlases. The 2026-09-11 manuscript display
revision removes those extra lines from the main synchronization figure and
splits the waiting outcomes from their mechanism comparison. It does not
discard the original expectations, negative results, or scanned settings.
The earlier combined waiting figure, including completed repairs per initial
conflict, is retained as supplementary material. No new simulations were run.

## Original outputs and full-scan supplements

`results/` contains editable SVG and vector PDF figures, the generating script
is `make_figures.py`, and `analysis-manifest.json` records input/output hashes
and the plotting environment.

| File | Content |
|---|---|
| `f1_repairs_overlap.pdf` / `.svg` | Repair starts and total observed repair effort versus nominal p; all five agent/dependency slices; reference avoidance 0 and synchronization interval 1. |
| `f2_sync_interval.pdf` / `.svg` | Overlap-pair rate, first-conflict rate and overlap lines at first conflict versus synchronization interval; all three avoidance values, all three p values; reference Bartender, four agents, no dependency. |
| `f3_attempts_and_landings.pdf` / `.svg` | Completed-attempt failure fraction, initial-cohort landings by cutoff, and completed repairs per initial conflict; three p facets, two snapshot timings; reference four agents, no dependency/avoidance, fixed repair time. |
| `table1_reference.pdf` / `.svg` / `table1-reference.csv` | Fifteen reference p and agent/dependency combinations, both policies' repair/effort means and intervals, and exact paired repair differences. |
| `all-cell-results.csv` | Every one of the 990 cells and 35 metrics, with original means/intervals/n and coordinate metadata; no cell or negative result excluded. |
| `all-paired-results.csv` | Every supplied paired contrast, with original interval and metadata. Differences are Bartender minus in-place repair. |
| `dispatch-ratios.csv` | Finite-window pooled dispatch ratio, original numerator/denominator intervals, and explicit unavailable ratio-interval fields. |
| `attempt-failures-and-censoring.csv` | All delay cells' completed-attempt failures, nominal q where identifiable, window budgets and zero-dependency initial-cohort accounting. |
| `NUMERIC_SUMMARY.md` / `.pdf`, `numeric-summary.json` | One-page descriptive numerical summary and machine-readable values. |
| `MECHANISM_CHECK.md` | Every-dispatch waiting semantics, observed failure rates, finite-window capacity and limits on tail correction. |

Display slices are layout choices made after collection, not new run parameters
or a preregistered figure selection. The supplementary atlases enumerate all
remaining settings without choosing by observed direction: F1 has 21 pages
(three avoidance values × seven intervals, every page containing all five
agent/dependency slices); F2 has 10 (five slices × both policies); F3 has 10
(five delay slices × both clocks). No additional scan was run.

## Quantities and intervals

F1 counts author repair **starts**, including a repair begun but unfinished at
cutoff. Observed repair effort includes the completed fraction of any repair
in progress. This abstract model effort is not wall time, tokens, human effort
or product latency. F2 first-conflict rate counts a patch once when it first
fails to apply, divided by the model horizon. Overlap-pair rate counts pairs,
not conflicts; only this first row is compared with C(n,2)pλ²τ, and only on
zero-dependency slices with the zero-avoidance series as the comparison.
The p coordinate is nominal, before the avoidance mechanism alters footprints.

All supplied pointwise intervals are mean ± 1.96 × sample SD / √n. They describe
variation across independent seeds, use a normal approximation and are not
adjusted for multiple comparisons. The original values are retained, including
any bounds outside a parameter's natural range. Of 34,650 aggregate rows, 673
have n<30, including 30 with n=0. Conditional metrics exclude undefined seeds;
an absent mean stays absent, never becomes zero. In particular, mean conflict
size is a mean of per-seed conditional means, not a pooled mean over patches.

F3 ratios pool the seed totals. Since their underlying counts each have n=30,
the ratio of their means equals the ratio of their totals. It is not the mean
of per-seed ratios. These aggregate inputs do not identify the covariance or
distribution required for a ratio interval. No interval is invented; original
component intervals remain in the full tables. Specifically:

- Failure fraction = failed completed repairs / completed repairs. At zero
  dependency these failures are overlap collisions. Completed attempts are
  selected by the queue and cutoff; their observed rate is not automatically
  the stationary probability of an independent future attempt.
- At zero dependency, initial conflicts landed by cutoff = completed repairs
  minus failed completed repairs. Conflict footprints do not disappear or
  become mechanically clean without a successful repair in this case. Divide
  by the initially conflicting cohort. With dependency, mechanical rescue
  after earlier repair is not fully separated in the aggregate fields; the
  cohort's landed fraction is marked unidentified, not inferred from total
  landed edits or filled with zero.
- Completed repairs per initial conflict is a finite-window quantity with
  unfinished and undispatched work at cutoff. It is explicitly labeled censored.

The window is held fixed over δ within each p/agent slice, and follows the
approved max(256, 32/μ) rule; it is not equal across all p values. Both snapshot
variants use δ/(1/μ) horizontally. With the fixed clock R=0.25, the dispatch-time
snapshot has collision exposure E=δ+R and re-reading at start has E=R. At δ=0
both therefore use E=R. The vertical line at one characteristic time is not a
threshold. Context-clock actual durations are not present in the CSVs, so those
supplement pages use δ and do not overlay an exposure-based prediction.

## Recorded analysis adjustment, 2026-09-09

The initial draft compared the observed finite-window dispatches per initial
conflict with the uncensored geometric expectation exp(μE). Source inspection
confirmed that δ is paid at **every** dispatch. At large δ the single repair
slot and fixed observation window permit only a small number of attempts in
total. The available pooled count therefore does not identify the uncensored
mean; the >5-ejections-and-unlanded fraction also is not the full censored cohort.

Following maintainer review, the exponential-mean overlay and its draft figure
were withdrawn for incompatible quantities, not removed because of curve
direction. Final F3 instead compares observed completed-attempt failure rates
with the nominal q=1−exp(−μE) and reports finite-window landings and completed
repairs separately. No model, parameter, observations or predicted values were
fitted or changed. This does **not** establish the independent collision law,
disprove the geometric law, or quantify the missing tail's contribution. The
uncensored dispatch-count distribution and a finite tail-correction upper bound
remain unidentifiable from these inputs. Any further analysis of retained
individual histories requires a separate scope decision.

The study stays private pending the existing publication and history-audit
process. This draft analysis is not a publication or repository visibility change.
