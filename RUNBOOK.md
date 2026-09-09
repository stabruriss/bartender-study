# Runbook: reproduce the scheduling study

**Treat every committed byte as public from the moment it is written.** Commit
only synthetic research inputs, technical instructions, and reproducibility
records. Use repository-relative paths and neutral roles. Keep personal or
account information, contact details, private correspondence, credentials,
device identifiers, host names, and unrelated project context out of files and
commit metadata. Do not paste full environment dumps, terminal transcripts,
screenshots, or absolute local paths into the repository. Review technical error
messages before copying them. The repository remains private until the complete
manuscript and research artifacts are released together; the runner must not
change its visibility, create a public release, or submit the manuscript.

## Purpose and current state

Measure how synchronization frequency and post-dispatch repair delay affect
integration in a declared synthetic worktree model, retaining every planned
outcome, including unfavorable and unfinished cases.

The formal parameter plan and this runbook are **awaiting approval**. A new runner
may prepare the environment, run controls, and run the bounded three-seed
reproducibility check. It must stop before formal execution until the approved
configuration, approved protocol digest, and matching M1/M4 check are present.
An architectural decision to use an M4 machine is not parameter approval.

The proposed study has 990 cells and seeds 1000–1029 for each cell: 29,700 runs.
The scientific definitions are in [README.md](README.md); the sole formal
parameter file is [configs/study-draft.json](configs/study-draft.json). Its filename
stays unchanged when its approval metadata is filled. The runner does not infer
missing choices from previous conversations and does not edit the model or plan.

## Environment

- CPython **3.12.4**, with `.python-version` recording the version. Exact patch
  matching is required for this cross-machine check. If it is unavailable, open
  a repository question; do not substitute another Python version silently.
- `requirements.lock` intentionally lists **zero third-party packages**. Runtime,
  controls, hashes, compression, and reporting use the standard library. A fresh
  virtual environment isolates them from machine-specific packages.
- `PYTHONHASHSEED=0` for every command below. Results are compared as canonical
  JSON content, not gzip bytes or wall-clock metadata.
- One Python process, no GPU, external model/API, application installation, or
  product/deployment data. Hardware performance changes elapsed time; it must not
  change the declared simulation. The intended execution machine is an M4 Mac.
- At least **20 GiB free disk space**, connected power, and wakefulness through
  execution and packaging. This allows headroom for about 4.1 GB of compressed
  raw records, an archive, and verification. No M4 runtime measurement exists yet.

All commands run from the repository root. If a command fails, preserve what it
wrote and follow the question protocol below. Do not continue past a failed gate.

## 1. Obtain the handoff and create the execution branch

The repository is already open in the execution workspace with its authorized
`origin` remote. Enter the Git worktree containing this file first; the app's chat
or session directory is not the repository root. Do not put account URLs or local
workspace paths into reports.

Use an ordinary checkout owned by this execution task. If Kota manages the
current worktree's branch, leave that branch alone and create a separate runner
checkout from its authorized remote (once, from the worktree containing this file):

```sh
git clone --branch simulation-pilot "$(git remote get-url origin)" ../bartender-study-runner
cd ../bartender-study-runner
```

Do not overwrite an existing runner checkout. All remaining commands, outputs,
and file communication belong to that checkout. Confirm there are no unknown
edits before switching:

```sh
git status --short
git fetch origin
git switch simulation-pilot
git pull --ff-only origin simulation-pilot
git switch -c run-m4
git config --local user.name 'Study Runner'
git config --local user.email 'study-runner@example.invalid'
git push -u origin run-m4
```

If `run-m4` already exists remotely, use `git switch --track origin/run-m4` instead
of creating it. If it already exists locally, use `git switch run-m4` and
`git pull --ff-only origin run-m4`. Never reset, force-push, or discard unknown
edits. Do not create a second execution branch for the same run.

Application sessions may inject Git author/committer environment variables that
override repository config. For every commit, use the explicit four-variable
identity prefix shown below; do not rely on `git config` alone. This applies to
question commits as well as validation and delivery commits.

## 2. Prepare Python and run all control tests

```sh
python3.12 --version
python3.12 -m venv .venv
.venv/bin/python -m pip install --no-index --require-hashes -r requirements.lock
PYTHONHASHSEED=0 .venv/bin/python handoff.py environment --output validation/environment-m4.json
PYTHONHASHSEED=0 .venv/bin/python handoff.py controls --output validation/controls-m4.json
```

The control report must say `pass`, with no failures, errors, or skipped tests.
The command runs all tests, including the 24 original model/control tests and
handoff checks. These checks are not scientific study results. If a test fails,
inspect it locally; put its test identifier and a minimal sanitized explanation
in `QUESTIONS.md`, not a raw traceback. Do not repair code on the execution branch.

Output records are created exclusively. If one already exists, do not delete it
to rerun unnoticed. A repeat after a maintainer-directed change needs a dated
question/answer and a distinct record name; archive the previous record before
the maintainers designate the new active control record.

## 3. Compare the two machines using three diagnostic seeds

`configs/determinism.json` fixes seeds **910001, 910002, 910003**, each replayed
under six short protocol cases: clean-first, in-place, and both baseline-read
times crossed with both repair-duration rules for delayed repair. This is
**18 short runs**, each with a 16-unit window, separate from all formal seeds.
Do not inspect these outcomes to select or alter formal parameters.

The maintainers compute `validation/determinism-m1.json` on the reference machine.
The execution agent must compute its own M4 record; never copy, relabel, or edit
the M1 values to create a candidate.

```sh
PYTHONHASHSEED=0 .venv/bin/python handoff.py determinism --label m4 --output validation/determinism-m4.json
PYTHONHASHSEED=0 .venv/bin/python handoff.py compare --output validation/determinism-comparison.json
git add -- validation/environment-m4.json validation/controls-m4.json validation/determinism-m4.json validation/determinism-comparison.json
env GIT_AUTHOR_NAME='Study Runner' GIT_AUTHOR_EMAIL='study-runner@example.invalid' \
    GIT_COMMITTER_NAME='Study Runner' GIT_COMMITTER_EMAIL='study-runner@example.invalid' \
    git commit -m 'Record M4 controls and cross-machine determinism check'
git push origin run-m4
```

Both the input-flow hash and full result-content hash must match exactly for
every case/seed. The result hash covers per-edit and per-repair records, metrics,
and descriptive survival records. Labels, environment descriptions, compression,
and elapsed time are outside the compared payload. The helper also checks fixture
and model-file hashes. A matching short check is necessary, not proof that all
possible runs on all hardware are identical.

If comparison fails, commit only the locally generated records that exist and
the dated question. Report which case/seed hashes differ. Do not round floats,
change the reference, skip a failing case, or begin the formal scan.

## 4. Receive the approved files

Communication is file-based. Maintain the execution branch as described below.
To receive a reviewed answer or approval, with local records already committed:

```sh
git fetch origin
git merge --no-edit origin/simulation-pilot
git push origin run-m4
PYTHONHASHSEED=0 .venv/bin/python handoff.py fingerprints
PYTHONHASHSEED=0 .venv/bin/python handoff.py preflight --run-id study-01
```

Formal execution requires **both** approval records:

1. The configuration's `approval` object records actual study-owner approval of
   its `parameters_sha256`, using a neutral role and UTC timestamp.
2. `RUN_APPROVAL.json` records actual review of the runbook and execution protocol:
   `status=approved`, `approved_by`, `approved_at`, `run_id=study-01`, and the exact
   parameter and protocol digests printed by `fingerprints`.

Only maintainers record these decisions after review; the runner must not fill
them to make a command pass. The protocol digest covers this runbook, the helper,
model, tests, runtime lock, fixture, and ignore rules. Approval fields themselves,
technical questions/answers, and generated reports are excluded. Changing any
covered file or scientific parameter requires another review. Approval metadata
records a decision; it is not a cryptographic authorization service.

`preflight` also checks current matching determinism records, passing controls
for this protocol, the exact runtime, branch `run-m4`, a clean worktree, free
space, and a fresh output path. A changed protocol makes the previous control
report stale. Ask how to archive and replace it; do not forge a new digest.

## 5. Run the entire approved study

After `preflight` reports `ready`, run once in a persistent terminal/task session:

```sh
caffeinate -i env PYTHONHASHSEED=0 .venv/bin/python handoff.py run --run-id study-01
```

`caffeinate` is the macOS wakefulness wrapper; on another approved platform, run
the same Python command under that platform's wakefulness facility. It is not a
scientific setting. Keep the laptop open and connected to power.

The helper repeats the gates and invokes the existing serial study runner.
Outputs go to `outputs/study-01/`; a fresh directory is required. Standard output
contains progress and error counts. It is acceptable to monitor those counts,
process liveness, and disk capacity. Do not read interim outcome tables to adjust
parameters, stop on a favorable result, or choose cells to rerun. Do not pull or
merge code while the run is executing.

Every planned seed is attempted, including negative outcomes. Runtime errors are
retained. A process interruption leaves partial data and an interrupted manifest.
There is **no resume command**. If interrupted or any run fails, preserve the
directory, collect what exists, report HOLD, and open a question. A new complete
run with a new id needs maintainer instructions and matching approval; never
overwrite the original or rerun only favorable/failed cells silently.

## 6. Verify, package, and return the delivery

```sh
PYTHONHASHSEED=0 .venv/bin/python handoff.py collect --run-id study-01
```

Collection checks membership of all cell/seed records; opens every compressed
run and flow; reconciles raw records with summaries, input hashes, the saved
configuration, and source hashes; and regenerates both CSVs for comparison.
It records PASS or HOLD. An error/partial scan is archived with HOLD, not erased.
Archiving/verification time is separate from the measured formal execution time.

Proposed output size, based on the earlier timing sample: **3.85 GB** of compressed
run records plus **0.23 GB** of deduplicated inputs (300 unique flows), about
**4.1 GB plus small metadata and summaries**. This is an estimate, not a measured
M4 artifact size. All 29,700 raw run files, per-seed summaries, inputs, errors,
configuration, and manifests stay on M4. The workflow does not require expanding
all compressed JSON at once.

The helper writes an archive as ordered parts of at most 1 GiB under
`archives/study-01/`. Each tar member has a relative name, zero numeric owner/group
ids, empty owner/group names, and normalized timestamps. `artifact-index.json`
lists every original file hash, each part's bytes/hash, and the concatenated tar
hash. These parts are retained on M4 for submission-day release attachments;
creating them is not permission to upload them publicly.

| Deliverable | Committed to `run-m4`? |
|---|---|
| `validation/`: environment, controls, both determinism records and comparison | Yes |
| `deliverables/study-01/summary.csv` and `paired-differences.csv` | Yes; all cells, including null/negative entries |
| `deliverables/study-01/config.json`, `cells.json`, `manifest.json`, `execution.json`, `RUN_APPROVAL.json` | Yes; exact plan, source, timing, environment, approval and checks |
| `deliverables/study-01/verification.json`, `artifact-index.json`, `RUN_REPORT.md` | Yes; acceptance, archive inventory, deviations |
| Root `RUN_REPORT.md`, `QUESTIONS.md`, `ANSWERS.md` | Yes; technical records only |
| `outputs/study-01/`, including `summaries.jsonl`, `runs/`, `flows/` | No; retained on M4 and in the archive |
| `archives/study-01/`, virtual environment, terminal logs | No |

Complete the deviations line in the generated report with either `None observed`
or the actual interruption/change and its question/answer ids. Do not report
scientific success based on a successful execution. Then copy the completed
report to the root template and review the exact staged files:

```sh
cp deliverables/study-01/RUN_REPORT.md RUN_REPORT.md
git add -- deliverables/study-01 RUN_REPORT.md
git diff --cached --stat
git diff --cached --check
env GIT_AUTHOR_NAME='Study Runner' GIT_AUTHOR_EMAIL='study-runner@example.invalid' \
    GIT_COMMITTER_NAME='Study Runner' GIT_COMMITTER_EMAIL='study-runner@example.invalid' \
    git commit -m 'Deliver complete study-01 execution records and archive hashes'
git push origin run-m4
```

Use an accurate HOLD/partial-run commit message when applicable. The helper
refuses a delivery larger than 100 MB. Do not bypass ignore rules with `git add -f`,
commit archives via Git/LFS, delete raw records to save space, or upload them to a
different service. Open a question if the delivery exceeds its budget.

For later recovery, concatenate parts in filename order, verify the full SHA-256
against `artifact-index.json`, then extract the tar in a separate directory.
Keep the parts until the publication archive has been uploaded and verified.

## Acceptance checklist

- All controls pass with no skips, for the approved protocol digest.
- All 18 result/flow hash pairs match between independently executed M1 and M4
  controls, with the same fixture, model files, CPython version, and hash seed.
- Both approval records match the actual parameter/protocol digests and run id.
- Exactly 990 cells × 30 seeds = 29,700 distinct completed run records for the
  current plan; zero failed runs; complete manifest; no missing or extra raw files.
  If the owner later changes the approved plan, use its exact expanded counts.
- Saved raw records, input content hashes, configuration, model hashes, and
  regenerated CSVs agree; verification says `pass`.
- The report includes what ran, UTC start/end, measured wall seconds, environment,
  failures, interruptions/deviations, and archive hashes. No unfinished template
  fields. All raw data remain recoverable on M4; only small, reviewed files enter Git.

## Questions and answers: repository files only

The M4 runner owns `run-m4`, writes one dated entry per issue in `QUESTIONS.md`,
commits it, and pushes that branch. Use ids such as `Q-YYYYMMDD-01`, a UTC date,
the blocked step, observed behavior, and one concrete question. Never paste
unrelated context or local identifying details. No other communication channel
is part of this execution protocol.

Maintainers inspect `origin/run-m4:QUESTIONS.md`, answer the same id in
`ANSWERS.md` on `simulation-pilot`, and push. The runner fetches and merges that
branch before acting, then records acknowledgment under the original question.
Answers cannot silently override frozen parameters or protocol approval. A
scientific/protocol change requires updated files and approval before a new run.
Do not resolve merge conflicts by replacing entire files; ask if ownership is
unclear. Preserve dated questions and answers as technical provenance.

## Prohibited changes

The execution agent must not modify `bartender_sim/`, tests, `handoff.py`, runtime
locks, either configuration, the M1 reference, this runbook, or approval records.
It must not tune from interim outcomes, omit cells, alter seeds, hide failures,
rewrite history, change visibility, or claim the synthetic study validates real
Git/application behavior. Bring required changes back through the file protocol.
