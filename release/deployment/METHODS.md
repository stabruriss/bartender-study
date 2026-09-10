# Bartender deployment records — methods

This is a descriptive, partially observed record of one Kota development deployment. It supports no causal or general reliability claim. All times are ISO 8601 instants; the study bounds use UTC.

## Window and sources

The fixed window is **2026-06-01 00:00 UTC through 2026-09-09 00:00 UTC, end exclusive (100 days)**: the first complete calendar month after the backend appears in Git history, through the last complete UTC day before extraction. This is not a verified release-to-date census. Extraction was on September 9. Main was frozen at source-snapshot-01 (700 reachable commits; tip committer time September 5, 07:53:25 UTC).

Sources are retained Bartender CLI request/result pairs, the structured Bartender actor handoff log, and reachable main Git history. Targeted agent-bus cross-checks did not establish additional conflict outcomes. No general chat or provider-native transcripts enter the dataset.

The backend first appears in retained Git history on May 21 UTC; CLI support appears June 18. Earliest retained observations are snapshot June 2 UTC, handoff June 12, and CLI receipt June 19. These are source-history/retention bounds, **not proven first deployment or complete logging dates**.

## Units, denominators, and findings

| Record set | Observed result | Meaning |
| --- | --- | --- |
| Historical participation | At least 10 identities | Union of positive receipt-publication, snapshot, or handoff evidence; 7 in receipts, 9 in snapshots, 2 in handoffs, with overlap |
| Paired CLI rounds | 82; 82 report success | 67 publish commits; 15 publish none; 176 commit operations and 5 snapshot operations |
| Reachable agent snapshots | 158 | Exact mechanical snapshot-subject match on main; not sync-round counts |
| Conflict handoff keys | 3, with 3 retained assignment records | 1 patch verified landed; 2 outcomes unknown |
| Enqueue-to-status interval | n=82; median 3.281 s, P95 32.883 s | Wall-clock proxy including any queueing; not active execution time |

One CLI request ID plus its result is one round. Neither commit counts nor handoffs are added to that denominator. All 82 initiators are unknown: the request does not store automatic/agent/user provenance. Manual and automatic UI paths invoke the shared engine directly without these per-request receipt files. Consequently **82 is not the total sync count; neither overall success rate nor conflict rate is estimable**. In particular, do not calculate 3/82.

One participant is one historically evidenced worktree/agent identity, pseudonymized W01–W10. No current-active roster filter is applied, so retired identities are not discarded. Current/departed status and participants without retained positive evidence remain unknown. This is not a human contributor count.

One conflict key combines target, conflicting commit, and room baseline. Repeated routing of the same key is suppressed; one retained handoff does not imply one attempt or zero retries. Handoff materialization is not native agent acceptance. A matching zero-context stable patch fingerprint plus contextual range-diff establishes one equivalent patch in frozen main. Two original Git objects are unavailable; subsequent same-title commits alone cannot prove their resolution. Unknown does not mean failed, pending, or requiring a human decision.

## Timing, missingness, and disclosure

Elapsed CLI time is result status.checkedAt minus request.createdAt; P95 uses nearest rank. The single verified conflict has a 177.685 s handoff-to-matching-commit **timestamp proxy**, not an observed main-update or repair duration. Detection time, actual landing time, busy/waiting versus active work, retries, empty cherry-pick skips, and human decisions are null where unobserved. No average conflict-resolution time is reported.

All retained request/result pairs matched and parsed. Empty failed/outbox/processing directories describe extraction-time contents only, not historical absence. Software and logging evolved during the window; retention is incomplete and the CLI subset is selected.

The JSON contains allowlisted timestamps, counts, pseudonyms, evidence classes, and nulls. Names, original IDs/hashes, paths, prompt bodies, and commit subjects are omitted; no identity mapping is distributed. Public tables permit aggregate recomputation, not independent raw-log re-extraction. Absence of a record is never substituted for zero.
