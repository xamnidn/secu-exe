import pytest
from secu.core.crypto_engine import CryptoEngine, HAS_ARGON


@pytest.mark.skipif(not HAS_ARGON, reason="argon2-cffi not installed")
def test_password_generation():
    salt = "v1.3.0::google.com:1"
    password = CryptoEngine.derive_password(
        "master",
        salt,
        16,
    )
    assert len(password) == 16
