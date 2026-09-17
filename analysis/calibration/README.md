# External workload range positioning

This directory positions published agentic pull-request conflict rates against
an effective per-cross-unit collision probability. It is a scenario-based
range-positioning exercise, separate from the first-order curves already
plotted in the main analysis; it is not an empirical calibration of the
synthetic parameter `p`.

The cited replication package contains `repo`, `prA`, and `prB` for all 747
rows, but not the frozen replay OIDs or final-diff hunk counts. The bounded
extractor in this directory therefore derives hunk and file counts from the PR
heads that GitHub can retrieve at extraction time. Its output is a
current-retrievable-subset sensitivity analysis, not an exact replay. No
simulation is rerun by these scripts.

Download the Xu et al. replication package from its archived record and pass
its `rq3_merge_replay_full.csv` to the read-only extractor:

```sh
python3 extract_pr_diff_counts.py \
  --pairs path/to/rq3_merge_replay_full.csv \
  --output pr-pair-diff-counts.csv \
  --log extraction-log.jsonl
```

The extractor validates the expected 747 input rows, pauses before the GitHub
core API budget falls below 500, records the API-reported head/base OIDs, the
actually fetched head OIDs and the computed merge-base OID, and uses the source
replay's depth-80/depth-600 fetch sequence. A head moving between the API call
and fetch is flagged rather than hidden. Temporary repositories are removed
after each pair. Diff bodies and conflicted paths are not written to the
output. Source rows already marked unavailable remain separate and are never
filled in.

After all rows are present, derive the workload and positioning tables:

```sh
python3 summarize_range_positioning.py \
  --source-pairs path/to/rq3_merge_replay_full.csv \
  --counts pr-pair-diff-counts.csv \
  --workload-summary workload-summary.csv \
  --positioning range-positioning.csv \
  --validation VALIDATION.json
```

The summary retains three pair-level textual-conflict readings instead of
silently choosing one: structural-inclusive, any conflict containing a content
component, and content-only. It propagates Wilson intervals and the observed
Q1/median/Q3 distribution of `m1*m2`. File products are a sensitivity reading;
hunk products are the main editor-unit reading.

The committed extraction result contains all 747 source keys: 715 pairs with
derived counts, 31 source-unavailable rows, and one additional current 404.
See `RESULTS.md` for the held interpretation and `VALIDATION.json` for the
mechanical checks. The result remains under second-eye review and must not be
described as calibration or validation.

The earlier scenario-only calculator remains available:

```sh
python3 calibration.py --input published-rates.csv --output calibration-results.csv
```

The script reports one effective `p_eff` value for each published rate and
each explicitly supplied editor-unit scenario. It never combines the 19.8%
and 41.7% Xu et al. rates. AgenticFlict's PR-to-base rate is reported
separately because its second side is an observed or reconstructed base, not
another PR.
