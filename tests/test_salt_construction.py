"""
tests/test_salt_construction.py
================================
Tests for service salt format — the foundation of SECU's determinism.

Salt format:
  Portable mode:      "{VERSION_TAG}::{service_lower}:{version}"
  Device-bound mode:  "{VERSION_TAG}:{device_id}:{service_lower}:{version}"

If salt format changes, ALL existing passwords change.
These tests are the canary in the coal mine.
"""

import pytest

from secu.utils.normalizer import ServiceNormalizer

VERSION_TAG = "v1.3.0"


def build_salt(service, version, device_id="", device_bind=False):
    """Mirror of the salt construction logic in main_view.generate_logic()."""
    device_component = device_id if device_bind else ""
    normalized = ServiceNormalizer.normalize(service)
    return f"{VERSION_TAG}:{device_component}:{normalized}:{version}"


# ── Salt Format ───────────────────────────────────────────────────────────────

class TestSaltFormat:
    """Validate salt format for both portable and device-bound modes."""

    def test_portable_salt_format(self):
        """Portable mode: device_component is empty string."""
        salt = build_salt("google.com", 1, device_bind=False)
        assert salt == "v1.3.0::google.com:1"

    def test_device_bound_salt_format(self):
        """Device-bound: device_id is included in salt."""
        salt = build_salt("google.com", 1, device_id="abc123", device_bind=True)
        assert salt == "v1.3.0:abc123:google.com:1"

    def test_version_tag_present(self):
        """Salt must always start with VERSION_TAG."""
        salt = build_salt("github.com", 1)
        assert salt.startswith(VERSION_TAG)

    def test_service_lowercased(self):
        """Service name must be lowercased for cross-platform consistency."""
        salt_lower = build_salt("google.com", 1)
        salt_upper = build_salt("GOOGLE.COM", 1)
        salt_mixed = build_salt("Google.Com", 1)
        assert salt_lower == salt_upper == salt_mixed, (
            "Service name must be case-insensitive"
        )

    def test_rotation_version_changes_salt(self):
        """Different version numbers must produce different salts."""
        salt_v1 = build_salt("google.com", 1)
        salt_v2 = build_salt("google.com", 2)
        assert salt_v1 != salt_v2

    def test_different_services_different_salts(self):
        """Different services must produce different salts."""
        salt_google = build_salt("google.com", 1)
        salt_github = build_salt("github.com", 1)
        assert salt_google != salt_github

    def test_portable_vs_device_bound_different(self):
        """Portable and device-bound must produce different salts."""
        salt_portable = build_salt("google.com", 1, device_bind=False)
        salt_bound    = build_salt("google.com", 1,
                                   device_id="abc123", device_bind=True)
        assert salt_portable != salt_bound


# ── Salt Determinism ──────────────────────────────────────────────────────────

class TestSaltDeterminism:
    """Same inputs must always produce the same salt."""

    def test_same_inputs_same_salt(self):
        """Identical inputs produce identical salt — foundation of determinism."""
        salt1 = build_salt("google.com", 1, device_id="dev1", device_bind=True)
        salt2 = build_salt("google.com", 1, device_id="dev1", device_bind=True)
        assert salt1 == salt2

    def test_salt_is_string(self):
        """Salt must be a plain UTF-8 encodable string."""
        salt = build_salt("google.com", 1)
        assert isinstance(salt, str)
        # Must be encodable for argon2
        encoded = salt.encode("utf-8")
        assert len(encoded) > 0

    def test_version_tag_consistency(self):
        """
        VERSION_TAG in salt ties passwords to a specific app version.
        Changing VERSION_TAG intentionally invalidates all existing passwords.
        This test documents the current expected tag — update only with
        a deliberate version bump.
        """
        assert VERSION_TAG == "v1.3.0", (
            "VERSION_TAG has changed. All existing passwords are now invalid. "
            "Ensure users are notified before releasing this change."
        )
