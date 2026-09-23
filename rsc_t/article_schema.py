"""Transforma hipóteses RSC em especificações de teste computacional."""

def build_test_spec(article, hypothesis, prediction, variables, null_model, outcome):
    return {"article":article,"hypothesis":hypothesis,"prediction":prediction,"variables":variables,"null_model":null_model,"outcome":outcome}

def core_rsc_hypotheses():
    return [
      {"id":"RSC-H1","name":"Organização espacial","question":"A distribuição celular muda de forma não aleatória durante o processo?","inputs":["x","y","z","time","cell_id"],"tests":["nearest-neighbor","density","spatial-permutation"]},
      {"id":"RSC-H2","name":"Coordenação temporal","question":"As mudanças celulares apresentam coerência temporal?","inputs":["cell_id","time","x","y"],"tests":["directional-coherence","trajectory-permutation"]},
      {"id":"RSC-H3","name":"Transições de estado","question":"Estados celulares aparecem em uma sequência organizada?","inputs":["cell_id","time","cell_state"],"tests":["transition-order","state-shuffle"]},
      {"id":"RSC-H4","name":"Coordenação molecular","question":"Marcadores moleculares apresentam associação espaço-temporal com a reorganização?","inputs":["marker","expression","x","y","time"],"tests":["spatiotemporal-coupling","label-permutation"]},
      {"id":"RSC-H5","name":"Distinção entre processos","question":"A organização observada distingue regeneração de controles ou outros processos?","inputs":["condition","features"],"tests":["effect-size","permutation","cross-validation"]}
    ]

def _template(description):
    tests = core_rsc_hypotheses()
    return {
        "description": description,
        "hypotheses": [
            {
                "id": h["id"],
                "name": h["name"],
                "hypothesis": h["question"],
                "prediction": "Definir previamente um padrão observável e mensurável nos dados.",
                "variables": h["inputs"],
                "test": ", ".join(h["tests"]),
                "null_model": "Permutação apropriada aos dados"
            }
            for h in tests
        ]
    }

ARTICLE_TEMPLATES = {
    "RSC Regenerativa": _template(
        "Validação computacional da hipótese de regeneração como organização espaço-temporal da matéria viva."
    ),
    "RSC Oncológica": _template(
        "Investigação da organização/reprogramação espaço-temporal em contexto tumoral, separada do artigo RSC Neuro."
    ),
    "RSC Neuro": _template(
        "Investigação da organização espaço-temporal neural, regeneração, plasticidade e comportamento."
    ),
    "RSC Animal": _template(
        "Aplicação comparativa da hipótese RSC em modelos animais de regeneração."
    ),
}
