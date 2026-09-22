def report_markdown(rep):
    s=f"# RSC-T Validation Report\n\n**Artigo:** {rep['article']}  \n**Linhas:** {rep['n_rows']}  \n**Permutações:** {rep['n_permutations']}\n\n## Testes\n"
    for x in rep['tests']: s+=f"- **{x['condition']} / {x['hypothesis']} / {x['metric']}**: observado={x['observed']:.4f}; nulo={x['null_mean']:.4f}; p={x['empirical_p']:.4g}; z={x['effect_z']:.3f}\n"
    s+='\n## Comparações\n'
    for x in rep['comparisons']: s+=f"- {x['baseline']} vs {x['condition']} — {x['metric']}: diferença={x['difference']:.4f}\n"
    return s+'\n> Resultados exigem replicatas independentes, controles e validação externa. Um p-valor não demonstra causalidade.'