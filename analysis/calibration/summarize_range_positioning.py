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
    return {
        "source_rows": len(source),
        "count_rows": len(counts),
        "source_unique_keys": len(source_set),
        "count_unique_keys": len(count_set),
        "missing_keys": [list(value) for value in sorted(source_set - count_set)],
        "extra_keys": [list(value) for value in sorted(count_set - source_set)],
        "duplicate_source_keys": len(source_keys) - len(source_set),
        "duplicate_count_keys": len(count_keys) - len(count_set),
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
                    "q1_type7": percentile(positive, 0.25) if positive else "",
                    "median_type7": percentile(positive, 0.5) if positive else "",
                    "q3_type7": percentile(positive, 0.75) if positive else "",
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
                    low = invert(q_low, n_value)
                    point = invert(q, n_value)
                    high = invert(q_high, n_value)
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
                            "p_eff_low": f"{low:.12g}",
                            "p_eff_point": f"{point:.12g}",
                            "p_eff_high": f"{high:.12g}",
                            "scan_min": f"{scan_min:.12g}",
                            "scan_max": f"{scan_max:.12g}",
                            "interval_position": interval_position(
                                low, high, scan_min, scan_max
                            ),
                        }
                    )
    return output


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
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--scan-min", type=float, default=0.003435063819150432)
    parser.add_argument("--scan-max", type=float, default=0.06872332143144783)
    args = parser.parse_args()

    source = read_csv(args.source_pairs)
    counts = read_csv(args.counts)
    checks = source_checks(source)
    mapping = validate_mapping(source, counts)
    statuses: dict[str, int] = {}
    for row in counts:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1

    source_checks_pass = all(bool(value["pass"]) for value in checks.values())
    mapping_pass = bool(mapping["one_to_one"])
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
    write_csv(args.workload_summary, summaries)
    write_csv(args.positioning, positions)

    validation = {
        "source_pairs_sha256": sha256(args.source_pairs),
        "counts_sha256": sha256(args.counts),
        "source_headline_checks": checks,
        "pair_mapping": mapping,
        "status_counts": dict(sorted(statuses.items())),
        "expected_source_unavailable": EXPECTED_SOURCE_UNAVAILABLE,
        "source_checks_pass": source_checks_pass,
        "pair_mapping_pass": mapping_pass,
        "extraction_complete": extraction_complete,
        "source_unavailable_pass": source_unavailable_pass,
        "current_retrieval_failures": current_retrieval_failures,
        "full_current_retrieval": not current_retrieval_failures,
        "head_oid_drifts": head_oid_drifts,
        "quantile_method": "type 7 linear interpolation over positive products",
        "zero_products": "reported in workload-summary.csv and excluded from inversion because N must be positive",
        "scan": {"minimum": args.scan_min, "maximum": args.scan_max},
        "review_status": "HOLD pending second-eye review",
        "pass": (
            source_checks_pass
            and mapping_pass
            and extraction_complete
            and source_unavailable_pass
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
