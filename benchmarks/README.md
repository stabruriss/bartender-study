# Runtime estimate, 2026-09-08

The proposed 29,700-run study has a **rough serial estimate of 5.8 hours** on the
measured machine. Reserve **8–10 hours of awake, plugged-in wall time** for a
first full run, allowing for sustained thermal throttling, competing workloads,
and sampling error. This is a planning allowance, not a guaranteed upper bound.
It excludes analysis, figures, manuscript work, and any reruns after code changes.

Machine: MacBook Air, Apple M1 (8 CPU cores: 4 performance, 4 efficiency), 16 GiB
RAM, macOS 26.5.2, Python 3.12.4. The current runner uses one Python process;
there is no measured multicore speedup, GPU work, or model/API cost.

## What was measured

[timing-2026-09-08.jsonl](timing-2026-09-08.jsonl) contains a selection plan written
before measurement, 90 timing-only records, and a completion record. All 90
finished without a diagnostic timeout or error, in 60.82 seconds overall.
Individual samples took 0.078–5.124 seconds. This measures execution performance,
not the scientific claims of the proposed study.

The model source is commit `daecfcb`; the log records hashes of every model module
and the parameter digest
`92dc23981ddd5628761f9c88967a408836c68185110469f7fe82f463155145c0`.
The worktree was dirty only because the new benchmark files were present.
The configuration remained `proposed`. Formal seeds 1000–1029 were not used.

Before any measurements, the diagnostic grouped proposed cells by question,
team/dependency/avoidance case, edit length, and policy: 30 synchronization
strata and 15 repair-delay strata. It selected two cells uniformly without
replacement from each stratum using selection seed 20260908. Each measurement
used a different reserved diagnostic seed, 900001–900090.

Each sample includes proposal generation, model replay, result construction,
descriptive survival-table construction, JSON encoding, and gzip compression
and local writes. Temporary full records are deleted; only input size, timing,
and compressed byte counts are retained. No outcome metrics, policy comparisons,
or study curves were inspected or retained. Timing does not change the model or
the proposed scientific parameters.

## Extrapolation

For each stratum, multiply its two-sample mean duration by its number of proposed
cells and by 30 study seeds. Sum those products for the complete estimate.

| Question | Planned runs | Model and record construction | Compression and writes | Total |
|---|---:|---:|---:|---:|
| Synchronization interval | 18,900 | 0.98 h | 0.80 h | 1.78 h |
| Post-dispatch repair delay | 10,800 | 1.96 h | 2.06 h | 4.01 h |
| Both | 29,700 | 2.93 h | 2.86 h | 5.80 h |

Using the smaller or larger observed time within each stratum instead of its
mean gives 5.12–6.47 hours. This is a sensitivity envelope, **not a confidence
interval or a runtime bound**; two timings per stratum do not cover all variability.

The benchmark charges for writing a compressed input flow on every sample. The
formal runner writes each unique flow once, so this part of the estimate is
conservative. Conversely, the short diagnostic does not establish sustained
fanless-laptop throughput. Checkpoint/summary writes and final across-seed CSV
aggregation are not timed separately. The 8–10 hour allocation allows for these
differences; it should be checked against actual approved-run progress.

Run records alone extrapolate to about 3.85 GB compressed. Repeated flow writes
would add about 11.54 GB, though the formal runner deduplicates them. These are
timing-sample storage estimates, not observed full-study artifact sizes.

## Reproduce the timing diagnostic

On macOS, from the repository root, choose a new log path:

```sh
python3 -m benchmarks.timing --output benchmarks/timing-new.jsonl
```

The diagnostic has a 45-second per-sample limit and a 600-second total limit.
Timeouts/errors remain in its log and must not be extrapolated as successful
complete-run timings. The formal study still requires explicit parameter
approval through its normal runner. After the recorded measurement, the script's
machine metadata collection was changed from the verified machine description
to direct `sysctl` reads; workload selection and timing were unchanged.
