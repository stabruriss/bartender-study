# Execution questions

The execution agent adds one dated entry per question on `run-m4`, then commits
and pushes. Maintainers answer the same id in `ANSWERS.md` on `simulation-pilot`.
Follow `RUNBOOK.md` or `RUNBOOK-CONFORMANCE.md`; name the runbook and step in
each question. Technical content only, with repository-relative paths.

Execution questions are recorded below.

Entry format:

```text
## Q-YYYYMMDD-01 | YYYY-MM-DDTHH:MM:SSZ | OPEN
Step: <runbook step>
Observed: <minimal technical observation; no full terminal dump>
Question: <one specific decision or clarification>
Acknowledgment: <runner fills after reading the matching answer; preserve history>
```

## Execution authorization record | 2026-09-09

The study owner instructed the runner to execute `RUNBOOK.md` and to raise
uncertainties with the owner or through its repository question/answer channel.
The owner permits additional script or scheduler changes only after explicit
permission for the concrete change, with the authorization and actual changes
recorded. This is a conditional exception to the runner's modification limits,
not blanket permission and not a replacement for the study approval files.
No research script, model, test, runtime lock, configuration, reference record,
runbook, or approval record has been modified. No recurring scheduler is active;
the proposed alternative in Q-20260909-02 has not been installed or enabled.

## Q-20260909-01 | 2026-09-09T05:42:07Z | OPEN
Step: RUNBOOK.md, Environment and steps 2-3, before the independent diagnostic comparison.
Observed: `handoff.py environment` generated `validation/environment-m4.json`
with `cpu="Apple M3"`, `architecture="arm64"`, and `python="3.12.4"`.
`validation/controls-m4.json` has `status="pass"`, `tests_run=28`, and empty
`failure_ids`, `error_ids`, and `skipped_ids`; its `environment.cpu` also records
`Apple M3`. The filenames follow the supplied commands and have not been changed;
they must not be read as evidence that this is an M4 machine. No independent
determinism candidate, comparison, or formal scan has been executed. The
runbook names an M4 execution machine and requires the `m4` candidate label.
Question: Should this actual M3 machine be accepted as the execution machine,
with explicit record-label and any required protocol/reapproval instructions,
or must execution move to an M4 machine?
Acknowledgment: Awaiting the study owner's machine decision and matching
maintainer instructions. Original generated records are preserved unchanged.
The existing restriction in `ANSWERS.md` against formal execution before the
evening of 2026-09-09 America/Los_Angeles remains in effect.

Owner decision | 2026-09-09T05:49:13Z: The study owner explicitly confirmed that
the actual M3 machine is acceptable. This resolves the machine-selection
question and authorizes continuing the already permitted bounded preparation
on this machine. The supplied command paths and candidate label `m4` are retained
as protocol identifiers; the generated environment remains the actual
`cpu="Apple M3"`. They do not assert M4 hardware. No script, runtime, parameter,
reference record, or approval file is changed for this decision. The runner will
generate the independent candidate with the unchanged handoff command and report
its comparison. Maintainers should acknowledge this machine exception and advise
if any further formal-execution record or approval adjustment is required.
The date restriction and all remaining formal-execution gates remain in effect.
This machine decision does not authorize the alternative scheduler in
Q-20260909-02 or the conformance scenarios in Q-20260909-03.

Execution follow-up | 2026-09-09T05:50:26Z: The unchanged `handoff.py determinism`
command independently generated `validation/determinism-m4.json` on the approved
M3 machine, retaining `environment.cpu="Apple M3"`. The unchanged `handoff.py
compare` command generated `validation/determinism-comparison.json` with
`status="pass"` and `records_compared=18`. Both generated files are preserved
without manual data changes. No formal scan or application fixture was started.

## Q-20260909-02 | 2026-09-09T05:42:07Z | OPEN
Step: RUNBOOK.md, Questions and answers, recurring two-hour file exchange.
Observed: The installed Ember CLI rejected `--cron '0 */2 * * *'` before task
creation because stepped/ranged cron fields are unsupported. `kota-ember list
--json` returned an empty list afterward. Its help has no interval-repeat
option. The public `v0.1.10` parser also accepts only a scalar minute and hour:
https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/ember.rs#L2084
No scheduler implementation has been changed. An inactive, syntax-checked
proposal is retained only under ignored `local-logs/scheduler-proposal/`.
It would use one macOS launchd job at even local hours to enqueue an Ember
reminder to the execution agent one minute later. The prompt performs only the
runbook's Git file exchange and defers merge/push during execution or collection;
it does not start a study run, fixture, or application sync. The study owner has
been asked for specific permission to enable this alternative; none is recorded
yet. No installer, research script, or existing scheduled task was modified.
Scheduler status: BLOCKED; no recurring task installed. Next scheduled UTC check:
unset until an approved scheduler is enabled. The initial post-submission manual
exchange began at `2026-09-09T05:42:35Z`: generated records and questions were
committed and pushed first, then fetch, neutral-identity merge, push, and
`ANSWERS.md` inspection completed. `origin/simulation-pilot` was already merged;
no responses to Q-20260909-01 through Q-20260909-03 were present. The scheduler
list remained empty. This does not claim an automatic check is scheduled.
Question: Is this launchd-to-Ember implementation acceptable for the required
two-hour file exchange, or which supported scheduler procedure should be used?
Acknowledgment: Awaiting the owner's specific permission and the maintainer
response; preserve the failed creation as an operational deviation.

CLI clarification | 2026-09-09T05:57:47Z: Rechecked installed `--help`,
`add --help`, and `update --help`, plus the public release's argument parser.
Ember does support recurring schedules. The CLI's supported cron forms create
daily, weekly, or monthly recurrence. `--end-after` and `--end-at` bound an
existing recurring schedule; they do not enable interval recurrence for
`--in 2h`, which remains one-shot. No `--repeat` or interval-repeat CLI option
is present in this version. The specific missing operation is direct CLI
creation of a single every-two-hours recurring task, not recurrence generally.
The native application UI exposes fixed-interval Repeat settings with hours
and minutes, and the backend supports that interval. A native UI-created
two-hour schedule is therefore the preferred proposed setup; the launchd
fallback remains inactive. After the owner creates the intended native task,
the runner can inspect it with `list`/`show` and update its reviewed prompt via
CLI without passing a timing option, preserving the recurrence. No schedule
has been created, changed, or enabled during this recheck.
Source references:
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/ember.rs#L2030
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/ember.rs#L2173
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/EmberScheduleInstrument.tsx#L1047

## Q-20260909-03 | 2026-09-09T05:42:07Z | OPEN
Step: RUNBOOK-CONFORMANCE.md, steps 1-2, installed version and separate approval.
Observed: `validation/conformance-version-m4.json` records the actual running
application and explicitly selected bundled CLI. Both binary hashes match the
corresponding files in the public `v0.1.10` release asset; the downloaded asset
matches its published SHA-256. The release tag resolves to public commit
`75eb8fda2b1040c0f1822e0403321a105fec4f6c`. The recorded backend tree equals the
reference backend tree. The read-only source inspection and release-distribution
provenance are included in that report. Its M4 filename follows the handoff,
but the machine discrepancy in Q-20260909-01 also applies. No application was
installed, replaced, rebuilt, or reconfigured; the release image was mounted
read-only for hashing and then detached. No fixture or sync request was created.
`CONFORMANCE_APPROVAL.json` remains pending.
Question: Does the version/source and workspace-setup evidence qualify for
separate conformance approval after the machine issue is resolved, or what
additional evidence/procedure is required?
Acknowledgment: Awaiting source/setup review and the separate approval file;
application scenario execution remains on HOLD.

Owner-assisted workspace proposal | 2026-09-09T05:55:53Z: The study owner
offered to create the required application workspaces if the count is at most
eight and explicitly authorized the execution agent to operate the seven other
owner-designated test workspaces directly using scripts, without asking their
resident agents to perform the operations. This is scoped cross-workspace
authorization, not permission to operate unrelated workspaces. No external
workspace has yet been identified, edited, created, or synchronized by the runner.

The unchanged conformance plan requires eight fresh application workspaces:
`single-clean`, `multiple-clean`, `one-conflict`, and `multiple-conflicts`, each
with independent repetitions `r1` and `r2`. Each fixture has its own ordinary
source checkout and respectively one, three, two, or three linked role worktrees.
The research workspace cannot serve as a fixture under the current procedure;
the eight test workspaces are additional to it and are operated sequentially.
Clarification requested from the owner: whether the offered workspace limit
includes the current research workspace or permits eight additional fixtures.

Precreating workspaces through the app changes the supplied construction
procedure, which asserts that each fixture workspace does not already exist.
An owner-created setup therefore needs a reviewed preparation adaptation, with
concrete fixture identities, clean initial Git state, and the existing
`conformance-disabled` role behavior retained unless explicitly revised and
approved. Resident agents must not introduce concurrent changes during an
observation. The owner's offer and scoped script-operation authorization are
recorded here for maintainer review of that adaptation; no constructor,
runbook, approval record, resident-agent configuration, or other workspace
has been changed. Separate conformance approval remains pending.

Terminology correction | 2026-09-09T06:04:23Z: The owner clarified that
"workspace" in the preceding offer means one agent's workspace, containing
one `project-files` checkout. The runner had used the same word for the
runbook's larger application/project workspace. These are different levels.
The constructor creates one fixture project root with `workspace.json` and
one to three `.agent-workspaces/<role>/project-files` linked worktrees, each
inside its own agent workspace and linked to the fixture's ordinary source
checkout. It does not put several worktrees inside one agent workspace.
The original plan requires eight independent fixture projects across its
repetitions, with at most three role agent workspaces per fixture. The owner's
stated agent-workspace count must not be interpreted as a limit or approval
for eight new application projects. The specific permission to operate the
other seven workspaces concerns owner-designated agent workspaces, not seven
unspecified project roots. The earlier count clarification conflated these
levels and is superseded by this correction. No other workspace has been
modified; the concrete fixture/setup mapping remains to be established.

Application loading gap | 2026-09-09T06:20:25Z: The owner reports that the
current application's normal project-opening UI accepts the authenticated
owner's GitHub repositories, with no local temporary-repository opening flow.
The inspected release's `ProjectSetupModal.tsx` prepares projects through
`prepareGithubProject`. Its backend can enumerate local `workspace.json`
records, and `App.tsx` loads those records into project tabs during initial
application loading. This supports a possible manually registered fixture
path in source, but does not establish an available local-import UI, hot
discovery of a newly written fixture, or successful fixture activation in the
currently running app. The source's preparation path may also normalize or
migrate loaded workspace metadata, which the runbook requires checking before
observation.

The runbook constructs fixture metadata and then instructs selection of the
fixture in the running app, without a demonstrated UI refresh/loading step
between them. The runner's prior explanation overstated the availability of
that selection step. No manually registered fixture has been loaded or tested,
and no application restart, metadata injection, or remote repository creation
has been performed. Conformance remains on HOLD at the setup gate.
Question: Please provide a reviewed way to make the new local fixture visible
and activate its Bartender watcher in this installed app while preserving the
required initial state, or revise and approve the preparation procedure to use
owner-authorized private GitHub test repositories opened through the normal UI.
This requests a setup decision; it does not authorize creating remote repos,
changing product code, or changing the conformance assertions.
Source references:
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/ProjectSetupModal.tsx#L129
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/App.tsx#L1613
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/integrations/mod.rs#L583

Local registration and target-routing review | 2026-09-09T06:28:19Z: The owner
proposed registering synthetic local project structures, restarting the app to
load them, and then trying an explicitly targeted cross-project CLI sync. The
owner also imposed a strict exclusion for an unrelated project. Its identity
and local operational restriction are retained only in ignored local records;
no identifying information or contents from that project are exported here.

Installed CLI help exposes `sync --json --project-root <path>`. The reviewed
`resolve_cli_project_root` gives the explicit path priority over inherited
project environment and CWD discovery; the sync enqueue path writes its request
under that target. Source therefore supports cross-project request routing,
subject to a matching application workspace and active consumer. This has not
been demonstrated with a live fixture or receipt.

The shared-app restart is not confined to the fixture: startup enumerates all
registered workspaces, runs adapter migration, and initializes each project's
Bartender watcher. Workspace enumeration calls preparation routines that may
normalize/migrate and save metadata. Watcher initialization creates the outbox
and processes pending requests. App-side resolution of an explicitly targeted
sync also enumerates/prepares workspaces before selecting its target. The
explicit CLI target alone therefore does not establish zero access or writes
to excluded project metadata. The runner did not inspect the excluded project
to determine its state and did not restart the app, register a fixture, or
send any sync request.

Question: What reviewed loading and request-resolution procedure can exercise
the synthetic fixture while respecting the owner's unrelated-project exclusion,
given these global startup and lookup effects? Conformance remains on HOLD at
setup; no approval fields or product code have been altered to bypass it.
Additional source references:
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1839
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L2012
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L12444
- https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L359

Owner scope clarification | 2026-09-09T06:32:43Z: The owner explicitly permits
Kota's normal scanning/loading of the excluded unrelated project. The restriction
is against runner-issued instructions that modify that project's content; the
runner will not direct edits, Git mutations, sync requests, fixture preparation,
or agent messages at it. Ordinary application discovery and associated metadata
preparation are not a reason to block the owner's local-registration/restart
proposal. The previous zero-access interpretation was too broad and is
superseded by this clarification. The isolation question immediately above no
longer blocks setup on that basis.

The proposed next sequence is to use the unchanged constructor for the first
fresh `conformance-01-single-clean-r1` fixture after the separate source/setup
approval; restart/load the app under the owner's proposed method; verify the
fixture source, role mapping, clean Git state, and unchanged initial records;
then invoke the bundled CLI with the fixture's explicit `--project-root` and
retain the matching application receipt. Startup source initializes Bartender
watchers for registered projects, so a target outside the runner's current CWD
has a source-supported dispatch path. The remaining pending approval should
address this precise local loading sequence and the existing disabled-provider
fixture behavior, without requiring remote repositories or a separate account
merely to prevent normal project scanning. No app restart, fixture registration,
sync request, product-code modification, or approval-record modification has
occurred in this clarification step.
