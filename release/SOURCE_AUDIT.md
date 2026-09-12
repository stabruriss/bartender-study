# Public source audit: Bartender integration and triggers

Reviewed on 2026-09-10. This document reports static source facts, not timing measurements or a proof of behavior under arbitrary concurrent writes. The separate fixed-fixture observations are in `deliverables/conformance-01/`; acceptance is recorded in `ANSWERS.md` and `validation/delivery-acceptance-m1.json`.

## Version and scope

- Public source: <https://github.com/stabruriss/kota-app>.
- Original integration audit: `b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7`.
- Release and trigger audit: `v0.1.10`, peeled commit `75eb8fda2b1040c0f1822e0403321a105fec4f6c`.
- Both commits have the same complete `app-v2` tree, `6042875c7b7a31dd4ea7fd1a57d124bfeb99f4ce`, and the same `app-v2/src-tauri/src` tree, `147cbc348cd1e3aa8a90d4f0c67e3652798b083a`.

The links below use the release commit. Tree equality connects the earlier integration audit to this release; it does not establish a reproducible binary build. Distribution provenance and the execution environment are documented separately in `validation/conformance-version-m4.json`.

To check the tree comparison in a clone of the public source repository:

```sh
git fetch origin tag v0.1.10
git rev-parse 'v0.1.10^{commit}'
git rev-parse 75eb8fda2b1040c0f1822e0403321a105fec4f6c:app-v2
git rev-parse b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7:app-v2
git diff --exit-code b3db3c8290d8dae5a1ee5f7f40222d3dcf77f1b7 75eb8fda2b1040c0f1822e0403321a105fec4f6c -- app-v2
```

## Local integration

| Source fact | Scope and limitation | Source anchor |
|---|---|---|
| Targets follow workspace metadata order, filtered to active, unique agents with existing worktrees. Dirty source and target trees may be snapshotted. | Metadata `active` is not a check that the agent has stopped writing. | [Collection](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L980-L1041), [targets](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1517-L1533) |
| Pending commits are recomputed against the current shared source HEAD before each target attempt, then cherry-picked sequentially. | A target can have multiple commits. Its successful prefix remains integrated if a later commit fails. Local publication is separate from a remote push. | [Publication and pending commits](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1169-L1277), [remote push](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L693-L779) |
| Failed targets are retained while the rest of the pass is processed. A further pass occurs only when failures remain and the previous complete pass published at least one commit. | Rechecking occurs after a pass, not after every successful target. Successful prefixes count as progress. Empty cherry-picks can be skipped. | [Pass loop](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1044-L1089), [empty handling](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1169-L1199) |
| At stagnation the loop returns remaining conflicts. The outer entry point attempts to hand back the first conflict. | The function does not wait for all authors to repair. Serial completion of all repairs is an analytical protocol assumption, not a lifecycle guarantee of one call. | [Termination and refresh](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1091-L1147), [CLI handback](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L495-L552), [UI handback](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L1823-L1858) |
| The handback names a freshly read shared HEAD, failed commit, Git error, and instructions to rebase, repair, and retry. | It carries a commit reference rather than full patch bytes; errors are not guaranteed structured conflict locations. A submitted message is not a completed or semantically verified repair. | [Payload](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L2043-L2137), [delivery and deduplication](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/agent_bus.rs#L328-L390) |
| The manager rejects concurrent synchronization through a `try_lock`, and holds a status-computation lock. Worktree reset/clean and status refresh are real operations. | The locks do not exclude arbitrary external Git writers. Conflict-free integration still has snapshot, scan, refresh, and locking costs. Equal file content need not imply identical commit identities. | [Locks](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L300-L355), [refresh](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1222-L1245) |

## Automatic trigger and explicit requests

**Citable statement.** In v0.1.10, the optional automatic trigger polls every 15 seconds and requires pending room changes, no UI-observed working or maybe-idle agent in the current room, no busy or conflict blocker, and a three-minute cooldown after the last observed composer prompt and sync completion; explicit user and agent requests enter the same local synchronizer without this automatic idle/cooldown gate.

The precise conditions are:

1. The component has a workspace and the project's AUTO setting is enabled. Missing stored settings default to false. This is a frontend component timer, not evidence that every background workspace is automatically synchronized. [Setting](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L265-L276), [workspace and setting state](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L1253-L1256).
2. The working set contains current-room agents whose reported work state is `working` or `maybeIdle`. The timer requires that set to be empty. This is an observed-state gate, not a filesystem-quiescence or task-completion proof; an unavailable state contributes no member to the set. [Definition](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/App.tsx#L1819-L1830), [prop](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/App.tsx#L4415-L4418), [count](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L1200-L1208).
3. Each 15-second tick reads the latest state ref. It requires a status with `roomChangeCount > 0`, no conflict blocker, no silent sync in progress, and no active busy action. External sync activity for the current workspace contributes to that busy state. Changes in dynamic state update the ref without restarting the interval. [Busy state](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L1243-L1250), [timer](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2950-L2983).
4. A fixed constant of three minutes governs two elapsed-time comparisons: the last observed composer prompt and last observed sync completion. A missing/invalid prompt timestamp or absent previous sync timestamp bypasses its respective comparison. An ineligible tick is skipped; no exponential retry delay is accumulated. Agent inactivity is checked at the tick, not required to have lasted three minutes. [Constant](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L130), [prompt events](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2817-L2822), [comparisons](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2975-L2981).
5. The sync timestamp starts at zero and updates after a UI call returns or throws. A tracked external request's completion/failure also updates it when it belongs to the current workspace. Thus failed calls also induce cooldown, but this component's timestamp is not a complete history of all calls. [Initialization](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L1203), [external completion](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2649-L2669), [UI completion](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2856-L2878).

| Route | Calls | Idle/cooldown scope |
|---|---|---|
| Automatic | Timer → `runSync('silent')` → `bartenderSyncLocal` → Tauri command → `sync_local_with_progress`. | Includes the automatic conditions above. |
| Explicit user button | `runSync('manual')` → the same UI and backend functions. | The common UI function checks workspace/busy/external activity/silent-running/conflict-blocker state, but not the working count or the two clocks. |
| Agent CLI request | `kota-bartender sync` → atomic JSON outbox write → running app watcher → `process_sync_dispatch` → `sync_local_with_progress`. | Does not traverse the frontend timer. The manager's execution locks still apply. A person can also invoke the CLI; receipts do not identify an agent-versus-human initiator. |

Route anchors: [manual button](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L3713-L3722), [shared UI function](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/chrome/RightColumn.tsx#L2838-L2858), [client bridge](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src/pty-client.ts#L2067-L2084), [Tauri entry](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/lib.rs#L1823-L1858), [CLI](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1768-L1772), [outbox](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L1885-L1900), [watcher/dispatch](https://github.com/stabruriss/kota-app/blob/75eb8fda2b1040c0f1822e0403321a105fec4f6c/app-v2/src-tauri/src/bartender.rs#L425-L513).

## Relationship to observations and models

The fixed conformance fixtures exercise explicit CLI requests with the app running. They do not test the automatic timer or establish safety under unobserved writes. The synthetic simulation has its own declared arrival, repair, dependency, and queue assumptions; its interval and delay axes are not measurements of this UI scheduler. The deployment dataset records CLI receipts with limited coverage, so it cannot establish the frequency of automatic or explicit user-button synchronization.

## Release-content review

On 2026-09-12 the three subsequent figure/provenance commits and the source-package additions were reviewed for release content; see [CONTENT_AUDIT.md](CONTENT_AUDIT.md). This does not change the application version, source facts or observation limits recorded above.
