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

Owner execution-time update | 2026-09-09T07:28:41Z: The owner explicitly permits
the formal work to begin now, superseding the prior not-before-evening timing
instruction in ANSWERS.md. The supplied scientific configuration, runtime,
protocol digest, and approval files remain unchanged. The owner requested that
the remaining local fixtures be prepared before an owner-performed app restart;
the formal scan will begin only after that restart and manual session recovery,
with a fresh successful preflight and unchanged output-preservation rules.

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

Owner-requested prompt clarification | 2026-09-09T07:06:16Z: A copyable native
Ember prompt is prepared in ignored `local-logs/scheduler-proposal/poll-prompt.txt`.
The proposed target is the execution agent, at a fixed interval of two hours,
with no preset repeat count. RUNBOOK.md requires removing the task after both
deliveries are accepted or the maintainers close execution. The prompt performs
repository file exchange only, defers merge/push during execution, retains
neutral Git identity and reviewed records, and does not start a study, fixture,
application sync, or dummy provider. Owner-specific execution boundaries remain
in local scope records. No task has been created or changed: the current
`kota-ember list --json` remains empty, and the first/next scheduled UTC check is
unset. The prior launchd-to-Ember draft remains inactive.

Native scheduler verified | 2026-09-09T07:25:17Z: The owner created the native
Ember task for the execution agent and explicitly chose a total of five runs.
The CLI `list` and `show` both report `status=scheduled`, `repeatEnabled=true`,
`repeatKind=fixed`, `repeatEveryMinutes=120`, `endMode=after`, `endAfterCount=5`,
and `runCount=0`. The first and next scheduled UTC check is
`2026-09-09T08:20:00Z`. This resolves the earlier absence of an installed timer;
no runner-created launchd fallback was enabled. The five-run limit is the
owner's explicit operational override of the prior unbounded proposal; the
runner must not automatically extend or recreate it. This reminder series is
expected to finish before the evening execution/maintainer polling schedule in
ANSWERS.md, so it is not evidence of coverage of that later period.

The saved prompt ends mid-sentence and retains the earlier unbounded wording.
The runner preserved its actual content and settings under ignored
`local-logs/scheduler-proposal/owner-created-20260909T072207Z.json`, prepared a
complete bounded replacement in `poll-prompt-five-runs.txt` in that directory,
and requested specific permission to update only the text while preserving all
timing, target, and count fields. No task update has been made at this observation.
The owner was also asked whether to retain the documented evening start or
explicitly move it earlier; no timing override is inferred from preparing the
machine or scheduler. No formal scan or additional conformance action has begun.

Post-restart scheduler check | 2026-09-09T07:38:10Z: The same native task now
contains the complete reminder text. Ember attributes its update at
`2026-09-09T07:27:27Z` to the human actor. Its execution target, first/next UTC
time, 120-minute interval, five-run limit, and scheduled status remain unchanged.
The runner has not modified this task. The owner's explicit five-run limit
continues to govern despite the older unbounded wording in its text; no further
text replacement is needed to repair the previously incomplete final sentence.

First recurring exchange | 2026-09-09T08:20:35Z: The execution session received
the native reminder. Ember reports `runCount=1`, `status=scheduled`, no error,
`lastRunAt=2026-09-09T08:20:07.633070Z`, and
`nextRunAt=2026-09-09T10:20:07.633070Z`; the 120-minute interval and five-run cap
are unchanged. The formal simulation was active. The runner fetched origin and
read `origin/simulation-pilot:ANSWERS.md` without merging or pushing. No answers
to the open questions were present. The fetched answer, scheduler state, remote
commit, and check time are retained under ignored
`local-logs/study-01-execution/poll-01/`. This technical entry is kept uncommitted
until execution/collection ends. No scheduler mutation, app sync, fixture action,
restart, or additional study process was triggered by this reminder.

Deferred exchange completed | 2026-09-09T09:38:36Z: Formal execution and
collection have both ended; no study or conformance process is active. The
pending reminder entry, Q-20260909-05, and reviewed HOLD delivery were committed
in `3af1cfe`. The runner then fetched origin and ran the neutral-identity merge
of `origin/simulation-pilot`, which was already up to date at `ca8b062`.
ANSWERS.md still contains no dated responses to Q-20260909-01 through
Q-20260909-05, and CONFORMANCE_APPROVAL.json remains pending. No answer has
been inferred or acknowledged as approval. The current answer, remote commit,
check time, and Ember snapshot are retained under ignored
`local-logs/study-01-execution/post-collection-exchange/`.

Ember still reports `status=scheduled`, `runCount=1`, no error, the unchanged
120-minute interval and five-run cap, and next check
`2026-09-09T10:20:07.633070Z`. No scheduler changes were made. Further scientific
execution remains on HOLD pending the Q-20260909-05 disposition; fixture sync
still requires the separate conformance approval.

Second recurring exchange | 2026-09-09T10:21:02Z: The runner and managed
worktree were clean, with no active simulation, collection, or conformance
process. Fetch and the explicit neutral-identity merge found
`origin/simulation-pilot` already current at `ca8b062`. ANSWERS.md has no new
dated responses to Q-20260909-01 through Q-20260909-05. The study-01 verification
remains HOLD pending Q-20260909-05, and CONFORMANCE_APPROVAL.json remains pending.
There is no new answer to acknowledge and no delivery-acceptance or closure
instruction that would stop the reminder.

Ember reports `status=scheduled`, `runCount=2`, `error=null`,
`lastRunAt=2026-09-09T10:20:17.068312Z`, and
`nextRunAt=2026-09-09T12:20:17.068312Z`. The 120-minute interval and owner-set
five-run cap remain in force. The answer, remote commit, check time, and actual
schedule snapshot are retained under ignored `local-logs/study-01-execution/poll-02/`.
This exchange changed only the technical question record; no script, timer,
experiment, fixture, sync, dummy provider, or application restart was triggered.

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

Owner-authorized setup probe | 2026-09-09T06:39:08Z: The owner explicitly
instructed the runner to create one local temporary repository first and then
restart Kota to try loading it. This authorizes the single-fixture preparation
and app restart despite the still-pending general conformance approval. It does
not fill or replace that approval record or authorize a completed-conformance
claim. The selected fixture is `conformance-01-single-clean-r1`, using the
unchanged constructor from this runbook with one disabled-provider role. All
other fixtures remain uncreated. The owner's unrelated-project exclusion and
permission for normal app discovery remain in force.

Operational additions for this action will remain under ignored
`local-logs/setup-probe/`: an exact extracted copy of the supplied constructor,
a one-shot app-restart helper, and restart/recovery diagnostics. The helper will
request an orderly quit of the identified Kota app, wait for that app process
to exit, and reopen the same installed bundle. It will not force-kill processes,
issue a sync, modify product code, or create a recurring task. A transient
launchd job is used solely so reopening can survive the current app/session
exiting. Research scripts, runtime locks, configurations, and approval files
remain unchanged. Resulting preparation and restart observations will be
appended after execution; any startup mutation will be preserved and reported.

Preparation observation | 2026-09-09T06:42:39Z: The unchanged runbook constructor
created the single selected fixture and its `conformance-disabled` role. The
ordinary source checkout is on `main`; source and role Git HEADs match the
constructor's `initial.json`, both worktrees are clean, and the role contains
the prescribed unmerged clean-file edit. The fixture's Bartender outbox does not
yet exist. No sync or other fixture was created. Pre-restart project/role
metadata copies and Git observations are retained under ignored
`local-logs/setup-probe/before-restart/` and `before-restart.json`; the source
and original initial record remain under
`local-logs/conformance/conformance-01-single-clean-r1/`.

The exact constructor copy is `local-logs/setup-probe/construct-from-runbook.py`.
The newly authored operational helper is
`local-logs/setup-probe/restart-kota-once.sh`; it only requests app quit, reopens
the same bundle, and observes process/outbox existence. Its shell syntax was
checked before launch. `local-logs/setup-probe/RECOVERY.md` records how to inspect
the restart and preserve any startup changes if the current session ends.
These are the concrete local additions under the owner's create-one-and-restart
authorization; no research or application code was changed. Restart completion
is not yet claimed by this preparation entry.

Restart/loading observation | 2026-09-09T07:06:16Z: The owner-authorized restart
reopened the same installed application at `2026-09-09T06:44:14Z`. The fixture
Bartender outbox appeared at `2026-09-09T06:44:15Z`, and the owner subsequently
confirmed that the local fixture loaded in the application. The post-restart
record in ignored `local-logs/setup-probe/after-restart.json`, observed at
`2026-09-09T07:01:55Z`, preserves source/role HEAD and content matches to the
initial fixture, clean worktrees, unchanged role identity/provider files, and
unchanged source/role mappings. The only changed project-metadata keys were
`localRootBytes` and `sourceDirBytes`, consistent with normal application size
bookkeeping; they have been preserved rather than reset. No Git operation
markers or fixture request files were present, and the runner issued no sync.
The role remains `conformance-disabled`; it must not be awakened or replaced
with a real provider. This is local setup/loading evidence, not a formal
conformance pass. The separate pending approval and startup-mutation review
remain with maintainers. Q-20260909-04 records a restart-helper deviation.

Owner-authorized batch preparation | 2026-09-09T07:28:41Z: After the successful
single-fixture loading probe, the owner instructed the runner to prepare the
remaining repositories before one owner-performed app restart and manual
execution-session recovery. This explicitly authorizes preparing the remaining
seven planned fixtures together, retaining the existing first fixture, despite
the still-pending general conformance approval. It is a recorded operational
exception to individual creation/loading, not a change to scenario contents or
an approved-conformance claim. Each new fixture will use the same unchanged
constructor from RUNBOOK-CONFORMANCE.md, verified against its extracted copy,
with disabled dummy providers. No sync is included in this preparation.

The runner will preserve before-restart observations for all eight fixtures,
then hand control to the owner without restarting the app or using the prior
restart helper. Formal simulation starts after manual session recovery so this
restart cannot interrupt its non-resumable execution. The conformance source/
setup review should address this batch-loading sequence and the previously
observed size-only metadata changes before accepting the prepared fixtures for
formal observations. Approval records remain unmodified.

Batch preparation observation | 2026-09-09T07:31:58Z: The remaining seven
constructor invocations completed successfully. All eight planned fixture
projects are now present. The extracted constructor still matches the supplied
runbook block byte for byte, SHA-256
`da822ddde40adf0848fe5097e93f8faa792bbe806af56b584423f010c516b8db`.
Each source/role HEAD, branch, and tracked file matches its initial record and
the specified fixture content. Indexes/worktrees are clean, with no unmerged
entries or active Git-operation markers. Ordered role mappings and disabled
provider/identity files match the constructor. No request files were present.
The previously loaded first fixture has a Bartender outbox; the seven new
fixtures do not yet have one and await the owner-performed app restart.

Local additions under this authorization are the seven fixture source/role
repositories and workspace registrations, read-only before-state snapshots in
`local-logs/setup-probe/batch-before-owner-restart/`, and the continuation note
`local-logs/setup-probe/NEXT-AFTER-OWNER-RESTART.md`. The original first fixture
was preserved. No research or product script, scientific setting, approval file,
or scheduled task was changed. No app restart, sync, or formal scan was issued
by the runner during this preparation. The continuation note separates the
authorized simulation start after manual session recovery from the still-pending
independent conformance approval.

Owner-performed restart verified | 2026-09-09T07:38:10Z: The owner confirmed
completion of the app restart and manually resumed the execution session.
The running process identifies the same installed application bundle. All
eight prepared fixtures now have Bartender outbox directories. Source/role
HEADs, branches, indexes/worktrees, all tracked contents, operation markers,
role order/mappings, identity files, and disabled provider files match their
before-restart records. Workspace metadata has no changed keys in this
comparison; the first fixture's earlier size-field change remains part of its
retained history. No request files were present and no runner sync was issued.

The separate after-restart snapshots are retained under ignored
`local-logs/setup-probe/batch-after-owner-restart/`, with the original before
records preserved. These are loading observations only. Independent conformance
approval remains pending. The owner's immediate-start authorization now permits
proceeding to the separately approved formal simulation after fresh preflight;
no further app restart is needed for that command.

## Q-20260909-04 | 2026-09-09T07:06:16Z | OPEN
Step: Owner-authorized single-fixture setup and application restart.
Observed: The temporary `launchctl submit` job intended to survive application
exit was configured with keepalive behavior and repeatedly reentered the restart
helper. The log contains only the initial actual quit/reopen sequence; later
invocations exited when the original app process could not be found by `ps`
under `set -e`, before any further quit command. The runner removed the job after
preserving diagnostics, verified that its label was absent, and confirmed that
the reopened app remained running. The last helper entry is dated
`2026-09-09T07:01:47Z`; no later entries appeared at the follow-up check.

Authorization and concrete changes: The owner explicitly permitted creating one
local temporary repository and restarting the app. The local constructor copy,
restart helper, and recovery records were added under that scope as documented
in Q-20260909-03. Removing the accidentally recurring restart job restores the
authorized one-time operation; it does not install a replacement or change an
Ember reminder. The runner corrected the local recovery/scope notes and retained
the original helper and logs under ignored `local-logs/setup-probe/`. Research
and product code and approval files remain unchanged. The helper/job will not be
reused as a schedule. This operational reentry is distinct from the uncreated
two-hour file-poll task in Q-20260909-02.

Question: For any future separately authorized app restart, which reviewed
one-shot launch mechanism should be used in place of this `launchctl submit`
invocation? The defective job is already removed and no retry is pending.
Acknowledgment: Awaiting a maintainer recommendation; cleanup is complete.

Owner-specified operational constraint | 2026-09-09T07:08:52Z: Application
relaunch does not restore the execution session; a human must manually wake the
session before work can continue. For any restart during ongoing work, the
runner must preserve a checkpoint and receive a fresh explicit human-attendance
confirmation before closing the current application instance. Prior permission,
silence, or a successful relaunch does not satisfy this requirement. The local
scope and recovery notes and the proposed reminder prompt now record this
constraint. No additional restart or schedule mutation occurred in this update.

## Q-20260909-05 | 2026-09-09T09:28:18Z | OPEN
Step: RUNBOOK.md, step 6, supplied collection and verification for study-01.
Observed: The unchanged formal command completed with process exit code 0.
`deliverables/study-01/execution.json` records `status=complete`, `exit_code=0`,
`started_at=2026-09-09T07:40:10.976022+00:00`, and
`finished_at=2026-09-09T09:19:56.255898+00:00`. The generated manifest records
`planned_runs=29700`, `completed_runs=29700`, and `failed_runs=0`. Execution used
the source commit recorded in the report, with the unchanged approved parameter
and protocol digests and the pinned runtime. The only tracked-file edit during
execution was a technical reminder entry in this question file; no merge or
push occurred then.

The unchanged `handoff.py collect --run-id study-01` command subsequently
returned process exit code 1. Its generated `verification.json` records
`status=hold`, `records_seen=29700`, `raw_run_files=29700`, `unique_flows=300`,
and exactly these issues:

- `paired-differences.csv does not match the per-seed records`
- `saved grid or parameter digest mismatch`

Collection still produced the archive, artifact index, and HOLD report. The
generated `artifact-index.json` records `archive_bytes=4200591360` and
`archive_sha256=2256b0bf734992aa37d1a59f176832f08cce8946fc514dee4f8b87d37e625beb`.
All listed archive parts and raw outputs remain local. The generated delivery
is retained unchanged except for completing the runbook-required deviations
line in RUN_REPORT.md. No data, configuration, code, approval, or expected result
was altered to bypass these checks, and no run or collection retry was issued.

Static source inspection suggests a possible serialization-order issue, not a
confirmed explanation of the data differences:

- `bartender_sim/__main__.py:_json` saves configuration with `sort_keys=True`.
  `bartender_sim/plan.py:cells` traverses `axes.values()` and `axes` in dictionary
  order. `handoff.py:verify_output` reloads the saved configuration, regenerates
  that list, and compares it to the saved cells list with order-sensitive
  equality. Sorted JSON keys can change this traversal order.
- The run uses in-memory summaries, while summaries.jsonl is written with
  `sort_keys=True`. `bartender_sim/report.py:summarize` builds paired differences
  by iterating `clean["metrics"].items()` and preserves insertion order in the
  contrast rows. Verification reloads those summaries and compares regenerated
  CSV bytes. This is another place where JSON key sorting can change row order.

The runner has not independently regenerated grids/CSVs, calculated study
results, established numeric equivalence, or repaired either output. The
original HOLD status remains authoritative pending review.

Delivery staging observation | 2026-09-09T09:35:59Z: The default
`git diff --cached --check` reported trailing-whitespace warnings for the
generated CSV files' CRLF endings. Its original diagnostics are retained under
ignored `local-logs/study-01-execution/staged-diff-check.txt`. A command-local
check using `core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol`
passed, and byte comparison confirmed that every staged delivery file matches
its working file. No line endings, CSV contents, Git configuration, attributes,
or scientific checks were changed. This staging-format observation does not
resolve or change either verification failure above.

Question: Please review both verification failures and provide the approved
disposition for the preserved study-01 outputs, including whether a reviewed
verification correction may examine these originals or a newly approved run is
required, with any necessary code/protocol approval updates and distinct output
paths before another command is authorized.
Acknowledgment: HOLD; original data and generated delivery preserved, awaiting
maintainer instructions through ANSWERS.md. Separate application conformance
also remains pending its own approval; no fixture sync has been issued.
