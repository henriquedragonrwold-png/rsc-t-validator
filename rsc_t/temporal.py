import numpy as np

def directional_coherence(trajectories):
    vectors = []
    for points in trajectories:
        points = np.asarray(points, dtype=float)
        if len(points) < 2:
            continue
        delta = np.diff(points, axis=0)
        norm = np.linalg.norm(delta, axis=1, keepdims=True) + 1e-9
        vectors.append(delta / norm)
    if not vectors:
        return np.nan
    return float(np.clip(np.linalg.norm(np.vstack(vectors).mean(axis=0)), 0, 1))
