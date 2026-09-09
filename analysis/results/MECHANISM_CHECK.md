# F3 mechanism and observable limits

Static source facts (unchanged study model):

1. Every call to `_dispatch` schedules repair start at current time plus δ for kick-back (`bartender_sim/model.py:301–307`). There is no first-dispatch exception. Failed repair completion clears the repair slot and requests another sync (`:393–411`), which dispatches through the same function (`:335–340`).
2. Completed-repair failure fraction below is the pooled sum of failed completions divided by completed repairs. It excludes scheduled mechanical apply failures and uncompleted attempts. With zero dependency, these failures are overlap collisions. It does not establish independence or a stationary probability for all future attempts.
3. No extra drain follows the fixed cutoff (`:429–446`). More than five ejections and still unlanded is a subset of right censoring, not its full extent. In the zero-dependency, fixed-footprint model, a detected conflict cannot disappear before a successful repair: subtracting successful repair completions from the initial-conflict count identifies the unlanded initial cohort. This identity is not applied to dependency cases.

Reference: four agents, zero dependency/avoidance, fixed repair time 0.25, post-dispatch wait 4/μ. All observed values are computed from the accepted CSV counts; model probabilities and window budgets use only approved grid metadata.

| Baseline read | p | Completed repair failures / completions | Nominal q | Pooled dispatches / initial conflict | Pooled initial conflicts unlanded | Seed-mean >5 ejections, unlanded | H/(δ+R) |
|---|---:|---:|---:|---:|---:|---:|---:|
| dispatch | 0.003435 | 0.83732 | 0.98173 | 1.927 | 72.58% | 6.22% | 7.995 |
| dispatch | 0.015562 | 0.78365 | 0.98190 | 1.763 | 66.67% | 6.11% | 7.977 |
| dispatch | 0.068723 | 0.72928 | 0.98260 | 2.063 | 48.42% | 4.48% | 13.027 |
| start | 0.003435 | 0.00478 | 0.00257 | 0.802 | 30.20% | 0.00% | 7.995 |
| start | 0.015562 | 0.00962 | 0.01160 | 0.804 | 30.41% | 0.00% | 7.977 |
| start | 0.068723 | 0.01657 | 0.05024 | 0.871 | 20.89% | 0.00% | 13.027 |

Each completed attempt occupies δ+R in the fixed-clock single repair slot. Thus H/(δ+R) bounds the total number of completed attempts per seed across all conflicts, not attempts per conflict. For the three reference p values this permits at most 7, 7 and 13 completions, respectively; without dependency rescue there can be at most one additional pending dispatch at cutoff. This is a within-window scheduling bound, not a bound on the missing future tail.

**No finite, data-supported upper bound on the uncensored mean correction is identifiable from the aggregate inputs.** The undispatched or repeatedly ejected conflicts can require an unknown number of future attempts; the aggregate files contain neither their individual histories nor their unobserved future. The >5 subgroup's observed contribution cannot be isolated from these CSVs either. A geometric continuation, stationary q, independence, or a guaranteed finite future horizon would be additional assumptions, not measured corrections. Therefore the finite-window ratio is not a direct estimate of the uncensored geometric mean exp(μE); the original exponential-mean overlay was withdrawn for incompatible estimands. Revised F3 compares observed completed-attempt failures with nominal q and shows finite-window landings separately; it is not a fitted survival estimate.

No simulation, parameter, approval, original output or first-order formula has been altered or fitted. Full dispatch-count distributions remain a separately scoped analysis decision.
