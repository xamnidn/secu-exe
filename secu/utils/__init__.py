# secu/utils/__init__.py
# CORRECTED — SECU v1.3.0
# Copy this file directly into: secu/utils/__init__.py
# Replaces the previous version which was missing the ServiceNormalizer export.

from .normalizer import ServiceNormalizer

__all__ = ["ServiceNormalizer"]
