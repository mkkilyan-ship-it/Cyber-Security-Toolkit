"""Générateur de mots de passe cryptographiquement sûrs."""
import argparse
import math
import secrets
import string

AMBIGUOUS_CHARS = "Il1O0"


def _build_charset(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    charset = ""
    if use_lower:
        charset += string.ascii_lowercase
    if use_upper:
        charset += string.ascii_uppercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += "!@#$%^&*()-_=+[]{};:,.<>?/"

    if not charset:
        raise ValueError("Au moins une catégorie de caractères doit être sélectionnée.")

    if exclude_ambiguous:
        charset = "".join(c for c in charset if c not in AMBIGUOUS_CHARS)

    return charset


def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True,
                       use_symbols=True, exclude_ambiguous=False):
    if length < 4 or length > 128:
        raise ValueError("La longueur doit être comprise entre 4 et 128 caractères.")

    charset = _build_charset(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)

    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append("!@#$%^&*()-_=+[]{};:,.<>?/")
    if exclude_ambiguous:
        pools = ["".join(c for c in p if c not in AMBIGUOUS_CHARS) for p in pools]
        pools = [p for p in pools if p]

    required = [secrets.choice(pool) for pool in pools]
    remaining = [secrets.choice(charset) for _ in range(length - len(required))]

    password_chars = required + remaining
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def estimate_strength(password):
    pool_size = 0
    if any(c.islower() for c in password):
        pool_size += 26
    if any(c.isupper() for c in password):
        pool_size += 26
    if any(c.isdigit() for c in password):
        pool_size += 10
    if any(not c.isalnum() for c in password):
        pool_size += 32

    entropy_bits = len(password) * math.log2(pool_size) if pool_size else 0

    if entropy_bits < 40:
        rating = "faible"
    elif entropy_bits < 60:
        rating = "moyen"
    elif entropy_bits < 80:
        rating = "fort"
    else:
        rating = "excellent"

    return {"entropy_bits": round(entropy_bits, 1), "rating": rating}


def main():
    parser = argparse.ArgumentParser(description="Générateur de mots de passe sécurisés.")
    parser.add_argument("-l", "--length", type=int, default=16)
    parser.add_argument("--no-upper", action="store_true")
    parser.add_argument("--no-lower", action="store_true")
    parser.add_argument("--no-digits", action="store_true")
    parser.add_argument("--no-symbols", action="store_true")
    parser.add_argument("--exclude-ambiguous", action="store_true")
    parser.add_argument("-n", "--count", type=int, default=1)
    args = parser.parse_args()

    for _ in range(args.count):
        pwd = generate_password(
            length=args.length,
            use_upper=not args.no_upper,
            use_lower=not args.no_lower,
            use_digits=not args.no_digits,
            use_symbols=not args.no_symbols,
            exclude_ambiguous=args.exclude_ambiguous,
        )
        strength = estimate_strength(pwd)
        print(f"{pwd}  (entropie: {strength['entropy_bits']} bits, {strength['rating']})")


if __name__ == "__main__":
    main()
