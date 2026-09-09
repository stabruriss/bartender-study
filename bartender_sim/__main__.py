"""Run `python3 -m bartender_sim plan --config configs/study-draft.json`."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from .model import Scenario, make_flow, simulate
from .plan import cells, describe, load_config, require_approval
from .report import kaplan_meier, summarize, write_csv


def source_fingerprint(root: Path) -> dict:
    files = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((root / "bartender_sim").glob("*.py"))}
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root,
                          capture_output=True, text=True)
    status = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root,
                            capture_output=True, text=True)
    return {"files_sha256": files, "git_head": head.stdout.strip() or None,
            "git_dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
            "python": platform.python_version(), "system": platform.system(),
            "machine": platform.machine()}


def _json(path: Path, data: dict, mode: str = "x") -> None:
    with path.open(mode) as handle:
        json.dump(data, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def run_study(config: dict, grid: list[dict], output: Path) -> int:
    require_approval(config)
    # A fresh output directory prevents quietly replacing an unfavorable run.
    output.mkdir(parents=True, exist_ok=False)
    (output / "runs").mkdir()
    (output / "flows").mkdir()
    manifest = {**describe(config, grid), "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_runs": 0, "failed_runs": 0,
                "interval_method": "mean +/- 1.96 * across-seed standard error (normal approximation)",
                "source": source_fingerprint(Path(__file__).resolve().parent.parent)}
    _json(output / "config.json", config)
    _json(output / "cells.json", grid)
    _json(output / "manifest.json", manifest)
    summaries = []
    flow_hashes = set()
    try:
        with (output / "summaries.jsonl").open("x") as summary_file:
            for cell in grid:
                for seed in config["seeds"]:
                    s = Scenario(**cell["scenario"], seed=seed)
                    record = {"suite": cell["suite"], "cell_id": cell["cell_id"],
                              "seed": seed, "scenario": asdict(s), "status": "ok"}
                    try:
                        flow = make_flow(s)
                        result = simulate(s, flow)
                        result["conflict_survival"] = kaplan_meier([
                            (r["observed_conflict_age"], not r["right_censored"])
                            for r in result["patches"] if r["first_failure"] is not None])
                        flow_hash = result["flow_sha256"]
                        if flow_hash not in flow_hashes:
                            with (output / "flows" / f"{flow_hash}.json.gz").open("xb") as handle:
                                with gzip.GzipFile(fileobj=handle, mode="wb", mtime=0, filename="") as zipped:
                                    zipped.write(json.dumps([asdict(p) for p in flow], sort_keys=True,
                                                            allow_nan=False).encode())
                            flow_hashes.add(flow_hash)
                        run_name = f"{cell['cell_id']}-{seed}.json.gz"
                        with (output / "runs" / run_name).open("xb") as handle:
                            with gzip.GzipFile(fileobj=handle, mode="wb", mtime=0, filename="") as zipped:
                                zipped.write(json.dumps(result, sort_keys=True, allow_nan=False).encode())
                        record.update(metrics=result["metrics"], flow_sha256=flow_hash,
                                      artifact=f"runs/{run_name}")
                        manifest["completed_runs"] += 1
                    except Exception as exc:
                        record.update(status="error", error=f"{type(exc).__name__}: {exc}", metrics={})
                        manifest["failed_runs"] += 1
                    summaries.append(record)
                    summary_file.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
                    summary_file.flush()
                _json(output / "manifest.json", manifest, mode="w")
                print(f"{cell['suite']} {cell['cell_id']}: "
                      f"{manifest['completed_runs']} complete, {manifest['failed_runs']} errors", flush=True)
        aggregates, contrasts = summarize(summaries)
        write_csv(output / "summary.csv", aggregates)
        write_csv(output / "paired-differences.csv", contrasts)
        manifest["status"] = "complete" if manifest["failed_runs"] == 0 else "complete_with_errors"
    except BaseException:
        manifest["status"] = "interrupted"
        raise
    finally:
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        _json(output / "manifest.json", manifest, mode="w")
    return 1 if manifest["failed_runs"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        p = sub.add_parser(name)
        p.add_argument("--config", type=Path, required=True)
        if name == "plan":
            p.add_argument("--cells", action="store_true", help="include all proposed cells; no simulation")
        else:
            p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        grid = cells(config)
        if args.command == "plan":
            result = describe(config, grid)
            if args.cells:
                result["grid"] = grid
            print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
            return 0
        return run_study(config, grid, args.output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
