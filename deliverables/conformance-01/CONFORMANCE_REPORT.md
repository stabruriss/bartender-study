# Application conformance: conformance-01

Status: PASS. Fixed runbook assertions only; maintainer acceptance pending.

- Actual app version/build: 0.1.10 / 0.1.10.
- App executable SHA-256: `f458f54ae851f646e7f41686ba1a96022e832c3c7c1366d5be15fd8cf8863e6d`.
- Bundled CLI SHA-256: `50d942c9e542c3213999488928f2b7e3fd9f665c163ff2f020b4aeeef558b1a4`.
- Actual public commit: `75eb8fda2b1040c0f1822e0403321a105fec4f6c`.
- Source/setup review: Q-20260909-03, 2026-09-09T15:47:28Z; `conformance-review-m1.json`.
- Runbook SHA-256: `e5144353270d4833c494e47cb6c69c2200e3a3ed48e1038baf6763120bba640e`.
- Exact approval and version-report snapshots: `CONFORMANCE_APPROVAL.json` and `conformance-version-m4.json`.
- Observed requests: 2026-09-09T18:23:42Z through 2026-09-09T18:32:52Z; observation interval wall seconds: 550.0.
- CLI start/end times were recorded at one-second resolution. Wall seconds are derived from those UTC records and include observation/review gaps between requests; they are not performance measurements.
- All eight planned executions and sixteen distinct requests completed. No failed or unobservable assertion, timeout, unrun row, or interrupted request was recorded.
- Per-execution statuses and native published/conflict counts: `summary.csv`. Per-request assertion tables, receipt projections, actor events and before/after Git states are in each case directory.

| Case | Repeat | Published 01 / 02 | Conflicts 01 / 02 | Status |
|---|---:|---:|---:|---|
| single-clean | 1 | 1 / 0 | 0 / 0 | PASS |
| multiple-clean | 1 | 3 / 0 | 0 / 0 | PASS |
| one-conflict | 1 | 1 / 0 | 1 / 1 | PASS |
| multiple-conflicts | 1 | 1 / 0 | 2 / 2 | PASS |
| single-clean | 2 | 1 / 0 | 0 / 0 | PASS |
| multiple-clean | 2 | 3 / 0 | 0 / 0 | PASS |
| one-conflict | 2 | 1 / 0 | 1 / 1 | PASS |
| multiple-conflicts | 2 | 1 / 0 | 2 / 2 | PASS |

The already prepared fixtures were used in the required case order, first repetition 1 then repetition 2. Every first request followed checks of retained initial Git state, contents, ordered role mappings, identity/provider hashes, empty dispatch queues and accepted metadata differences. Every second request followed a new unchanged-state check. There were no overlapping requests, revalidation/collection overlap, fixture reconstruction, product-code changes, or further app restart.

Q-20260909-03 records the owner-authorized single loading probe and batch restart, the accepted size-field metadata exception, and source/setup review. Q-20260909-04 records the earlier restart-helper cleanup accepted by maintainers. Each setup.json projects the retained before/after restart originals and lists their hashes; current workspace projections and raw-original hashes accompany every Git snapshot. Source and fixture workspace prefixes are replaced with source/ and workspace/. Original metadata, Git repositories, native dispatch files and actor logs remain local.

The execution agent used scoped inline standard-library capture commands for the prescribed Git observations, exact fixed assertions and technical projections under the owner-authorized direct fixture operations. No supplied research/product script, constructor, configuration or approval was edited by the runner. Git commits/merges for repository communication use the four explicit neutral identity variables. Native actor evidence is counted by unique event id, with no duplicate projection counted twice.

Conflict cases retained the blocked roles and recorded a resolve-conflict notice only for the first blocked role, plus delivery-skipped. The raw actor file was absent in clean cases; no actor notice was observed there. Repeated syncs retained the same conflict-notice event ids and unchanged Git states. These observations cover routing and recording with disabled providers; they do not establish delivery to a real repair agent, successful author repair, internal pass counts, full worktree atomicity, or wider scenario coverage.

Scheduler: the owner-created native task is hourly with two runs. The observed state and next UTC check are in scheduler-state.json. The runner did not modify the schedule. Preserve all fixture artifacts pending acceptance; no cleanup, workspace deletion or app change is authorized by this delivery.
