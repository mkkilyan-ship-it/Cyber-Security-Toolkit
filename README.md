# Cyber Security Toolkit

![CI](https://github.com/mkkilyan-ship-it/Cyber-Security-Toolkit/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

Application web regroupant plusieurs outils de cybersécurité destinés à
**l'apprentissage** et aux **tests sur des systèmes autorisés**. Interface
HTML/CSS/JavaScript servie par un backend Python (Flask).

> ⚠️ **Avertissement** : ces outils (en particulier le scanner de ports) ne
> doivent être utilisés que sur des systèmes vous appartenant ou pour
> lesquels vous disposez d'une autorisation explicite. Toute utilisation non
> autorisée peut être illégale.

## Fonctionnalités

| Outil | Description |
|---|---|
| 🔑 **Générateur de mots de passe** | Génère des mots de passe cryptographiquement sûrs (module `secrets`), avec estimation d'entropie et de robustesse. |
| 🔍 **Scanner de ports** | Scan TCP « connect » multithread sur une plage de ports, identification des services courants. |
| 🔒 **Chiffrement de fichiers** | Chiffrement/déchiffrement symétrique (AES via `Fernet`) à partir d'un mot de passe (dérivation de clé PBKDF2-HMAC-SHA256). |
| ✅ **Vérification d'intégrité** | Calcul d'empreintes MD5 / SHA-1 / SHA-256 / SHA-512 et comparaison à une empreinte de référence. |

Chaque outil est aussi utilisable en ligne de commande via les modules du
dossier `tools/`.

## Structure du projet

```
Cyber-Security-Toolkit/
├── app.py                     # Application Flask (routes API + page web)
├── tools/                     # Logique métier, réutilisable en CLI
│   ├── password_generator.py
│   ├── port_scanner.py
│   ├── file_crypto.py
│   └── integrity_checker.py
├── templates/index.html       # Interface web
├── static/
│   ├── css/style.css
│   └── js/                    # Un script par outil + navigation par onglets
├── tests/                     # Tests unitaires (pytest)
├── requirements.txt
└── .github/workflows/ci.yml   # Intégration continue
```

## Installation

```bash
git clone https://github.com/mkkilyan-ship-it/Cyber-Security-Toolkit.git
cd Cyber-Security-Toolkit
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application web

```bash
python app.py
```

Puis ouvrez [http://localhost:5000](http://localhost:5000) dans votre navigateur.

## Utilisation en ligne de commande

```bash
# Générateur de mots de passe
python -m tools.password_generator -l 20 -n 3

# Scanner de ports (usage autorisé uniquement)
python -m tools.port_scanner 127.0.0.1 -p 1-1024

# Chiffrement / déchiffrement de fichiers
python -m tools.file_crypto encrypt document.pdf document.pdf.enc -p "mot-de-passe"
python -m tools.file_crypto decrypt document.pdf.enc document.pdf -p "mot-de-passe"

# Vérification d'intégrité
python -m tools.integrity_checker document.pdf
python -m tools.integrity_checker document.pdf -e <empreinte_attendue>
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Stack technique

- **Backend** : Python, Flask, `cryptography`
- **Frontend** : HTML5, CSS3, JavaScript (vanilla, sans framework)
- **Tests** : pytest
- **CI** : GitHub Actions

## Licence

Distribué sous licence [MIT](LICENSE).
