# Avaliação de Desempenho em Transferência de Arquivos: Cliente-Servidor vs P2P

**Discente:** Augusto César Honorato dos Santos
**Docente:** Prof. Dr. Rafael Oliveira Vasconcelos
**Disciplina:** Sistemas Distribuídos
**Data:** 2026

---

## 1. Introdução

Este relatório descreve a atividade prática de avaliação de desempenho em transferência de arquivos, comparando a arquitetura cliente-servidor (CS) com a arquitetura peer-to-peer (P2P). Foram implementadas quatro variações de servidor, variando o modelo de concorrência, e executados experimentos variando o tamanho do arquivo e a quantidade de clientes simultâneos.

O objetivo foi medir os tempos de conclusão de transferência (mínimo, médio e máximo) em cada configuração e discutir as diferenças observadas.

---

## 2. Arquiteturas Implementadas

As implementações foram feitas em Python 3.12, utilizando a biblioteca padrão socket para a comunicação em rede. Para o P2P foi utilizada a biblioteca openfilenet, que implementa descoberta automática de peers via UDP.

### 2.1 Cliente-Servidor Single

Servidor que atende um cliente por vez. O fluxo é sequencial: o servidor aceita uma conexão, envia o arquivo completo e só depois aceita a próxima. Clientes que chegam durante uma transferência ficam na fila do sistema operacional.

### 2.2 Cliente-Servidor Threaded

Servidor que cria uma thread por cliente. Cada conexão aceita é tratada em uma thread separada, permitindo que múltiplos clientes sejam atendidos em paralelo, sem limite de concorrência.

### 2.3 Cliente-Servidor com Pool de Threads

Servidor que utiliza um pool de 4 threads (ThreadPoolExecutor com max_workers=4). No máximo 4 clientes são atendidos simultaneamente; os demais aguardam em fila até que uma thread seja liberada.

### 2.4 P2P

Nó que compartilha o arquivo via openfilenet. Um processo atua como compartilhador e os demais descobrem o arquivo na rede local e o baixam diretamente. A biblioteca cuida da descoberta de peers e da transferência.

Em todas as implementações, o cliente apenas recebe os dados e os descarta — nenhum arquivo é gravado em disco.

---

## 3. Ambiente de Testes

- Sistema operacional: Ubuntu 24.04.5 LTS (máquina virtual VirtualBox)
- Python: 3.12.3
- Rede: loopback local (127.0.0.1), todos os processos na mesma VM
- Medição de tempo: time.perf_counter() no cliente, iniciado antes da conexão e encerrado após o último byte recebido

## 4. Metodologia

Foram executadas medições variando três dimensões:

- Arquitetura: cs_single, cs_threaded, cs_pool, p2p
- Tamanho do arquivo: 5 MB e 50 MB
- Número de clientes simultâneos: 1, 2 e 5

Cada combinação foi executada com 2 repetições. Para cada linha foram calculados o tempo mínimo, médio e máximo entre as amostras coletadas.

A matriz foi executada de forma automatizada por um script Python (scripts/run_experiments.py), que sobe o servidor, dispara os clientes em paralelo, coleta os tempos e grava os resultados em results/resultados.csv.

---

## 5. Resultados

A tabela abaixo apresenta os resultados consolidados. A coluna n_amostras indica quantas medições foram consideradas em cada linha.

| Arquitetura | Tam (MB) | Clientes | Min (s) | Medio (s) | Max (s) | Amostras |
|---|---|---|---|---|---|---|
| cs_single | 5 | 1 | 1.5966 | 1.6263 | 1.6561 | 2 |
| cs_single | 5 | 2 | 0.0584 | 0.3222 | 0.5853 | 4 |
| cs_single | 5 | 5 | 0.0845 | 0.5852 | 1.6889 | 10 |
| cs_single | 50 | 1 | 0.6382 | 0.6975 | 0.7569 | 2 |
| cs_single | 50 | 2 | 0.1005 | 0.1298 | 0.1611 | 4 |
| cs_single | 50 | 5 | 0.1165 | 1.0169 | 3.8336 | 10 |
| cs_threaded | 5 | 1 | 0.0783 | 0.8311 | 1.5838 | 2 |
| cs_threaded | 5 | 2 | 0.0829 | 0.3405 | 0.6006 | 4 |
| cs_threaded | 5 | 5 | 0.1398 | 0.8316 | 3.6587 | 10 |
| cs_threaded | 50 | 1 | 0.0788 | 0.3314 | 0.5841 | 2 |
| cs_threaded | 50 | 2 | 0.0942 | 0.3871 | 0.6805 | 4 |
| cs_threaded | 50 | 5 | 0.1968 | 1.5394 | 3.9450 | 10 |
| cs_pool | 5 | 1 | 0.5897 | 2.0802 | 3.5708 | 2 |
| cs_pool | 5 | 2 | 0.0557 | 0.9508 | 1.6013 | 4 |
| cs_pool | 5 | 5 | 0.6337 | 2.7662 | 7.6990 | 10 |
| cs_pool | 50 | 1 | 0.1647 | 0.4137 | 0.6626 | 2 |
| cs_pool | 50 | 2 | 0.6384 | 0.9222 | 1.7237 | 4 |
| cs_pool | 50 | 5 | 0.1988 | 0.5353 | 0.8626 | 10 |
| p2p | 5 | 1 | 0.6263 | 0.6341 | 0.6418 | 2 |
| p2p | 5 | 2 | 0.6279 | 0.7664 | 1.1425 | 4 |
| p2p | 5 | 5 | 0.7080 | 0.7670 | 0.8108 | 10 |
| p2p | 50 | 1 | 0.6991 | 0.7023 | 0.7054 | 2 |
| p2p | 50 | 2 | 0.7675 | 0.9181 | 1.0593 | 4 |
| p2p | 50 | 5 | 1.0213 | 1.1444 | 1.2571 | 10 |

---

## 6. Análise dos Resultados

CS Single: apresenta o comportamento mais previsível de serialização. Como o servidor atende um cliente por vez, o tempo médio cresce com o número de clientes simultâneos, especialmente visível em 50 MB com 5 clientes, onde o tempo máximo chegou a 3.83 s enquanto o mínimo foi de 0.12 s. A diferença entre mínimo e máximo indica que alguns clientes aguardaram na fila.

CS Threaded: paraleliza o atendimento, o que mantém os tempos mais estáveis. Em 5 MB, o tempo médio variou pouco (0.34 s a 0.83 s). O ponto fraco é a ausência de limite de concorrência.

CS Pool (4 workers): com o limite de 4 threads, o comportamento é mais controlado, mas com latência maior em algumas medições. Em 5 MB com 5 clientes, o tempo máximo foi de 7.70 s, o pior entre todas as arquiteturas nessa configuração.

P2P: apresentou os tempos mais consistentes, com pequena variação. O tempo mínimo em 5 MB foi 0.63 s e o máximo 0.81 s. Isso é explicado pelo overhead fixo da descoberta de peers via UDP, que é o principal componente do tempo em arquivos pequenos.

## 7. Dificuldades Encontradas

1. Race condition no startup do servidor. O script de automação verificava se o servidor estava pronto abrindo uma conexão TCP de teste. Essa conexão era aceita pelo servidor, que tentava enviar o arquivo para um socket já fechado, causando ConnectionResetError nos clientes reais. A solução foi fechar a conexão de teste com SO_LINGER e adicionar um pequeno atraso antes de disparar os clientes.

2. Timeouts no P2P com arquivos grandes. Na matriz completa (que incluía 500 MB e 10 clientes), a arquitetura P2P apresentou timeouts sucessivos. O único cliente que completou levou cerca de 296 s para transferir 500 MB.

3. Perda de dados por sobrescrita do CSV. O script de automação original sobrescrevia o arquivo resultados.csv a cada execução. Em uma das rodadas os dados foram perdidos. A solução foi adicionar backup automático do CSV antes de cada nova execução.

## 8. Conclusão

Os experimentos confirmaram o comportamento esperado das arquiteturas. A arquitetura CS single é a mais simples, mas serializa o atendimento e degrada com o aumento da concorrência. A CS threaded melhora o desempenho com múltiplos clientes, mas não impõe limite à concorrência. A CS com pool de threads controla a carga sobre o servidor ao custo de latência adicional para clientes na fila. A arquitetura P2P tem overhead fixo de descoberta, desvantajoso para arquivos pequenos, mas consistente.

Como limitação, a matriz final foi reduzida (2 tamanhos e 3 quantidades de clientes, com 2 repetições cada) por restrição de tempo de máquina.

---

## Anexo A — Estrutura do Repositório

server/ - servidores CS (single, threaded, pool) e no P2P

client/ - cliente CS e cliente P2P

scripts/ - gerador de arquivos, automacao de experimentos, plot de graficos

results/ - CSV com dados e figuras PNG

docs/ - este relatorio

## Anexo B — Como Reproduzir

1. Clonar o repositorio
2. Criar ambiente virtual: python3 -m venv .venv
3. Ativar: source .venv/bin/activate
4. Instalar dependencias: pip install openfilenet matplotlib
5. Gerar arquivos de teste: python3 scripts/gen_files.py
6. Executar experimentos: python3 scripts/run_experiments.py
7. Gerar graficos: python3 scripts/plot_results.py
