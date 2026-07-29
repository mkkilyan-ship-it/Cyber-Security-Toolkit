"""Chiffrement / déchiffrement de fichiers par mot de passe (AES via Fernet)."""
import argparse
import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
KDF_ITERATIONS = 390_000


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_data(data: bytes, password: str) -> bytes:
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(data)
    return salt + token


def decrypt_data(data: bytes, password: str) -> bytes:
    if len(data) < SALT_SIZE:
        raise ValueError("Fichier chiffré invalide ou corrompu.")

    salt, token = data[:SALT_SIZE], data[SALT_SIZE:]
    key = _derive_key(password, salt)
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken:
        raise ValueError("Mot de passe incorrect ou fichier corrompu.")


def main():
    parser = argparse.ArgumentParser(description="Chiffrement / déchiffrement de fichiers.")
    parser.add_argument("action", choices=["encrypt", "decrypt"])
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("-p", "--password", required=True)
    args = parser.parse_args()

    with open(args.input_file, "rb") as f:
        data = f.read()

    if args.action == "encrypt":
        result = encrypt_data(data, args.password)
    else:
        result = decrypt_data(data, args.password)

    with open(args.output_file, "wb") as f:
        f.write(result)

    print(f"{args.action} terminé -> {args.output_file}")


if __name__ == "__main__":
    main()
