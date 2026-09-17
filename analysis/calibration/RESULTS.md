# External workload range-positioning result

Status: **HOLD pending second-eye review**. Date: 2026-09-16/17 UTC.

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
33.14%–50.88%), respectively. The content-only readings are 88/601 (14.64%,
12.04%–17.69%) and 36/115 (31.30%, 23.55%–40.27%). The intermediate
“any content component” readings remain in `range-positioning.csv`.

For hunk products `N = m1*m2`, the positive-pair Q1/median/Q3 values are
12/102/1,292 for 525 of 600 retrievable same-type/model pairs, and
492/3,407/19,798 for 110 of 115 cross-type/model pairs. The remaining 75 and
5 pairs have zero hunk product and are reported but excluded from inversion,
because the mapping requires positive `N`. File-product sensitivity values are
4/19/121 and 39.25/453/1,751.5.

## Range position

Under `q = 1 - (1 - p_eff)^N`, the main hunk-product readings are:

| Stratum and outcome | N scenario | p_eff (Wilson-mapped interval) | Position vs scan 0.003435–0.06872 |
|---|---:|---:|---|
| same type/model, structural-inclusive | Q1 12 | 0.01822 (0.01522–0.02173) | inside |
| same type/model, structural-inclusive | median 102 | 0.002161 (0.001803–0.002581) | below |
| same type/model, content-only | Q1 12 | 0.01311 (0.01063–0.01610) | inside |
| same type/model, content-only | median 102 | 0.001551 (0.001257–0.001907) | below |
| cross type/model, structural-inclusive | Q1 492 | 0.001097 (0.000818–0.001444) | below |
| cross type/model, structural-inclusive | median 3,407 | 0.0001586 (0.0001181–0.0002086) | below |
| cross type/model, content-only | Q1 492 | 0.0007629 (0.0005456–0.001047) | below |
| cross type/model, content-only | median 3,407 | 0.0001102 (0.00007881–0.0001512) | below |

All hunk-product Q3 readings are below the scan. In the file-product
sensitivity, all Q1 readings and the same-type/model medians are inside the
scan; the cross-type/model medians and all Q3 readings are below it. Thus the
scan covers some small-changeset scenarios, while the independence mapping for
median and larger hunk products yields lower effective per-pair probabilities.
This statement positions ranges only; clustered edits, structural conflicts,
current rather than frozen heads, and the unavailable rows prevent a direct
parameter identification.

## Gate

No supplementary simulation cell has been run. Scientific use and any rerun
decision remain on hold until the second reader accepts the row mapping,
conflict scopes, positive-product quantiles, Wilson propagation and stated
current-head boundary.
