# sd-file-transfer

Atividade prática da disciplina de Sistemas Distribuídos — avaliação de desempenho em transferência de arquivos comparando arquitetura cliente-servidor (CS) com P2P.

**Discente:** Augusto César Honorato dos Santos
**Docente:** Prof. Dr. Rafael Oliveira Vasconcelos

## Estrutura

- `server/` — servidores CS (single, threaded, pool) e nó P2P
- `client/` — clientes de download (CS e P2P)
- `scripts/` — gerador de arquivos, automação de experimentos e geração de gráficos
- `results/` — dados coletados (`resultados.csv`) e figuras
- `docs/` — relatório final em Markdown e DOCX

## Como reproduzir

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openfilenet matplotlib

python3 scripts/gen_files.py
python3 scripts/run_experiments.py
python3 scripts/plot_results.py
python3 scripts/plot_results.py
