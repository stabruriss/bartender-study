# Execution answers

Maintainers add one dated response for each question id, commit on
`simulation-pilot`, and push. The execution agent fetches and merges that branch
before acting. Neither silence nor a technical answer constitutes run approval.

Current state, 2026-09-09 19:06 UTC: **both deliveries are accepted by the
study maintainer**. `study-01` passed approved collect-only `verify-02`;
`conformance-01` passed its four fixed cases, two repetitions and sixteen
requests. The original HOLD remains a historical record. Execution is closed;
the runner stops this run's polling and does not renew it. Preserve the raw
archive and fixture originals. Analysis is now a maintainer responsibility.
The dated acceptance and scope limits are below; no further simulation,
collection, fixture request or cleanup is authorized by acceptance.

Initial timing instruction, superseded by the owner's immediate-start decision
recorded in Q-20260909-01 at 2026-09-09T07:28:41Z: the study owner schedules the formal
M4 scan for the evening of **2026-09-09, America/Los_Angeles**. Environment setup,
controls, and the cross-machine check may be prepared earlier; do not start the
formal scan before that evening. All execution gates still apply. Maintainer
question polling was planned to start at **2026-09-09 20:00 America/Los_Angeles**
and continue every two hours. That future task was cancelled when both
deliveries were accepted. This historical schedule is no longer active.

Entry format:

```text
## Q-YYYYMMDD-01 | YYYY-MM-DDTHH:MM:SSZ
Answer: <specific technical action or clarification>
Affected files: <repository-relative paths, or None>
Approval impact: <unchanged / new approval required>
```

## Q-20260909-01 | 2026-09-09T15:30:48Z
Answer: Acknowledged. The study owner's decision to execute on the actual Apple M3 machine stands. Keep the protocol identifiers and the `m4` record labels unchanged; the environment records already state the actual CPU, and the run report's deviations line records the machine. No reapproval is required for this deviation: RUN_APPROVAL.json and the parameter and protocol digests remain valid as recorded.
Affected files: None
Approval impact: unchanged

## Q-20260909-02 | 2026-09-09T15:30:48Z
Answer: The owner-created native Ember task (120-minute interval, five runs) satisfies the recurring file exchange for this run; do not enable the launchd fallback. When the five runs are exhausted, do not recreate the task yourself. Maintainers poll `origin/run-m4` on their own schedule, and any further exchange is triggered by dated answers on `simulation-pilot`. Keep the deferral rule: no merge or push while an execution or collection is active.
Affected files: None
Approval impact: unchanged

## Q-20260909-04 | 2026-09-09T15:30:48Z
Answer: For any future separately authorized restart, do not use `launchctl submit` with keepalive. The preferred mechanism is a manual restart performed by the owner, which is also required by the owner's session-recovery constraint. If a restart is delegated, use a one-shot job with keepalive explicitly disabled and a single run-at-load, which removes itself after the relaunch. Cleanup of the defective job is accepted as complete. The owner's human-attendance requirement before closing the application is now an operating constraint; record it before any restart.
Affected files: None
Approval impact: unchanged

## Q-20260909-03 | 2026-09-09T15:30:48Z
Answer (interim): Setup evidence received: the version and source binding (release asset hashes, tag resolving to public commit 75eb8fda2b1040c0f1822e0403321a105fec4f6c, backend tree equal to the reference), the single-fixture loading probe, and the batch preparation of all eight fixtures with before-state snapshots. Maintainers are reviewing the local-registration and restart loading sequence and the size-only metadata changes before recording CONFORMANCE_APPROVAL.json. Until that file reads `approved`, issue no sync request and awaken no role. A dated answer with the approval or the required changes follows on this branch.
Affected files: None yet
Approval impact: pending

## Q-20260909-05 | 2026-09-09T15:30:48Z
Answer (interim): HOLD confirmed, and your disposition is correct: keep every original output, archive part, and generated delivery file unchanged; do not rerun, regenerate, or repair anything. Maintainers are reproducing the two verification issues on the reference machine against the retained pilot data and the delivered CSVs. Your static observations about `sort_keys=True` versus insertion-ordered traversal in `plan.cells` and `report.summarize` are the first hypothesis under test. If the discrepancy is confined to ordering inside the verification tool, the disposition will be a reviewed correction to the verification code only, re-approved with a new protocol digest, followed by a re-run of `collect` against the preserved originals under a distinct verification record name; the scientific outputs would not be regenerated. If the issue is in the outputs themselves, a new run id will be approved. Take no action before that dated answer.
Affected files: None yet
Approval impact: pending

## Q-20260909-03 | 2026-09-09T15:47:28Z
Answer (source/setup decision): Approved for the eight planned fixture
observations, under the revised `RUNBOOK-CONFORMANCE.md` and the independent
`CONFORMANCE_APPROVAL.json` signed by the study maintainer. This is permission
to observe the fixed assertions, not a conformance PASS.

The public release asset digest agrees with the reported binding; tag v0.1.10
resolves to `75eb8fda2b1040c0f1822e0403321a105fec4f6c`, and comparison with
`b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7` is empty across `app-v2`. Source
supports registry loading at startup, dispatch-watcher creation, and explicit
CLI target resolution. The installed-binary comparison and before/after loading
observations remain your reported evidence, with originals retained locally;
this is release-distribution provenance, not a reproducible-build claim.
The review is recorded in `validation/conformance-review-m1.json`.

The constructor is unchanged, SHA-256
`da822ddde40adf0848fe5097e93f8faa792bbe806af56b584423f010c516b8db`.
Use the eight fixtures already loaded by the owner-performed restart reported
at 07:38:10Z. No further restart or reconstruction is needed. Immediately before
each first request, recheck its original Git HEADs/branches/content, clean
state, absent operation markers, role order/mappings, and disabled-provider
files. No prior sync or concurrent writes may have affected it. Only
`localRootBytes` and `sourceDirBytes` additions/changes to nonnegative integers
are accepted as metadata differences, with both original versions preserved;
all other differences mean HOLD. Do not launch a real provider.

Include a technical setup projection and hashes of the retained before/after
originals in the conformance delivery; exclude absolute paths and unrelated
project records. Use the explicit fixture `--project-root` in every request.
Run the cases sequentially in the documented order. Do not overlap them with
collection/revalidation, and stop at the first failed or unobservable assertion.

Affected files: `RUNBOOK-CONFORMANCE.md`, `CONFORMANCE_APPROVAL.json`,
`validation/conformance-review-m1.json`.
Approval impact: independent conformance observation approved; runbook SHA-256
`e5144353270d4833c494e47cb6c69c2200e3a3ed48e1038baf6763120bba640e`.

## Q-20260909-05 | 2026-09-09T15:47:28Z
Answer (verification disposition): Keep the original HOLD record and every
original scientific output unchanged. The verifier correction is ready, with
34 passing controls, but revalidation still needs the study owner's approval
in `REVALIDATION_APPROVAL.json`. Do not rerun the simulation.
Do not claim that the study results are usable until the complete retained-output
revalidation returns PASS and the maintainers accept that delivery.

On M1 the delivered 990 grid rows match the regenerated rows field for field
and with the same multiplicities; only list order differs. The parameter digest,
current configuration and model-file hashes are unchanged. The timing pilot
retained timing/size records only, as documented in `benchmarks/README.md`; its
full results were temporary. A separate zero-edit diagnostic using seeds
800001–800030 reproduced exactly both reported HOLD issues. After the verifier
correction it passes, with every diagnostic file hash unchanged. This control
does not constitute a study sample. See `validation/study-01-order-review-m1.json`
and `validation/controls-m1-revalidation-01.json`.

The correction compares grid-row multisets and CSV fields with their duplicate
counts, without a numerical tolerance. It ignores row order, retains the exact
CSV header and field strings, and still rejects changed values, missing rows,
duplicates, altered raw data and unapproved execution provenance. M1 does not
yet have the formal per-seed summaries: their numeric agreement with the formal
paired CSV is not claimed until the complete retained-output check passes.

**Authorized diagnostic delivery now, without running collection:** when no
simulation, collection or fixture observation is active, transfer a compressed
copy of the existing per-seed summary through this branch. First confirm that
`outputs/study-01/summaries.jsonl` has SHA-256
`47693e36f4b1fc449674337176cf15281c6d0f38153486714364b02ae24c3bfb`, matching the
first artifact index. Preserve the original. If the destination already exists,
do not overwrite it; inspect its decompressed hash instead.

```sh
shasum -a 256 outputs/study-01/summaries.jsonl
mkdir -p deliverables/study-01/diagnostics
gzip -n -c outputs/study-01/summaries.jsonl > deliverables/study-01/diagnostics/summaries.jsonl.gz
gzip -dc deliverables/study-01/diagnostics/summaries.jsonl.gz | shasum -a 256
```

Both displayed content hashes must match the value above. Compression is a byte
transfer, not data generation or outcome calculation. Commit/push only the new
compressed copy and a dated Q-05 acknowledgment using the documented Git
identity. Do not regenerate or edit either CSV, and do not add other raw runs.
This transfer lets M1 independently check the delivered CSV against every
original summary while the separate revalidation approval is pending.

**After `REVALIDATION_APPROVAL.json` reads approved:** verify it binds
`run_id=study-01`, `verification_id=verify-02`, `scope=collect-only`, original
execution protocol `f7e0530b35d4aae962a2a60cf7c2e3f329aaa06d455871d994b51bbd2c0c5215`,
and new verification protocol
`fce2615ee240633100a05d5c3c9f69eeff1c4f4a275668c5abf0081dc5bafc2d`.
It also binds the original execution receipt, execution approval, first
verification record and artifact index by hash. Then run, in order:

```sh
git status --short
git fetch origin
env GIT_AUTHOR_NAME='Study Runner' GIT_AUTHOR_EMAIL='study-runner@example.invalid' \
    GIT_COMMITTER_NAME='Study Runner' GIT_COMMITTER_EMAIL='study-runner@example.invalid' \
    git merge --no-edit origin/simulation-pilot
git push origin run-m4
PYTHONHASHSEED=0 .venv/bin/python handoff.py fingerprints
PYTHONHASHSEED=0 .venv/bin/python handoff.py controls --output validation/controls-m4-revalidation-01.json
PYTHONHASHSEED=0 .venv/bin/python handoff.py collect --run-id study-01 --verification-id verify-02
```

Start the exchange on `run-m4` with reviewed local records committed and no
active execution. After merge, reread the approval and this answer and compare
the fingerprints before running controls or collection. These commands are
sequential checkpoints, not permission to continue after a failed check.

If the controls path already exists, inspect it: a matching PASS for this exact
protocol may be used, but never overwrite it. If the verification destination
already exists, stop and request another approved verification id. The command
parses all original run and flow records, checks both CSVs, and hashes every raw
file against the first artifact index. It creates only
`deliverables/study-01/rechecks/verify-02/verification.json`, an approval snapshot,
and `REVALIDATION_REPORT.md`. It produces no replacement CSVs or archive and does
not modify the original HOLD report. Commit/push the new controls and recheck
directory with a dated Q-05 acknowledgment; preserve any further HOLD exactly.

Affected files: `handoff.py`, `tests/test_revalidation.py`,
`REVALIDATION_APPROVAL.json`, the two M1 validation records named above.
Approval impact: study-owner approval required for the collect-only protocol;
original simulation parameters, model and execution approval remain unchanged.

## Q-20260909-05 | 2026-09-09T17:57:31+00:00
Approval recorded: The study owner approved the collect-only revalidation `verify-02`. `REVALIDATION_APPROVAL.json` now reads `approved`, signed by `study owner` at 2026-09-09T17:57:31+00:00; all other binding fields are unchanged. Fetch and merge `origin/simulation-pilot`, then follow the commands and checkpoints above. The scientific simulation is not rerun, and the results remain HOLD until revalidation returns PASS and the maintainers accept the delivery.
Affected files: `REVALIDATION_APPROVAL.json`.
Approval impact: collect-only revalidation approved; original execution approval and parameters unchanged.

## Q-20260909-05 | 2026-09-09T19:06:41Z
Answer (formal acceptance): **ACCEPT `study-01` / `verify-02`.** The delivered
revalidation has no issues, records 29,700 successful retained run files and
300 flows, and verifies every original file against the first inventory. Its
approval, execution receipt, original approval/HOLD, inventory, new protocol and
34 passing controls match the approved bindings. It ran from 18:14:22 through
18:19:30 UTC, wall time 307.707 seconds, without a simulation rerun.

M1 independently checked the compressed diagnostic transfer against the original
uncompressed hash and size, all 990 approved cells and all 29,700 unique
cell/seed records. Reapplying the unchanged summary function reproduces all
34,650 summary rows and 11,010 paired rows with exact headers, field strings
and multiplicities. Both original CSV hashes are unchanged. The original HOLD
and its report remain untouched; this accepted revalidation is the current
verification conclusion. The data may now enter maintainer analysis.

Evidence: `validation/review_delivery.py` and
`validation/delivery-acceptance-m1.json` (297 checks across both deliveries,
all passing). The script performs read-only verification, never simulation.
M1 verified the transferred summaries, not the multi-part raw archive itself;
raw run/flow identity rests on the approved execution-machine revalidation.
Retain that archive and its recorded hashes for release. This is data acceptance,
not a claim about any scientific hypothesis or publication approval.
Affected files: `ANSWERS.md`, `validation/review_delivery.py`,
`validation/delivery-acceptance-m1.json`.
Approval impact: existing approvals unchanged; accepted execution closed.

## Q-20260909-03 | 2026-09-09T19:06:41Z
Answer (formal acceptance): **ACCEPT `conformance-01` within the fixed scope.**
The four cases, each repeated in a fresh fixture, and all sixteen distinct
requests pass independent review of the delivered projections. The review
checks unchanged pre/post loading Git and role identities, permitted metadata
changes only, source content and commit ancestry, clean/blocked role states,
native receipt/request matching, conflict order, first-role notice binding,
and unchanged second-sync state with no duplicate notice. All requests occurred
after revalidation and sequentially. Version and approval snapshots are bound
to v0.1.10, public commit `75eb8fda2b1040c0f1822e0403321a105fec4f6c`.

The observations support the documented routing/recording assertions with
`conformance-disabled` providers. They do not demonstrate delivery to a real
repair agent, successful author repair, internal pass counts, full worktree
atomicity, performance or wider scenario coverage. M1 reviewed technical
projections with retained-original hashes; native fixture originals remain on
the execution machine. The binary/source binding is release-distribution
provenance, not an independent reproducible build. These limits are retained in
the acceptance record and must remain in the paper.
Affected files: `ANSWERS.md`, `validation/delivery-acceptance-m1.json`.
Approval impact: independent observation accepted and closed; no more requests.

## Q-20260909-02 | 2026-09-09T19:06:41Z
Answer (execution closure): Both deliveries are accepted and Q-01 through Q-05
are resolved by the dated answers. Stop this run's repository polling; do not
renew or recreate it. On reading this closure, inspect your scheduler and cancel
only the remaining task for this run's repository exchange, if it is still
scheduled. Leave unrelated tasks unchanged. Record the observed cancellation or
already-exhausted state once in QUESTIONS.md and push `run-m4`; no new polling
series is needed. The maintainer's future polling task has been cancelled.

Preserve the originals and fixtures. Acceptance does not authorize workspace
removal, app restart or artifact cleanup. Analysis is performed by maintainers;
the execution agent has no remaining calculation or interpretation work.
Affected files: `ANSWERS.md`; runner acknowledgment in `QUESTIONS.md`.
Approval impact: execution and its scheduled exchange closed by owner direction.
