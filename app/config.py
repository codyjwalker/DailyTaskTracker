# app/config.py
"""
Utility module that fetches the Flask SECRET_KEY from a file
(or falls back to an environment variable).

The file must contain a single line: the key itself (no quotes).
"""

import os

SECRET_KEY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'secret_key.txt'
)


def get_secret_key() -> str:
    """Return the secret key, or raise RuntimeError if not found."""
    # 1️⃣  Try the file first
    if os.path.isfile(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, 'r', encoding='utf-8') as f:
            key = f.read().strip()
            if key:
                return key

    # 2️⃣  Fallback to environment variable (useful for Docker / CI)
    key = os.getenv('FLASK_SECRET_KEY')
    if key:
        return key

    # 3️⃣  Nothing found – abort loudly
    raise RuntimeError(
        "SECRET_KEY not found. Create 'secret_key.txt' or set FLASK_SECRET_KEY."
    )

