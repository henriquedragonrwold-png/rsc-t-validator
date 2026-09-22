import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="RSC-T Validator v1", page_icon="🧬", layout="wide")
st.title("🧬 RSC-T Validator v1")
st.caption("Protótipo experimental para análise de organização espaço-temporal. Não é ferramenta diagnóstica.")

st.sidebar.header("Experimento")
mode = st.sidebar.radio("Fonte dos dados", ["Demo sintético", "CSV"])
seed = st.sidebar.number_input("Seed", 0, 99999, 42)
n_cells = st.sidebar.slider("Células (demo)", 20, 500, 120)
n_time = st.sidebar.slider("Pontos temporais (demo)", 3, 30, 10)

def make_demo(seed, n_cells, n_time):
    rng = np.random.default_rng(seed)
    rows = []
    for cond, coherence in [("Controle", 0.15), ("Regeneração_demo", 0.75)]:
        x0 = rng.normal(0, 1, n_cells)
        y0 = rng.normal(0, 1, n_cells)
        for t in range(n_time):
            phase = t / max(n_time - 1, 1)
            for i in range(n_cells):
                if coherence > 0.5:
                    x = (1 - phase) * x0[i] + 0.20 * np.sin(2*np.pi*phase) + rng.normal(0, 0.08)
                    y = (1 - phase) * y0[i] + 0.20 * np.cos(2*np.pi*phase) + rng.normal(0, 0.08)
                else:
                    x = x0[i] + rng.normal(0, 0.18)
                    y = y0[i] + rng.normal(0, 0.18)
                rows.append([cond, i, t, x, y])
    return pd.DataFrame(rows, columns=["condition","cell_id","time","x","y"])

if mode == "Demo sintético":
    df = make_demo(seed, n_cells, n_time)
else:
    up = st.sidebar.file_uploader("CSV com condition, cell_id, time, x, y", type=["csv"])
    if up is None:
        st.info("Envie um CSV ou use o modo Demo sintético.")
        st.stop()
    df = pd.read_csv(up)

required = {"condition","cell_id","time","x","y"}
missing = required - set(df.columns)
if missing:
    st.error("Colunas ausentes: " + ", ".join(sorted(missing)))
    st.stop()

df = df.dropna(subset=list(required)).copy()
for col in ["time", "x", "y"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["time","x","y"])

def metrics(g):
    g = g.sort_values(["cell_id","time"])
    spatial_scores = []
    for _, gt in g.groupby("time"):
        pts = gt[["x","y"]].to_numpy()
        if len(pts) > 2:
            d = np.sqrt(((pts[:, None, :] - pts[None, :, :])**2).sum(axis=2))
            d[d == 0] = np.inf
            nn = d.min(axis=1)
            spatial_scores.append(1 / (1 + np.mean(nn)))

    directions = []
    for _, gc in g.groupby("cell_id"):
        gc = gc.sort_values("time")
        if len(gc) >= 2:
            dx = np.diff(gc["x"].to_numpy())
            dy = np.diff(gc["y"].to_numpy())
            norm = np.sqrt(dx*dx + dy*dy) + 1e-9
            directions.append(np.c_[dx/norm, dy/norm])

    temporal = float(np.clip(np.linalg.norm(np.vstack(directions).mean(axis=0)), 0, 1)) if directions else np.nan
    spatial = float(np.mean(spatial_scores)) if spatial_scores else np.nan
    return spatial, temporal

results = []
for cond, g in df.groupby("condition"):
    s, t = metrics(g)
    results.append([cond, s, t, np.nanmean([s, t])])

res = pd.DataFrame(results, columns=["condition","spatial","temporal","rsc_t_index"])

st.subheader("Resultado exploratório")
st.dataframe(res.style.format({"spatial":"{:.3f}","temporal":"{:.3f}","rsc_t_index":"{:.3f}"}), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.metric("Condições", len(res))
with c2:
    st.metric("Observações", len(df))

st.subheader("Trajetórias celulares")
fig, ax = plt.subplots(figsize=(8, 5))
for cond, g in df.groupby("condition"):
    for cid in g["cell_id"].drop_duplicates().head(25):
        z = g[g.cell_id == cid].sort_values("time")
        ax.plot(z.x, z.y, alpha=0.35, label=cond if cid == g["cell_id"].drop_duplicates().iloc[0] else None)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Trajetórias celulares")
if len(res) <= 8:
    ax.legend()
st.pyplot(fig, clear_figure=True)

st.subheader("Interpretação")
st.warning(
    "O índice exibido é um protótipo exploratório, não um biomarcador validado. "
    "A versão científica deve incluir controles experimentais, modelos nulos, "
    "permutação/bootstrap, replicatas independentes e validação externa."
)

report = {
    "software": "RSC-T Validator v1",
    "status": "prototype",
    "n_rows": int(len(df)),
    "conditions": res.to_dict(orient="records"),
    "note": "Não interpretar como diagnóstico ou prova da hipótese RSC."
}
st.download_button(
    "Baixar relatório JSON",
    json.dumps(report, indent=2, ensure_ascii=False),
    file_name="rsc_t_report.json",
    mime="application/json"
)
