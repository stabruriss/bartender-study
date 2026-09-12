"""Independently verify exported artist coordinates against accepted aggregates.

Uses the Python standard library only. Does not import the plotting generator,
its helpers, Matplotlib, or simulation code. Never reads raw run histories.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "summary.csv": "5209b6b2f833ff958bc9320af9d577cef3453eb94ff185822028da80be7e5505",
    "paired-differences.csv": "e703f0a7cacdbf4b7f38a82fbb83ed6fd9dd96096495be52ec6208b842327056",
    "cells.json": "086034341ac0f852c2a6fcb69ec68e2113652b7c74c62a48ad7ff7f71f98ef48",
}
BASELINE = "Bartender (immediate dispatch; δ does not apply)"
READS = {"dispatch": "Kick-back: base at dispatch", "start": "Kick-back: re-read at repair start"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expected_coordinates():
    source = ROOT / "deliverables/study-01"
    for name, value in INPUTS.items():
        require(sha(source / name) == value, "Accepted input hash mismatch: " + name)
    with (source / "summary.csv").open(newline="") as handle:
        summary = list(csv.DictReader(handle))
    grid = json.loads((source / "cells.json").read_text())
    require(len(summary) == 34650 and len(grid) == 990, "Unexpected accepted input dimensions")
    index = {(r["cell_id"], r["metric"]): r for r in summary}
    require(len(index) == len(summary), "Duplicate source cell/metric")
    expected = {}

    def select(suite, **fields):
        return [c for c in grid if c["suite"] == suite and all(c["scenario"][k] == v for k, v in fields.items())]

    def mean(c, metric):
        r = index[c["cell_id"], metric]
        require(r["mean"] != "" and r["runs_failed"] == "0", "Unavailable source mean")
        return float(r["mean"])

    def add(fig, axis, panel, label, cells, xs, ys, formula, x_definition, metrics=(),
            line="-", marker="None", xscale="linear", yscale="linear", intervals=False):
        if len(cells) == 1:
            cells = cells * len(xs)
        require(len(cells) == len(xs) == len(ys), "Invalid independent specification")
        for i, (c, x, y) in enumerate(zip(cells, xs, ys)):
            low, high = "", ""
            if intervals:
                row = index[c["cell_id"], metrics[0]]
                low, high = float(row["ci95_low"]), float(row["ci95_high"])
            key = (fig, str(axis), label, str(i))
            require(key not in expected, "Duplicate expected point")
            expected[key] = {"panel": panel, "cell_id": c["cell_id"], "source_metrics": "|".join(metrics),
                             "source_components_json": json.dumps({metric: {
                                 field: index[c["cell_id"], metric][field]
                                 for field in ["n", "mean", "ci95_low", "ci95_high"]}
                                 for metric in metrics}, sort_keys=True, separators=(",", ":")),
                             "observations_sha256": "" if formula.startswith("nominal_") else INPUTS["summary.csv"],
                             "metadata_sha256": INPUTS["cells.json"], "formula": formula,
                             "x_definition": x_definition, "x": x, "y": y, "ci95_low": low, "ci95_high": high,
                             "line_style": line, "marker": marker, "x_axis_scale": xscale, "y_axis_scale": yscale}

    metrics = ["author_repair_starts", "observed_repair_effort"]
    slices = [(2, 0.), (4, 0.), (8, 0.), (4, .1), (4, .3)]
    for row, (n, d) in enumerate(slices):
        for policy, label, line, marker in [("clean_first", "Bartender", "-", "o"), ("in_place", "In-place repair", "--", "s")]:
            cells = sorted(select("sync_interval", n=n, dependency=d, avoidance=0., tau=1., policy=policy), key=lambda c: c["p_nominal"])
            require(len(cells) == 3, "Incomplete repair slice")
            for col, metric in enumerate(metrics):
                add("fig4_repairs_overlap", row*2+col, f"agents={n};dependency={d:g};metric={metric}",
                    label, cells, [c["p_nominal"] for c in cells], [mean(c, metric) for c in cells],
                    "summary_mean", "nominal_overlap_probability", (metric,), line, marker, "log", "log", True)

    for col, length in enumerate([4, 16, 64]):
        cells = sorted(select("sync_interval", n=4, dependency=0., avoidance=0., policy="clean_first", length=length),
                       key=lambda c: c["scenario"]["tau"])
        require(len(cells) == 7, "Incomplete synchronization slice")
        xs = [c["scenario"]["tau"] for c in cells]
        for row, metric in enumerate(["overlap_pairs_per_time", "first_failures_per_time", "mean_first_failure_overlap_lines"]):
            add("fig5_sync_interval", row*3+col, f"edit_lines={length};metric={metric}", "Simulation", cells,
                xs, [mean(c, metric) for c in cells], "summary_mean", "sync_interval", (metric,),
                "-", "o", "log", "linear", True)
        prediction = [c["scenario"]["n"]*(c["scenario"]["n"]-1)/2*c["p_nominal"]*c["scenario"]["rate"]**2*c["scenario"]["tau"] for c in cells]
        add("fig5_sync_interval", col, f"edit_lines={length};metric=overlap_pairs_per_time", "First-order model (theory)",
            cells, xs, prediction, "nominal_overlap_pair_rate", "sync_interval", line="--", xscale="log")

    for col, length in enumerate([4, 16, 64]):
        for figure, formula, used_metrics in [
            ("fig6_wait_resolved", "completed_minus_failed_over_initial", ("author_repair_completions", "failed_repair_completions", "conflict_cohort_n")),
            ("fig7_wait_failures", "failed_over_completed", ("failed_repair_completions", "author_repair_completions")),
        ]:
            zeros = []
            zero_cell = None
            for refresh in ["dispatch", "start"]:
                cells = sorted(select("repair_delay", n=4, dependency=0., avoidance=0., repair_clock="fixed", refresh_at=refresh, length=length),
                               key=lambda c: c["delta_multiple"])
                xs = [c["delta_multiple"] for c in cells]
                require(xs == [0., .25, .5, 1., 2., 4.], "Incomplete waiting slice")
                ys = []
                for c in cells:
                    require(all(index[c["cell_id"], metric]["n"] == "30" for metric in used_metrics), "Unequal seed counts in pooled ratio")
                    completed, failed = mean(c, "author_repair_completions"), mean(c, "failed_repair_completions")
                    ys.append(failed/completed if figure == "fig7_wait_failures" else (completed-failed)/mean(c, "conflict_cohort_n"))
                zeros.append(ys[0])
                if refresh == "dispatch":
                    zero_cell = cells[0]
                add(figure, col, f"edit_lines={length}", READS[refresh], cells, xs, ys, formula,
                    "wait_in_characteristic_units", used_metrics, "--", "o" if refresh == "dispatch" else "s")
                if figure == "fig7_wait_failures":
                    c = cells[0]
                    # Independently reconstruct mu from p, n and lambda.
                    mu = c["p_nominal"] * (c["scenario"]["n"]-1) * c["scenario"]["rate"]
                    require(math.isclose(mu, c["mu_nominal"], rel_tol=1e-14), "Nominal mu disagrees with its factors")
                    fine = [4*i/200 for i in range(201)]
                    values = [1-math.exp(-(mu*c["scenario"]["repair_time"] + (x if refresh == "dispatch" else 0))) for x in fine]
                    add(figure, col, f"edit_lines={length}", "First-order theory: " + ("dispatch" if refresh == "dispatch" else "repair start"),
                        [c], fine, values, "nominal_failure_probability", "comparator_wait_characteristic_units", line=":")
            require(zeros[0] == zeros[1], "Immediate reference differs between base-read timings")
            add(figure, col, f"edit_lines={length}", BASELINE, [zero_cell], [0., 4.], [zeros[0], zeros[0]],
                "zero_wait_reference:"+formula, "comparator_wait_characteristic_units", used_metrics, "-", "o")
    require(len(expected) == 1434, "Unexpected independent coordinate count")
    return expected


def verify(directory):
    expected = expected_coordinates()
    with (directory / "plot-data.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    actual = {}
    for row in rows:
        key = tuple(row[k] for k in ["figure", "axes_index", "series", "point_index"])
        require(key not in actual, "Duplicate displayed coordinate: " + str(key))
        actual[key] = row
    require(set(actual) == set(expected), f"Coordinate coverage mismatch: {len(set(expected)-set(actual))} missing, {len(set(actual)-set(expected))} unexpected")
    numeric = {"x", "y", "ci95_low", "ci95_high"}
    checked = 0
    for key, e in expected.items():
        for field, value in e.items():
            supplied = actual[key][field]
            if field in numeric and value != "":
                require(supplied != "" and math.isclose(float(supplied), value, rel_tol=1e-12, abs_tol=1e-12),
                        f"Coordinate/interval mismatch: {key} {field}")
            else:
                require(supplied == value, f"Source/style mismatch: {key} {field}")
            checked += 1
    manifest = json.loads((directory / "manifest.json").read_text())
    require(manifest["inputs"] == INPUTS, "Manifest input anchors differ")
    require(manifest["plot_coordinate_rows"] == len(rows), "Manifest coordinate count differs")
    for name, info in manifest["outputs"].items():
        path = directory / name
        require(sha(path) == info["sha256"] and path.stat().st_size == info["bytes"], "Output manifest mismatch: " + name)
    for name, value in manifest["scripts"].items():
        require(sha(ROOT / "analysis" / name) == value, "Generator/helper hash mismatch: " + name)
    return {"status": "pass", "coordinates_checked": len(rows), "fields_checked": checked,
            "figure_counts": dict(Counter(r["figure"] for r in rows)),
            "formula_counts": dict(Counter(r["formula"] for r in rows)), "issues": [],
            "source_hashes": INPUTS, "plot_data_sha256": sha(directory / "plot-data.csv"),
            "plot_manifest_sha256": sha(directory / "manifest.json"), "verifier_sha256": sha(Path(__file__)),
            "source_intervals_checked": sum(r["ci95_low"] != "" for r in rows),
            "ratio_intervals_inferred": False,
            "comparison_tolerance": {"relative": 1e-12, "absolute": 1e-12},
            "scope": "Actual exported Matplotlib artist coordinates versus accepted aggregates and approved metadata; no raw-output read or simulation rerun."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "analysis/manuscript")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.directory)
    except (ValueError, KeyError, OSError) as exc:
        result = {"status": "fail", "issues": [str(exc)]}
    report = args.report or args.directory / "plot-verification.json"
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k in ["status", "coordinates_checked", "fields_checked", "issues"]}))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
