# Numerical summary — study-01, descriptive draft

All values below are generated from the accepted aggregate CSVs; p values are
0.003435, 0.015562, 0.068723 in ascending order. The reference display uses four agents,
zero dependency and zero avoidance unless stated otherwise.

**F1.** At synchronization interval 1, mean repair starts are
4.87, 24.37, 100.70 for Bartender and 4.97, 26.93, 281.07 for in-place repair;
mean observed effort is 8.51, 41.18, 176.48 and 8.54, 45.44, 2136.92, respectively.
Across all 315 paired synchronization cells, Bartender's mean repair count is
lower in 259, equal in 49 and higher in 7; these are signs of observed means, not significance decisions.

**F2.** For the largest p and zero avoidance, increasing the synchronization
interval from 0.125 to 32 changes observed overlap pairs per time from
0.0579 to 16.1236; the corresponding first-order line runs
from 0.0515 to 13.1949.
Mean first-conflict rate changes from 0.0552 to 2.1376
per time, and mean overlap size at first conflict from 33.78 to 56.75 lines.
At interval 32, the overlap-pair rates for avoidance 0, 0.5 and 0.9 are
16.1236, 16.1715, 16.3581 per time, respectively.

**F3.** At post-dispatch waiting time 4/μ with dispatch-time snapshots and a
fixed repair clock, completed-attempt failure fractions are
0.8373, 0.7837, 0.7293, against nominal q values
0.9817, 0.9819, 0.9826; re-reading at repair
start gives 0.0048, 0.0096, 0.0166 against
0.0026, 0.0116, 0.0502.
The pooled initial-conflict landing fractions at the window end are
27.42, 33.33, 51.58% for dispatch-time
snapshots and 69.80, 69.59, 79.11% for
re-reading; completed repairs per initial conflict are
1.685, 1.541, 1.905 and
0.701, 0.703, 0.804, respectively.

Coverage and statistical note: all 990 cells, 35 metrics and 11,010 paired
rows are retained. Of 34,650 aggregate rows, 673
have fewer than 30 nonmissing seed observations, including
30 with n=0. Source intervals are mean ±
1.96 × sample SD / √n, pointwise and unadjusted. F3 uses finite-window pooled
totals, not an uncensored expected number of rounds; a ratio interval and a
dispatch-count distribution cannot be recovered from these aggregate inputs.
Both variants use waiting time δ on the horizontal axis; the starting-point
baseline has E=R throughout. Both q curves use nominal μ without fitting.
The initial-conflict landing identity is used only at zero dependency.
