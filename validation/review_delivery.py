"""Read-only maintainer review of the two retained deliveries; never simulate.

Run from the repository root with the pinned study Python. The compressed
per-seed summary is used only to verify the original CSVs, not for analysis.
"""
from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bartender_sim.plan import cells, parameters_digest  # noqa: E402
from bartender_sim.report import summarize  # noqa: E402
from handoff import protocol_hash  # noqa: E402

checks: list[dict] = []


def check(name, condition):
    checks.append({"check": name, "status": "pass" if condition else "hold"})


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def csv_content(text):
    rows = list(csv.reader(io.StringIO(text)))
    return rows[0], Counter(map(tuple, rows[1:]))


def generated_csv_content(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return csv_content(buffer.getvalue())


def dt(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def study():
    base = Path("deliverables/study-01")
    recheck = base / "rechecks/verify-02"
    approval = read("REVALIDATION_APPROVAL.json")
    verification = read(recheck / "verification.json")
    controls = read(approval["controls_record"])
    check("approved collect-only scope and ids", approval["status"] == "approved"
          and approval["approved_by"] == "study owner" and approval["scope"] == "collect-only"
          and approval["run_id"] == "study-01" and approval["verification_id"] == "verify-02")
    check("exact delivered approval snapshot", sha("REVALIDATION_APPROVAL.json") == sha(recheck / "REVALIDATION_APPROVAL.json"))
    bindings = {
        "artifact_index_sha256": base / "artifact-index.json",
        "execution_approval_sha256": base / "RUN_APPROVAL.json",
        "execution_receipt_sha256": base / "execution.json",
        "original_verification_sha256": base / "verification.json",
    }
    for key, path in bindings.items():
        check("approval binding: " + key, approval[key] == sha(path))
    check("current approved verification protocol", approval["protocol_sha256"] == protocol_hash())
    for a, v in [("protocol_sha256", "verification_protocol_sha256"),
                 ("execution_protocol_sha256", "execution_protocol_sha256"),
                 ("artifact_index_sha256", "artifact_index_sha256"),
                 ("original_verification_sha256", "original_verification_sha256")]:
        check("verification binding: " + v, approval[a] == verification[v])
    check("verification binds approved receipt", verification["revalidation_approval_sha256"] == sha("REVALIDATION_APPROVAL.json"))
    check("verification binds controls", verification["controls_sha256"] == sha(approval["controls_record"]))
    check("34 revised controls pass without skips", controls["status"] == "pass"
          and controls["tests_run"] == 34 and not any(controls[k] for k in ["failure_ids", "error_ids", "skipped_ids"])
          and controls["protocol_sha256"] == approval["protocol_sha256"])
    check("retained-output verification passes", verification["status"] == "pass"
          and not verification["issues"] and verification["raw_files_match_original_inventory"] is True
          and verification["planned_runs"] == verification["records_seen"] == verification["raw_run_files"] == 29700
          and verification["unique_flows"] == 300)
    execution = read(base / "execution.json")
    check("complete original run, before approved revalidation", execution["status"] == "complete"
          and execution["exit_code"] == 0
          and dt(execution["finished_at"]) < dt(approval["approved_at"]) < dt(verification["started_at"]))
    check("original HOLD remains historical", read(base / "verification.json")["status"] == "hold")
    index = {r["path"]: r for r in read(base / "artifact-index.json")["files"]}
    for name in ["RUN_APPROVAL.json", "cells.json", "config.json", "execution.json", "manifest.json", "summary.csv", "paired-differences.csv"]:
        entry = index["study-01/" + name]
        check("original delivered bytes: " + name, sha(base / name) == entry["sha256"]
              and (ROOT / base / name).stat().st_size == entry["bytes"])
    raw = gzip.decompress((ROOT / base / "diagnostics/summaries.jsonl.gz").read_bytes())
    entry = index["study-01/summaries.jsonl"]
    check("transferred per-seed summary matches original hash and size", len(raw) == entry["bytes"]
          and hashlib.sha256(raw).hexdigest() == entry["sha256"])
    records = [json.loads(line) for line in raw.splitlines()]
    config, grid = read(base / "config.json"), read(base / "cells.json")
    check("approved scientific parameters", parameters_digest(config) == approval["parameters_sha256"])
    check("990 saved cells exactly match approved grid", len(grid) == 990
          and Counter(map(canon, grid)) == Counter(map(canon, cells(config))))
    expected = {(c["cell_id"], seed) for c in grid for seed in config["seeds"]}
    check("29700 unique successful seed/cell records", len(records) == len(expected) == 29700
          and {(r["cell_id"], r["seed"]) for r in records} == expected and all(r["status"] == "ok" for r in records))
    by_id = {c["cell_id"]: c for c in grid}
    check("every record matches its approved scenario and suite", all(
        r["scenario"] == {**by_id[r["cell_id"]]["scenario"], "seed": r["seed"]}
        and r["suite"] == by_id[r["cell_id"]]["suite"] for r in records))
    aggregates, paired = summarize(records)
    for name, rows in [("summary.csv", aggregates), ("paired-differences.csv", paired)]:
        check("independently reproduced exact fields and multiplicities: " + name,
              csv_content((ROOT / base / name).read_text()) == generated_csv_content(rows))
    return verification, {"records": len(records), "cells": len(grid), "summary_rows": len(aggregates), "paired_rows": len(paired)}


def clean(git):
    return git["status"] == git["unmerged"] == "" and not any(git["operation_markers"].values())


def git_state(git):
    return {k: git[k] for k in ["head", "branch", "contents", "status", "unmerged", "operation_markers"]}


def metadata_ok(a, b):
    changed = {k for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
    return changed <= {"localRootBytes", "sourceDirBytes"} and all(type(b[k]) is int and b[k] >= 0 for k in changed)


def conformance(verification):
    base = Path("deliverables/conformance-01")
    approval, env = read(base / "CONFORMANCE_APPROVAL.json"), read(base / "environment-check.json")
    version = read(base / "conformance-version-m4.json")
    check("conformance approval exact snapshot", sha(base / "CONFORMANCE_APPROVAL.json") == sha("CONFORMANCE_APPROVAL.json"))
    check("conformance separately approved at exact runbook", approval["status"] == "approved"
          and approval["run_id"] == "conformance-01"
          and approval["protocol_sha256"] == sha("RUNBOOK-CONFORMANCE.md") == env["runbook_sha256"])
    check("version report and source review snapshots", approval["version_report_sha256"] == sha(base / "conformance-version-m4.json")
          == env["approved_version_report_sha256"]
          and sha(base / "conformance-review-m1.json") == sha("validation/conformance-review-m1.json"))
    check("actual public commit and both reported binary hashes", approval["public_commit"]
          == version["public_commit"] == env["public_commit"] == "75eb8fda2b1040c0f1822e0403321a105fec4f6c"
          and all(env[k] == version[k] for k in ["app_executable_sha256", "cli_executable_sha256", "app_version", "app_build"]))
    summary = list(csv.DictReader((ROOT / base / "summary.csv").open(newline="")))
    cases = {"single-clean": (["a"], [], 1), "multiple-clean": (["a", "b", "c"], [], 3),
             "one-conflict": (["a", "b"], ["a"], 1), "multiple-conflicts": (["a", "b", "c"], ["a", "b"], 1)}
    check("exact eight-case order", [(r["case"], int(r["repetition"])) for r in summary]
          == [(c, r) for r in [1, 2] for c in cases])
    request_ids, intervals = [], []
    baseline = {name: "baseline\n" for name in ["clean-one.txt", "clean-two.txt", "clean-three.txt", "shared-one.txt", "shared-two.txt"]}
    for row in summary:
        case, rep = row["case"], int(row["repetition"])
        path = base / f"{case}-r{rep}"
        prefix = f"{case}-r{rep}: "
        roles, blocked, published = cases[case]
        setup = read(path / "setup.json")
        initial, pre = setup["initial"], read(path / "pre-01.json")
        check(prefix + "fresh setup and only approved metadata differences", metadata_ok(setup["before_workspace_metadata"], setup["after_workspace_metadata"])
              and metadata_ok(setup["after_workspace_metadata"], pre["workspace_metadata"])
              and all(not v for v in setup["before_reload"]["request_file_names"].values())
              and all(not v for v in pre["request_file_names"].values()) and not pre["actor_record"]["exists"])
        check(prefix + "initial source and role identities match retained setup", pre["source"]["head"] == initial["source_head"]
              and [r["role"] for r in pre["roles"]] == roles
              and all(r["git"]["head"] == i["head"] and r["git"]["branch"] == i["branch"]
                      and r["git"]["contents"] == {**baseline, i["changed_file"]: i["content"]}
                      for r, i in zip(pre["roles"], initial["agents"])))
        initial_source = dict(baseline)
        if blocked:
            initial_source["shared-one.txt"] = "source-one\n"
        if len(blocked) == 2:
            initial_source["shared-two.txt"] = "source-two\n"
        expected_source = dict(initial_source)
        for r in initial["agents"]:
            if r["role"] not in blocked:
                expected_source[r["changed_file"]] = r["content"]
        check(prefix + "exact initial source content", pre["source"]["contents"] == initial_source)
        for phase in ["before_reload", "after_reload"]:
            snapshot = setup[phase]
            check(prefix + phase + " retained Git and identity state", git_state(snapshot["source"]) == git_state(pre["source"])
                  and [r["agent_id"] for r in snapshot["roles"]] == [r["agent_id"] for r in pre["roles"]]
                  and all(git_state(a["git"]) == git_state(b["git"])
                          and a["identity_sha256"] == b["identity_sha256"] and a["shell_sha256"] == b["shell_sha256"]
                          for a, b in zip(snapshot["roles"], pre["roles"]))
                  and all(not values for values in snapshot["request_file_names"].values()))
        before_roles = {r["role"]: r for r in pre["roles"]}
        delivered = []
        previous_after, first_events = None, None
        for number in [1, 2]:
            suffix = f"{number:02}"
            before, after = read(path / f"pre-{suffix}.json"), read(path / f"after-{suffix}.json")
            req, response = read(path / f"request-{suffix}.json"), read(path / f"response-{suffix}.json")
            evidence, assertions = read(path / f"evidence-{suffix}.json"), read(path / f"assertions-{suffix}.json")
            events = read(path / f"actor-events-{suffix}.json")
            label = prefix + suffix + ": "
            rid, result = req["requestId"], response["result"]
            request_ids.append(rid)
            intervals.append((dt(evidence["started_at"]), dt(evidence["finished_at"])))
            check(label + "request within observation timeout", 0 <= (intervals[-1][1] - intervals[-1][0]).total_seconds() <= 1800
                  and dt(before["observed_at"]) <= dt(req["createdAt"]) <= dt(after["observed_at"]))
            delivered += [rid + ".json", rid + ".result.json"]
            conflicts = [before_roles[r]["agent_id"] for r in blocked]
            check(label + "native sync receipt, transport and fixed counts", rid == response["requestId"] == evidence["request_id"] == row[f"request_{suffix}_id"]
                  and req["schema"] == "kota.bartender.dispatch.v1" and req["action"] == "sync" and req["projectRoot"] == "workspace/"
                  and evidence["cli_exit_code"] == 0 and evidence["cli_stderr_empty"]
                  and result["snapshotCount"] == 0 and result["publishedCommitCount"] == (published if number == 1 else 0)
                  and result["ok"] == response["ok"] == (not blocked)
                  and [c["agentId"] for c in result["conflicts"]] == conflicts
                  and all(c["commit"] == before_roles[r]["git"]["head"] for c, r in zip(result["conflicts"], blocked)))
            check(label + "summary agrees with native receipt", row["assertion_status"] == "PASS" and not row["hold_reason"]
                  and int(row[f"published_{suffix}"]) == result["publishedCommitCount"]
                  and int(row[f"conflicts_{suffix}"]) == len(result["conflicts"]))
            check(label + "clean source and all expected file contents", clean(after["source"])
                  and after["source"]["branch"] == "main" and after["source"]["contents"] == expected_source)
            history = after["source"]["log"]
            new_count = published if number == 1 else 0
            check(label + "source ancestry and count", len(history) > new_count
                  and history[0].split()[0] == after["source"]["head"]
                  and history[new_count].split()[0] == before["source"]["head"]
                  and all(history[i].split()[1] == history[i+1].split()[0] for i in range(new_count)))
            for role in after["roles"]:
                old = before_roles[role["role"]]
                check(label + role["role"] + " git state and identity", clean(role["git"])
                      and role["identity_sha256"] == old["identity_sha256"] and role["shell_sha256"] == old["shell_sha256"]
                      and role["git"]["branch"] == old["git"]["branch"]
                      and (git_state(role["git"]) == git_state(old["git"]) if role["role"] in blocked else
                           role["git"]["head"] == after["source"]["head"] and role["git"]["contents"] == expected_source))
            for snap in [before, after]:
                mapping = snap["workspace_metadata"]["agents"]
                check(label + snap["phase"] + " stable disabled roles and metadata", not snap["issues"]
                      and metadata_ok(setup["before_workspace_metadata"], snap["workspace_metadata"])
                      and [r["agentId"] for r in mapping] == [r["agent_id"] for r in pre["roles"]]
                      and all(r["cli"] == "conformance-disabled" for r in mapping)
                      and clean(snap["source"]) and all(clean(r["git"]) for r in snap["roles"]))
            check(label + "only intended request files, empty queues", sorted(after["request_file_names"]["delivered"]) == sorted(delivered)
                  and all(not after["request_file_names"][k] for k in ["failed", "outbox", "processing"]))
            notices = [e for e in events if e["intent"] == "resolve-conflict"]
            skips = [e for e in events if e["intent"] == "delivery-skipped"]
            check(label + "unique actor events with only expected intents", len(events) == len({e["event_id"] for e in events})
                  and len(events) == len(notices) + len(skips))
            if blocked:
                failed = before_roles[blocked[0]]["git"]["head"]
                check(label + "first blocked role notice and delivery-skipped", len(notices) == len(skips) == 1
                      and notices[0]["target_agent_ids"] == skips[0]["target_agent_ids"] == conflicts[:1]
                      and failed in notices[0]["event_id"] and after["source"]["head"] in notices[0]["event_id"]
                      and failed in notices[0]["text"] and after["source"]["head"] in notices[0]["text"]
                      and "retry sync" in notices[0]["text"] and "rebase" in notices[0]["text"].lower())
            else:
                check(label + "no actor notice in clean case", not events and not after["actor_record"]["exists"])
            check(label + "all supplied assertions observable and passing", assertions["status"] == "pass"
                  and assertions["request_id"] == rid and all(a["status"] == "pass" for a in assertions["assertions"]))
            if number == 2:
                check(label + "unedited repeat and no extra notices", git_state(before["source"]) == git_state(previous_after["source"]) == git_state(after["source"])
                      and before["roles"] == previous_after["roles"] == after["roles"] and events == first_events)
            else:
                first_events = events
            previous_after = after
    check("16 distinct requests after verification, no request overlap", len(request_ids) == len(set(request_ids)) == 16
          and all(a <= b for a, b in intervals) and intervals[0][0] > dt(verification["finished_at"])
          and all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])))
    return {"cases": len(summary), "distinct_requests": len(request_ids), "public_commit": approval["public_commit"]}


def main():
    verification, study_counts = study()
    conformance_counts = conformance(verification)
    failures = [r["check"] for r in checks if r["status"] != "pass"]
    result = {
        "schema_version": 1, "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "reviewer_role": "study maintainer", "status": "hold" if failures else "accepted",
        "study": study_counts, "conformance": conformance_counts,
        "checks_passed": len(checks) - len(failures), "checks_total": len(checks),
        "issues": failures, "checks": checks,
        "limits": [
            "M1 independently verified delivered summaries and projected observations; original raw run/flow archives and native fixture originals remain on the execution machine.",
            "Raw-file identity is evidenced by the separately approved execution-machine revalidation, not by rehashing the archive on M1.",
            "Conformance covers four fixed cases repeated twice and the unedited second sync, with disabled providers; not real-agent delivery/repair, internal pass count, performance or full worktree atomicity.",
            "Binary/source binding is release-distribution provenance, not an independently reproducible build.",
        ],
        "delivery_sha256": {str(p.relative_to(ROOT)): sha(p) for folder in ["deliverables/study-01", "deliverables/conformance-01"]
                            for p in sorted((ROOT / folder).rglob("*")) if p.is_file()},
    }
    output = ROOT / "validation/delivery-acceptance-m1.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "checks_passed", "checks_total", "issues", "study", "conformance"]}, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
