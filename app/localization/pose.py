from __future__ import annotations
import numpy as np
from app.perception.lie_feature import lie_state


def estimate_pose(bbox, image_size, workspace=(30.0, 20.0)):
    x, y, w, h = bbox
    iw, ih = image_size
    cx, cy = x + w/2, y + h/2
    return (cx / max(iw,1) * workspace[0], cy / max(ih,1) * workspace[1])


def lie_physical_state(alpha, beta, zoom):
    return lie_state(alpha, beta, zoom).tolist()
