"""Paired bootstrap for E1 (PREREGISTRATION: 10,000 paired samples of question IDs, seed 20261003). OWNER: Jabin."""
from __future__ import annotations

import random
from collections import defaultdict

PREREG_N, PREREG_SEED = 10_000, 20261003


def paired_bootstrap(a: list[float], b: list[float], n: int = PREREG_N, seed: int = PREREG_SEED,
                     groups: list[str] | None = None) -> tuple[float, float, float]:
    """a[i], b[i]: per-question scores (each question's samples already averaged), aligned by question.
    groups: optional group id per question (e.g. intent_id) to resample whole groups (the sensitivity analysis).
    Returns (mean(a) - mean(b), lo, hi) with a percentile 95% interval."""
    if len(a) != len(b) or not a:
        raise ValueError("a and b must be non-empty and aligned")
    rng = random.Random(seed)
    units: list[list[int]]
    if groups:
        by = defaultdict(list)
        for i, g in enumerate(groups):
            by[g].append(i)
        units = list(by.values())
    else:
        units = [[i] for i in range(len(a))]
    diff = sum(a) / len(a) - sum(b) / len(b)
    stats = []
    for _ in range(n):
        idx = [i for _ in units for i in units[rng.randrange(len(units))]]
        stats.append(sum(a[i] for i in idx) / len(idx) - sum(b[i] for i in idx) / len(idx))
    stats.sort()
    return diff, stats[int(0.025 * n)], stats[min(n - 1, int(0.975 * n))]
