# RSC-T Validator v1

Protótipo computacional para explorar a hipótese de organização espaço-temporal em sistemas biológicos.

## O que a V1 faz

- gera dados celulares sintéticos para demonstração;
- aceita CSV com `condition, cell_id, time, x, y`;
- calcula métricas exploratórias espaciais e temporais;
- visualiza trajetórias celulares;
- gera um índice exploratório RSC-T;
- exporta um relatório JSON.

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Formato do CSV

```text
condition,cell_id,time,x,y
Controle,1,0,10.2,8.4
Controle,1,1,10.5,8.7
Regeneracao,1,0,9.8,7.9
```

## Interpretação científica

O RSC-T Validator não assume que a hipótese RSC esteja correta. A finalidade da ferramenta é testar se os dados apresentam organização espaço-temporal mensurável e se essa organização excede estruturas esperadas por modelos nulos.

Os índices da V1 são exploratórios e não são biomarcadores validados, diagnóstico ou comprovação da hipótese.

## Roadmap

- V1.1: estados celulares e eventos de divisão/morte;
- V1.2: integração WNT, FGF, BMP, SHH e HAND2;
- V1.3: dados espaciais/transcriptômicos;
- V2: modelos de aprendizado de máquina e inferência causal.
