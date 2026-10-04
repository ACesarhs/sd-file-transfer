"""Roda a matriz de experimentos CS e P2P, gera results/resultados.csv."""
import csv
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)
CSV_PATH = RESULTS_DIR / "resultados.csv"

SIZES = [5, 50, 500]
CLIENTS = [1, 2, 5, 10]
REPS = 3

ARCHS = {
    "cs_single":   {"script": "server/cs_single.py",   "port": 5000, "kind": "cs"},
    "cs_threaded": {"script": "server/cs_threaded.py", "port": 5001, "kind": "cs"},
    "cs_pool":     {"script": "server/cs_pool.py",     "port": 5002, "kind": "cs"},
    "p2p":         {"script": "server/p2p_share.py",   "port": None, "kind": "p2p"},
}

CLIENT_CS = "client/download.py"
CLIENT_P2P = "client/p2p_fetch.py"


def wait_port(host, port, timeout=10):
    """Espera a porta TCP aceitar conexao (servidor pronto)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def start_server(arch, size):
    cfg = ARCHS[arch]
    path = f"data/test_{size}MB.bin"
    cmd = [sys.executable, cfg["script"], path]
    log = open(ROOT / f"results/server_{arch}_{size}MB.log", "w")
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    if cfg["port"] is not None:
        if not wait_port("127.0.0.1", cfg["port"]):
            proc.kill()
            log.close()
            raise RuntimeError(f"Servidor {arch} nao subiu na porta {cfg['port']}")
        # Deixa o servidor processar a conexao-fantasma do wait_port
        time.sleep(1.0)
    else:
        # P2P: espera o share ficar visivel
        time.sleep(4)
    return proc, log


def run_client(arch, size, results, idx):
    """Roda um cliente e guarda o tempo (em segundos) em results[idx]."""
    cfg = ARCHS[arch]
    if cfg["kind"] == "cs":
        cmd = [sys.executable, CLIENT_CS, "127.0.0.1", str(cfg["port"])]
    else:
        cmd = [sys.executable, CLIENT_P2P]

    t0 = time.perf_counter()
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"    [cliente {idx}] TIMEOUT", flush=True)
        results[idx] = None
        return
    elapsed = time.perf_counter() - t0
    if out.returncode != 0:
        print(f"    [cliente {idx}] FALHOU rc={out.returncode}", flush=True)
        print(f"      stdout: {out.stdout.strip()}", flush=True)
        print(f"      stderr: {out.stderr.strip()}", flush=True)
        results[idx] = None
        return
    results[idx] = elapsed


def run_combination(arch, size, n_clients):
    """Roda N clientes em paralelo, REPEATS vezes, retorna lista de tempos."""
    all_times = []
    for rep in range(REPS):
        proc, log = None, None
        try:
            proc, log = start_server(arch, size)
            time.sleep(0.5)

            results = [None] * n_clients
            threads = []
            for i in range(n_clients):
                t = threading.Thread(target=run_client, args=(arch, size, results, i))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

            times = [r for r in results if r is not None]
            all_times.extend(times)
            print(f"  rep {rep+1}/{REPS}: {len(times)}/{n_clients} OK "
                  f"tempos={[f'{t:.3f}' for t in times]}", flush=True)
        finally:
            if proc is not None:
                proc.kill()
                proc.wait()
            if log is not None:
                log.close()
            time.sleep(0.5)

    return all_times


def write_row(arch, size, n_clients, times):
    if not times:
        row = [arch, size, n_clients, "", "", "", 0]
    else:
        row = [arch, size, n_clients,
               f"{min(times):.4f}",
               f"{sum(times)/len(times):.4f}",
               f"{max(times):.4f}",
               len(times)]
    with open(CSV_PATH, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow(row)


def main():
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["arquitetura", "tamanho_mb", "n_clientes",
                        "min_s", "medio_s", "max_s", "n_amostras"])

    total = len(ARCHS) * len(SIZES) * len(CLIENTS)
    done = 0
    for arch in ARCHS:
        for size in SIZES:
            for n in CLIENTS:
                done += 1
                print(f"\n[{done}/{total}] {arch} | {size}MB | {n} cliente(s) "
                      f"| {REPS} reps", flush=True)
                try:
                    times = run_combination(arch, size, n)
                    write_row(arch, size, n, times)
                except Exception as e:
                    print(f"  ERRO: {e}", flush=True)
                    write_row(arch, size, n, [])
    print("\n== EXPERIMENTOS CONCLUIDOS ==")
    print(f"CSV: {CSV_PATH}")


if __name__ == "__main__":
    main()
