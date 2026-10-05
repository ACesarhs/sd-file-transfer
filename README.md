# 📡 Avaliação de Desempenho em Transferência de Arquivos
### Cliente-Servidor vs P2P

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420?style=flat-square&logo=ubuntu&logoColor=white)
![UFS](https://img.shields.io/badge/UFS-Sistemas%20Distribu%C3%ADdos-blue?style=flat-square)

Trabalho prático da disciplina de **Sistemas Distribuídos** da Universidade Federal de Sergipe (UFS), com o objetivo de comparar o desempenho de arquiteturas **cliente-servidor** e **peer-to-peer** na transferência de arquivos, variando o tamanho do arquivo e a quantidade de clientes simultâneos.

---

## 👤 Autor

| | |
|---|---|
| **Discente** | Augusto César Honorato dos Santos |
| **Docente** | Prof. Dr. Rafael Oliveira Vasconcelos |
| **Disciplina** | Sistemas Distribuídos |
| **Instituição** | Universidade Federal de Sergipe (UFS) |

---

## 🎯 Objetivo

Implementar e comparar quatro variações de servidor sob diferentes condições de carga:

1. **Cliente-Servidor Single** — atende 1 cliente por vez
2. **Cliente-Servidor Threaded** — atende todos os clientes simultaneamente (1 thread por cliente)
3. **Cliente-Servidor Pool** — atende no máximo N clientes por vez (pool de 4 threads)
4. **P2P** — nó compartilhador baseado na biblioteca `openfilenet`

---

## 📂 Estrutura do Repositório

- **server/** — implementações de servidor
  - cs_single.py — CS: 1 cliente por vez
  - cs_threaded.py — CS: thread por cliente
  - cs_pool.py — CS: pool de 4 threads
  - p2p_share.py — nó P2P compartilhador
- **client/** — clientes de download
  - download.py — cliente CS (descarta o arquivo)
  - p2p_fetch.py — cliente P2P
- **scripts/** — automação
  - gen_files.py — gera arquivos de teste (5/50/500 MB)
  - run_experiments.py — executa a matriz completa de experimentos
  - plot_results.py — gera os gráficos a partir do CSV
- **results/** — resultados coletados
  - resultados.csv — dados brutos dos experimentos
  - fig1_bars.png, fig2_scaling.png, fig3_heatmap.png — gráficos
- **docs/** — relatório final (relatorio.md e relatorio.docx)

---

## ⚙️ Como Reproduzir

### Pré-requisitos

- Python 3.12 ou superior
- Virtualenv (recomendado)

### Passo a passo

1. Clonar o repositório:
   `git clone https://github.com/ACesarhs/sd-file-transfer.git`

2. Entrar na pasta e criar ambiente virtual:
   - `cd sd-file-transfer`
   - `python3 -m venv .venv`
   - `source .venv/bin/activate` (Linux/macOS) ou `.venv\Scripts\activate` (Windows)

3. Instalar dependências:
   `pip install openfilenet matplotlib`

4. Gerar arquivos de teste:
   `python3 scripts/gen_files.py`

5. Executar a matriz de experimentos:
   `python3 scripts/run_experiments.py`

6. Gerar os gráficos:
   `python3 scripts/plot_results.py`

> Os arquivos de teste são gerados em `data/` e **não são versionados** (ver `.gitignore`).
> Os resultados são gravados incrementalmente em `results/resultados.csv`.

---

## 🧪 Metodologia

Os experimentos variaram três dimensões:

| Dimensão | Valores testados |
|---|---|
| **Arquitetura** | `cs_single`, `cs_threaded`, `cs_pool`, `p2p` |
| **Tamanho do arquivo** | 5 MB, 50 MB, 500 MB |
| **Clientes simultâneos** | 1, 2, 5, 10 |
| **Repetições** | 3 por combinação |

### Ambiente

- **SO:** Ubuntu 24.04.5 LTS (máquina virtual VirtualBox)
- **Python:** 3.12.3
- **Rede:** loopback local (`127.0.0.1`)
- **Medição:** `time.perf_counter()` no cliente

---

## 📊 Resultados

### Tempo médio de transferência (s)

| Arquitetura | 5 MB / 1 | 5 MB / 5 | 5 MB / 10 | 500 MB / 1 | 500 MB / 10 |
|---|---:|---:|---:|---:|---:|
| `cs_single`   | 1.18 | 4.08 | 7.23 | 1.25 | 6.57 |
| `cs_threaded` | 0.50 | 1.36 | 1.29 | 2.29 | 13.07 |
| `cs_pool`     | 0.71 | 1.47 | 2.16 | 1.67 | 7.55 |
| `p2p`         | 0.77 | 1.32 | 2.28 | 8.98 | ⚠️ timeout |

> ⚠️ O P2P com **500 MB e 10 clientes** apresentou timeout — apenas 1 cliente completou a transferência (296 s). Isso indica que o nó compartilhador se torna gargalo quando há muitos clientes simultâneos.

### Visualizações

| Gráfico | Descrição |
|---|---|
| `fig1_bars.png` | Tempo médio por arquitetura, agrupado por tamanho e nº de clientes |
| `fig2_scaling.png` | Escalabilidade — tempo médio vs nº de clientes |
| `fig3_heatmap.png` | Heatmap arquitetura × tamanho de arquivo |

As figuras estão disponíveis em `results/`.

---

## 🔍 Principais Observações

- **CS Single** serializa o atendimento — o tempo cresce linearmente com o número de clientes.
- **CS Threaded** paraleliza sem limite — bom desempenho, mas risco de contenção com muitas threads.
- **CS Pool (N=4)** impõe um teto de concorrência — mais estável, mas com latência adicional em fila.
- **P2P** tem overhead fixo de descoberta (~0.6–0.7 s) — vantajoso para arquivos grandes, mas não escala bem quando um único nó concentra toda a carga.

---

## 🐛 Dificuldades Encontradas

1. **Race condition no startup do servidor** — a verificação de prontidão via TCP abria conexões fantasma que o servidor tentava atender. Solução: fechar com `SO_LINGER` (RST) e adicionar atraso antes de disparar clientes.

2. **Timeouts no P2P com arquivos grandes** — `openfilenet` não lida bem com 500 MB × 10 clientes simultâneos.

3. **Perda de dados por sobrescrita do CSV** — o script original recriava o arquivo a cada execução. Solução: backup automático antes de sobrescrever.

4. **Compatibilidade com a API do `openfilenet` 0.1.1** — `get_file()` exige dois argumentos posicionais (`peer_id`, `path`), diferente da documentação consultada.

---

## 📄 Relatório

O relatório completo está disponível em:

- `docs/relatorio.md` — versão Markdown
- `docs/relatorio.docx` — versão editável

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.12** — linguagem principal
- **socket** — comunicação TCP entre cliente e servidor
- **threading** / **concurrent.futures** — concorrência nos servidores CS
- **openfilenet 0.1.1** — biblioteca P2P com descoberta UDP
- **matplotlib** — geração dos gráficos
- **pandoc** — conversão do relatório para `.docx`
