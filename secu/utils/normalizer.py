# secu/utils/normalizer.py
import unicodedata

class ServiceNormalizer:
    RESERVED_CHAR = ":"

    @staticmethod
    def normalize(service: str) -> str:
        """
        Normalize a service name for use in the Argon2 salt.

        Steps:
          1. Strip leading/trailing whitespace
          2. Apply Unicode NFC normalization (cross-platform consistency)
          3. Convert to lowercase

        Raises ValueError if the result contains ':' (salt injection risk).
        Raises TypeError if service is not a string.
        """
        if not isinstance(service, str):
            raise TypeError(f"service must be str, got {type(service).__name__}")

        stripped = service.strip()
        normalized = unicodedata.normalize("NFC", stripped)
        lowered = normalized.lower()

        if ServiceNormalizer.RESERVED_CHAR in lowered:
            raise ValueError(
                f"Service name must not contain '{ServiceNormalizer.RESERVED_CHAR}'. "
                f"Use an alias (e.g. 'mybank' instead of 'my:bank')."
            )

        return lowered

    @staticmethod
    def is_valid(service: str) -> bool:
        """Return True if the service name would pass normalize() without error."""
        try:
            ServiceNormalizer.normalize(service)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def preview(service: str) -> str:
        """
        Return normalized form without raising exceptions.
        Safe for live UI preview. Returns empty string on invalid input.

        If normalization fails (e.g., contains ':' or invalid type), returns
        a best-effort stripped+lowercased version (may not be fully normalized)
        to avoid crashing the preview display.
        """
        if not isinstance(service, str):
            return ""

        try:
            return ServiceNormalizer.normalize(service)
        except (ValueError, TypeError):
            # Fallback: just strip and lowercase for preview (not fully NFC-normalized,
            # but prevents crash and still gives a reasonable visual hint)
            return service.strip().lower()