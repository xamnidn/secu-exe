"""
tests/test_crypto_engine.py
===========================
Unit tests for SECU CryptoEngine.

Run with:
    pip install pytest
    pytest tests/ -v
"""

import math
import pytest
from secu.core.crypto_engine import (
    CryptoEngine,
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_MEMORY_COST_MIN,
    ARGON2_HASH_LEN,
    _get_adaptive_memory_cost,
)


# ── Charset Consistency ───────────────────────────────────────────────────────

class TestCharsetConsistency:
    """Validate single source of truth: charset_size always matches build_charset."""

    def test_all_flags_consistent(self):
        """charset_size must equal len(build_charset) for every flag combination."""
        flag_combos = [
            (u, l, n, s)
            for u in [True, False]
            for l in [True, False]
            for n in [True, False]
            for s in [True, False]
        ]
        for flags in flag_combos:
            u, l, n, s = flags
            charset = CryptoEngine.build_charset(u, l, n, s)
            size    = CryptoEngine.charset_size(u, l, n, s)
            assert len(charset) == size, (
                f"Mismatch for flags {flags}: "
                f"build_charset={len(charset)}, charset_size={size}"
            )

    def test_symbol_count(self):
        """Symbols defined in build_charset must be exactly 28 characters."""
        full = CryptoEngine.build_charset(upper=False, lower=False,
                                           numbers=False, symbols=True)
        assert len(full) == 28, (
            f"Expected 28 symbols, got {len(full)}: {full!r}"
        )

    def test_full_charset_size(self):
        """All flags on: 26 upper + 26 lower + 10 digits + 28 symbols = 90."""
        assert CryptoEngine.charset_size(True, True, True, True) == 90

    def test_alphanumeric_only(self):
        """No symbols: 26 + 26 + 10 = 62."""
        assert CryptoEngine.charset_size(True, True, True, False) == 62

    def test_no_charset_fallback(self):
        """All flags off: fallback to ascii_letters + digits, never empty."""
        size = CryptoEngine.charset_size(False, False, False, False)
        assert size >= 1, "charset_size must never return 0"

    def test_charset_no_duplicates(self):
        """build_charset must not contain duplicate characters."""
        charset = CryptoEngine.build_charset()
        assert len(charset) == len(set(charset)), (
            "Duplicate characters found in charset"
        )


# ── Deterministic Output ──────────────────────────────────────────────────────

class TestDeterministicOutput:
    """
    CRITICAL: identical inputs must always produce identical passwords.
    If this test fails after a code change, existing users would lose
    access to all their passwords.
    """

    def test_same_seed_same_output(self):
        """Calling generate twice with identical args returns identical result."""
        seed = b"secu_test_seed_abc123"
        charset = CryptoEngine.build_charset()
        pw1 = CryptoEngine.generate_password_deterministic(seed, charset, 16)
        pw2 = CryptoEngine.generate_password_deterministic(seed, charset, 16)
        assert pw1 == pw2

    def test_output_length_respected(self):
        """Output length must exactly match the requested length."""
        seed = b"length_test_seed"
        charset = CryptoEngine.build_charset()
        for length in [8, 16, 32, 64, 128]:
            pw = CryptoEngine.generate_password_deterministic(seed, charset, length)
            assert len(pw) == length, f"Expected length {length}, got {len(pw)}"

    def test_different_seeds_different_output(self):
        """Different seeds must produce different passwords (avalanche effect)."""
        charset = CryptoEngine.build_charset()
        pw1 = CryptoEngine.generate_password_deterministic(b"seed_aaa", charset, 32)
        pw2 = CryptoEngine.generate_password_deterministic(b"seed_bbb", charset, 32)
        assert pw1 != pw2

    def test_output_only_contains_charset_chars(self):
        """Every character in output must come from the allowed charset."""
        seed    = b"charset_validation_seed"
        charset = CryptoEngine.build_charset(upper=True, lower=True,
                                              numbers=True, symbols=False)
        pw = CryptoEngine.generate_password_deterministic(seed, charset, 32)
        for ch in pw:
            assert ch in charset, (
                f"Character {ch!r} not in allowed charset"
            )

    def test_known_output_regression(self):
        """
        Regression guard: hardcoded expected output for a fixed seed.
        If this fails after a code change, password generation logic
        has changed — which would break ALL existing users.
        UPDATE this expected value only intentionally and with a
        version bump that notifies users.
        """
        seed    = b"secu_regression_v1.3"
        charset = CryptoEngine.build_charset()
        pw      = CryptoEngine.generate_password_deterministic(seed, charset, 16)
        expected = "[Rs2$O.w7fbR$:$V"
        assert isinstance(pw, str)
        assert len(pw) == 16
        assert pw == expected, (
            f"REGRESSION: password generation output has changed! "
            f"Expected {expected!r}, got {pw!r}. "
            "Existing users will lose access to their passwords. "
            "This requires a major version bump and user notification."
        )


# ── Argon2 Parameters ─────────────────────────────────────────────────────────

class TestArgon2Parameters:
    """
    Validate Argon2 parameters meet OWASP minimum recommendations.
    These tests protect against accidental weakening during refactoring.
    """

    def test_memory_cost_default(self):
        """Default memory cost must be at least 64MB (65536 KB) for GPU resistance."""
        assert ARGON2_MEMORY_COST >= 65536, (
            f"ARGON2_MEMORY_COST={ARGON2_MEMORY_COST} is below OWASP minimum of 65536"
        )

    def test_memory_cost_minimum_floor(self):
        """Memory cost floor must be at least 65536 KB (64 MB, OWASP)."""
        assert ARGON2_MEMORY_COST_MIN >= 65536, (
            f"ARGON2_MEMORY_COST_MIN={ARGON2_MEMORY_COST_MIN} "
            f"is below OWASP minimum of 65536 (64 MB)"
        )

    def test_memory_cost_fixed(self):
        """Memory cost must always be 65536 KB regardless of platform."""
        assert _get_adaptive_memory_cost() == 65536, (
            "Memory cost must be fixed at 65536 KB for cross-platform consistency"
        )

    def test_time_cost_minimum(self):
        """Time cost must be at least 3 iterations to resist brute-force."""
        assert ARGON2_TIME_COST >= 3, (
            f"time_cost={ARGON2_TIME_COST} is below recommended minimum of 3"
        )

    def test_hash_len_minimum(self):
        """Hash output must be at least 32 bytes (256 bits)."""
        assert ARGON2_HASH_LEN >= 32, (
            f"hash_len={ARGON2_HASH_LEN} is below minimum of 32 bytes"
        )


# ── Entropy Calculation ───────────────────────────────────────────────────────

class TestEntropyCalculation:
    """Validate entropy math is correct."""

    def test_entropy_formula(self):
        """entropy = length × log2(charset_size)."""
        assert CryptoEngine.entropy(16, 90) == pytest.approx(16 * math.log2(90))
        assert CryptoEngine.entropy(32, 62) == pytest.approx(32 * math.log2(62))
        assert CryptoEngine.entropy(128, 90) == pytest.approx(128 * math.log2(90))

    def test_entropy_increases_with_length(self):
        """Longer password = higher entropy."""
        e16  = CryptoEngine.entropy(16,  90)
        e32  = CryptoEngine.entropy(32,  90)
        e128 = CryptoEngine.entropy(128, 90)
        assert e16 < e32 < e128

    def test_entropy_increases_with_charset(self):
        """Larger charset = higher entropy for same length."""
        e_small = CryptoEngine.entropy(16, 26)   # letters only
        e_large = CryptoEngine.entropy(16, 90)   # full charset
        assert e_small < e_large
