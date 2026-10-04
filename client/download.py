import socket
import struct
import sys
import time

CHUNK = 1024 * 1024
MAX_RETRIES = 5


def _try_download(host, port):
    with socket.create_connection((host, port), timeout=15) as s:
        s.sendall(b"G")
        raw = b""
        while len(raw) < 8:
            raw += s.recv(8 - len(raw))
        size = struct.unpack(">Q", raw)[0]

        received = 0
        while received < size:
            data = s.recv(CHUNK)
            if not data:
                break
            received += len(data)
    return size


def download(host, port):
    last_err = None
    delay = 0.5
    for attempt in range(1, MAX_RETRIES + 1):
        start = time.perf_counter()
        try:
            size = _try_download(host, port)
            elapsed = time.perf_counter() - start
            return elapsed, size
        except (ConnectionResetError, ConnectionError, OSError) as e:
            last_err = e
            time.sleep(delay)
            delay *= 2  # backoff exponencial
    raise last_err


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    elapsed, size = download(host, port)
    mb = size / (1024 * 1024)
    print(f"Recebido {mb:.2f} MB em {elapsed:.3f}s ({mb/elapsed:.2f} MB/s)")


if __name__ == "__main__":
    main()
