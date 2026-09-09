"""Execution handoff helpers. Run from the repository root; see RUNBOOK.md."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest

from bartender_sim.__main__ import run_study, source_fingerprint
from bartender_sim.model import Scenario, make_flow, simulate
from bartender_sim.plan import cells, describe, load_config, parameters_digest, require_approval
from bartender_sim.report import kaplan_meier, summarize, write_csv


ROOT = Path(__file__).resolve().parent
CONFIG = Path("configs/study-draft.json")
REFERENCE = Path("validation/determinism-m1.json")
CANDIDATE = Path("validation/determinism-m4.json")
CONTROLS = Path("validation/controls-m4.json")
REVALIDATION_APPROVAL = Path("REVALIDATION_APPROVAL.json")


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value, *, mode="x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode) as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("use a repository-relative path without parent traversal")
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError("path resolves outside the repository")
    return path


def run_name(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise ValueError("run id must contain only lowercase letters, digits, and hyphens")
    return value


def environment() -> dict:
    result = {"python": platform.python_version(), "implementation": platform.python_implementation(),
              "os": platform.system(), "os_version": platform.mac_ver()[0] or platform.release(),
              "architecture": platform.machine(), "logical_cpus": os.cpu_count(),
              "python_hash_seed": os.environ.get("PYTHONHASHSEED", "unset"),
              "workers": 1, "third_party_runtime_dependencies": []}
    if platform.system() == "Darwin":
        for name, key in (("cpu", "machdep.cpu.brand_string"), ("ram_bytes", "hw.memsize")):
            value = subprocess.check_output(["sysctl", "-n", key], text=True).strip()
            result[name] = int(value) if name == "ram_bytes" else value
    return result


def require_environment() -> None:
    if platform.python_implementation() != "CPython" or platform.python_version() != "3.12.4":
        raise ValueError("this handoff requires CPython 3.12.4")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise ValueError("start the command with PYTHONHASHSEED=0")


def protocol_hash() -> str:
    paths = [Path(p) for p in ("handoff.py", "RUNBOOK.md", ".python-version", "requirements.lock",
                              ".gitignore", "configs/determinism.json")]
    paths += sorted(Path("bartender_sim").glob("*.py"))
    paths += sorted(Path("tests").glob("test_*.py"))
    return digest({str(p): file_hash(p) for p in paths})


def control_record() -> dict:
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return {"status": "pass" if result.wasSuccessful() and not result.skipped and result.testsRun else "fail",
            "tests_run": result.testsRun, "failure_ids": [t.id() for t, _ in result.failures],
            "error_ids": [t.id() for t, _ in result.errors],
            "skipped_ids": [t.id() for t, _ in result.skipped],
            "environment": environment(), "protocol_sha256": protocol_hash()}


def determinism_record(label: str) -> dict:
    config = read(Path("configs/determinism.json"))
    if set(config["seeds"]) & set(load_config(CONFIG)["seeds"]):
        raise ValueError("diagnostic seeds must not overlap study seeds")
    records = []
    for case in config["cases"]:
        for seed in config["seeds"]:
            s = Scenario(**config["common"], **{k: v for k, v in case.items() if k != "name"}, seed=seed)
            flow = make_flow(s)
            result = simulate(s, flow)
            result["conflict_survival"] = kaplan_meier([
                (r["observed_conflict_age"], not r["right_censored"])
                for r in result["patches"] if r["first_failure"] is not None])
            records.append({"case": case["name"], "seed": seed,
                            "flow_sha256": digest([asdict(p) for p in flow]),
                            "result_sha256": digest(result)})
    payload = {"fixture_sha256": digest(config), "records": records,
               "model_files_sha256": source_fingerprint(ROOT)["files_sha256"]}
    return {"label": label, "environment": environment(), "payload": payload,
            "payload_sha256": digest(payload)}


def compare(reference: dict, candidate: dict) -> dict:
    fixture = read(Path("configs/determinism.json"))
    expected = {(case["name"], seed) for case in fixture["cases"] for seed in fixture["seeds"]}
    for record in (reference, candidate):
        if record["payload_sha256"] != digest(record["payload"]):
            raise ValueError("a determinism record has an invalid payload hash")
        if record["payload"]["model_files_sha256"] != source_fingerprint(ROOT)["files_sha256"]:
            raise ValueError("determinism record does not match the current model files")
        if record["payload"]["fixture_sha256"] != digest(fixture):
            raise ValueError("determinism record does not match the current fixture")
        items = record["payload"]["records"]
        if len(items) != len(expected) or {(r["case"], r["seed"]) for r in items} != expected:
            raise ValueError("determinism record is missing or duplicating a case/seed")
        if record["environment"]["python"] != "3.12.4" or record["environment"]["python_hash_seed"] != "0":
            raise ValueError("determinism environment does not match the pinned runtime")
    if reference["payload"] != candidate["payload"]:
        raise ValueError("cross-machine canonical result hashes differ; stop and open a question")
    return {"status": "pass", "records_compared": len(reference["payload"]["records"]),
            "payload_sha256": reference["payload_sha256"]}


def preflight(run_id: str) -> dict:
    require_environment()
    config = load_config(CONFIG)
    require_approval(config)
    approval = read(Path("RUN_APPROVAL.json"))
    if (approval.get("status") != "approved" or not approval.get("approved_by")
            or not approval.get("approved_at") or approval.get("run_id") != run_id
            or approval.get("parameters_sha256") != parameters_digest(config)
            or approval.get("protocol_sha256") != protocol_hash()):
        raise ValueError("runbook/protocol approval is missing or does not match this run")
    controls = read(CONTROLS)
    if (controls.get("status") != "pass" or not controls.get("tests_run")
            or controls.get("failure_ids") or controls.get("error_ids") or controls.get("skipped_ids")
            or controls.get("protocol_sha256") != protocol_hash()
            or controls.get("environment", {}).get("python") != "3.12.4"
            or controls.get("environment", {}).get("python_hash_seed") != "0"):
        raise ValueError("passing controls for this protocol are required")
    reference, candidate = read(REFERENCE), read(CANDIDATE)
    if reference.get("label") != "m1" or candidate.get("label") != "m4":
        raise ValueError("independent m1 and m4 records are required")
    match = compare(reference, candidate)
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    if branch != "run-m4":
        raise ValueError("formal execution belongs on branch run-m4")
    if subprocess.check_output(["git", "status", "--porcelain"], text=True).strip():
        raise ValueError("commit reviewed handoff records first; the tracked worktree must be clean")
    if Path("outputs", run_id).exists():
        raise ValueError("output already exists; do not overwrite or resume it")
    if shutil.disk_usage(ROOT).free < 20 * 1024 ** 3:
        raise ValueError("reserve at least 20 GiB free disk space before the full run")
    return {"status": "ready", "run_id": run_id, "plan": describe(config, cells(config)),
            "protocol_sha256": protocol_hash(), "determinism": match, "environment": environment(),
            "controls_sha256": file_hash(CONTROLS), "approval_sha256": file_hash(Path("RUN_APPROVAL.json"))}


def execute(run_id: str) -> int:
    receipt = preflight(run_id)
    output = Path("outputs", run_id)
    config = load_config(CONFIG)
    approval_snapshot = Path("RUN_APPROVAL.json").read_bytes()
    start = time.perf_counter()
    receipt.update(started_at=datetime.now(timezone.utc).isoformat(), status="running")
    try:
        code = run_study(config, cells(config), output)
        receipt.update(status="complete" if code == 0 else "complete_with_errors", exit_code=code)
        return code
    except BaseException as exc:
        receipt.update(status="interrupted", exception_type=type(exc).__name__)
        raise
    finally:
        receipt.update(wall_seconds=time.perf_counter() - start,
                       finished_at=datetime.now(timezone.utc).isoformat())
        if output.exists():
            write(output / "execution.json", receipt)
            with (output / "RUN_APPROVAL.json").open("xb") as stream:
                stream.write(approval_snapshot)


def csv_contents(path: Path) -> tuple:
    """Preserve every field and duplicate row, but ignore CSV row order."""
    with path.open(newline="") as stream:
        rows = csv.reader(stream)
        return tuple(next(rows, [])), Counter(tuple(row) for row in rows)


def verify_output(output: Path, *, execution_protocol_sha256: str | None = None) -> dict:
    """Check full membership, parse every raw file, and regenerate aggregate CSVs."""
    config = read(output / "config.json")
    grid = cells(config)
    manifest = read(output / "manifest.json")
    expected = {(c["cell_id"], seed): c for c in grid for seed in config["seeds"]}
    records = [json.loads(line) for line in (output / "summaries.jsonl").read_text().splitlines()]
    counts = Counter((r["cell_id"], r["seed"]) for r in records)
    issues = []
    try:
        require_approval(config)
    except ValueError:
        issues.append("saved parameters are not approved")
    if set(counts) != set(expected) or any(v != 1 for v in counts.values()):
        issues.append("missing, duplicate, or unexpected cell/seed records")
    if manifest["status"] != "complete" or manifest["failed_runs"] != 0:
        issues.append("run incomplete or contains failures")
    if manifest["completed_runs"] != len(expected):
        issues.append("completed run count differs from the plan")
    saved_grid = read(output / "cells.json")
    if (Counter(canonical(c) for c in saved_grid) != Counter(canonical(c) for c in grid)
            or manifest["parameters_sha256"] != parameters_digest(config)):
        issues.append("saved grid or parameter digest mismatch")
    if config != load_config(CONFIG):
        issues.append("saved configuration differs from the current approved configuration")
    if manifest["source"]["files_sha256"] != source_fingerprint(ROOT)["files_sha256"]:
        issues.append("recorded model differs from current model")
    if manifest["source"].get("git_dirty") is not False:
        issues.append("execution source was not recorded as clean")
    receipt = read(output / "execution.json")
    approval = read(output / "RUN_APPROVAL.json")
    if (receipt.get("status") != "complete" or receipt.get("exit_code") != 0
            or receipt.get("protocol_sha256") != (execution_protocol_sha256 or protocol_hash())
            or receipt.get("approval_sha256") != file_hash(output / "RUN_APPROVAL.json")
            or approval.get("status") != "approved" or not approval.get("approved_by")
            or not approval.get("approved_at") or approval.get("run_id") != output.name
            or approval.get("parameters_sha256") != parameters_digest(config)
            or approval.get("protocol_sha256") != receipt.get("protocol_sha256")):
        issues.append("execution receipt or protocol approval mismatch")
    env = receipt.get("environment", {})
    if (env.get("python") != "3.12.4" or env.get("implementation") != "CPython"
            or env.get("python_hash_seed") != "0"):
        issues.append("execution runtime does not match the pinned environment")
    seconds = receipt.get("wall_seconds")
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
        issues.append("execution wall time is missing or invalid")
    for key in ("started_at", "finished_at"):
        if datetime.fromisoformat(receipt[key]).utcoffset() is None:
            issues.append("execution timestamps must include their timezone")
    expected_files, flows = set(), set()
    for record in records:
        key = record["cell_id"], record["seed"]
        if key not in expected or record["status"] != "ok":
            issues.append("failed or unexpected run record")
            continue
        scenario = {**expected[key]["scenario"], "seed": key[1]}
        name = f"runs/{key[0]}-{key[1]}.json.gz"
        expected_files.add(name)
        with gzip.open(output / name, "rt") as stream:
            raw = json.load(stream)
        if (record["scenario"] != scenario or raw["scenario"] != scenario
                or record["artifact"] != name or raw["metrics"] != record["metrics"]
                or raw["flow_sha256"] != record["flow_sha256"]
                or len(raw["patches"]) != raw["metrics"]["generated_edits"]):
            issues.append("raw result and summary disagree")
        flows.add(record["flow_sha256"])
    actual = {p.relative_to(output).as_posix() for p in (output / "runs").iterdir()}
    if actual != expected_files:
        issues.append("raw run file membership differs from completed records")
    if {p.name for p in (output / "flows").iterdir()} != {f"{h}.json.gz" for h in flows}:
        issues.append("input flow membership differs from completed records")
    for flow_hash in sorted(flows):
        with gzip.open(output / "flows" / f"{flow_hash}.json.gz", "rt") as stream:
            if digest(json.load(stream)) != flow_hash:
                issues.append("input flow content hash mismatch")
    # CSV regeneration is a consistency check, not a new outcome analysis.
    aggregates, contrasts = summarize(records)
    with tempfile.TemporaryDirectory(prefix="bartender-verify-") as temporary:
        for name, rows in (("summary.csv", aggregates), ("paired-differences.csv", contrasts)):
            path = Path(temporary) / name
            write_csv(path, rows)
            if csv_contents(path) != csv_contents(output / name):
                issues.append(f"{name} does not match the per-seed records")
    return {"status": "pass" if not issues else "hold", "planned_runs": len(expected),
            "records_seen": len(records), "raw_run_files": len(actual), "unique_flows": len(flows),
            "issues": sorted(set(issues))}


class ArchiveParts:
    """Write a tar stream in bounded chunks, with no local identity metadata."""
    def __init__(self, directory: Path, part_bytes: int = 1024 ** 3):
        directory.mkdir(parents=True, exist_ok=False)
        self.directory, self.limit = directory, part_bytes
        self.parts, self.stream, self.size = [], None, 0
        self.whole_hash = hashlib.sha256()

    def write(self, data: bytes) -> int:
        original = len(data)
        self.whole_hash.update(data)
        while data:
            if self.stream is None:
                self.path = self.directory / f"raw.tar.part{len(self.parts):03d}"
                self.stream = self.path.open("xb")
                self.part_hash, self.size = hashlib.sha256(), 0
            chunk, data = data[:self.limit - self.size], data[self.limit - self.size:]
            self.stream.write(chunk)
            self.part_hash.update(chunk)
            self.size += len(chunk)
            if self.size == self.limit:
                self.close_part()
        return original

    def close_part(self):
        if self.stream is not None:
            self.stream.close()
            self.parts.append({"path": self.path.as_posix(), "bytes": self.size,
                               "sha256": self.part_hash.hexdigest()})
            self.stream = None


def archive(output: Path, directory: Path, *, part_bytes=1024 ** 3) -> dict:
    parts = ArchiveParts(directory, part_bytes)
    files = []
    try:
        with tarfile.open(fileobj=parts, mode="w|", format=tarfile.PAX_FORMAT) as packed:
            for path in sorted(output.rglob("*")):
                if path.is_symlink():
                    raise ValueError("raw output must not contain symbolic links")
                if not path.is_file():
                    continue
                name = f"{output.name}/{path.relative_to(output).as_posix()}"
                member = tarfile.TarInfo(name)
                member.size, member.mode, member.mtime = path.stat().st_size, 0o644, 0
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                files.append({"path": name, "bytes": member.size, "sha256": file_hash(path)})
                with path.open("rb") as stream:
                    packed.addfile(member, stream)
    finally:
        parts.close_part()
    if any(file_hash(Path(part["path"])) != part["sha256"] for part in parts.parts):
        raise ValueError("written archive part failed its hash check")
    return {"format": "tar split into ordered parts; concatenate before extracting",
            "archive_sha256": parts.whole_hash.hexdigest(), "parts": parts.parts, "files": files,
            "raw_bytes": sum(f["bytes"] for f in files),
            "archive_bytes": sum(p["bytes"] for p in parts.parts)}


def retained_files_match(output: Path, inventory: dict) -> bool:
    """Bind revalidation to the exact raw bytes indexed by the first collection."""
    expected = inventory["files"]
    actual = []
    for path in sorted(output.rglob("*")):
        if path.is_symlink():
            return False
        if path.is_file():
            actual.append({"path": f"{output.name}/{path.relative_to(output).as_posix()}",
                           "bytes": path.stat().st_size, "sha256": file_hash(path)})
    return Counter(canonical(f) for f in actual) == Counter(canonical(f) for f in expected)


def recollect(run_id: str, verification_id: str) -> int:
    """Recheck retained outputs under a separate approval; never regenerate data."""
    require_environment()
    output, original = Path("outputs", run_id), Path("deliverables", run_id)
    destination = original / "rechecks" / verification_id
    if destination.exists():
        raise ValueError("verification record already exists; preserve it and use a newly approved id")
    approval = read(REVALIDATION_APPROVAL)
    receipt = read(output / "execution.json")
    config = load_config(CONFIG)
    require_approval(config)
    if (approval.get("status") != "approved" or approval.get("scope") != "collect-only"
            or not approval.get("approved_by") or not approval.get("approved_at")
            or approval.get("run_id") != run_id or approval.get("verification_id") != verification_id
            or approval.get("parameters_sha256") != parameters_digest(config)
            or approval.get("protocol_sha256") != protocol_hash()
            or approval.get("execution_protocol_sha256") != receipt.get("protocol_sha256")
            or approval.get("execution_receipt_sha256") != file_hash(output / "execution.json")
            or approval.get("execution_approval_sha256") != file_hash(output / "RUN_APPROVAL.json")
            or approval.get("artifact_index_sha256") != file_hash(original / "artifact-index.json")
            or approval.get("original_verification_sha256") != file_hash(original / "verification.json")):
        raise ValueError("separate collect-only approval is missing or does not match the retained run")
    controls = read(relative(approval["controls_record"]))
    if (controls.get("status") != "pass" or not controls.get("tests_run")
            or controls.get("failure_ids") or controls.get("error_ids") or controls.get("skipped_ids")
            or controls.get("protocol_sha256") != protocol_hash()
            or controls.get("environment", {}).get("python") != "3.12.4"
            or controls.get("environment", {}).get("python_hash_seed") != "0"):
        raise ValueError("passing controls for the revised verification protocol are required")
    start = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    inventory = read(original / "artifact-index.json")
    try:
        validation = verify_output(output, execution_protocol_sha256=approval["execution_protocol_sha256"])
        unchanged = retained_files_match(output, inventory)
        if not unchanged:
            validation["issues"].append("raw files differ from the original archive inventory")
            validation["status"] = "hold"
    except Exception as exc:
        unchanged = False
        validation = {"status": "hold", "issues": [f"validation could not complete: {type(exc).__name__}"]}
    validation.update(run_id=run_id, verification_id=verification_id,
                      scope="collect-only", raw_files_match_original_inventory=unchanged,
                      execution_protocol_sha256=approval["execution_protocol_sha256"],
                      verification_protocol_sha256=protocol_hash(),
                      revalidation_approval_sha256=file_hash(REVALIDATION_APPROVAL),
                      artifact_index_sha256=approval["artifact_index_sha256"],
                      original_verification_sha256=approval["original_verification_sha256"],
                      controls_sha256=file_hash(relative(approval["controls_record"])),
                      environment=environment(), started_at=started_at,
                      finished_at=datetime.now(timezone.utc).isoformat(),
                      verification_wall_seconds=time.perf_counter() - start)
    destination.mkdir(parents=True, exist_ok=False)
    write(destination / "verification.json", validation)
    shutil.copyfile(REVALIDATION_APPROVAL, destination / "REVALIDATION_APPROVAL.json")
    (destination / "REVALIDATION_REPORT.md").write_text(f"""# Revalidation: {run_id} / {verification_id}

Status: {validation['status'].upper()}; verification only, with no scientific interpretation.

- Original execution: `deliverables/{run_id}/execution.json`.
- Original verification and report remain unchanged in `deliverables/{run_id}/`.
- Verification details, environment, timestamps and wall time: `verification.json`.
- Raw files match the original archive inventory: {unchanged}.
- Original archive SHA-256: `{inventory['archive_sha256']}`.
- Execution protocol SHA-256: `{approval['execution_protocol_sha256']}`.
- Verification protocol SHA-256: `{validation['verification_protocol_sha256']}`.
- No simulation, CSV replacement, raw-data change, or new archive was produced.
""")
    return 0 if validation["status"] == "pass" else 1


def collect(run_id: str, verification_id: str | None = None) -> int:
    if verification_id is not None:
        return recollect(run_id, verification_id)
    output, delivery = Path("outputs", run_id), Path("deliverables", run_id)
    if not output.is_dir():
        raise ValueError("no raw output directory exists for this run")
    delivery.mkdir(parents=True, exist_ok=False)
    try:
        validation = verify_output(output)
    except Exception as exc:
        validation = {"status": "hold", "issues": [f"validation could not complete: {type(exc).__name__}"]}
    write(delivery / "verification.json", validation)
    inventory = archive(output, Path("archives", run_id))
    write(delivery / "artifact-index.json", inventory)
    for name in ("config.json", "cells.json", "manifest.json", "execution.json", "RUN_APPROVAL.json",
                 "summary.csv", "paired-differences.csv"):
        if (output / name).is_file():
            shutil.copyfile(output / name, delivery / name)
    manifest = read(output / "manifest.json") if (output / "manifest.json").exists() else {}
    receipt = read(output / "execution.json") if (output / "execution.json").exists() else {}
    report = f"""# Run report: {run_id}

Status: {validation['status'].upper()}; no scientific interpretation in this report.

- Plan: {manifest.get('planned_runs', 'UNKNOWN')} runs; {manifest.get('cells', 'UNKNOWN')} cells.
- Parameters SHA-256: `{manifest.get('parameters_sha256', 'UNKNOWN')}`.
- Model/source Git commit: `{manifest.get('source', {}).get('git_head', 'UNKNOWN')}`.
- Started (UTC): {receipt.get('started_at', 'UNKNOWN')}.
- Finished (UTC): {receipt.get('finished_at', 'UNKNOWN')}.
- Measured execution wall seconds: {receipt.get('wall_seconds', 'UNKNOWN')}.
- Completed: {manifest.get('completed_runs', 'UNKNOWN')}; failed: {manifest.get('failed_runs', 'UNKNOWN')}.
- Verification: see `deliverables/{run_id}/verification.json`.
- Environment and checks: see `deliverables/{run_id}/execution.json` and `validation/`.
- Raw output: `outputs/{run_id}/`, retained on the execution machine.
- Archive: `archives/{run_id}/`; {inventory['archive_bytes']} bytes in {len(inventory['parts'])} parts.
- Concatenated archive SHA-256: `{inventory['archive_sha256']}`.
- Deviations or interruptions: RUNNER MUST COMPLETE THIS LINE before committing the report.
- Verification/archive preparation time is excluded from execution wall seconds.

Raw data were not added to Git. All errors and incomplete records remain in the archive.
"""
    (delivery / "RUN_REPORT.md").write_text(report)
    if sum(p.stat().st_size for p in delivery.rglob("*") if p.is_file()) > 100_000_000:
        raise ValueError("delivery exceeds the Git budget; preserve files and open a question")
    return 0 if validation["status"] == "pass" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fingerprints")
    for command in ("environment", "controls", "determinism", "compare"):
        p = sub.add_parser(command)
        p.add_argument("--output", required=True)
        if command == "determinism":
            p.add_argument("--label", choices=("m1", "m4"), required=True)
        if command == "compare":
            p.add_argument("--reference", default=str(REFERENCE))
            p.add_argument("--candidate", default=str(CANDIDATE))
    for command in ("preflight", "run"):
        sub.add_parser(command).add_argument("--run-id", default="study-01")
    p = sub.add_parser("collect")
    p.add_argument("--run-id", default="study-01")
    p.add_argument("--verification-id", help="recheck retained outputs under separate collect-only approval")
    args = parser.parse_args()
    if Path.cwd().resolve() != ROOT:
        parser.exit(2, "error: run from the repository root\n")
    try:
        if args.command == "fingerprints":
            value = {"parameters_sha256": parameters_digest(load_config(CONFIG)),
                     "protocol_sha256": protocol_hash()}
        elif args.command == "environment":
            require_environment()
            value = environment()
        elif args.command == "controls":
            require_environment()
            value = control_record()
        elif args.command == "determinism":
            require_environment()
            value = determinism_record(args.label)
        elif args.command == "compare":
            value = compare(read(relative(args.reference)), read(relative(args.candidate)))
        elif args.command == "preflight":
            value = preflight(run_name(args.run_id))
        elif args.command == "run":
            return execute(run_name(args.run_id))
        else:
            return collect(run_name(args.run_id),
                           run_name(args.verification_id) if args.verification_id else None)
        if hasattr(args, "output"):
            write(relative(args.output), value)
        print(json.dumps(value if args.command in {"fingerprints", "preflight", "compare"}
                         else {"status": value.get("status", "recorded"), "output": args.output}, sort_keys=True))
        return 1 if value.get("status") == "fail" else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
