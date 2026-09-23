import json
import pandas as pd
import streamlit as st
from rsc_t.engine import validate_dataframe, generate_report
from rsc_t.article_schema import ARTICLE_TEMPLATES
from rsc_t.article_parser import extract_article_text, detect_hypotheses
from rsc_t.report import report_markdown

st.set_page_config(page_title="RSC-T Validator", page_icon="🧬", layout="wide")
st.title("🧬 RSC-T Validator")
st.caption("Artigo → hipótese → previsão → teste → modelo nulo → evidência.")

article_names = list(ARTICLE_TEMPLATES)
with st.sidebar:
    st.header("1 · Artigos")
    article_files = st.file_uploader(
        "Envie seus artigos (.docx/.pdf)",
        type=["docx", "pdf"],
        accept_multiple_files=True,
        help="Você pode enviar os 4 artigos de uma vez. Cada artigo continua sendo analisado separadamente."
    )

    if article_files:
        if len(article_files) > 4:
            st.error("Envie no máximo 4 artigos por vez.")
            article_files = article_files[:4]
        st.success(f"{len(article_files)}/4 artigo(s) carregado(s)")
        active_name = st.selectbox(
            "Artigo em análise",
            [f.name for f in article_files],
            key="active_article_file"
        )
        article_file = next(f for f in article_files if f.name == active_name)
        article = st.selectbox("Tipo do artigo", article_names, key="active_article_type")
    else:
        article = st.selectbox("Escolha o artigo", article_names)
        article_file = None
        st.caption("Sem arquivo enviado: o aplicativo usa o modelo estruturado do artigo selecionado.")

    st.header("2 · Dados")
    data_file = st.file_uploader(
        "Dados experimentais",
        type=["csv", "xlsx"],
        help="Arquivo separado do artigo. Mínimo: condition, cell_id, time, x, y."
    )
    n_perm = st.slider("Permutações", 100, 5000, 1000, 100)
    execute = st.button("▶ Executar validação", type="primary", use_container_width=True)

article_text = ""
if article_file:
    try:
        article_text = extract_article_text(article_file.name, article_file.getvalue())
    except Exception as e:
        st.error(f"Não foi possível ler o artigo: {e}")

tabs = st.tabs(["📄 Artigo", "🧪 Hipóteses", "📊 Dados", "📈 Testes", "📑 Relatório"])

with tabs[0]:
    if article_file:
        st.success(f"Documento carregado: {article_file.name}")
        st.caption(f"Tipo selecionado: {article}")
        st.text_area("Texto extraído", article_text[:15000], height=350)
    else:
        st.subheader(article)
        st.write(ARTICLE_TEMPLATES[article]["description"])

with tabs[1]:
    hs = detect_hypotheses(article_text) if article_text else ARTICLE_TEMPLATES[article]["hypotheses"]
    st.subheader(f"Hipóteses disponíveis ({len(hs)})")
    for h in hs:
        with st.expander(f'{h["id"]} · {h["name"]}'):
            st.write("Hipótese:", h["hypothesis"])
            st.write("Previsão:", h["prediction"])
            st.write("Variáveis:", ", ".join(h["variables"]))
            st.write("Teste:", h["test"])
            st.write("Modelo nulo:", h["null_model"])

df = None
with tabs[2]:
    if data_file:
        df = pd.read_excel(data_file) if data_file.name.lower().endswith(".xlsx") else pd.read_csv(data_file)
        st.success(f"{len(df):,} linhas × {len(df.columns)} colunas")
        st.dataframe(df.head(100), use_container_width=True)
        st.caption("Mínimo executável: condition, cell_id, time, x, y. Opcional: cell_state, marker, expression.")
    else:
        st.info("Envie um CSV/XLSX com os dados experimentais.")

result = None
if execute:
    if df is None:
        st.error("Envie os dados experimentais antes de executar.")
    else:
        try:
            result = validate_dataframe(df, n_perm=n_perm)
        except Exception as e:
            st.error(str(e))

with tabs[3]:
    if result:
        st.dataframe(result["tests"], use_container_width=True)
        st.subheader("Comparações")
        st.dataframe(result["comparisons"], use_container_width=True)
    else:
        st.info("Execute a validação para obter os testes.")

with tabs[4]:
    if result:
        rep = generate_report(result, article)
        md = report_markdown(rep)
        st.markdown(md)
        st.download_button(
            "Baixar JSON",
            json.dumps(rep, ensure_ascii=False, indent=2),
            file_name="rsc_t_report.json",
            mime="application/json"
        )
        st.download_button(
            "Baixar Markdown",
            md,
            file_name="rsc_t_report.md",
            mime="text/markdown"
        )
    else:
        st.info("O relatório aparece após a execução.")

st.divider()
st.warning(
    "Resultado positivo = organização observada em relação ao modelo nulo escolhido. "
    "Não é, isoladamente, prova da hipótese RSC, causalidade, diagnóstico ou eficácia terapêutica."
)
