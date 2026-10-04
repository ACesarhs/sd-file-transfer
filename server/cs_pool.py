import os
import socket
import struct
import sys
from concurrent.futures import ThreadPoolExecutor

HOST = "0.0.0.0"
PORT = 5002
CHUNK = 1024 * 1024
MAX_WORKERS = 4  # N clientes simultaneos


def serve_file(conn, path):
    size = os.path.getsize(path)
    conn.sendall(struct.pack(">Q", size))
    with open(path, "rb") as f:
        while True:
            data = f.read(CHUNK)
            if not data:
                break
            conn.sendall(data)


def handle(conn, addr, path):
    print(f"[pool] atendendo {addr}")
    try:
        serve_file(conn, path)
    except Exception as e:
        print(f"[pool] erro com {addr}: {e}")
    finally:
        conn.close()
        print(f"[pool] finalizado {addr}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/test_5MB.bin"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(64)
    print(f"[pool] ouvindo em {HOST}:{PORT} servindo {path} (max_workers={MAX_WORKERS})")

    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    try:
        while True:
            conn, addr = sock.accept()
            executor.submit(handle, conn, addr, path)
    finally:
        executor.shutdown(wait=False)


if __name__ == "__main__":
    main()
