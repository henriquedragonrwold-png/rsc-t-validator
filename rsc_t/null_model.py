import numpy as np

def shuffle_positions(df, seed=42):
    out = df.copy()
    rng = np.random.default_rng(seed)
    xy = out[["x", "y"]].to_numpy().copy()
    rng.shuffle(xy, axis=0)
    out[["x", "y"]] = xy
    return out
