"""Load, enumerate and validate proposed or approved parameter sets."""

from __future__ import annotations

from dataclasses import asdict, fields
import hashlib
import itertools
import json
import math
from pathlib import Path

from .controls import interval_overlap_probability
from .model import Scenario


def parameters_digest(config: dict) -> str:
    payload = {k: v for k, v in config.items() if k != "approval"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_config(path: Path) -> dict:
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    config = json.loads(path.read_text(), object_pairs_hook=pairs)
    if config.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    allowed = {"schema_version", "title", "approval", "common", "seeds", "suites"}
    if set(config) - allowed:
        raise ValueError(f"unknown configuration keys: {set(config) - allowed}")
    seeds = config["seeds"]
    if len(seeds) < 30 or len(set(seeds)) != len(seeds):
        raise ValueError("a study needs at least 30 distinct seeds per cell")
    if any(type(seed) is not int or seed < 0 for seed in seeds):
        raise ValueError("seeds must be nonnegative integers")
    if not config["suites"]:
        raise ValueError("at least one suite is required")
    return config


def require_approval(config: dict) -> None:
    a = config.get("approval", {})
    if (a.get("status") != "approved" or not a.get("approved_by")
            or not a.get("approved_at") or a.get("parameters_sha256") != parameters_digest(config)):
        raise ValueError("study parameters are not approved at this SHA-256; plan and tests remain available")


def cells(config: dict) -> list[dict]:
    result, seen, names = [], set(), set()
    allowed_fields = {f.name for f in fields(Scenario)} - {"seed"}
    for suite in config["suites"]:
        allowed_suite = {"name", "fixed", "cases", "axes", "delay_multiples",
                         "horizon_characteristic_multiples"}
        if set(suite) - allowed_suite:
            raise ValueError(f"unknown suite keys: {set(suite) - allowed_suite}")
        name = suite["name"]
        if not name or name in names:
            raise ValueError("suite names must be nonempty and unique")
        names.add(name)
        axes = suite["axes"]
        if any(not values for values in axes.values()):
            raise ValueError("sweep axes cannot be empty")
        for case_index, case in enumerate(suite.get("cases", [{}])):
            for axis_values in itertools.product(*axes.values()):
                values = {**config["common"], **suite.get("fixed", {}),
                          **case, **dict(zip(axes, axis_values))}
                if set(values) - allowed_fields:
                    raise ValueError(f"unknown scenario fields: {set(values) - allowed_fields}")
                Scenario(**values).validate()
                p = interval_overlap_probability(values["files"], values["lines"], values["length"])
                mu = p * (values["n"] - 1) * values["rate"]
                for multiplier in suite.get("delay_multiples", [None]):
                    actual = dict(values)
                    if multiplier is not None:
                        if not math.isfinite(multiplier) or multiplier < 0 or mu <= 0:
                            raise ValueError("delay sweep needs nonnegative multiples and positive nominal mu")
                        actual["delta"] = multiplier / mu
                    if "horizon_characteristic_multiples" in suite:
                        h = suite["horizon_characteristic_multiples"]
                        if not math.isfinite(h) or h <= 0 or mu <= 0:
                            raise ValueError("invalid characteristic observation window")
                        actual["horizon"] = max(actual["horizon"], h / mu)
                    Scenario(**actual).validate()
                    payload = json.dumps(actual, sort_keys=True, separators=(",", ":"))
                    key = name, payload
                    if key in seen:
                        raise ValueError(f"duplicate scenario in {name}")
                    seen.add(key)
                    cell_id = hashlib.sha256((name + ":" + payload).encode()).hexdigest()[:16]
                    result.append({"suite": name, "case": case_index, "cell_id": cell_id,
                                   "p_nominal": p, "mu_nominal": mu,
                                   "delta_multiple": multiplier, "scenario": actual})
    if not result:
        raise ValueError("no scenarios")
    return result


def describe(config: dict, grid: list[dict]) -> dict:
    return {
        "status": config.get("approval", {}).get("status", "proposed"),
        "parameters_sha256": parameters_digest(config),
        "cells": len(grid), "seeds_per_cell": len(config["seeds"]),
        "planned_runs": len(grid) * len(config["seeds"]),
        "suites": {name: sum(c["suite"] == name for c in grid)
                   for name in sorted({c["suite"] for c in grid})},
        "p_by_length": {str(c["scenario"]["length"]): c["p_nominal"] for c in grid},
        "horizon_min": min(c["scenario"]["horizon"] for c in grid),
        "horizon_max": max(c["scenario"]["horizon"] for c in grid),
    }
