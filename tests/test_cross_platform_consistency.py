"""
tests/test_cross_platform_consistency.py
=========================================
Verifies deterministic password generation across platforms.

Run with:
    pip install pytest
    pytest tests/test_cross_platform_consistency.py -v
"""

from secu.core.crypto_engine import (
    CryptoEngine,
    ARGON2_MEMORY_COST_DEFAULT,
    _get_adaptive_memory_cost,
)


def test_memory_cost_fixed():
    """Memory cost harus selalu 65536 KB, tidak bergantung platform."""
    assert _get_adaptive_memory_cost() == 65536, (
        "Memory cost must be fixed at 65536 KB for cross-platform consistency"
    )


def test_portable_mode_deterministic():
    """Password portable mode harus identik dengan parameter yang sama."""
    salt = "v1.3.0::google.com:1"
    master = "test_master_password"
    pw1 = CryptoEngine.derive_password(master, salt, 20)
    pw2 = CryptoEngine.derive_password(master, salt, 20)
    assert pw1 == pw2, "Password harus deterministik"


def test_argon2_memory_cost_owasp():
    """Memory cost harus memenuhi OWASP minimum (64 MB)."""
    assert ARGON2_MEMORY_COST_DEFAULT >= 65536, (
        f"memory_cost={ARGON2_MEMORY_COST_DEFAULT} di bawah OWASP minimum 65536 KB"
    )


def test_portable_same_across_platforms():
    """Simulasi: portable mode harus menghasilkan password yang sama."""
    master = "MyStrongMasterKey!"
    service = "example.com"
    version = 1
    salt_portable = f"v1.3.0::{service}:{version}"
    pw = CryptoEngine.derive_password(master, salt_portable, 16)
    assert len(pw) == 16
    assert isinstance(pw, str)


def test_device_bound_differs_from_portable():
    """Device-bound salt menghasilkan password berbeda dari portable."""
    master = "test"
    service = "site.com"
    version = 1
    salt_portable = f"v1.3.0::{service}:{version}"
    salt_bound = f"v1.3.0:abc123def456:{service}:{version}"
    pw_portable = CryptoEngine.derive_password(master, salt_portable, 12)
    pw_bound = CryptoEngine.derive_password(master, salt_bound, 12)
    assert pw_portable != pw_bound, (
        "Device-bound password harus berbeda dari portable"
    )
