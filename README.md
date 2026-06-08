# SECU Password Generator v1.3.0

Secure Argon2id-based deterministic password generator for desktop.

## Features

- **Argon2id key derivation** — OWASP-recommended memory-hard hashing
- **Fixed memory cost** — always 64 MB (OWASP-compliant), ensures identical passwords across all platforms in portable mode
- **Deterministic output** — same master password + service = same generated password
- **Device binding** — optional hardware-bound password
- **Automatic clipboard clearing** — clipboard overwritten after 10 seconds
- **Rotation version** — change passwords without changing master password
- **Live normalization preview** — see how service names are canonicalized

## Requirements

- Python 3.10+
- Dependencies: `argon2-cffi`, `Pillow`, `pyperclip`

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Project Structure

```
secu/
├── core/          # Cryptography logic (Argon2id, SHA-256)
├── ui/            # Tkinter interface
│   └── views/     # Screen views (main, help, about)
├── utils/         # Cross-cutting utilities (normalizer, platform)
tests/             # Pytest test suite
```

## Architectural Rules

- Core layer must NOT import tkinter
- UI layer must NOT store secrets
- Clipboard abstraction lives in `utils/platform.py`

## Security Notes

**Known limitation:** Due to Python's immutable string model, the master
password may persist in process heap memory until garbage collection after
the Argon2 thread completes. This is a language-level constraint with no
complete mitigation in pure Python. Close the application when done to
clear sensitive sessions.

## License

MIT
