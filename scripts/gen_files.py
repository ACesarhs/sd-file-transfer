import os

SIZES_MB = [5, 50, 500]

def main():
    os.makedirs("data", exist_ok=True)
    for mb in SIZES_MB:
        path = f"data/test_{mb}MB.bin"
        if os.path.exists(path):
            print(f"Ja existe: {path}")
            continue
        print(f"Gerando {path} ...")
        with open(path, "wb") as f:
            chunk = b"\x00" * (1024 * 1024)
            for _ in range(mb):
                f.write(chunk)
        print(f"OK: {path}")

if __name__ == "__main__":
    main()
