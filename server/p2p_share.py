"""No P2P que compartilha um arquivo via openfilenet."""
import openfilenet as ofn
import sys
import time

TOKEN = "sd-experiment-2026"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/test_5MB.bin"
    ofn.token = TOKEN

    shared = ofn.share_files(path)
    print(f"[p2p-share] token='{TOKEN}' compartilhando: {path}")
    print(f"[p2p-share] objeto retornado: {shared}")
    print(f"[p2p-share] aguardando peers... (Ctrl+C para sair)")

    try:
        while True:
            time.sleep(5)
            files = ofn.list_files()
            if files:
                print(f"[p2p-share] arquivos visiveis agora: "
                      f"{[getattr(f, 'name', str(f)) for f in files]}")
    except KeyboardInterrupt:
        print("\n[p2p-share] encerrando")


if __name__ == "__main__":
    main()
