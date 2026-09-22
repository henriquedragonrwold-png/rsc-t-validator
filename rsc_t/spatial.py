import numpy as np

def mean_nearest_neighbor(points):
    points = np.asarray(points, dtype=float)
    if len(points) < 2:
        return np.nan
    d = np.sqrt(((points[:, None, :] - points[None, :, :]) ** 2).sum(axis=2))
    d[d == 0] = np.inf
    return float(np.mean(d.min(axis=1)))
