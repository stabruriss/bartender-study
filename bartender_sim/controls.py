"""Finite fixed-footprint control model and analytic reference quantities.

These controls have stronger assumptions than the dynamic simulator. Their
inequalities must not be used as assertions on the dynamic study results.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class StaticResult:
    clean: frozenset[int]
    repairs: tuple[int, ...]
    contexts: dict[int, frozenset[int]]


def fixed_batch(footprints: tuple[frozenset, ...], initial: frozenset,
                policy: str, repaired: dict[int, frozenset] | None = None) -> StaticResult:
    """Each repaired patch lands immediately, retaining its stated footprint.

    Supplying `repaired` changes the model and is used for counterexamples.
    """
    if policy not in {"clean_first", "in_place"}:
        raise ValueError("unknown fixed-batch policy")
    ground, landed, clean, repairs, contexts = set(initial), set(), set(), [], {}
    held = []
    repaired = repaired or {}

    def repair(i: int) -> None:
        contexts[i] = frozenset(landed)
        repairs.append(i)
        ground.update(repaired.get(i, footprints[i]))
        landed.add(i)

    for i, footprint in enumerate(footprints):
        if ground.intersection(footprint):
            if policy == "clean_first":
                held.append(i)
            else:
                repair(i)
        else:
            clean.add(i)
            landed.add(i)
            ground.update(footprint)
    for i in held:
        repair(i)
    return StaticResult(frozenset(clean), tuple(repairs), contexts)


def interval_overlap_probability(files: int, lines: int, length: int) -> float:
    """Exact p for uniform files and inclusive integer starts of fixed length."""
    if files < 1 or not 1 <= length <= lines:
        raise ValueError("invalid interval geometry")
    m = lines - length + 1
    r = min(length - 1, m - 1)
    ordered_overlapping_starts = m * (2 * r + 1) - r * (r + 1)
    return ordered_overlapping_starts / (files * m * m)


def expected_overlap_pairs_per_window(n: int, rate: float, p: float, tau: float) -> float:
    return math.comb(n, 2) * p * rate**2 * tau**2


def retry_reference(mu: float, stale_window: float) -> dict[str, float]:
    """Fixed-window Poisson renewal reference, not the simulator's mechanism."""
    if min(mu, stale_window) < 0 or not all(map(math.isfinite, (mu, stale_window))):
        raise ValueError("mu and window must be finite and nonnegative")
    return {"retry_probability": -math.expm1(-mu * stale_window),
            "expected_attempts": math.exp(mu * stale_window)}
