"""Across-seed summaries and paired policy contrasts; retain missing values."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import statistics


def mean_interval(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "mean": None, "ci95_low": None, "ci95_high": None}
    mean = statistics.mean(values)
    width = 1.96 * statistics.stdev(values) / math.sqrt(len(values)) if len(values) >= 2 else None
    return {"n": len(values), "mean": mean,
            "ci95_low": mean - width if width is not None else None,
            "ci95_high": mean + width if width is not None else None}


def summarize(records: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[str, list[dict]] = {}
    pairs: dict[tuple, dict] = {}
    for record in records:
        grouped.setdefault(record["cell_id"], []).append(record)
        if record["status"] != "ok" or record["scenario"]["policy"] == "kick_back":
            continue
        scenario = record["scenario"]
        pair_key = (record["suite"], tuple(sorted((k, v) for k, v in scenario.items()
                                                 if k != "policy")))
        pairs.setdefault(pair_key, {})[scenario["policy"]] = record
    aggregates = []
    for cell_id, group in grouped.items():
        successes = [r for r in group if r["status"] == "ok"]
        metric_names = sorted({k for r in successes for k in r["metrics"]})
        if not metric_names:
            aggregates.append({"suite": group[0]["suite"], "cell_id": cell_id,
                               "metric": "all_runs_failed", "runs_seen": len(group),
                               "runs_failed": len(group), **mean_interval([])})
        for metric in metric_names:
            values = [r["metrics"][metric] for r in successes if r["metrics"][metric] is not None]
            aggregates.append({"suite": group[0]["suite"], "cell_id": cell_id,
                               "metric": metric, "runs_seen": len(group),
                               "runs_failed": len(group) - len(successes), **mean_interval(values)})
    differences: dict[tuple, list[float]] = {}
    for pair in pairs.values():
        if not {"clean_first", "in_place"} <= pair.keys():
            continue
        clean, inline = pair["clean_first"], pair["in_place"]
        if clean["flow_sha256"] != inline["flow_sha256"]:
            raise ValueError("paired policies did not receive identical proposal streams")
        for metric, value in clean["metrics"].items():
            baseline = inline["metrics"][metric]
            if value is not None and baseline is not None:
                key = clean["suite"], clean["cell_id"], inline["cell_id"], metric
                differences.setdefault(key, []).append(value - baseline)
    contrasts = [{"suite": key[0], "clean_first_cell": key[1], "in_place_cell": key[2],
                  "metric": key[3], **mean_interval(values)} for key, values in differences.items()]
    return aggregates, contrasts


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("x", newline="") as handle:
        if rows:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def kaplan_meier(observations: list[tuple[float, bool]]) -> list[dict]:
    """Descriptive conflict survival: (observed age, landed) pairs.

    Events precede censoring at ties. No confidence interval is inferred by
    treating patches from the same seed as independent replicates.
    """
    counts: dict[float, list[int]] = {}
    for age, landed in observations:
        if age < 0 or not math.isfinite(age):
            raise ValueError("invalid observed age")
        pair = counts.setdefault(age, [0, 0])
        pair[0 if landed else 1] += 1
    at_risk, survival, result = len(observations), 1.0, []
    for age, (events, censored) in sorted(counts.items()):
        survival *= 1 - events / at_risk
        result.append({"age": age, "at_risk": at_risk, "landings": events,
                       "censored": censored, "survival": survival})
        at_risk -= events + censored
    return result
