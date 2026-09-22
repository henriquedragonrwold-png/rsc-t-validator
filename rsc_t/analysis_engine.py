"""Testes executáveis para dados tabulares RSC-T."""
import numpy as np
import pandas as pd

def _spatial_score(g):
    vals=[]
    for _,t in g.groupby("time"):
        p=t[["x","y"]].to_numpy(float)
        if len(p)<3: continue
        d=np.sqrt(((p[:,None,:]-p[None,:,:])**2).sum(2)); np.fill_diagonal(d,np.inf)
        vals.append(1/(1+np.mean(d.min(1))))
    return float(np.mean(vals)) if vals else np.nan

def _temporal_score(g):
    dirs=[]
    for _,c in g.groupby("cell_id"):
        c=c.sort_values("time")
        if len(c)<2: continue
        dx=np.diff(c.x.to_numpy(float)); dy=np.diff(c.y.to_numpy(float))
        n=np.hypot(dx,dy)
        ok=n>0
        if ok.any(): dirs.append(np.c_[dx[ok]/n[ok],dy[ok]/n[ok]])
    return float(np.linalg.norm(np.vstack(dirs).mean(0))) if dirs else np.nan

def _state_score(g):
    if "cell_state" not in g.columns: return np.nan
    seqs=[]
    for _,c in g.groupby("cell_id"):
        c=c.sort_values("time")
        states=c.cell_state.dropna().astype(str).tolist()
        if len(states)>=2: seqs.append(len(set(states))/len(states))
    return float(np.mean(seqs)) if seqs else np.nan

def _molecular_score(g):
    if not {"expression","x","y","time"}.issubset(g.columns): return np.nan
    x=pd.to_numeric(g.expression,errors="coerce")
    spatial=g.groupby("time").apply(lambda q: _spatial_score(q), include_groups=False)
    if len(spatial)<2 or x.std()==0: return np.nan
    # associação temporal simples entre média molecular e organização espacial
    means=g.assign(_e=x).groupby("time")._e.mean()
    z=pd.concat([means.rename("m"),spatial.rename("s")],axis=1).dropna()
    return float(z.m.corr(z.s)) if len(z)>=3 else np.nan

def observed(df, family):
    rows=[]
    for cond,g in df.groupby("condition", dropna=False):
        if family=="spatial": v=_spatial_score(g)
        elif family=="temporal": v=_temporal_score(g)
        elif family=="state": v=_state_score(g)
        elif family=="molecular": v=_molecular_score(g)
        else:
            v=np.nan
        rows.append({"condition":str(cond),"observed":v})
    return pd.DataFrame(rows)

def null_distribution(df, family, n=500, seed=42):
    rng=np.random.default_rng(seed)
    base=df.copy()
    vals=[]
    if family in ("spatial","temporal"):
        for _ in range(n):
            z=base.copy()
            if family=="spatial":
                # quebra a relação espacial entre células mantendo marginais
                z["x"]=rng.permutation(z["x"].to_numpy())
                z["y"]=rng.permutation(z["y"].to_numpy())
            else:
                # embaralha posição ao longo do tempo, mantendo cada célula
                z["time"]=z.groupby("cell_id")["time"].transform(lambda s:rng.permutation(s.to_numpy()))
            ob=observed(z,family)["observed"].dropna()
            if len(ob): vals.append(float(ob.mean()))
    elif family=="state":
        if "cell_state" not in base.columns: return np.array([])
        for _ in range(n):
            z=base.copy(); z["cell_state"]=rng.permutation(z.cell_state.to_numpy())
            ob=observed(z,family)["observed"].dropna()
            if len(ob): vals.append(float(ob.mean()))
    elif family=="molecular":
        if "expression" not in base.columns: return np.array([])
        for _ in range(n):
            z=base.copy(); z["expression"]=rng.permutation(z.expression.to_numpy())
            ob=observed(z,family)["observed"].dropna()
            if len(ob): vals.append(float(ob.mean()))
    return np.asarray(vals,float)

def empirical_p(observed_value, null):
    null=np.asarray(null,float); null=null[np.isfinite(null)]
    if not len(null) or not np.isfinite(observed_value): return np.nan
    return float((1+(null>=observed_value).sum())/(len(null)+1))

def summarize(df, family, permutations=500, seed=42):
    obs=observed(df,family)
    val=float(obs.observed.mean()) if obs.observed.notna().any() else np.nan
    null=null_distribution(df,family,permutations,seed)
    return {
        "family":family,"observed_mean":val,
        "null_mean":float(null.mean()) if len(null) else np.nan,
        "null_sd":float(null.std(ddof=1)) if len(null)>1 else np.nan,
        "empirical_p_greater":empirical_p(val,null),
        "n_null":int(len(null)),
        "by_condition":obs.to_dict("records")
    }
