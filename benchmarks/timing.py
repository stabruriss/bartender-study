"""Bounded timing diagnostics; never save or report scientific outcomes.

Run from the repository root with `python3 -m benchmarks.timing --output PATH`.
Two cells per suite/case/edit-length/policy stratum are selected before timing.
Diagnostic seeds are disjoint from study seeds. Full transient outputs are
compressed like study outputs, then deleted; only timing and input size remain.
This command neither approves nor invokes the formal study runner.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import platform
import random
import signal
import subprocess
import tempfile
import time

from bartender_sim.__main__ import source_fingerprint
from bartender_sim.model import Scenario, make_flow, simulate
from bartender_sim.plan import cells, describe, load_config
from bartender_sim.report import kaplan_meier


def selection(grid: list[dict]) -> list[tuple[tuple, int, dict]]:
    groups = defaultdict(list)
    for cell in grid:
        s = cell["scenario"]
        groups[(cell["suite"], cell["case"], s["length"], s["policy"])].append(cell)
    rng = random.Random(20260908)
    return [(key, len(group), cell) for key, group in sorted(groups.items())
            for cell in rng.sample(sorted(group, key=lambda c: c["cell_id"]), 2)]


def measure(cell: dict, seed: int) -> dict:
    s = Scenario(**cell["scenario"], seed=seed)
    start = time.perf_counter()
    flow = make_flow(s)
    result = simulate(s, flow)
    result["conflict_survival"] = kaplan_meier([
        (r["observed_conflict_age"], not r["right_censored"])
        for r in result["patches"] if r["first_failure"] is not None])
    modeled = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="bartender-timing-") as temporary:
        output = Path(temporary)
        # Charging every measurement for a flow write overestimates the study's
        # deduplicated flow I/O; report that limitation with the estimate.
        for name, data in (("flow", [asdict(p) for p in flow]), ("run", result)):
            with (output / f"{name}.json.gz").open("xb") as handle:
                with gzip.GzipFile(fileobj=handle, mode="wb", mtime=0, filename="") as zipped:
                    zipped.write(json.dumps(data, sort_keys=True, allow_nan=False).encode())
        run_bytes = (output / "run.json.gz").stat().st_size
        flow_bytes = (output / "flow.json.gz").stat().st_size
    finish = time.perf_counter()
    return {"status": "ok", "proposals": len(flow),
            "model_seconds": modeled - start, "write_seconds": finish - modeled,
            "wall_seconds": finish - start,
            "run_gzip_bytes": run_bytes, "flow_gzip_bytes": flow_bytes}


def timeout(signum, frame):
    raise TimeoutError("timing-only sample exceeded its wall-time budget")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/study-draft.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    grid = cells(config)
    selected = selection(grid)
    seeds = list(range(900001, 900001 + len(selected)))
    if set(seeds) & set(config["seeds"]):
        raise ValueError("diagnostic and study seeds must be disjoint")
    # Do not collect hardware serial numbers, UUIDs, host names, or user names.
    def sysctl(key):
        return subprocess.check_output(["sysctl", "-n", key], text=True).strip()
    machine = {"model": sysctl("hw.model"), "chip": sysctl("machdep.cpu.brand_string"),
               "cpu_cores": int(sysctl("hw.physicalcpu")),
               "logical_cpus": int(sysctl("hw.logicalcpu")),
               "ram_gib": int(sysctl("hw.memsize")) / 1024 ** 3,
               "workers": 1, "python": platform.python_version(),
               "macos": platform.mac_ver()[0]}
    header = {"kind": "timing_plan", "started_at": datetime.now(timezone.utc).isoformat(),
              "purpose": "runtime estimate only; no study outcomes retained or inspected",
              "plan": describe(config, grid), "machine": machine,
              "source": source_fingerprint(Path(__file__).resolve().parent.parent),
              "selection_seed": 20260908, "diagnostic_seeds": seeds,
              "sample_limit_seconds": 45, "total_limit_seconds": 600,
              "samples": [{"stratum": key, "stratum_cells": size, "cell_id": c["cell_id"],
                           "scenario": c["scenario"], "seed": seed}
                          for (key, size, c), seed in zip(selected, seeds)]}
    signal.signal(signal.SIGALRM, timeout)
    overall_start = time.perf_counter()
    with args.output.open("x") as output:
        def emit(record):
            output.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            output.flush()
        emit(header)
        for i, ((key, size, cell), seed) in enumerate(zip(selected, seeds), 1):
            remaining = 600 - (time.perf_counter() - overall_start)
            if remaining <= 0:
                emit({"kind": "end", "status": "budget_exhausted", "measured_samples": i - 1})
                return
            signal.setitimer(signal.ITIMER_REAL, min(45, remaining))
            sample_start = time.perf_counter()
            try:
                measured = measure(cell, seed)
            except Exception as exc:
                measured = {"status": "timeout" if isinstance(exc, TimeoutError) else "error",
                            "error": f"{type(exc).__name__}: {exc}",
                            "wall_seconds": time.perf_counter() - sample_start}
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            emit({"kind": "timing", "index": i, "stratum": key, "stratum_cells": size,
                  "cell_id": cell["cell_id"], "seed": seed, **measured})
            print(f"timing {i}/{len(selected)} {key}: "
                  f"{measured['status']} {measured['wall_seconds']:.3f}s", flush=True)
        emit({"kind": "end", "status": "complete", "measured_samples": len(selected),
              "wall_seconds": time.perf_counter() - overall_start})


if __name__ == "__main__":
    main()
