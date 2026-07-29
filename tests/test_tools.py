import pytest

from tools.file_crypto import decrypt_data, encrypt_data
from tools.integrity_checker import compute_hashes, verify_hash
from tools.password_generator import estimate_strength, generate_password
from tools.port_scanner import scan_range


class TestPasswordGenerator:
    def test_default_length(self):
        assert len(generate_password()) == 16

    def test_custom_length(self):
        assert len(generate_password(length=32)) == 32

    def test_rejects_invalid_length(self):
        with pytest.raises(ValueError):
            generate_password(length=2)

    def test_requires_at_least_one_category(self):
        with pytest.raises(ValueError):
            generate_password(use_upper=False, use_lower=False, use_digits=False, use_symbols=False)

    def test_excludes_ambiguous_characters(self):
        from tools.password_generator import AMBIGUOUS_CHARS
        password = generate_password(length=128, exclude_ambiguous=True)
        assert not any(c in AMBIGUOUS_CHARS for c in password)

    def test_strength_estimation_increases_with_length(self):
        weak = estimate_strength("a" * 6)
        strong = estimate_strength("Aa1!Aa1!Aa1!Aa1!")
        assert strong["entropy_bits"] > weak["entropy_bits"]


class TestPortScanner:
    def test_rejects_invalid_range(self):
        with pytest.raises(ValueError):
            scan_range("127.0.0.1", 100, 1)

    def test_rejects_too_many_ports(self):
        with pytest.raises(ValueError):
            scan_range("127.0.0.1", 1, 70000)

    def test_scan_localhost_returns_structure(self):
        result = scan_range("127.0.0.1", 1, 20, timeout=0.1)
        assert result["host"] == "127.0.0.1"
        assert result["scanned_ports"] == 20
        assert isinstance(result["open_ports"], list)


class TestFileCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        original = b"donnees confidentielles"
        encrypted = encrypt_data(original, "mot-de-passe-solide")
        assert encrypted != original

        decrypted = decrypt_data(encrypted, "mot-de-passe-solide")
        assert decrypted == original

    def test_wrong_password_fails(self):
        encrypted = encrypt_data(b"secret", "correct-password")
        with pytest.raises(ValueError):
            decrypt_data(encrypted, "wrong-password")

    def test_corrupted_data_fails(self):
        with pytest.raises(ValueError):
            decrypt_data(b"trop-court", "password")


class TestIntegrityChecker:
    def test_compute_hashes_keys(self):
        hashes = compute_hashes(b"hello world")
        assert set(hashes.keys()) == {"md5", "sha1", "sha256", "sha512"}

    def test_verify_hash_match(self):
        data = b"integrity check"
        sha256 = compute_hashes(data)["sha256"]
        result = verify_hash(data, sha256)
        assert result["match"] is True
        assert result["algorithm"] == "sha256"

    def test_verify_hash_mismatch(self):
        result = verify_hash(b"data", "0" * 64)
        assert result["match"] is False

    def test_verify_hash_unknown_length(self):
        with pytest.raises(ValueError):
            verify_hash(b"data", "not-a-hash")
