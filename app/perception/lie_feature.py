from __future__ import annotations
import numpy as np


def lie_state(alpha: float, beta: float, zoom: float) -> np.ndarray:
    """Project camera physical state to a compact tangent-space vector."""
    return np.asarray([alpha, beta, np.log(max(float(zoom), 1e-6))], dtype=np.float32)


def lie_distance(a, b) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return float(np.linalg.norm(a - b))


def lie_bracket(a, b) -> np.ndarray:
    """A compact 3D Lie-bracket surrogate used for feature relation strength."""
    a = np.asarray(a, dtype=np.float32).reshape(-1)
    b = np.asarray(b, dtype=np.float32).reshape(-1)
    if a.size != 3 or b.size != 3:
        raise ValueError("Lie state must have three components")
    return np.cross(a, b).astype(np.float32)
