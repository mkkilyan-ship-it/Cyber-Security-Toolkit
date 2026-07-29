"""Vérification d'intégrité de fichiers par empreintes cryptographiques."""
import argparse
import hashlib

ALGORITHMS = ("md5", "sha1", "sha256", "sha512")

HASH_LENGTHS = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}


def compute_hashes(data: bytes) -> dict:
    return {algo: hashlib.new(algo, data).hexdigest() for algo in ALGORITHMS}


def verify_hash(data: bytes, expected_hash: str) -> dict:
    expected_hash = expected_hash.strip().lower()
    algo = HASH_LENGTHS.get(len(expected_hash))
    if algo is None:
        raise ValueError("Longueur d'empreinte non reconnue (md5, sha1, sha256, sha512).")

    computed = hashlib.new(algo, data).hexdigest()
    return {"algorithm": algo, "computed_hash": computed, "match": computed == expected_hash}


def main():
    parser = argparse.ArgumentParser(description="Vérification d'intégrité de fichiers.")
    parser.add_argument("file")
    parser.add_argument("-e", "--expected", help="Empreinte attendue à comparer")
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    if args.expected:
        result = verify_hash(data, args.expected)
        status = "CORRESPOND" if result["match"] else "NE CORRESPOND PAS"
        print(f"[{result['algorithm']}] {result['computed_hash']} -> {status}")
    else:
        for algo, digest in compute_hashes(data).items():
            print(f"{algo}: {digest}")


if __name__ == "__main__":
    main()
