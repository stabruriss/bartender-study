# External workload calibration

This directory maps published agentic pull-request conflict rates to the
per-edit overlap probability used by the synthetic study. It is an external
calibration, separate from the first-order curves already plotted in the main
analysis.

The current artifact is an input-and-assumptions package. The hunk/file
summaries needed to instantiate `m1` and `m2` are recorded as pending until
they are transcribed from the cited papers and checked by a second reader.
No simulation is rerun by the calibration script.

Run:

```sh
python3 calibration.py --input published-rates.csv --output calibration-results.csv
```

The script reports one p interval for each published rate and each supplied
editor-unit sensitivity case. It never combines the 19.8% and 41.7% Xu et al.
rates. AgenticFlict's PR-to-base rate is reported separately because its second
side is a concurrent landed base rather than another PR.
