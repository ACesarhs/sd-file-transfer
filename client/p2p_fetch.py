"""No P2P que baixa um arquivo via openfilenet."""
import openfilenet as ofn
import sys
import time

TOKEN = "sd-experiment-2026"


def fetch(timeout=60):
    ofn.token = TOKEN
    start = time.perf_counter()

    files = []
    while time.perf_counter() - start < timeout:
        files = ofn.list_files()
        if files:
            break
        time.sleep(0.5)

    if not files:
        print(f"[p2p-fetch] timeout: nenhum arquivo encontrado em {timeout}s")
        return None

    target = files[0]
    peer_id = target.get("peer_id")
    path = target.get("path")
    size = target.get("size")
    print(f"[p2p-fetch] encontrado: peer={peer_id} path={path} size={size}")

    t0 = time.perf_counter()
    data = ofn.get_file(peer_id, path)
    elapsed = time.perf_counter() - t0

    nbytes = len(data) if data is not None else 0
    mb = nbytes / (1024 * 1024)
    rate = mb / elapsed if elapsed > 0 else 0
    print(f"[p2p-fetch] recebido {mb:.2f} MB em {elapsed:.3f}s ({rate:.2f} MB/s)")
    return elapsed, nbytes


def main():
    fetch()


if __name__ == "__main__":
    main()
