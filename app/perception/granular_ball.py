from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class GranularBall:
    indices: list
    center: np.ndarray
    radius: float


def aggregate_granular_balls(features, max_radius: float = 1.0):
    """Lightweight granular-ball grouping for physical/visual feature aggregation."""
    x = np.asarray(features, dtype=np.float32)
    if x.size == 0:
        return []
    if x.ndim == 1:
        x = x[None, :]
    center = x.mean(axis=0)
    dist = np.linalg.norm(x - center, axis=1)
    near = np.where(dist <= max_radius)[0].tolist()
    far = np.where(dist > max_radius)[0].tolist()
    balls = []
    if near:
        balls.append(GranularBall(near, x[near].mean(axis=0), float(dist[near].max(initial=0.0))))
    for idx in far:
        balls.append(GranularBall([idx], x[idx], 0.0))
    return balls
