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
  --cells ../../deliverables/study-01/cells.json \
  --study-summary ../../deliverables/study-01/summary.csv \
  --dimensionless dimensionless-positioning.csv \
  --sync-grid sync-grid-positioning.csv \
  --reference-cells dimensionless-reference-cells.csv \
  --validation VALIDATION.json
```

The summary retains three pair-level textual-conflict readings instead of
silently choosing one: structural-inclusive, any conflict containing a content
component, and content-only. It propagates Wilson intervals and the observed
Q1/median/Q3 distribution of `m1*m2`. File products are a sensitivity reading;
hunk products are the main edit-unit reading.

The “any content component” scope is the closest of the three to the
simulation's at-least-one line-range overlap, but is not identical to it.
Structural-inclusive is broader; content-only excludes mixed events and is a
strict event-definition lower sensitivity. The source rates select one first
qualifying pair per repository within each stratum, so their Wilson intervals
are not pair-weighted estimates over all co-active pairs.

The committed extraction result contains all 747 source keys: 715 pairs with
derived counts, 31 source-unavailable rows, and one additional current 404.
See `RESULTS.md` for the held interpretation and `VALIDATION.json` for the
mechanical checks. The result has scoped second-eye approval for
current-retrievable scenario positioning and must not be described as
calibration or validation.

`dimensionless-positioning.csv` reports the independent-Bernoulli expected
overlap count `E = N*p_eff = N*[1-(1-q)^(1/N)]` at the observed hunk-product
Q1, median and Q3. Wilson intervals for `q` are mapped monotonically through
the same formula and labeled transformed intervals. The file also reports
`-ln(1-q)` as a Poisson-equivalent hazard and the small difference between it
and `E`; the two agree only in the small-`p_eff` limit.

The first-order model counterpart is `p*(lambda*tau)^2` per agent pair in one
synchronization interval. The numerical comparison uses the fixed-`N`
independent-Bernoulli mapping plus an event-definition and workload-scale
analogy. The Poisson/rare-event limit is used only to interpret `-ln(1-q)`, not
to compute `E` or target `tau`. Dividing the model quantity by `tau` and
summing over agent pairs gives the Figure 5 rate
`C(n,2)*p*lambda^2*tau`.

`sync-grid-positioning.csv` reads all 21 accepted Figure 5 coordinate cells
for four agents, zero dependency and relocation, and the `clean_first`
selection convention. For each cell it records `p*(lambda*tau)^2` and the
accepted means and intervals for overlap-pair rate, first-conflict rate and
first-conflict overlap lines. `dimensionless-reference-cells.csv` identifies
the nearest sampled `tau` for every median-`N` conflict scope, stratum and
scanned `p` value. These are read-only lookups from the
accepted `cells.json` and `summary.csv`; no interpolation is reported as an
observation and no simulation is rerun.

The earlier scenario-only calculator remains available:

```sh
python3 calibration.py --input published-rates.csv --output calibration-results.csv
```

The script reports one effective `p_eff` value for each published rate and
each explicitly supplied edit-unit scenario. It never combines the 19.8%
and 41.7% Xu et al. rates. AgenticFlict's PR-to-base rate is reported
separately because its second side is an observed or reconstructed base, not
another PR.
