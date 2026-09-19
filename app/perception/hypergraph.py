from __future__ import annotations
import numpy as np
from .lie_feature import lie_distance


def build_adaptive_hyperedges(states, threshold: float = 1.5):
    """Build adaptive high-order groups from physical-state similarity."""
    states = np.asarray(states, dtype=np.float32)
    if states.size == 0:
        return []
    if states.ndim == 1:
        states = states[None, :]
    edges = []
    for i in range(len(states)):
        group = [i]
        for j in range(i + 1, len(states)):
            if lie_distance(states[i], states[j]) <= threshold:
                group.append(j)
        if len(group) > 1:
            edges.append(group)
    if not edges and len(states) > 1:
        edges.append(list(range(len(states))))
    return edges
