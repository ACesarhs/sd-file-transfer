import os
import socket
import struct
import sys

HOST = "0.0.0.0"
PORT = 5000
CHUNK = 1024 * 1024  # 1MB


def serve_file(conn, path):
    """Envia tamanho (8 bytes big-endian) + conteudo do arquivo."""
    size = os.path.getsize(path)
    conn.sendall(struct.pack(">Q", size))
    with open(path, "rb") as f:
        while True:
            data = f.read(CHUNK)
            if not data:
                break
            conn.sendall(data)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/test_5MB.bin"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print(f"[single] ouvindo em {HOST}:{PORT} servindo {path}")

    while True:
        conn, addr = sock.accept()
        print(f"[single] cliente {addr} conectado")
        try:
            serve_file(conn, path)
        except Exception as e:
            print(f"[single] erro: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
