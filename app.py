"""Cyber Security Toolkit - application web Flask.

Regroupe : générateur de mots de passe, scanner de ports, chiffrement de
fichiers et vérification d'intégrité. Destiné à l'apprentissage et aux
tests sur des systèmes que vous possédez ou pour lesquels vous disposez
d'une autorisation explicite.
"""
import io

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import HTTPException

from tools.file_crypto import decrypt_data, encrypt_data
from tools.integrity_checker import compute_hashes, verify_hash
from tools.password_generator import estimate_strength, generate_password
from tools.port_scanner import scan_range

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 Mo


@app.errorhandler(ValueError)
def handle_value_error(err):
    return jsonify({"error": str(err)}), 400


@app.errorhandler(HTTPException)
def handle_http_error(err):
    return jsonify({"error": err.description}), err.code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/password", methods=["POST"])
def api_password():
    payload = request.get_json(force=True, silent=True) or {}

    password = generate_password(
        length=int(payload.get("length", 16)),
        use_upper=bool(payload.get("upper", True)),
        use_lower=bool(payload.get("lower", True)),
        use_digits=bool(payload.get("digits", True)),
        use_symbols=bool(payload.get("symbols", True)),
        exclude_ambiguous=bool(payload.get("exclude_ambiguous", False)),
    )
    strength = estimate_strength(password)
    return jsonify({"password": password, **strength})


@app.route("/api/scan", methods=["POST"])
def api_scan():
    payload = request.get_json(force=True, silent=True) or {}

    host = (payload.get("host") or "").strip()
    if not host:
        raise ValueError("L'hôte est requis.")

    start_port = int(payload.get("start_port", 1))
    end_port = int(payload.get("end_port", 1024))

    result = scan_range(host, start_port, end_port)
    return jsonify(result)


@app.route("/api/hash", methods=["POST"])
def api_hash():
    uploaded = request.files.get("file")
    if uploaded is None or uploaded.filename == "":
        raise ValueError("Aucun fichier fourni.")

    data = uploaded.read()
    hashes = compute_hashes(data)
    return jsonify({"filename": uploaded.filename, "size": len(data), "hashes": hashes})


@app.route("/api/verify", methods=["POST"])
def api_verify():
    uploaded = request.files.get("file")
    expected_hash = (request.form.get("expected_hash") or "").strip()

    if uploaded is None or uploaded.filename == "":
        raise ValueError("Aucun fichier fourni.")
    if not expected_hash:
        raise ValueError("L'empreinte attendue est requise.")

    data = uploaded.read()
    result = verify_hash(data, expected_hash)
    return jsonify({"filename": uploaded.filename, **result})


@app.route("/api/encrypt", methods=["POST"])
def api_encrypt():
    uploaded = request.files.get("file")
    password = request.form.get("password") or ""

    if uploaded is None or uploaded.filename == "":
        raise ValueError("Aucun fichier fourni.")
    if not password:
        raise ValueError("Un mot de passe est requis.")

    encrypted = encrypt_data(uploaded.read(), password)
    return send_file(
        io.BytesIO(encrypted),
        as_attachment=True,
        download_name=f"{uploaded.filename}.enc",
        mimetype="application/octet-stream",
    )


@app.route("/api/decrypt", methods=["POST"])
def api_decrypt():
    uploaded = request.files.get("file")
    password = request.form.get("password") or ""

    if uploaded is None or uploaded.filename == "":
        raise ValueError("Aucun fichier fourni.")
    if not password:
        raise ValueError("Un mot de passe est requis.")

    decrypted = decrypt_data(uploaded.read(), password)
    output_name = uploaded.filename
    if output_name.endswith(".enc"):
        output_name = output_name[: -len(".enc")]
    else:
        output_name = f"{output_name}.dec"

    return send_file(
        io.BytesIO(decrypted),
        as_attachment=True,
        download_name=output_name,
        mimetype="application/octet-stream",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
