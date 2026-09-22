import json
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
from rsc_t.engine import validate_dataframe, generate_report
from rsc_t.article_schema import ARTICLE_TEMPLATES, core_rsc_hypotheses
from rsc_t.article_parser import extract_article_text, detect_hypotheses
from rsc_t.report import report_markdown

st.set_page_config(page_title="RSC-T Validator", page_icon="🧬", layout="wide")
st.title("🧬 RSC-T Validator")
st.caption("Plataforma experimental: artigo → hipótese → previsão → teste computacional → modelo nulo → evidência.")

with st.sidebar:
    st.header("1 · Artigo")
    article = st.selectbox("Escolha o artigo", list(ARTICLE_TEMPLATES)+["Meu artigo (.docx/.pdf)"])
    uploaded_article = None
    if article == "Meu artigo (.docx/.pdf)":
        uploaded_article = st.file_uploader("Envie seu artigo", type=["docx","pdf"])
    st.header("2 · Dados")
    data_file = st.file_uploader("CSV ou XLSX experimental", type=["csv","xlsx"])
    n_perm = st.slider("Permutações", 100, 5000, 1000, step=100)
    run = st.button("▶ Executar validação", type="primary", use_container_width=True)

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📄 Artigo","🧪 Hipóteses","📊 Dados","📈 Testes","📑 Relatório"])

article_text=""
if uploaded_article:
    article_text=extract_article_text(uploaded_article.name, uploaded_article.getvalue())
with tab1:
    st.subheader("Documento e escopo")
    if uploaded_article:
        st.success(f"Artigo carregado: {uploaded_article.name}")
        st.text_area("Texto extraído (prévia)", article_text[:12000], height=300)
        detected=detect_hypotheses(article_text)
        st.info(f"Hipóteses/padrões detectados: {len(detected)}")
    else:
        tpl=ARTICLE_TEMPLATES[article]
        st.markdown(f"### {article}")
        st.write(tpl["description"])
        st.write("Este módulo usa hipóteses estruturadas como ponto de partida; não substitui leitura crítica do artigo.")

with tab2:
    st.subheader("Hipóteses testáveis")
    hs=detect_hypotheses(article_text) if article_text else ARTICLE_TEMPLATES[article]["hypotheses"]
    for h in hs:
        with st.expander(f'{h["id"]} · {h["name"]}', expanded=False):
            st.write("**Hipótese:**",h["hypothesis"])
            st.write("**Previsão:**",h["prediction"])
            st.write("**Variáveis:**",", ".join(h["variables"]))
            st.write("**Teste:**",h["test"])
            st.write("**Modelo nulo:**",h["null_model"])

df=None
with tab3:
    st.subheader("Dados experimentais")
    if data_file:
        df=pd.read_excel(data_file) if data_file.name.lower().endswith(".xlsx") else pd.read_csv(data_file)
        st.success(f"{len(df):,} linhas × {len(df.columns)} colunas")
        st.dataframe(df.head(100),use_container_width=True)
        st.caption("Colunas espaciais mínimas: condition, cell_id, time, x, y. Estados/marcadores são opcionais.")
    else:
        st.info("Envie um CSV/XLSX ou use o conjunto demonstrativo.")
        if st.button("Carregar demo sintético"):
            rng=np.random.default_rng(42); rows=[]
            for cond,coh in [("Controle",0.15),("Regeneracao_demo",0.75)]:
                for cell in range(60):
                    x0,y0=rng.normal(),rng.normal()
                    for t in range(10):
                        p=t/9
                        x=(1-p)*x0+rng.normal(0,.15 if coh<.5 else .07)
                        y=(1-p)*y0+rng.normal(0,.15 if coh<.5 else .07)
                        rows.append([cond,cell,t,x,y])
            df=pd.DataFrame(rows,columns=["condition","cell_id","time","x","y"])
            st.dataframe(df.head(20),use_container_width=True)

result=None
if run:
    if df is None:
        st.error("Envie os dados experimentais primeiro.")
    else:
        result=validate_dataframe(df,n_perm=n_perm)

with tab4:
    st.subheader("Resultado dos testes")
    if result is None:
        st.info("Carregue os dados e clique em Executar validação.")
    else:
        st.dataframe(result["tests"],use_container_width=True)
        st.metric("Testes executados",len(result["tests"]))
        st.metric("Comparações",len(result["comparisons"]))

with tab5:
    st.subheader("Relatório científico")
    if result:
        rep=generate_report(result,article)
        st.markdown(report_markdown(rep))
        st.download_button("Baixar relatório JSON",json.dumps(rep,ensure_ascii=False,indent=2),file_name="rsc_t_validation_report.json",mime="application/json")
        st.download_button("Baixar relatório Markdown",report_markdown(rep),file_name="rsc_t_validation_report.md",mime="text/markdown")
    else:
        st.info("O relatório será gerado após a execução.")

st.divider()
st.warning("Importante: um resultado positivo indica organização observada em relação ao modelo nulo escolhido. Não constitui, isoladamente, prova de RSC, causalidade, diagnóstico ou eficácia terapêutica.")
