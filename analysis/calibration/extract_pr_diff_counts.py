#!/usr/bin/env python3
"""Derive final-diff hunk and file counts for the Xu et al. PR-pair sample.

The extractor is read-only. It queries public GitHub pull-request metadata,
fetches public PR refs into a temporary repository, writes one metadata row,
and deletes the repository. Diff bodies never leave the temporary directory or
process memory. The retrieved PR heads are current, not frozen replay OIDs.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


REQUIRED_INPUT_FIELDS = (
    "stratum",
    "repo",
    "prA",
    "prB",
    "agentA",
    "agentB",
    "label",
    "n_files",
    "files",
    "types",
)

DERIVED_FIELDS = (
    "retrieved_at_utc",
    "oid_scope",
    "git_version",
    "fetch_parameters",
    "diff_parameters",
    "api_headA_oid",
    "api_headB_oid",
    "headA_oid",
    "headB_oid",
    "baseA_oid",
    "baseB_oid",
    "merge_base_oid",
    "filesA",
    "hunksA",
    "filesB",
    "hunksB",
    "status",
)

OUTPUT_SOURCE_FIELDS = (
    "stratum",
    "repo",
    "prA",
    "prB",
    "label",
    "conflict_has_content",
    "conflict_is_content_only",
)

ENV = {
    **os.environ,
    "GH_FORCE_TTY": "0",
    "GIT_TERMINAL_PROMPT": "0",
    "NO_COLOR": "1",
}

FETCH_PARAMETERS = (
    "refs/pull/N/head; --no-tags; depth 80; depth 600 retry if no merge base"
)
DIFF_PARAMETERS = (
    "git -c diff.renames=true -c diff.algorithm=myers diff --no-ext-diff "
    "--no-textconv --unified=0; default whitespace; binary paths count as "
    "files and contribute zero hunks"
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_text(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        env=ENV,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )


def run_bytes(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 180,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        cwd=cwd,
        env=ENV,
        text=False,
        capture_output=True,
        timeout=timeout,
    )


def write_log(path: Path, event: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def rate_state() -> tuple[int, int]:
    process = run_text(
        [
            "gh",
            "api",
            "rate_limit",
            "--jq",
            '"\\(.resources.core.remaining) \\(.resources.core.reset)"',
        ]
    )
    if process.returncode != 0:
        raise RuntimeError(f"cannot read GitHub rate limit: {process.stderr.strip()}")
    remaining, reset = process.stdout.strip().split()
    return int(remaining), int(reset)


def wait_for_rate_budget(floor: int, log_path: Path) -> int:
    while True:
        remaining, reset = rate_state()
        # Two PR metadata calls follow. Do not cross the declared floor.
        if remaining >= floor + 2:
            return remaining
        now = int(time.time())
        delay = min(60, max(5, reset - now + 5))
        write_log(
            log_path,
            {
                "event": "rate_pause",
                "at": utc_now(),
                "remaining": remaining,
                "floor": floor,
                "reset_epoch": reset,
                "sleep_seconds": delay,
            },
        )
        time.sleep(delay)


def github_json(endpoint: str, retries: int = 3) -> tuple[dict[str, object] | None, str]:
    failure = "API_FAILED"
    for attempt in range(1, retries + 1):
        process = run_text(["gh", "api", endpoint])
        if process.returncode == 0:
            return json.loads(process.stdout), ""
        if "HTTP 404" in process.stderr:
            failure = "API_NOT_FOUND"
            break
        if attempt < retries:
            time.sleep(2 * attempt)
    return None, failure


def git_diff_counts(repo: Path, base: str, head: str) -> tuple[int, int]:
    common = [
        "git",
        "-c",
        "diff.renames=true",
        "-c",
        "diff.algorithm=myers",
        "diff",
        "--no-ext-diff",
        "--no-textconv",
    ]
    names = run_bytes(common + ["--name-only", "-z", base, head], cwd=repo)
    if names.returncode != 0:
        raise RuntimeError("git diff --name-only failed")
    files = sum(1 for value in names.stdout.split(b"\0") if value)

    patch = run_bytes(common + ["--unified=0", base, head], cwd=repo)
    if patch.returncode != 0:
        raise RuntimeError("git diff --unified=0 failed")
    hunks = sum(1 for line in patch.stdout.splitlines() if line.startswith(b"@@ "))
    return files, hunks


def blank_output(row: dict[str, str], git_version: str) -> dict[str, str]:
    conflict_types = {value for value in row["types"].split("|") if value}
    has_content = row["label"] == "CONFLICT" and "content" in conflict_types
    content_only = has_content and conflict_types == {"content"}
    return {
        "stratum": row["stratum"],
        "repo": row["repo"],
        "prA": row["prA"],
        "prB": row["prB"],
        "label": row["label"],
        "conflict_has_content": str(has_content).lower(),
        "conflict_is_content_only": str(content_only).lower(),
        "retrieved_at_utc": utc_now(),
        "oid_scope": "current-pr-heads-at-extraction; not frozen replay OIDs",
        "git_version": git_version,
        "fetch_parameters": FETCH_PARAMETERS,
        "diff_parameters": DIFF_PARAMETERS,
        "api_headA_oid": "",
        "api_headB_oid": "",
        "headA_oid": "",
        "headB_oid": "",
        "baseA_oid": "",
        "baseB_oid": "",
        "merge_base_oid": "",
        "filesA": "",
        "hunksA": "",
        "filesB": "",
        "hunksB": "",
        "status": "",
    }


def extract_pair(
    row: dict[str, str],
    *,
    rate_floor: int,
    log_path: Path,
    git_version: str,
) -> dict[str, str]:
    result = blank_output(row, git_version)
    if row["label"].startswith("UNAVAIL"):
        result["status"] = row["label"]
        return result

    wait_for_rate_budget(rate_floor, log_path)
    repo_name = row["repo"]
    pr_a = row["prA"]
    pr_b = row["prB"]
    data_a, error_a = github_json(f"repos/{repo_name}/pulls/{pr_a}")
    if data_a is None:
        result["status"] = f"{error_a}_A"
        return result
    data_b, error_b = github_json(f"repos/{repo_name}/pulls/{pr_b}")
    if data_b is None:
        result["status"] = f"{error_b}_B"
        return result

    result["api_headA_oid"] = str(data_a.get("head", {}).get("sha", ""))
    result["api_headB_oid"] = str(data_b.get("head", {}).get("sha", ""))
    result["baseA_oid"] = str(data_a.get("base", {}).get("sha", ""))
    result["baseB_oid"] = str(data_b.get("base", {}).get("sha", ""))
    if not result["api_headA_oid"] or not result["api_headB_oid"]:
        result["status"] = "API_MISSING_HEAD_OID"
        return result

    temp = Path(tempfile.mkdtemp(prefix="jss-range-positioning-"))
    try:
        if run_text(["git", "init", "-q"], cwd=temp).returncode != 0:
            result["status"] = "GIT_INIT_FAILED"
            return result
        if run_text(
            ["git", "remote", "add", "origin", f"https://github.com/{repo_name}.git"],
            cwd=temp,
        ).returncode != 0:
            result["status"] = "GIT_REMOTE_FAILED"
            return result

        fetch = run_text(
            [
                "git",
                "-c",
                "protocol.version=2",
                "fetch",
                "-q",
                "--no-tags",
                "--depth",
                "80",
                "origin",
                f"refs/pull/{pr_a}/head:prA",
                f"refs/pull/{pr_b}/head:prB",
            ],
            cwd=temp,
        )
        if fetch.returncode != 0:
            result["status"] = "FETCH_FAILED"
            return result

        fetched_a = run_text(["git", "rev-parse", "prA"], cwd=temp)
        fetched_b = run_text(["git", "rev-parse", "prB"], cwd=temp)
        if fetched_a.returncode != 0 or fetched_b.returncode != 0:
            result["status"] = "FETCHED_HEAD_MISSING"
            return result
        result["headA_oid"] = fetched_a.stdout.strip()
        result["headB_oid"] = fetched_b.stdout.strip()

        merge_base = run_text(["git", "merge-base", "prA", "prB"], cwd=temp)
        if merge_base.returncode != 0 or not merge_base.stdout.strip():
            fetch = run_text(
                [
                    "git",
                    "-c",
                    "protocol.version=2",
                    "fetch",
                    "-q",
                    "--no-tags",
                    "--depth",
                    "600",
                    "origin",
                    f"refs/pull/{pr_a}/head:prA",
                    f"refs/pull/{pr_b}/head:prB",
                ],
                cwd=temp,
            )
            if fetch.returncode != 0:
                result["status"] = "FETCH_DEEP_FAILED"
                return result
            fetched_a = run_text(["git", "rev-parse", "prA"], cwd=temp)
            fetched_b = run_text(["git", "rev-parse", "prB"], cwd=temp)
            if fetched_a.returncode != 0 or fetched_b.returncode != 0:
                result["status"] = "FETCHED_HEAD_MISSING"
                return result
            result["headA_oid"] = fetched_a.stdout.strip()
            result["headB_oid"] = fetched_b.stdout.strip()
            merge_base = run_text(["git", "merge-base", "prA", "prB"], cwd=temp)
        if merge_base.returncode != 0 or not merge_base.stdout.strip():
            result["status"] = "NO_MERGE_BASE"
            return result

        result["merge_base_oid"] = merge_base.stdout.strip()
        files_a, hunks_a = git_diff_counts(temp, result["merge_base_oid"], "prA")
        files_b, hunks_b = git_diff_counts(temp, result["merge_base_oid"], "prB")
        heads_changed = (
            result["headA_oid"] != result["api_headA_oid"]
            or result["headB_oid"] != result["api_headB_oid"]
        )
        result.update(
            filesA=str(files_a),
            hunksA=str(hunks_a),
            filesB=str(files_b),
            hunksB=str(hunks_b),
            status="OK_HEAD_CHANGED" if heads_changed else "OK",
        )
        return result
    except subprocess.TimeoutExpired:
        result["status"] = "TIMEOUT"
        return result
    except RuntimeError as error:
        result["status"] = str(error).upper().replace(" ", "_")
        return result
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def read_input(path: Path, expected_rows: int) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit("input CSV has no header")
        missing = [field for field in REQUIRED_INPUT_FIELDS if field not in reader.fieldnames]
        if missing:
            raise SystemExit(f"input CSV missing fields: {', '.join(missing)}")
        rows = list(reader)
    if expected_rows and len(rows) != expected_rows:
        raise SystemExit(f"expected {expected_rows} rows, found {len(rows)}")
    keys = [(row["stratum"], row["repo"], row["prA"], row["prB"]) for row in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("input CSV has duplicate pair keys")
    return rows


def completed_keys(path: Path, expected_fields: list[str]) -> set[tuple[str, ...]]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_fields:
            raise SystemExit("existing output header does not match this extractor")
        return {
            (row["stratum"], row["repo"], row["prA"], row["prB"])
            for row in reader
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--expected-rows", type=int, default=747)
    parser.add_argument("--rate-floor", type=int, default=500)
    parser.add_argument("--max-new", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    rows = read_input(args.pairs, args.expected_rows)
    output_fields = list(OUTPUT_SOURCE_FIELDS) + list(DERIVED_FIELDS)
    if args.output.exists() and not args.resume:
        raise SystemExit("output exists; pass --resume or choose a new path")
    done = completed_keys(args.output, output_fields) if args.resume else set()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists():
        with args.output.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(
                handle, fieldnames=output_fields, lineterminator="\n"
            ).writeheader()

    git_version_process = run_text(["git", "--version"])
    if git_version_process.returncode != 0:
        raise SystemExit("git --version failed")
    git_version = git_version_process.stdout.strip()
    write_log(
        args.log,
        {
            "event": "start",
            "at": utc_now(),
            "input": args.pairs.name,
            "input_sha256": sha256(args.pairs),
            "input_rows": len(rows),
            "already_complete": len(done),
            "git_version": git_version,
            "rate_floor": args.rate_floor,
        },
    )

    written = 0
    for index, row in enumerate(rows, start=1):
        key = (row["stratum"], row["repo"], row["prA"], row["prB"])
        if key in done:
            continue
        result = extract_pair(
            row,
            rate_floor=args.rate_floor,
            log_path=args.log,
            git_version=git_version,
        )
        with args.output.open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(
                handle, fieldnames=output_fields, lineterminator="\n"
            ).writerow(result)
            handle.flush()
            os.fsync(handle.fileno())
        write_log(
            args.log,
            {
                "event": "pair",
                "at": utc_now(),
                "input_row": index,
                "stratum": row["stratum"],
                "repo": row["repo"],
                "prA": row["prA"],
                "prB": row["prB"],
                "status": result["status"],
            },
        )
        written += 1
        if written % 10 == 0:
            print(f"new_rows={written} input_row={index} status={result['status']}", flush=True)
        if args.max_new and written >= args.max_new:
            break

    write_log(
        args.log,
        {"event": "stop", "at": utc_now(), "new_rows": written},
    )


if __name__ == "__main__":
    main()
