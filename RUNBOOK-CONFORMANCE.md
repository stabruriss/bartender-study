# Runbook: observe application conformance on M4

**Treat every committed byte as public.** Use only synthetic files, neutral
fixture roles, and relative paths. Keep account details, personal information,
credentials, unrelated projects, screenshots, full terminal logs, and absolute
local paths out of this repository. Generated application configuration may need
absolute paths locally; never commit it verbatim. The repository stays private
until the complete manuscript and artifacts are released together. The runner
does not change visibility or publish artifacts.

## Purpose and scope

Observe whether a version-identified, running Kota application integrates clean
worktrees while returning unresolved conflicts and recording the first author's
repair notice. The CLI queues a request for the app; it is not a standalone
implementation of synchronization.

This procedure has an **independent approval gate**. Reporting the installed
version is allowed before approval. Scenario execution requires `CONFORMANCE_APPROVAL.json`;
`RUN_APPROVAL.json` and simulation parameter approval do not approve it. Use
`run-m4` and the file question/answer protocol in [RUNBOOK.md](RUNBOOK.md).
Do not run conformance observations during the timed simulation scan.

The minimum consists of four scenarios, each on two fresh fixtures. Each fixture
receives one initial sync and one further sync with no intervening edits:
**eight fixture executions and sixteen distinct CLI requests**. These are finite
conformance observations, not performance measurements or proof of the full
repair lifecycle. There is no automatic extension to additional scenarios.
The execution agent uses the construction and observation commands below without
adding simulation or analysis logic. It records the specified Git/receipt fields
and assertion outcomes; it does not invent metrics or interpret the findings.

## 1. Report the installed version before preparing fixtures

Identify the actual running application bundle and the CLI binary it supplies.
Do not assume the account's `kota-bartender` shim selects that binary. Read the
bundle's `Contents/Info.plist` version/build fields, hash its main executable and
the selected CLI with SHA-256, and record macOS, architecture, and Git version.
Keep bundle paths and command output that identifies the account local.

Create `validation/conformance-version-m4.json` with these fields:

- `reported_at`: UTC timestamp; `app_version` and `app_build`: observed values.
- `app_executable_sha256` and `cli_executable_sha256`: actual binary hashes.
- `os_version`, `architecture`, and `git_version`: technical environment only.
- `public_repository`: `https://github.com/stabruriss/kota-app`;
  `public_commit`: a full public commit SHA, or `null` if it cannot be established.
- `binary_source_basis`: release asset/checksum/build-provenance links that bind
  the installed app and CLI to that commit, or a clean build record for that
  commit. A version string or a freshly cloned source tree alone is insufficient.
- `backend_tree`: the commit's `app-v2/src-tauri/src` Git tree id;
  `reference_comparison`: `same`, `different`, or `unknown`.
- `workspace_setup_basis`: how this version loads a new disposable workspace
  and enables its dispatch watcher; cite public source or documentation.

The prior source audit used commit
`b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7`. Tag `v0.1.10` resolves to
`75eb8fda2b1040c0f1822e0403321a105fec4f6c`; both have backend source tree
`147cbc348cd1e3aa8a90d4f0c67e3652798b083a`. This equality covers that directory,
not the complete repository or installed binaries. Use the actual commit as the
result's version anchor even when the relevant trees match.

For a read-only public source comparison, keep the checkout under ignored logs:

```sh
mkdir -p local-logs
git clone --filter=blob:none --no-checkout https://github.com/stabruriss/kota-app.git local-logs/kota-public
git -C local-logs/kota-public fetch origin --tags
git -C local-logs/kota-public rev-parse "${CONFORMANCE_PUBLIC_COMMIT}^{commit}"
git -C local-logs/kota-public rev-parse "${CONFORMANCE_PUBLIC_COMMIT}:app-v2/src-tauri/src"
git -C local-logs/kota-public diff --name-status b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7 "$CONFORMANCE_PUBLIC_COMMIT" -- app-v2
```

Set `CONFORMANCE_PUBLIC_COMMIT` locally to the established full SHA first. If the
checkout already exists, inspect its origin and preserve it instead of cloning
over it. Do not install, replace, downgrade, or rebuild the app merely to obtain
the expected version.

Push the version report and a dated question **before executing any fixture**.
For a different or unknown version/source binding, maintainers first review the
changed sync, workspace loading, dispatch, and message paths and reconcile the
manuscript's source-audit section with that commit. They then approve an updated
procedure or report HOLD in `ANSWERS.md`. Do not apply old expected behavior to a
new version silently, and do not label a result as the reference release merely
because its About box says `0.1.10`.

## 2. Receive the separate approval

Maintainers record the actual decision in `CONFORMANCE_APPROVAL.json`, with
`status=approved`, a neutral `approved_by` role, UTC `approved_at`,
`run_id=conformance-01`, the actual `public_commit`,
`source_review_status=approved`, and the relevant `source_review_answer_id`.
The two digests are SHA-256 of the exact files below:

```sh
shasum -a 256 RUNBOOK-CONFORMANCE.md validation/conformance-version-m4.json
```

`protocol_sha256` covers this entire file, including fixture construction and
assertions. `version_report_sha256` binds the reported app/CLI binaries and source
review. These are separate from the simulation protocol digest. The runner
checks all fields and the matching answer before continuing; this is an explicit
manual gate, not a command enforced by `handoff.py`. Do not fill approval fields
yourself. A changed document, app, CLI, source binding, or fixture plan requires
renewed review before another execution.

## 3. Prepare and load the disposable workspaces

Use the existing running app after its version and setup path pass review.
The reference implementation reads workspace metadata from the app account's
`Kota/Workspaces` directory. It may enumerate other workspace metadata; this
procedure does not claim process or account isolation. Read and export only the
new synthetic fixture. Never repoint an existing workspace or reuse the study
repository as the fixture source.

Each fixture has an ordinary Git source checkout on `main`, one to three linked
worktrees, and a new application workspace. A bare repository cannot be the
source checkout because synchronization cherry-picks into its working tree.
No remote is needed for these local scenarios. The research branch's push is
separate from application integration; do not use the app's GitHub push action.

The commands below construct the reference backend's on-disk workspace schema.
This is a research fixture setup, not a claimed general-purpose app import API.
Use it only after the version/setup review in step 2 accepts this schema and the
disabled-provider behavior for the installed app. Set these local variables:

```sh
export CONFORMANCE_RUN_ID=conformance-01
export CONFORMANCE_CASE=single-clean
export CONFORMANCE_REPEAT=1
export CONFORMANCE_WORKSPACES_DIR="$(.venv/bin/python -c 'from pathlib import Path; print(Path.home() / "Kota" / "Workspaces")')"
```

Use CPython 3.12.4 from the environment instructions in `RUNBOOK.md`. For the
other fixtures, select the case names in step 5 and repetitions `1` and `2`.
If the actual app uses another workspace registry, obtain a reviewed setup
instruction; changing `KOTA_HOME` or the shell's current directory does not
isolate or redirect the reference app's registry.

Prepare all four cases with repetitions 1 and 2 using the unchanged constructor
below, before one owner-performed app restart. Each invocation still creates a
distinct, fresh fixture. Preserve source/role HEADs, branches, contents, clean
Git status, operation-marker checks, ordered mappings, identity/provider files,
and project metadata before loading. No sync is part of preparation.

For `conformance-01`, Q-20260909-03 records that these eight fixtures are already
prepared and loaded. Use those retained fixtures only after their pre-request
state passes the checks below. Do not recreate them or restart the app again.
For a future separately approved execution, local registration is loaded by app
startup: checkpoint first, obtain an explicit human-attendance confirmation,
let the owner quit/reopen the same app, and wait for manual session recovery.
Do not use an automated restart helper. Normal app discovery of other registered
projects is allowed; direct no edits, sync requests, or messages to those projects.

```sh
.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
import subprocess

cases = {
    "single-clean": [("a", "clean-one.txt", "landed-a\n")],
    "multiple-clean": [("a", "clean-one.txt", "landed-a\n"),
                       ("b", "clean-two.txt", "landed-b\n"),
                       ("c", "clean-three.txt", "landed-c\n")],
    "one-conflict": [("a", "shared-one.txt", "agent-a\n"),
                     ("b", "clean-one.txt", "landed-b\n")],
    "multiple-conflicts": [("a", "shared-one.txt", "agent-a\n"),
                           ("b", "shared-two.txt", "agent-b\n"),
                           ("c", "clean-one.txt", "landed-c\n")],
}
case = os.environ["CONFORMANCE_CASE"]
repeat = int(os.environ["CONFORMANCE_REPEAT"])
assert os.environ["CONFORMANCE_RUN_ID"] == "conformance-01"
assert case in cases and repeat in (1, 2)
fixture_id = f"conformance-01-{case}-r{repeat}"
local = (Path("local-logs/conformance") / fixture_id).resolve()
registry = Path(os.environ["CONFORMANCE_WORKSPACES_DIR"]).resolve()
assert registry.is_dir(), "Verify the running app's existing registry first"
workspace = registry / fixture_id
assert not local.exists() and not workspace.exists(), "Preserve existing fixtures"
source = local / "source"
source.mkdir(parents=True)
workspace.mkdir()
(local / "empty-hooks").mkdir()
for name in (".agent-workspaces", "project-memory", "project-rules"):
    (workspace / name).mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
env.update(GIT_AUTHOR_NAME="Study Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="Study Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], env=env,
                                   text=True, stderr=subprocess.PIPE).strip()

git(source, "init", "-b", "main")
for key, value in {"user.name": "Study Fixture", "user.email": "fixture@example.invalid",
                   "commit.gpgsign": "false", "core.hooksPath": str(local / "empty-hooks"),
                   "core.autocrlf": "false", "rerere.enabled": "false",
                   "rerere.autoupdate": "false"}.items():
    git(source, "config", "--local", key, value)
for name in ("shared-one.txt", "shared-two.txt", "clean-one.txt", "clean-two.txt", "clean-three.txt"):
    (source / name).write_text("baseline\n")
git(source, "add", "--", ".")
git(source, "commit", "-m", "Synthetic fixture base")
base = git(source, "rev-parse", "HEAD")
specs, before = [], []
for role, filename, content in cases[case]:
    agent_id = f"{fixture_id}-{role}"
    cwd = workspace / ".agent-workspaces" / agent_id
    cwd.mkdir()
    tree = cwd / "project-files"
    branch = f"fixture/{fixture_id}/{role}"
    git(source, "worktree", "add", "-b", branch, str(tree), base)
    (cwd / "agent.yaml").write_text(f"id: {agent_id}\nstatus: active\ndisplay-name: Fixture {role.upper()}\n")
    (cwd / "SHELL.yaml").write_text("provider: conformance-disabled\ncommand: conformance-disabled\n")
    (tree / filename).write_text(content)
    git(tree, "add", "--", filename)
    git(tree, "commit", "-m", f"Synthetic {case} role {role}")
    specs.append(dict(agentId=agent_id, cli="conformance-disabled", cwd=str(cwd),
                      projectRoot=str(workspace), worktreeRoot=str(tree),
                      sharedDir=str(workspace / "project-memory"), rulesDir=str(workspace / "project-rules"),
                      adapterPath="", projectId=fixture_id, projectRemote="", projectBaseRef=base))
    before.append(dict(role=role, agent_id=agent_id, branch=branch, head=git(tree, "rev-parse", "HEAD"),
                       changed_file=filename, content=content))
if case in ("one-conflict", "multiple-conflicts"):
    (source / "shared-one.txt").write_text("source-one\n")
    if case == "multiple-conflicts":
        (source / "shared-two.txt").write_text("source-two\n")
    git(source, "add", "--", ".")
    git(source, "commit", "-m", "Synthetic source divergence")
metadata = dict(projectId=fixture_id, repoFullName=fixture_id, remoteUrl="", githubHtmlUrl="",
                defaultBranch="main", baseRef=base, localRoot=str(workspace), sourceDir=str(source),
                sharedDir=str(workspace / "project-memory"), rulesDir=str(workspace / "project-rules"),
                agents=specs, archived=False)
(workspace / "workspace.json").write_text(json.dumps(metadata, indent=2) + "\n")
(local / "paths.local.json").write_text(json.dumps({"workspace": str(workspace), "source": str(source)}, indent=2) + "\n")
(local / "initial.json").write_text(json.dumps(dict(fixture_id=fixture_id, case=case, repeat=repeat,
    base=base, source_head=git(source, "rev-parse", "HEAD"), agents=before), indent=2) + "\n")
print(fixture_id)
PY
```

All worktrees are active metadata entries, with intentionally unsupported
`conformance-disabled` providers and no running terminals. At the reference
commit this prevents launching a repair agent, while allowing the application
to record a conflict notice and skipped delivery. Do not replace this provider
with a real agent. The observations cover routing/recording, not successful
terminal delivery or author repair. If the reviewed app cannot load this setup,
report HOLD instead of changing its code or substituting a real provider.

After loading, confirm each fixture is available in the app and has its
Bartender outbox directory. Startup establishes the watcher for registered
workspaces; existence of the directory is a setup observation, not evidence
that a request was consumed. If needed, select only that fixture and open its
Bartender status/card. Do not click sync yet.

Immediately before the first request on each fixture, check that `workspace.json`
still names exactly its source and roles, in the listed order, and that every
Git HEAD/branch and tracked file matches `initial.json` and the retained initial
snapshot. The source and all worktrees must be clean, with no merge/rebase/
cherry-pick in progress. Identity and disabled-provider files must be unchanged;
no earlier request, automatic sync, or concurrent writer may have affected it.

The only accepted project-metadata differences are addition or changes of
`localRootBytes` and `sourceDirBytes` to nonnegative integers, provided all source,
role, Git, content, and provider checks above pass. These size fields are outside
the scenario's integration assertions. Preserve both metadata versions and
their hashes; never reset them to hide a startup change. Any other metadata
change, reordered/missing role, Git/content change, or automatic sync invalidates
the fixture: retain it and ask. Do not silently restore and reuse its execution id.

## 4. Trigger through the CLI and observe the app's receipt

Set `CONFORMANCE_CLI` locally to the reviewed CLI executable, then load the
fixture's workspace/source paths. Do not commit these variable values. Start
the sync in a persistent terminal and observe it from another task/session:

```sh
CONFORMANCE_FIXTURE_ID="${CONFORMANCE_RUN_ID}-${CONFORMANCE_CASE}-r${CONFORMANCE_REPEAT}"
CONFORMANCE_LOCAL="local-logs/conformance/${CONFORMANCE_FIXTURE_ID}"
CONFORMANCE_WORKSPACE="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["workspace"])' "$CONFORMANCE_LOCAL/paths.local.json")"
CONFORMANCE_SOURCE="$(.venv/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["source"])' "$CONFORMANCE_LOCAL/paths.local.json")"
"$CONFORMANCE_CLI" sync --json --project-root "$CONFORMANCE_WORKSPACE" \
    > "$CONFORMANCE_LOCAL/sync-01.stdout.json" 2> "$CONFORMANCE_LOCAL/sync-01.stderr.txt"
```

Use the explicit fixture workspace root, not the agent CWD or an inherited
project environment. For the reference commit, the CLI atomically creates a
`sync-...` request under `workspace/project-memory/.violet/bartender/outbox/`.
The running app moves it through `processing/` to `delivered/` or `failed/`.
The delivered request remains available as `<request-id>.json`, with a paired
`<request-id>.result.json`; the failure path has `<request-id>.error.txt`.
Never manufacture these files or invoke the Rust library instead of the CLI.

For each call, record the UTC start/end, request id, CLI exit code, and separate
facts for request creation, app consumption, and the returned integration result.
The delivered request's schema/action/project mapping can establish creation
even if the watcher consumes the outbox file too quickly to sample. Require its
request id to match the result. A queued file alone is not completion. A CLI exit
code of zero or a `delivered` receipt does not mean `result.ok` is true: unresolved
conflicts are expected in two scenarios.

The observation window is **1,800 seconds per request**, matching the reference
CLI's waiting bound. Monitor only this fixture while the request runs. If no
terminal receipt exists at cutoff, preserve the pending state, report HOLD, and
start no further request. A stopped CLI does not cancel app processing. Do not
delete outbox files, stop the user's app, or issue retries to clear the state.

Before and after each request, observe each source/worktree with:

```sh
git -C "$CONFORMANCE_GIT_TREE" rev-parse HEAD
git -C "$CONFORMANCE_GIT_TREE" symbolic-ref --short HEAD
git -C "$CONFORMANCE_GIT_TREE" status --porcelain=v1
git -C "$CONFORMANCE_GIT_TREE" ls-files --unmerged
git -C "$CONFORMANCE_GIT_TREE" log --format='%H %P %s' -n 8
```

Set `CONFORMANCE_GIT_TREE` to each path already recorded in the local manifest.
Also capture all five tracked file contents and check Git operation markers
using `git rev-parse --git-path` for `CHERRY_PICK_HEAD`, `MERGE_HEAD`, `rebase-merge`,
and `rebase-apply`. Compare content and ancestry; cherry-picked commits need not
retain the input SHA. Capture only this fixture's Bartender actor records from
`project-memory/raw_logs/actor-bartender.md` or its corresponding chat records.
Count unique event ids, not multiple projections of the same message.

After recording the initial result, make no edits and send one more CLI sync.
It generates a **new request id**. This tests repeated logical synchronization,
not replay of an identical dispatch UUID; the CLI offers no fixed-id option.
Save the second call as `sync-02.stdout.json` and `sync-02.stderr.txt`, preserving
the first pair. Do not copy a delivered JSON file back into outbox.

## 5. Assert the four fixed scenarios

The construction in step 3 makes every agent commit branch from the same base.
For conflict cases, source then changes the same one-line file before dispatch,
so the first role fails before the clean role is attempted.

| Case | Roles in order | Expected first result and source content |
|---|---|---|
| `single-clean` | a edits `clean-one.txt` | One commit lands; `result.ok=true`; no conflicts; `clean-one.txt` is `landed-a`. |
| `multiple-clean` | a, b, c edit three distinct clean files | Three commits land; `result.ok=true`; no conflicts; all three `landed-*` values are present. |
| `one-conflict` | a edits `shared-one.txt`; b edits `clean-one.txt` | One clean commit lands despite a's conflict; `result.ok=false`; conflicts contain a only; source retains `source-one` and gains `landed-b`. |
| `multiple-conflicts` | a edits `shared-one.txt`; b edits `shared-two.txt`; c edits `clean-one.txt` | One clean commit lands despite both earlier conflicts; `result.ok=false`; conflicts contain a then b; source retains `source-one`/`source-two` and gains `landed-c`. |

All table values include the final newline written by the constructor. Untouched
files must still contain `baseline` plus newline. In every case require:

1. The receipt names the correct request and fixture; `snapshotCount=0` and the
   published count matches the table. No reset failure or unexpected Git error.
2. The source HEAD advances by the expected successful commits, remains on
   `main`, and has a clean index/worktree with no active Git operation. Failed
   changes are absent from source; no partial conflict markers remain.
3. With no conflicts, every role reaches final source HEAD and is clean. With
   conflicts, the clean role reaches final source HEAD; each blocked role keeps
   its exact pre-request HEAD, branch, file contents, and clean status.
4. Clean scenarios create no `resolve-conflict` notice. Conflict scenarios create
   one such notice for a, identifying its failed commit and the final source
   HEAD with repair/retry instructions. The two-conflict case creates none for b.
   The disabled provider's `delivery-skipped` record is expected; it is not proof
   that a real author received or completed the task.
5. The second, unedited sync leaves source and all role HEADs/content unchanged,
   publishes zero commits, and preserves the expected conflict set. It creates
   no additional `resolve-conflict` event for the same role/failed-commit/source
   HEAD key. Other status/progress records may still be emitted.

Run `single-clean`, `multiple-clean`, `one-conflict`, `multiple-conflicts`, first
with repetition 1 and then repetition 2, using the separately prepared fresh
fixture for each execution. Loading all eight together does not authorize
concurrent requests or skipping the immediate pre-request checks.
Do not infer internal pass counts, full worktree atomicity, successful repair,
or coverage of the larger scenario catalog from these external observations.

## 6. Deliver results and apply stopping rules

For each fixture write relative-path snapshots, the two request/receipt records,
the relevant normalized actor events, and an assertion table under
`deliverables/conformance-01/<case>-r<repeat>/`. Keep original generated workspace
metadata, Git repositories, and raw logs locally under their recorded paths.
Export only a reviewed technical projection: replace fixture path prefixes with
`source/` and `workspace/`, include hashes of retained originals, and omit any
unrelated record entirely. Never commit `paths.local.json` or raw account logs.
Do not copy the workspace recursively or follow its projections into shared
account storage.

Add `deliverables/conformance-01/summary.csv` with one row for each of the eight
planned executions: case, repetition, actual public commit, both request ids,
observed published/conflict counts, assertion status, and failure/HOLD reason.
Include unrun rows if the procedure stops. Retain all observed outcomes.
Write `deliverables/conformance-01/CONFORMANCE_REPORT.md` with:

- Actual app/CLI versions and hashes, public commit, source-review answer id,
  exact approval/version-report snapshots, and this runbook's SHA-256.
- What ran, UTC times, wall seconds, all eight row statuses, and each failed or
  unobservable assertion. Expected conflicts are not execution failures.
- Setup deviations, request timeouts, evidence files and hashes, scheduler
  status, and any limits on source or message observability.
- Overall `PASS` only if both repetitions of all four scenarios and their
  second-sync assertions pass. Otherwise `HOLD`; never relabel an unrun case.

Review and commit only the version report, technical Q/A, and delivery files to
`run-m4`, using the four explicit neutral Git identity variables from `RUNBOOK.md`.
Push the branch so maintainers can review it. Both sides use the two-hour file
exchange; the runner must not schedule extra fixture syncs. Preserve fixture
artifacts until their delivery is accepted; do not remove an active workspace or
change the user's running app as cleanup without an explicit instruction.

Stop immediately on uncertain version binding, unapproved setup, wrong workspace,
an unexpected provider launch, concurrent writes, app startup failure, missing
receipt/message visibility, timeout, or an assertion failure. Preserve the
observation and write one dated `QUESTIONS.md` entry. Do not repair the product,
revise expected values after seeing results, silently rerun a failed fixture, or
switch to a static-only study. Maintainers decide the next step and any changes
to the manuscript's claims.

## Fixed source references

These are static anchors for the reference implementation, not execution results:

- For the reviewed release commit `75eb8fda2b1040c0f1822e0403321a105fec4f6c`:
  [initial workspace loading](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/App.tsx#L1613),
  [registry enumeration](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/integrations/mod.rs#L583),
  [size-field schema](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/integrations/mod.rs#L199),
  [startup dispatch watchers](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L12444),
  [explicit target resolution](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L2012).

- [CLI dispatch and result waiting](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/bartender.rs#L1726),
  [app consumer](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/bartender.rs#L425).
- [Workspace schema](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/integrations/mod.rs#L200),
  [disk role discovery](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/integrations/mod.rs#L2711),
  [status enables the watcher](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/lib.rs#L1787).
- [Integration and refresh](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/bartender.rs#L980),
  [first-conflict notice](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/lib.rs#L2043),
  [message recording and delivery](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/agent_bus.rs#L328),
  [unsupported-provider rejection](https://github.com/stabruriss/kota-app/blob/b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7/app-v2/src-tauri/src/lib.rs#L6879).
