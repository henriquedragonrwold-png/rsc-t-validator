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
        help="Você pode enviar os 4 artigos de uma vez. Cada artigo continua separado."
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

    st.header("2 · Dados experimentais")
    data_file = st.file_uploader(
        "CSV/XLSX (opcional nesta etapa)",
        type=["csv", "xlsx"],
        help="Os dados são necessários somente para a validação quantitativa."
    )
    n_perm = st.slider("Permutações", 100, 5000, 1000, 100)

    st.header("3 · Executar")
    analyze_article = st.button(
        "🔎 Analisar artigo(s)",
        use_container_width=True
    )
    execute_validation = st.button(
        "▶ Executar validação quantitativa",
        type="primary",
        use_container_width=True
    )

article_records = []
if article_files:
    for f in article_files:
        try:
            txt = extract_article_text(f.name, f.getvalue())
            article_records.append({"file": f, "text": txt})
        except Exception as e:
            article_records.append({"file": f, "text": "", "error": str(e)})
else:
    article_records = [{"file": None, "text": "", "error": None}]

tabs = st.tabs(["📄 Artigos", "🧪 Hipóteses", "📊 Dados", "📈 Validação", "📑 Relatório"])

with tabs[0]:
    if article_files:
        st.subheader(f"Artigos carregados: {len(article_files)}/4")
        for rec in article_records:
            f = rec["file"]
            with st.expander(f"📄 {f.name}", expanded=False):
                if rec.get("error"):
                    st.error(rec["error"])
                else:
                    st.success("Artigo lido com sucesso.")
                    st.text_area(
                        "Texto extraído",
                        rec["text"][:12000],
                        height=250,
                        key=f"preview_{f.name}"
                    )
    else:
        st.subheader(article)
        st.write(ARTICLE_TEMPLATES[article]["description"])
        st.info("Envie um ou até quatro artigos para analisar os seus documentos.")

with tabs[1]:
    if article_files:
        for rec in article_records:
            f = rec["file"]
            if rec.get("error"):
                continue
            selected_type = article if f.name == active_name else article
            hs = detect_hypotheses(rec["text"])
            if not hs:
                hs = ARTICLE_TEMPLATES[selected_type]["hypotheses"]
            with st.expander(f"🧪 {f.name}", expanded=False):
                st.write(f"**Hipóteses encontradas: {len(hs)}**")
                for h in hs:
                    with st.expander(f'{h["id"]} · {h["name"]}'):
                        st.write("Hipótese:", h["hypothesis"])
                        st.write("Previsão:", h["prediction"])
                        st.write("Variáveis:", ", ".join(h["variables"]))
                        st.write("Teste:", h["test"])
                        st.write("Modelo nulo:", h["null_model"])
    else:
        hs = ARTICLE_TEMPLATES[article]["hypotheses"]
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
        try:
            df = pd.read_excel(data_file) if data_file.name.lower().endswith(".xlsx") else pd.read_csv(data_file)
            st.success(f"{len(df):,} linhas × {len(df.columns)} colunas")
            st.dataframe(df.head(100), use_container_width=True)
            st.caption("Mínimo executável: condition, cell_id, time, x, y.")
        except Exception as e:
            st.error(f"Não foi possível ler os dados: {e}")
    else:
        st.info(
            "Nenhum dado experimental foi enviado. "
            "Você pode analisar os artigos sem dados; a validação quantitativa fica disponível quando os dados forem enviados."
        )

result = None
if execute_validation:
    if df is None:
        st.warning(
            "A análise dos artigos pode ser feita sem dados. "
            "Para executar a validação quantitativa, envie um CSV/XLSX experimental."
        )
    else:
        try:
            result = validate_dataframe(df, n_perm=n_perm)
            st.session_state["rsc_result"] = result
        except Exception as e:
            st.error(str(e))

if analyze_article:
    st.session_state["article_analysis_requested"] = True

if result is None:
    result = st.session_state.get("rsc_result")

with tabs[3]:
    if result:
        st.success("Validação quantitativa executada.")
        st.dataframe(result["tests"], use_container_width=True)
        st.subheader("Comparações")
        st.dataframe(result["comparisons"], use_container_width=True)
    elif article_files:
        st.info(
            "Os artigos já podem ser analisados nas abas Artigos e Hipóteses. "
            "A validação quantitativa será feita quando você fornecer dados experimentais."
        )
    else:
        st.info("Envie os artigos para análise ou dados experimentais para validação quantitativa.")

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
    elif article_files:
        st.info(
            "O relatório quantitativo aparecerá após a validação experimental. "
            "A análise estrutural dos artigos está disponível nas abas Artigos e Hipóteses."
        )
    else:
        st.info("Carregue um artigo para começar.")

st.divider()
st.warning(
    "Os resultados quantitativos representam organização observada em relação ao modelo nulo escolhido. "
    "Eles não constituem, isoladamente, prova da hipótese RSC, causalidade, diagnóstico ou eficácia terapêutica."
)
