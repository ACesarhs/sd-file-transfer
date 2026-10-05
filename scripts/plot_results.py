"""Gera os graficos do relatorio a partir de results/resultados.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "results" / "resultados.csv"
OUT_DIR = ROOT / "results"

ARCHS = ["cs_single", "cs_threaded", "cs_pool", "p2p"]
LABELS = {
    "cs_single": "CS Single",
    "cs_threaded": "CS Threaded",
    "cs_pool": "CS Pool (N=4)",
    "p2p": "P2P",
}
COLORS = {
    "cs_single": "#d62728",
    "cs_threaded": "#1f77b4",
    "cs_pool": "#2ca02c",
    "p2p": "#ff7f0e",
}


def load_data():
    """Le o CSV. Tolerante a BOM e nomes de coluna."""
    print(f"Lendo: {CSV_PATH}")
    print(f"Existe: {CSV_PATH.exists()}")
    data = {}
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        print(f"Colunas detectadas: {reader.fieldnames}")
        for row in reader:
            # normaliza nomes de coluna (remove BOM e espacos)
            row = {(k or "").strip().lstrip("\ufeff"): (v or "").strip()
                   for k, v in row.items()}
            medio = row.get("medio_s", "")
            if not medio:
                continue
            try:
                key = (row["arquitetura"],
                       int(row["tamanho_mb"]),
                       int(row["n_clientes"]))
                data[key] = {
                    "min": float(row["min_s"]),
                    "avg": float(medio),
                    "max": float(row["max_s"]),
                    "n": int(row["n_amostras"]),
                }
            except (KeyError, ValueError) as e:
                print(f"  ignorando linha: {row} -> {e}")
    return data


def _safe_log_scale(ax):
    """Ativa escala log so se todos os valores plotados forem > 0."""
    ymin, ymax = ax.get_ylim()
    if ymin > 0:
        ax.set_yscale("log")
    else:
        ax.set_yscale("linear")


def fig1_bars(data):
    sizes = [5, 50, 500]
    clients = [1, 2, 5, 10]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    for ax, size in zip(axes, sizes):
        x = np.arange(len(clients))
        width = 0.2
        any_bar = False
        for i, arch in enumerate(ARCHS):
            ys = []
            for n in clients:
                d = data.get((arch, size, n))
                ys.append(d["avg"] if d else 0)
            if any(y > 0 for y in ys):
                any_bar = True
            offset = (i - 1.5) * width
            bars = ax.bar(x + offset, ys, width, label=LABELS[arch],
                          color=COLORS[arch], edgecolor="black", linewidth=0.5)
            for bar, y in zip(bars, ys):
                if y > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, y * 1.05,
                            f"{y:.1f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels([str(c) for c in clients])
        ax.set_xlabel("Numero de clientes")
        ax.set_title(f"Arquivo {size}MB")
        if any_bar:
            ax.set_yscale("log")
        ax.grid(axis="y", linestyle="--", alpha=0.3)

    axes[0].set_ylabel("Tempo medio (s)")
    axes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle("Fig 1 - Tempo medio de transferencia por arquitetura", fontsize=13)
    fig.tight_layout()
    out = OUT_DIR / "fig1_bars.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"OK: {out}")


def fig2_scaling(data):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
    sizes = [5, 50, 500]
    clients = [1, 2, 5, 10]

    for ax, size in zip(axes, sizes):
        any_line = False
        for arch in ARCHS:
            xs, ys = [], []
            for n in clients:
                d = data.get((arch, size, n))
                if d and d["avg"] > 0:
                    xs.append(n)
                    ys.append(d["avg"])
            if ys:
                any_line = True
                ax.plot(xs, ys, marker="o", label=LABELS[arch],
                        color=COLORS[arch], linewidth=2, markersize=8)
        ax.set_xscale("log")
        if any_line:
            ax.set_yscale("log")
        ax.set_xticks(clients)
        ax.set_xticklabels([str(c) for c in clients])
        ax.set_xlabel("Numero de clientes")
        ax.set_title(f"Arquivo {size}MB")
        ax.grid(True, which="both", linestyle="--", alpha=0.3)

    axes[0].set_ylabel("Tempo medio (s)")
    axes[0].legend(fontsize=9)
    fig.suptitle("Fig 2 - Escalabilidade: tempo medio vs numero de clientes", fontsize=13)
    fig.tight_layout()
    out = OUT_DIR / "fig2_scaling.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"OK: {out}")


def fig3_heatmap(data):
    sizes = [5, 50, 500]
    matrix = np.full((len(ARCHS), len(sizes)), np.nan)
    for i, arch in enumerate(ARCHS):
        for j, size in enumerate(sizes):
            vals = [data[(arch, size, n)]["avg"]
                    for n in [1, 2, 5, 10]
                    if (arch, size, n) in data and data[(arch, size, n)]["avg"] > 0]
            if vals:
                matrix[i, j] = np.mean(vals)

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto",
                   norm=matplotlib.colors.LogNorm(vmin=0.5, vmax=300))
    ax.set_xticks(np.arange(len(sizes)))
    ax.set_yticks(np.arange(len(ARCHS)))
    ax.set_xticklabels([f"{s}MB" for s in sizes])
    ax.set_yticklabels([LABELS[a] for a in ARCHS])
    ax.set_xlabel("Tamanho do arquivo")
    ax.set_title("Fig 3 - Tempo medio (s) por arquitetura e tamanho\n"
                 "(media entre 1, 2, 5 e 10 clientes)")
    for i in range(len(ARCHS)):
        for j in range(len(sizes)):
            v = matrix[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        color="black" if v < 50 else "white", fontsize=11)
    fig.colorbar(im, ax=ax, label="Tempo (s, escala log)")
    fig.tight_layout()
    out = OUT_DIR / "fig3_heatmap.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"OK: {out}")


def main():
    data = load_data()
    print(f"Carregados {len(data)} pontos de dados")
    if not data:
        print("ERRO: nenhum dado carregado. Verifique o CSV.")
        return
    fig1_bars(data)
    fig2_scaling(data)
    fig3_heatmap(data)
    print("Todos os graficos gerados em results/")


if __name__ == "__main__":
    main()
