# External workload range positioning

This directory positions published agentic pull-request conflict rates against
an effective per-cross-unit collision probability. It is a scenario-based
range-positioning exercise, separate from the first-order curves already
plotted in the main analysis; it is not an empirical calibration of the
synthetic parameter `p`.

The current artifact is an input-and-assumptions package. A feasibility check
confirmed that the cited replication package contains `repo`, `prA`, and `prB`
for all 747 rows, and that the GitHub API is reachable for PR head/base
metadata; see `FEASIBILITY.md`. The cited papers and
their replication packages do not provide the required final-diff hunk
distribution for the exact replay samples, so `m1` and `m2` remain pending.
No simulation is rerun by the calibration script.

Run:

```sh
python3 calibration.py --input published-rates.csv --output calibration-results.csv
```

The script reports one effective `p_eff` value for each published rate and
each explicitly supplied editor-unit scenario. It never combines the 19.8%
and 41.7% Xu et al. rates. AgenticFlict's PR-to-base rate is reported
separately because its second side is an observed or reconstructed base, not
another PR.
