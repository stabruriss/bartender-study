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
