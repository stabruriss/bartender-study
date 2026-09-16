# Bartender scheduling study

This repository contains a synthetic discrete-event model of continuous worktree
integration and author repair. The simulator does not run Kota, Git conflict
resolution, or an LLM. A separate application conformance procedure is described
in [RUNBOOK-CONFORMANCE.md](RUNBOOK-CONFORMANCE.md); deployment observations are
outside both execution procedures.

Status, 2026-09-09: **study-01 and conformance-01 are accepted**. The formal
scan completed 29,700 runs without failure on the approved Apple M3 machine.
The original collection HOLD is preserved; independently approved collect-only
`verify-02` passed with original data unchanged. Maintainer acceptance checked
the delivered summaries and application evidence in
[the acceptance record](validation/delivery-acceptance-m1.json).
The four manuscript result figures, complete tables and numerical summary are in
[analysis/](analysis/README.md). Code, configurations, seeds and the accepted
scan record are public. The manuscript source package is in
[release/arxiv/](release/arxiv/); arXiv submission status is separate from
repository availability.

The raw simulation archive is now publicly downloadable in four parts. See
[the archive index](release/RAW_ARCHIVES.json) for current URLs and SHA-256
values, and [the download check](release/RAW_DOWNLOAD_VERIFICATION.json) for
independent verification of all part hashes and the complete archive hash.

The v1 preprint is archived on Zenodo at
[10.5281/zenodo.22802897](https://zenodo.org/records/22802897); the concept DOI
is [10.5281/zenodo.22802896](https://zenodo.org/records/22802896).

The completed execution procedure is [RUNBOOK.md](RUNBOOK.md).
It specifies the pinned environment, file-only communication, cross-machine
checks, approval gates, raw-data retention, and required delivery. The handoff
received formal approval in `RUN_APPROVAL.json`; independent controls and
the cross-machine comparison passed. The `m4` file/branch labels were retained
after approval of the actual M3 machine. The runbook's draft-status
paragraph is retained as part of the frozen approved document; approval status
comes from the configuration and `RUN_APPROVAL.json`. Application conformance
has its own approved `CONFORMANCE_APPROVAL.json` and accepted fixed observations
at v0.1.10 / public commit `75eb8fda2b1040c0f1822e0403321a105fec4f6c`.
The observations do not establish real-agent repair, performance, or wider
scenario coverage. Execution and its recurring file exchange are closed;
the dated dispositions and retained-original requirements are in `ANSWERS.md`.

## Inspect and test

The current execution handoff requires CPython 3.12.4 and the standard library
only. `requirements.lock` records that there are no third-party dependencies.

```sh
python3 -m bartender_sim plan --config configs/study-draft.json
python3 -m unittest discover -s tests -v
```

`plan --cells` also prints every fully resolved configuration, including the
derived response delays and observation windows. Planning generates no edit
stream and performs no simulation. Tests use hand-constructed streams, finite
control models, and a temporary zero-edit output check; they are not study runs.

Maintainers have recorded study-owner parameter approval in the configuration's
`approval` object: status `approved`, role, timestamp, and
the `parameters_sha256` printed by `plan`. A change to the parameter plan or seeds
invalidates that approval. The M4 operator also needs the runbook/protocol approval
and cross-machine check in `RUNBOOK.md`; use its guarded entry point:

```sh
PYTHONHASHSEED=0 .venv/bin/python handoff.py preflight --run-id study-01
caffeinate -i env PYTHONHASHSEED=0 .venv/bin/python handoff.py run --run-id study-01
```

The output directory must be new. Missing or mismatched approvals, controls, or
cross-machine checks are rejected before any output directory is created.
Approval metadata records a decision; it is not proof of when a researcher first saw data. No command
changes repository visibility.

A separate [timing diagnostic](benchmarks/README.md) estimates the proposed full
scan at roughly 5.8 hours on an M1 MacBook Air, with an 8–10 hour planning allowance.
Its 90 reserved-seed invocations retain timing only, not scientific outcomes;
they do not approve or replace the study runs.

## Approved numerical plan

Time is measured in units of one agent's mean inter-edit time. It is not a
calibrated number of minutes. The edit rate is 1 per agent per unit time.

| Quantity | Approved values |
|---|---|
| Agents | 2, 4, 8 |
| Geometry | 8 files, 256 lines each; edit lengths 4, 16, 64 |
| Nominal pair overlap probability | 0.00343506, 0.01556232, 0.06872332, respectively |
| Dependency probability | 0, 0.1, 0.3 in the synchronization study |
| Avoidance probability | 0, 0.5, 0.9 in the synchronization study |
| Synchronization interval | 0.125, 0.25, 0.5, 1, 2, 8, 32 |
| Post-dispatch response delay | 0, 0.25, 0.5, 1, 2, 4 times the nominal characteristic time |
| Base repair duration | 0.25 |
| Repair context weight | 0.05 per unseen foreign landed edit |
| Seeds | 1000 through 1029; 30 per cell |
| Dependency / visibility history | Last 32 proposals / last 32 visible shared revisions |
| Avoidance attempts | Four fixed alternative location proposals; keep the original if none qualifies |
| Long-unresolved indicator | More than five ejections and still unlanded at cutoff |

The geometry probability is exact for independent uniform file and integer start
choices. With `m = L - length + 1` and `r = min(length - 1, m - 1)`, it is
`[m(2r+1) - r(r+1)] / (K m²)`. It is not an independent Bernoulli conflict knob.
Avoidance and dependencies change the realized process.

The plan uses declared slices rather than a full factorial over every parameter:

- **Synchronization interval:** five `(n, d)` cases: `(2, 0)`, `(4, 0)`,
  `(8, 0)`, `(4, 0.1)`, `(4, 0.3)`. Each crosses all three lengths, all three
  avoidance probabilities, seven intervals, and the clean-first and in-place
  policies. Fixed repair duration; refresh at repair start. Horizon 256.
  This gives 630 cells.
- **Repair delay:** five `(n, d, a)` cases: `(2, 0, 0)`, `(4, 0, 0)`,
  `(8, 0, 0)`, `(4, 0.1, 0)`, `(4, 0.1, 0.5)`. Each crosses three lengths,
  six delays, both baseline-read times, and both repair-duration rules.
  Synchronization interval 0.5. Horizon `max(256, 32 / mu_nominal)`, identical
  across response delays and repair rules for a given geometry/team size.
  This gives 360 cells. The zero-delay kick-back point is clean-first;
  deterministic tests check exact equality rather than counting it twice.

Total: **990 cells, 29,700 planned runs**. The longest observation window is
9315.693 model time units. These are approved coverage choices, not results.
`mu_nominal = p_nominal (n-1) rate` assumes prompt background landing only for
axis scaling. Actual landings are endogenous and are recorded.

## What the dynamic model does

Each actor generates Poisson arrivals independently. Arrival times, locations,
alternative locations, and dependency candidates are drawn before policy replay
from separate, deterministic actor streams. Policy, repair, and synchronization
decisions draw no new randomness. Comparisons therefore share exogenous
proposals; realized locations and visibility can differ between policies.

An edit is one indivisible, fixed-length interval. It depends on its own actor's
previous edit; an optional foreign prerequisite is selected from the last 32
proposals, always earlier in time. This dependency graph is acyclic. Edits
continue arriving while authors repair; actor capacity is not modeled.

Actors with no pending work refresh their view after synchronization. Actors
with blocked work keep their previous view. A later edit that has seen an older
overlapping edit is sequential even when avoidance is zero. Avoidance only
relocates a proposed edit away from recently visible foreign work; it does not
magically prevent a conflict with invisible work or discard an edit.

A pending edit fails if its prerequisite has not landed or if it overlaps a
foreign edit newer than its covered shared revision. Within each worktree,
commits are attempted in order; a failed prefix blocks its successors. Successful
prefixes stay landed. The synthetic shared history is append-only; lines do not
shift and commits do not become content-equivalent.

The policies use the same fixed actor order:

- **Clean-first:** attempt each worktree, hold failures, and repeat full passes
  while any edit lands. After stalling, dispatch one author's first held edit.
  Other clean work can land at later scheduled synchronizations during repair.
- **In-place:** stop at the first failed edit and finish its repair before
  continuing the captured batch. Synchronization requests during that repair
  do not advance shared state. Missing later prerequisites can cause blocking;
  repairs do not invent or bypass those prerequisites.
- **Kick-back:** the same clean-first protocol with an added response delay.
  One dispatched item occupies the serial repair slot while waiting or repairing.
  Queue wait before dispatch is separate from the configured response delay.

A completed repair triggers another synchronization. A waiting, not-yet-started
repair can be cancelled when automatic dependency rescue lands that edit first.
Only dependency rescue is modeled; equal-content/empty-cherry-pick rescue,
renames, semantic checks, and dynamic footprint expansion/shrinkage are excluded.

Equal-time event order is repair completion, edit arrival, scheduled sync, repair
start. Application attempts have zero modeled duration, but are counted. Thus
this model cannot measure Git overhead or establish zero wall-clock cost.
Arrivals occur in `[0, H)`; completions and scheduled ticks at `H` count. There
is no extra drain period or forced final synchronization.

## Repair snapshot and cost assumptions

Two repair protocols are explicit. Reading at dispatch leaves a stale window
of response delay plus repair duration. Reading again at repair start absorbs
the intervening work, leaving a stale window of the repair duration alone.
Neither protocol is claimed to be a verified product behavior.

Repair context is the count of unseen foreign landed edits at the chosen read
revision. Overlapping lines are deduplicated within that repair. Work units are
`1 + 0.05 * context_count + overlapping_lines / edit_length`. This is a declared
cost proxy, not measured human effort, tokens, or correctness. Duration is either
the fixed base duration or base duration times those work units. The duration
rule is scanned for repair delay so waiting is not forced to produce an
exponential retry curve by construction.

The earliest failed-edit-to-start delay may also include queueing. Each repair
record stores dispatch, start, read revision/time, duration, context, and outcome,
so that queue delay, attention delay, and the stale window can be distinguished.

## Counters, censoring, and reporting

Count overlapping concurrent **edit pairs**, edits that ever fail, failed
application attempts, dispatches, author repair starts, and completed repairs
separately. Repeated automatic attempts do not increment author repair counts.
One initial failure is one ejection; each failed repaired submission adds one.
Repair of multiple commits is not silently collapsed into one worktree event.

Overlap pairs are counted once when the later edit arrives and has not seen the
older foreign edit. Finite files do not cap this count. Unique overlapping lines
and the fraction of failed edits are separate bounded quantities. Per-time and
per-generated-edit denominators are both supplied. Per-scheduled-interval pair
counts are not interpreted as per-actual-sync failure counts.

Every generated edit remains in the output, including unattempted suffixes and
unfinished repairs. A non-landed edit is right-censored at the common cutoff.
The more-than-five-ejections indicator reports its denominator, with a separate
early conflict cohort (first failure in the first half of the window). It is
not a permanent-starvation probability. Mean observed latency is a truncated
quantity, not the mean of only completed cases or an uncensored lifetime estimate.

For unfinished repairs, actual busy time and proportional work consumed up to
the cutoff are counted. Per-run Kaplan–Meier records retain censored conflicts;
they are descriptive, without pretending patches in one seed are independent
replicates. Across-seed means use approximate normal 95% intervals, with valid
sample counts and undefined rates retained as null. Paired policy differences
are calculated within seed before averaging. Sparse rates and censoring must be
considered when interpreting those intervals; they are not significance tests.

The output directory contains the exact config, complete cell list, code hashes,
Python/OS versions, Git revision/dirty flag, compressed input flows, per-edit and
per-repair records, per-seed summaries, aggregate CSV, and paired contrasts.
All failed runs remain listed; partial scans retain an interrupted status.
Unexpected and negative results stay in the full scan record. Figures will be
made only after the approved runs, with the full tables retained even when a
figure is not selected for the main paper.

## Deterministic checks and interpretation boundary

The separate fixed-batch control keeps conflict edges unchanged and makes each
repair succeed immediately. Tests enumerate all 1–4 item graphs and initial
blocking masks (1098 cases), checking repair-set and identity-context inclusion.
A four-item shrinking-footprint counterexample deliberately reverses the repair
count inequality. These assertions do not constrain the dynamic study.

Other tests check nonblocking clean work, successful commit prefixes, dependency
rescue and in-place blocking, zero-delay policy identity, both baseline-read
times, nonzero repair exposure, interval probability, input pairing, censoring,
and the execution/parameter approval boundary. The accepted study figures
and bounded application observations are linked above; the controls alone do
not establish product performance or repair correctness.
