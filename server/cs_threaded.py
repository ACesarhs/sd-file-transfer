import os
import socket
import struct
import sys
import threading

HOST = "0.0.0.0"
PORT = 5001
CHUNK = 1024 * 1024


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
    print(f"[threaded] cliente {addr} conectado (thread={threading.current_thread().name})")
    try:
        serve_file(conn, path)
    except Exception as e:
        print(f"[threaded] erro com {addr}: {e}")
    finally:
        conn.close()
        print(f"[threaded] cliente {addr} desconectado")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/test_5MB.bin"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(64)
    print(f"[threaded] ouvindo em {HOST}:{PORT} servindo {path}")

    while True:
        conn, addr = sock.accept()
        t = threading.Thread(target=handle, args=(conn, addr, path), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
