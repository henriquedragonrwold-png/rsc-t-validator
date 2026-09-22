import numpy as np

def rsc_t_index(spatial, temporal, weights=None):
    values = np.array([spatial, temporal], dtype=float)
    if weights is None:
        weights = np.array([0.5, 0.5])
    mask = np.isfinite(values)
    if not mask.any():
        return np.nan
    w = np.asarray(weights, dtype=float)[mask]
    v = values[mask]
    w = w / w.sum()
    return float(np.sum(w * v))
