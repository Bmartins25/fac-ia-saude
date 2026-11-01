# FAC-IA Saúde — MVP aprimorado

Aplicação Streamlit para avaliação de conformidade baseada na dissertação final PPGIT/UFMG (2026).

## Execução

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Recursos
- 45 critérios originais do Apêndice A, incluindo requisito, pilares, evidências esperadas e verificação.
- Cadastro de sistemas e avaliações, SQLite local criado na primeira execução.
- Estados AV, NA, NV; notas 0 a 4 somente para AV.
- Conformidade e cobertura calculadas separadamente, por domínio e globalmente.
- Evidências, justificativas, responsáveis, datas e recomendações.
- Exportação CSV, JSON e TXT.

## Limites
Instrumento acadêmico de apoio, não certificação. A análise MIMIC-IV na dissertação é exploratória. O aplicativo não contém dados clínicos, não executa modelos preditivos nem constitui validação empírica integral.


## Interface modernizada
Identidade visual com logos UFMG e PPGIT recortados da imagem fornecida pelo usuário, navegação azul-marinho, painel responsivo, indicadores e desempenho por domínio. As rotinas de avaliação e o banco SQLite foram preservados.
