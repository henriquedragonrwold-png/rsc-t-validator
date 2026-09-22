# 🧬 RSC-T Validator

Aplicativo Streamlit para transformar hipóteses dos artigos RSC em testes computacionais reproduzíveis.

## Recursos
- Upload de artigos DOCX/PDF e extração de texto.
- Detecção inicial de hipóteses.
- Templates separados: RSC Regenerativa, RSC Oncológica, RSC Neuro e RSC Animal.
- Upload CSV/XLSX.
- Testes executáveis de organização espacial e coerência temporal.
- Modelos nulos por permutação, p-valor empírico e tamanho de efeito z.
- Comparação entre condições e relatórios JSON/Markdown.

## Publicação
Pronto para Streamlit Community Cloud: conecte este repositório, branch main e arquivo app.py. Após o deploy, o serviço fornece um link público.

## Dados mínimos
condition,cell_id,time,x,y

Opcionalmente: cell_state, marker, expression.

## Limite científico
O software testa organização mensurável contra modelos nulos. Não assume que RSC esteja correta e não transforma resultado estatístico isolado em prova de teoria, causalidade, diagnóstico ou eficácia terapêutica.