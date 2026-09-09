# Execution answers

Maintainers add one dated response for each question id, commit on
`simulation-pilot`, and push. The execution agent fetches and merges that branch
before acting. Neither silence nor a technical answer constitutes run approval.

No questions have been answered yet. Parameters and the execution protocol are
approved in the configuration and `RUN_APPROVAL.json`. The frozen runbook retains
its drafting-time pending-status paragraph; these approval files determine the
current status. M4 must still complete its independent controls and comparison.
Application conformance remains pending in `CONFORMANCE_APPROVAL.json`.

Execution timing, recorded 2026-09-09 UTC: the study owner schedules the formal
M4 scan for the evening of **2026-09-09, America/Los_Angeles**. Environment setup,
controls, and the cross-machine check may be prepared earlier; do not start the
formal scan before that evening. All execution gates still apply. Maintainer
question polling starts at **2026-09-09 20:00 America/Los_Angeles** and continues
every two hours. This schedule does not approve application conformance.

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
