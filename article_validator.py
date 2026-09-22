import json
import pandas as pd
import streamlit as st
from rsc_t.article_schema import core_rsc_hypotheses, build_test_spec

st.set_page_config(page_title="RSC-T Article Validator",page_icon="📄",layout="wide")
st.title("📄 RSC-T Article Validator")
st.caption("Hipótese → previsão observável → variáveis → modelo nulo → teste.")
article=st.sidebar.selectbox("Artigo",["RSC Regenerativa","RSC Oncológica","RSC Neuro","RSC Animal","Personalizado"])
hypotheses=core_rsc_hypotheses()
if article=="Personalizado":
    hypothesis=st.text_area("Hipótese","Digite a hipótese testável.")
    prediction=st.text_area("Previsão observável","Descreva o padrão que deveria aparecer nos dados.")
else:
    h=st.selectbox("Hipótese central",hypotheses,format_func=lambda x:f'{x["id"]} — {x["name"]}')
    hypothesis=h["question"]
    prediction=st.text_area("Previsão observável","Defina o padrão mensurável esperado se a hipótese estiver correta.")
variables=st.text_input("Variáveis disponíveis","condition, cell_id, time, x, y")
null_model=st.selectbox("Modelo nulo",["Permutação espacial","Permutação temporal","Permutação de identidade celular","Bootstrap"])
outcome=st.selectbox("Desfecho",["organização espacial","coerência temporal","transição de estado","acoplamento molecular","diferença entre condições"])
spec=build_test_spec(article,hypothesis,prediction,variables,null_model,outcome)
st.subheader("Especificação do teste")
st.json(spec)
st.subheader("Dados experimentais")
up=st.file_uploader("CSV experimental",type=["csv"])
if up:
    df=pd.read_csv(up); st.write(f"{len(df)} observações"); st.dataframe(df.head(20),use_container_width=True)
    missing=[c.strip() for c in variables.split(",") if c.strip() and c.strip() not in df.columns]
    if missing: st.error("Variáveis ausentes: "+", ".join(missing))
    else: st.success("Estrutura mínima encontrada. A próxima camada pode executar o teste correspondente.")
st.info("Um resultado positivo não constitui, isoladamente, prova da hipótese RSC. O relatório deve incluir efeito, incerteza e comparação com o modelo nulo.")
st.download_button("Baixar especificação JSON",json.dumps(spec,indent=2,ensure_ascii=False),file_name="rsc_t_test_spec.json",mime="application/json")
