# Numerical display summary

All observations come from accepted study-01 aggregates. No simulations were run.

## Repair comparison

Reference: four agents, no dependency or relocation, synchronization interval 1. Means over 30 seeds.

| Edit lines | Nominal overlap | Repair starts: Bartender / in-place | Repair work: Bartender / in-place |
|---:|---:|---:|---:|
| 4 | 0.0034351 | 4.87 / 4.97 | 8.51 / 8.54 |
| 16 | 0.0155623 | 24.37 / 26.93 | 41.18 / 45.44 |
| 64 | 0.0687233 | 100.70 / 281.07 | 176.48 / 2136.92 |

At high overlap, the in-place/Bartender work ratio is 12.1 for four agents and 28.8 for eight agents, both without dependency. All five slices, including their small reversals and supplied intervals, remain in Figure 4. Ratios divide means; no ratio interval or significance claim is inferred.

## Waiting: all three overlaps

Four agents, no dependency or relocation, fixed repair time 0.25. Values pool the 30 seeds. Each row reports the share of initial conflicts resolved by the cutoff and the failure share among completed repair attempts, in percent.

### 4-line edits

| Wait, in 1/μ | Dispatch: resolved % | Dispatch: failed % | Re-read: resolved % | Re-read: failed % |
|---:|---:|---:|---:|---:|
| 0 | 100.00 | 0.00 | 100.00 | 0.00 |
| 0.25 | 97.36 | 10.09 | 97.61 | 0.24 |
| 0.5 | 94.35 | 18.55 | 95.34 | 0.16 |
| 1 | 87.01 | 34.24 | 91.04 | 0.22 |
| 2 | 68.86 | 55.48 | 83.24 | 0.00 |
| 4 | 27.42 | 83.73 | 69.80 | 0.48 |

### 16-line edits

| Wait, in 1/μ | Dispatch: resolved % | Dispatch: failed % | Re-read: resolved % | Re-read: failed % |
|---:|---:|---:|---:|---:|
| 0 | 100.00 | 0.00 | 100.00 | 0.00 |
| 0.25 | 97.27 | 9.46 | 97.51 | 0.51 |
| 0.5 | 94.17 | 19.04 | 95.21 | 0.50 |
| 1 | 86.98 | 32.52 | 90.88 | 0.44 |
| 2 | 68.09 | 56.56 | 83.02 | 0.45 |
| 4 | 33.33 | 78.37 | 69.59 | 0.96 |

### 64-line edits

| Wait, in 1/μ | Dispatch: resolved % | Dispatch: failed % | Re-read: resolved % | Re-read: failed % |
|---:|---:|---:|---:|---:|
| 0 | 99.76 | 0.00 | 99.76 | 0.00 |
| 0.25 | 98.18 | 12.51 | 98.35 | 2.38 |
| 0.5 | 96.21 | 18.55 | 96.61 | 2.25 |
| 1 | 91.49 | 32.49 | 93.92 | 1.91 |
| 2 | 81.21 | 47.64 | 88.65 | 1.21 |
| 4 | 51.58 | 72.93 | 79.11 | 1.66 |

At zero wait the resolved fractions are 100%, 100%, and 99.7622% for 4-, 16-, and 64-line edits respectively, for both read timings. At the longest wait, dispatch-time reading resolves 27.4–51.6%; re-reading resolves 69.6–79.1%. Completed-attempt failure fractions are 72.9–83.7% and 0.5–1.7%, respectively.

The window is max(256, 32/μ), held fixed across waiting values within each overlap slice. The queue and cutoff select which attempts complete. These are finite-window proportions, not mean completion times or an uncensored geometric mean. Nominal q is an unfitted comparison, not a verified independent-attempt probability.

`wait-reference.csv` retains all three component means, seed counts, and supplied 95% intervals. The resolved numerator is completed minus failed attempts; its interval and ratio intervals cannot be recovered without covariance. `repair-paper-table.csv` contains all seven repair rows used in the paper, with exact means, supplied intervals, and paired differences.

## Synchronization interval

Figure 5 shows only relocation 0. The overlap-pair rate and first-conflict rate rise over the seven synchronization intervals. First-conflict overlap grows for the longer edits; the short-edit series remains nearly flat. The first-order line is drawn only for overlap pairs. The full three-setting relocation scan remains in `../results/`, together with every original aggregate and paired result.
