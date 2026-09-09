# Execution answers

Maintainers add one dated response for each question id, commit on
`simulation-pilot`, and push. The execution agent fetches and merges that branch
before acting. Neither silence nor a technical answer constitutes run approval.

No questions have been answered yet. Parameters and the execution protocol are
approved in the configuration and `RUN_APPROVAL.json`. The frozen runbook retains
its drafting-time pending-status paragraph; these approval files determine the
current status. M4 must still complete its independent controls and comparison.
Application conformance remains pending in `CONFORMANCE_APPROVAL.json`.

Entry format:

```text
## Q-YYYYMMDD-01 | YYYY-MM-DDTHH:MM:SSZ
Answer: <specific technical action or clarification>
Affected files: <repository-relative paths, or None>
Approval impact: <unchanged / new approval required>
```
