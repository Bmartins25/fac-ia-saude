# FAC-IA Saúde — versão com apresentação institucional no estilo Veritas

## O que foi replicado
- Hierarquia visual: hero institucional, destaques, cartões, CTAs e perfil do pesquisador.
- Navegação superior real nas sete páginas públicas.
- Acesso à plataforma via botão funcional, com retorno ao site institucional.
- CSS responsivo para telas menores.
- Identidade acadêmica FAC-IA Saúde/UFMG/PPGIT, sem reproduzir a marca Veritas.

## O que foi preservado
- Critérios do arquivo `criteria.json`, SQLite, lógica de avaliação, indicadores e relatórios.
- Fotografia e arquivos de identidade acadêmica.

## Publicação
Envie `app.py`, `criteria.json`, `requirements.txt`, `.streamlit/` e `assets/` ao repositório GitHub, preservando os caminhos. O arquivo principal é `app.py`. Não publique dados reais de pacientes.

## Atenção
O banco SQLite no Streamlit Community Cloud não garante persistência durável; use armazenamento persistente externo para operação real. Teste a interface em celular e desktop após publicar.
