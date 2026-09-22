import numpy as np

def empirical_pvalue(observed, null_values):
    v=np.asarray(null_values,dtype=float); v=v[np.isfinite(v)]
    if len(v)==0 or not np.isfinite(observed): return np.nan
    return float((1+np.sum(v>=observed))/(len(v)+1))

def effect_z(observed, null_values):
    v=np.asarray(null_values,dtype=float); v=v[np.isfinite(v)]
    if len(v)<2: return np.nan
    sd=np.std(v,ddof=1)
    return float((observed-v.mean())/sd) if sd>0 else np.nan

def summarize_test(observed,null_values):
    return {"observed":float(observed),"null_mean":float(np.mean(null_values)),"null_sd":float(np.std(null_values,ddof=1)),"empirical_p_greater":empirical_pvalue(observed,null_values),"effect_z":effect_z(observed,null_values)}
