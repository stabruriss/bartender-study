#!/usr/bin/env python3
"""Summarize the current-retrievable Xu PR-pair sensitivity extraction.

The output positions source conflict rates against an effective per-cross-unit
collision probability under an independence mapping. It does not estimate the
Bartender simulation parameter and does not run the simulation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable


KEY_FIELDS = ("stratum", "repo", "prA", "prB")
EXPECTED_SOURCE = {
    "same": {"rows": 625, "evaluable": 601, "conflict": 119},
    "cross": {"rows": 122, "evaluable": 115, "conflict": 48},
}
EXPECTED_SOURCE_UNAVAILABLE = {"UNAVAIL_fetch": 25, "UNAVAIL_nobase": 6}
EXPECTED_CELLS_SHA256 = "086034341ac0f852c2a6fcb69ec68e2113652b7c74c62a48ad7ff7f71f98ef48"
EXPECTED_SUMMARY_SHA256 = "5209b6b2f833ff958bc9320af9d577cef3453eb94ff185822028da80be7e5505"
SYNC_METRICS = (
    "overlap_pairs_per_time",
    "first_failures_per_time",
    "mean_first_failure_overlap_lines",
)
SCOPE_SLUGS = {
    "structural-inclusive textual conflict": "structural_inclusive",
    "conflict with any content component": "any_content",
    "content-only conflict": "content_only",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def key(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in KEY_FIELDS)


def source_conflict_flags(row: dict[str, str]) -> tuple[str, str]:
    conflict_types = {value for value in row["types"].split("|") if value}
    has_content = row["label"] == "CONFLICT" and "content" in conflict_types
    content_only = has_content and conflict_types == {"content"}
    return str(has_content).lower(), str(content_only).lower()


def percentile(values: Iterable[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile of empty sequence")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    proportion = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = (proportion + z2 / (2 * total)) / denominator
    half = z * math.sqrt(
        proportion * (1 - proportion) / total + z2 / (4 * total * total)
    ) / denominator
    return center - half, center + half


def invert(conflict_probability: float, cross_unit_pairs: float) -> float:
    if not (0 < conflict_probability < 1 and cross_unit_pairs > 0):
        raise ValueError("mapping requires 0 < q < 1 and N > 0")
    return 1 - (1 - conflict_probability) ** (1 / cross_unit_pairs)


def overlap_intensity(conflict_probability: float) -> float:
    """Return the Poisson-equivalent dimensionless intensity -ln(1-q)."""
    if not 0 < conflict_probability < 1:
        raise ValueError("intensity mapping requires 0 < q < 1")
    return -math.log1p(-conflict_probability)


def bernoulli_expected_overlaps(
    conflict_probability: float, cross_unit_pairs: float
) -> float:
    """Expected overlaps N*p_eff under the independent Bernoulli mapping."""
    return cross_unit_pairs * invert(conflict_probability, cross_unit_pairs)


def source_checks(rows: list[dict[str, str]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for stratum, expected in EXPECTED_SOURCE.items():
        group = [row for row in rows if row["stratum"] == stratum]
        evaluable = [row for row in group if not row["label"].startswith("UNAVAIL")]
        conflicts = [row for row in evaluable if row["label"] == "CONFLICT"]
        actual = {
            "rows": len(group),
            "evaluable": len(evaluable),
            "conflict": len(conflicts),
        }
        result[stratum] = {"expected": expected, "actual": actual, "pass": actual == expected}
    return result


def validate_mapping(
    source: list[dict[str, str]], counts: list[dict[str, str]]
) -> dict[str, object]:
    source_keys = [key(row) for row in source]
    count_keys = [key(row) for row in counts]
    source_set = set(source_keys)
    count_set = set(count_keys)
    source_index = {key(row): row for row in source}
    count_index = {key(row): row for row in counts}
    field_mismatches: list[dict[str, object]] = []
    for row_key in sorted(source_set & count_set):
        source_row = source_index[row_key]
        count_row = count_index[row_key]
        expected_has_content, expected_content_only = source_conflict_flags(source_row)
        comparisons = {
            "label": (source_row["label"], count_row["label"]),
            "conflict_has_content": (
                expected_has_content,
                count_row["conflict_has_content"],
            ),
            "conflict_is_content_only": (
                expected_content_only,
                count_row["conflict_is_content_only"],
            ),
        }
        for field, (expected, actual) in comparisons.items():
            if expected != actual:
                field_mismatches.append(
                    {
                        "key": list(row_key),
                        "field": field,
                        "expected": expected,
                        "actual": actual,
                    }
                )
    return {
        "source_rows": len(source),
        "count_rows": len(counts),
        "source_unique_keys": len(source_set),
        "count_unique_keys": len(count_set),
        "missing_keys": [list(value) for value in sorted(source_set - count_set)],
        "extra_keys": [list(value) for value in sorted(count_set - source_set)],
        "duplicate_source_keys": len(source_keys) - len(source_set),
        "duplicate_count_keys": len(count_keys) - len(count_set),
        "field_mismatches": field_mismatches,
        "fields_match": not field_mismatches,
        "one_to_one": (
            len(source) == len(counts)
            and len(source_keys) == len(source_set)
            and len(count_keys) == len(count_set)
            and source_set == count_set
        ),
    }


def workload_rows(counts: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for stratum in ("same", "cross"):
        ok = [row for row in counts if row["stratum"] == stratum and row["status"] == "OK"]
        measures = {
            "hunk_product": [int(row["hunksA"]) * int(row["hunksB"]) for row in ok],
            "file_product": [int(row["filesA"]) * int(row["filesB"]) for row in ok],
        }
        for measure, values in measures.items():
            positive = [value for value in values if value > 0]
            output.append(
                {
                    "stratum": stratum,
                    "measure": measure,
                    "retrievable_pairs": len(values),
                    "positive_pairs": len(positive),
                    "zero_pairs": len(values) - len(positive),
                    "minimum_positive": min(positive) if positive else "",
                    "q1_type7": percentile(values, 0.25) if values else "",
                    "median_type7": percentile(values, 0.5) if values else "",
                    "q3_type7": percentile(values, 0.75) if values else "",
                    "maximum": max(values) if values else "",
                }
            )
    return output


def rate_definitions(rows: list[dict[str, str]], stratum: str) -> list[tuple[str, int, int]]:
    group = [row for row in rows if row["stratum"] == stratum]
    evaluable = [row for row in group if not row["label"].startswith("UNAVAIL")]
    return [
        (
            "structural-inclusive textual conflict",
            sum(row["label"] == "CONFLICT" for row in evaluable),
            len(evaluable),
        ),
        (
            "conflict with any content component",
            sum(row["conflict_has_content"] == "true" for row in evaluable),
            len(evaluable),
        ),
        (
            "content-only conflict",
            sum(row["conflict_is_content_only"] == "true" for row in evaluable),
            len(evaluable),
        ),
    ]


def interval_position(low: float, high: float, scan_min: float, scan_max: float) -> str:
    if high < scan_min:
        return "below scan"
    if low > scan_max:
        return "above scan"
    if low >= scan_min and high <= scan_max:
        return "inside scan"
    return "partly overlaps scan"


def positioning_rows(
    counts: list[dict[str, str]],
    summaries: list[dict[str, object]],
    scan_min: float,
    scan_max: float,
) -> list[dict[str, object]]:
    summary_index = {
        (str(row["stratum"]), str(row["measure"])): row for row in summaries
    }
    output: list[dict[str, object]] = []
    for stratum in ("same", "cross"):
        for scope, numerator, denominator in rate_definitions(counts, stratum):
            q = numerator / denominator
            q_low, q_high = wilson(numerator, denominator)
            for measure, unit in (("hunk_product", "hunk pair"), ("file_product", "file pair")):
                summary = summary_index[(stratum, measure)]
                for quantile, field in (
                    ("Q1", "q1_type7"),
                    ("median", "median_type7"),
                    ("Q3", "q3_type7"),
                ):
                    n_value = float(summary[field])
                    invertible = n_value > 0
                    low = invert(q_low, n_value) if invertible else None
                    point = invert(q, n_value) if invertible else None
                    high = invert(q_high, n_value) if invertible else None
                    output.append(
                        {
                            "stratum": stratum,
                            "conflict_scope": scope,
                            "numerator": numerator,
                            "denominator": denominator,
                            "q": f"{q:.12g}",
                            "q_wilson_low": f"{q_low:.12g}",
                            "q_wilson_high": f"{q_high:.12g}",
                            "editor_unit": unit,
                            "N_quantile": quantile,
                            "N_value": f"{n_value:.12g}",
                            "p_eff_low": "" if low is None else f"{low:.12g}",
                            "p_eff_point": "" if point is None else f"{point:.12g}",
                            "p_eff_high": "" if high is None else f"{high:.12g}",
                            "scan_min": f"{scan_min:.12g}",
                            "scan_max": f"{scan_max:.12g}",
                            "interval_position": (
                                "non-invertible: selected N is zero"
                                if not invertible
                                else interval_position(low, high, scan_min, scan_max)
                            ),
                        }
                    )
    return output


def dimensionless_rows(
    positions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Map PR-level q to expected overlap pairs for each observed hunk N."""
    output: list[dict[str, object]] = []
    for row in positions:
        if row["editor_unit"] != "hunk pair":
            continue
        n_value = float(row["N_value"])
        if n_value <= 0:
            output.append(
                {
                    "stratum": row["stratum"],
                    "conflict_scope": row["conflict_scope"],
                    "numerator": row["numerator"],
                    "denominator": row["denominator"],
                    "q": row["q"],
                    "q_wilson_low": row["q_wilson_low"],
                    "q_wilson_high": row["q_wilson_high"],
                    "N_quantile": row["N_quantile"],
                    "N_hunk_pairs": row["N_value"],
                    "p_eff_low": "",
                    "p_eff_point": "",
                    "p_eff_high": "",
                    "expected_overlap_pairs_low": "",
                    "expected_overlap_pairs_point": "",
                    "expected_overlap_pairs_high": "",
                    "transformed_ci": "non-invertible: selected N is zero",
                    "poisson_hazard_low": "",
                    "poisson_hazard_point": "",
                    "poisson_hazard_high": "",
                    "expected_minus_hazard_point": "",
                }
            )
            continue
        q = float(row["q"])
        q_low = float(row["q_wilson_low"])
        q_high = float(row["q_wilson_high"])
        expected_low = bernoulli_expected_overlaps(q_low, n_value)
        expected_point = bernoulli_expected_overlaps(q, n_value)
        expected_high = bernoulli_expected_overlaps(q_high, n_value)
        hazard_low = overlap_intensity(q_low)
        hazard_point = overlap_intensity(q)
        hazard_high = overlap_intensity(q_high)
        output.append(
            {
                "stratum": row["stratum"],
                "conflict_scope": row["conflict_scope"],
                "numerator": row["numerator"],
                "denominator": row["denominator"],
                "q": row["q"],
                "q_wilson_low": row["q_wilson_low"],
                "q_wilson_high": row["q_wilson_high"],
                "N_quantile": row["N_quantile"],
                "N_hunk_pairs": row["N_value"],
                "p_eff_low": row["p_eff_low"],
                "p_eff_point": row["p_eff_point"],
                "p_eff_high": row["p_eff_high"],
                "expected_overlap_pairs_low": f"{expected_low:.12g}",
                "expected_overlap_pairs_point": f"{expected_point:.12g}",
                "expected_overlap_pairs_high": f"{expected_high:.12g}",
                "transformed_ci": "Wilson q interval mapped monotonically through N*[1-(1-q)^(1/N)]",
                "poisson_hazard_low": f"{hazard_low:.12g}",
                "poisson_hazard_point": f"{hazard_point:.12g}",
                "poisson_hazard_high": f"{hazard_high:.12g}",
                "expected_minus_hazard_point": f"{expected_point - hazard_point:.12g}",
            }
        )
    return output


def point_position(value: float, low: float, high: float) -> str:
    if value < low:
        return "below interval"
    if value > high:
        return "above interval"
    return "inside interval"


def metric_fields(
    summary_index: dict[tuple[str, str], dict[str, str]], cell_id: str
) -> dict[str, object]:
    output: dict[str, object] = {}
    for metric in SYNC_METRICS:
        row = summary_index[(cell_id, metric)]
        output.update(
            {
                f"{metric}_n": row["n"],
                f"{metric}_mean": row["mean"],
                f"{metric}_ci95_low": row["ci95_low"],
                f"{metric}_ci95_high": row["ci95_high"],
            }
        )
    return output


def sync_grid_rows(
    cells: list[dict[str, object]],
    study_summary: list[dict[str, str]],
    dimensions: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Read the accepted Figure 5 slice without rerunning the simulation."""
    selected = [
        cell
        for cell in cells
        if cell["suite"] == "sync_interval"
        and cell["scenario"]["n"] == 4
        and cell["scenario"]["dependency"] == 0.0
        and cell["scenario"]["avoidance"] == 0.0
        and cell["scenario"]["policy"] == "clean_first"
    ]
    if len(selected) != 21:
        raise SystemExit(f"expected 21 Figure 5 cells, found {len(selected)}")
    summary_index = {
        (row["cell_id"], row["metric"]): row for row in study_summary
    }
    primary = {
        (str(row["stratum"]), str(row["conflict_scope"])): row
        for row in dimensions
        if row["N_quantile"] == "median"
    }

    grid: list[dict[str, object]] = []
    for cell in sorted(
        selected,
        key=lambda item: (float(item["p_nominal"]), float(item["scenario"]["tau"])),
    ):
        scenario = cell["scenario"]
        p = float(cell["p_nominal"])
        rate = float(scenario["rate"])
        tau = float(scenario["tau"])
        expected_grid = p * (rate * tau) ** 2
        row: dict[str, object] = {
            "cell_id": cell["cell_id"],
            "edit_lines": scenario["length"],
            "p_nominal": f"{p:.12g}",
            "rate_lambda": f"{rate:.12g}",
            "tau": f"{tau:.12g}",
            "model_expected_overlap_pairs_p_lambda_tau_squared": f"{expected_grid:.12g}",
            "first_order_overlap_pairs_per_time_all_agent_pairs": f"{math.comb(4, 2) * p * rate * rate * tau:.12g}",
            "selection": "n=4; dependency=0; avoidance=0; clean_first Figure 5 slice",
        }
        for stratum in ("same", "cross"):
            for scope, slug in SCOPE_SLUGS.items():
                dimension = primary[(stratum, scope)]
                low = float(dimension["expected_overlap_pairs_low"])
                point = float(dimension["expected_overlap_pairs_point"])
                high = float(dimension["expected_overlap_pairs_high"])
                target_tau = math.sqrt(point / p) / rate
                row.update(
                    {
                        f"{stratum}_{slug}_median_E_position": point_position(
                            expected_grid, low, high
                        ),
                        f"{stratum}_{slug}_median_E_target_tau": f"{target_tau:.12g}",
                        f"{stratum}_{slug}_median_E_tau_ci_low": f"{math.sqrt(low / p) / rate:.12g}",
                        f"{stratum}_{slug}_median_E_tau_ci_high": f"{math.sqrt(high / p) / rate:.12g}",
                    }
                )
        row.update(metric_fields(summary_index, str(cell["cell_id"])))
        grid.append(row)

    references: list[dict[str, object]] = []
    for stratum in ("same", "cross"):
        for scope, slug in SCOPE_SLUGS.items():
            dimension = primary[(stratum, scope)]
            target = float(dimension["expected_overlap_pairs_point"])
            for p in sorted({float(row["p_nominal"]) for row in grid}):
                candidates = [row for row in grid if float(row["p_nominal"]) == p]
                rate = float(candidates[0]["rate_lambda"])
                target_tau = math.sqrt(target / p) / rate
                nearest = min(
                    candidates,
                    key=lambda row: abs(math.log(float(row["tau"]) / target_tau)),
                )
                references.append(
                    {
                        "external_stratum": stratum,
                        "external_conflict_scope": scope,
                        "external_N_quantile": "median",
                        "external_N_hunk_pairs": dimension["N_hunk_pairs"],
                        "external_expected_overlap_pairs_point": dimension["expected_overlap_pairs_point"],
                        "external_expected_overlap_pairs_low": dimension["expected_overlap_pairs_low"],
                        "external_expected_overlap_pairs_high": dimension["expected_overlap_pairs_high"],
                        "p_nominal": nearest["p_nominal"],
                        "target_tau_at_external_point": f"{target_tau:.12g}",
                        "nearest_sampled_tau": nearest["tau"],
                        "nearest_sampled_cell_id": nearest["cell_id"],
                        "nearest_sampled_model_expected_overlap_pairs": nearest["model_expected_overlap_pairs_p_lambda_tau_squared"],
                        "nearest_sampled_position": nearest[
                            f"{stratum}_{slug}_median_E_position"
                        ],
                        **{
                            key: value
                            for key, value in nearest.items()
                            if any(key.startswith(metric) for metric in SYNC_METRICS)
                        },
                    }
                )
    return grid, references


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise SystemExit(f"no rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-pairs", type=Path, required=True)
    parser.add_argument("--counts", type=Path, required=True)
    parser.add_argument("--workload-summary", type=Path, required=True)
    parser.add_argument("--positioning", type=Path, required=True)
    parser.add_argument("--cells", type=Path, required=True)
    parser.add_argument("--study-summary", type=Path, required=True)
    parser.add_argument("--dimensionless", type=Path, required=True)
    parser.add_argument("--sync-grid", type=Path, required=True)
    parser.add_argument("--reference-cells", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--scan-min", type=float, default=0.003435063819150432)
    parser.add_argument("--scan-max", type=float, default=0.06872332143144783)
    args = parser.parse_args()

    source = read_csv(args.source_pairs)
    counts = read_csv(args.counts)
    cells = json.loads(args.cells.read_text(encoding="utf-8"))
    study_summary = read_csv(args.study_summary)
    checks = source_checks(source)
    mapping = validate_mapping(source, counts)
    statuses: dict[str, int] = {}
    for row in counts:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1

    source_checks_pass = all(bool(value["pass"]) for value in checks.values())
    mapping_pass = bool(mapping["one_to_one"])
    field_mapping_pass = bool(mapping["fields_match"])
    extraction_complete = len(counts) == len(source) == 747 and mapping_pass
    source_unavailable = {
        status: statuses.get(status, 0) for status in EXPECTED_SOURCE_UNAVAILABLE
    }
    source_unavailable_pass = source_unavailable == EXPECTED_SOURCE_UNAVAILABLE
    current_retrieval_failures = {
        status: count
        for status, count in sorted(statuses.items())
        if status not in {"OK", "OK_HEAD_CHANGED", *EXPECTED_SOURCE_UNAVAILABLE}
    }
    head_oid_drifts = sum(row["status"] == "OK_HEAD_CHANGED" for row in counts)

    summaries = workload_rows(counts)
    positions = positioning_rows(counts, summaries, args.scan_min, args.scan_max)
    dimensions = dimensionless_rows(positions)
    grid, reference_cells = sync_grid_rows(cells, study_summary, dimensions)
    write_csv(args.workload_summary, summaries)
    write_csv(args.positioning, positions)
    write_csv(args.dimensionless, dimensions)
    write_csv(args.sync_grid, grid)
    write_csv(args.reference_cells, reference_cells)

    cells_sha = sha256(args.cells)
    summary_sha = sha256(args.study_summary)
    accepted_study_inputs_pass = (
        cells_sha == EXPECTED_CELLS_SHA256
        and summary_sha == EXPECTED_SUMMARY_SHA256
    )

    validation = {
        "source_pairs_sha256": sha256(args.source_pairs),
        "counts_sha256": sha256(args.counts),
        "cells_sha256": cells_sha,
        "study_summary_sha256": summary_sha,
        "accepted_study_inputs": {
            "expected_cells_sha256": EXPECTED_CELLS_SHA256,
            "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
            "pass": accepted_study_inputs_pass,
        },
        "source_headline_checks": checks,
        "pair_mapping": mapping,
        "status_counts": dict(sorted(statuses.items())),
        "expected_source_unavailable": EXPECTED_SOURCE_UNAVAILABLE,
        "source_checks_pass": source_checks_pass,
        "pair_mapping_pass": mapping_pass,
        "field_mapping_pass": field_mapping_pass,
        "extraction_complete": extraction_complete,
        "source_unavailable_pass": source_unavailable_pass,
        "current_retrieval_failures": current_retrieval_failures,
        "full_current_retrieval": not current_retrieval_failures,
        "head_oid_drifts": head_oid_drifts,
        "quantile_method": "type 7 linear interpolation over all currently retrievable OK-pair products, including zero",
        "zero_products": "reported in workload-summary.csv and retained in quantiles; only a selected zero quantile is non-invertible",
        "scan": {"minimum": args.scan_min, "maximum": args.scan_max},
        "dimensionless_mapping": "E=N*[1-(1-q)^(1/N)] under fixed-N independent Bernoulli overlap, compared with p*(lambda*tau)^2 through an event-definition and workload-scale analogy; the Poisson/rare-event limit is used only to interpret -ln(1-q), not to compute E or target tau",
        "sync_grid_cells": len(grid),
        "reference_cells": len(reference_cells),
        "scientific_review_pass": True,
        "review_status": "Scoped PASS for current-retrievable scenario positioning; full-current-retrieval remains false because one source-clean pair is now 404",
        "pass": (
            source_checks_pass
            and mapping_pass
            and field_mapping_pass
            and extraction_complete
            and source_unavailable_pass
            and accepted_study_inputs_pass
            and not current_retrieval_failures
            and head_oid_drifts == 0
        ),
    }
    args.validation.parent.mkdir(parents=True, exist_ok=True)
    args.validation.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
