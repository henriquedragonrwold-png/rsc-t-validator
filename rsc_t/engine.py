import numpy as np
import pandas as pd
from .article_tests import empirical_pvalue,effect_z
REQUIRED={'condition','cell_id','time','x','y'}
def spatial(g):
    vals=[]
    for _,t in g.groupby('time'):
        p=t[['x','y']].to_numpy(float)
        if len(p)<3: continue
        d=np.sqrt(((p[:,None,:]-p[None,:,:])**2).sum(2)); np.fill_diagonal(d,np.inf)
        vals.append(1/(1+float(np.mean(d.min(1)))))
    return float(np.mean(vals)) if vals else np.nan
def temporal(g):
    ds=[]
    for _,c in g.groupby('cell_id'):
        c=c.sort_values('time')
        if len(c)<2: continue
        dx=np.diff(c.x.to_numpy(float)); dy=np.diff(c.y.to_numpy(float)); n=np.hypot(dx,dy); k=n>1e-12
        if k.any(): ds.append(np.c_[dx[k]/n[k],dy[k]/n[k]])
    return float(np.linalg.norm(np.vstack(ds).mean(0))) if ds else np.nan
def perm_spatial(g,r):
    z=g.copy(); z['x']=r.permutation(z.x.to_numpy()); z['y']=r.permutation(z.y.to_numpy()); return spatial(z)
def perm_temporal(g,r):
    z=g.copy()
    for _,idx in z.groupby('cell_id').groups.items():
        ids=np.asarray(list(idx)); z.loc[ids,'x']=r.permutation(z.loc[ids,'x'].to_numpy()); z.loc[ids,'y']=r.permutation(z.loc[ids,'y'].to_numpy())
    return temporal(z)
def summarize(o,n):
    n=np.asarray(n,float); n=n[np.isfinite(n)]
    return {'observed':float(o),'null_mean':float(n.mean()) if len(n) else np.nan,'null_sd':float(n.std(ddof=1)) if len(n)>1 else np.nan,'empirical_p':empirical_pvalue(o,n),'effect_z':effect_z(o,n)}
def validate_dataframe(df,n_perm=1000,seed=42):
    missing=REQUIRED-set(df.columns)
    if missing: raise ValueError('Colunas ausentes: '+', '.join(sorted(missing)))
    d=df.dropna(subset=list(REQUIRED)).copy()
    for c in ['time','x','y']: d[c]=pd.to_numeric(d[c],errors='coerce')
    d=d.dropna(subset=['time','x','y']); r=np.random.default_rng(seed); rows=[]
    for cond,g in d.groupby('condition'):
        rows.append({'condition':cond,'hypothesis':'RSC-H1','metric':'spatial_organization',**summarize(spatial(g),[perm_spatial(g,r) for _ in range(n_perm)])})
        rows.append({'condition':cond,'hypothesis':'RSC-H2','metric':'temporal_coherence',**summarize(temporal(g),[perm_temporal(g,r) for _ in range(n_perm)])})
    tests=pd.DataFrame(rows); comps=[]; cs=list(d.condition.unique())
    if len(cs)>1:
        base=cs[0]
        for c in cs[1:]:
            for m in ['spatial_organization','temporal_coherence']:
                a=tests[(tests.condition==base)&(tests.metric==m)].iloc[0]; b=tests[(tests.condition==c)&(tests.metric==m)].iloc[0]
                comps.append({'baseline':base,'condition':c,'metric':m,'difference':float(b.observed-a.observed)})
    return {'tests':tests,'comparisons':pd.DataFrame(comps),'n_rows':len(d),'n_perm':n_perm}
def generate_report(result,article):
    return {'software':'RSC-T Validator','version':'2.0','article':article,'n_rows':result['n_rows'],'n_permutations':result['n_perm'],'tests':result['tests'].to_dict('records'),'comparisons':result['comparisons'].to_dict('records')}