import hashlib
import math
import string
import sys

try:
    from argon2.low_level import hash_secret_raw, Type
    HAS_ARGON = True
    ARGON2_TYPE = Type.ID
except ImportError:
    HAS_ARGON = False
    ARGON2_TYPE = None

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST_DEFAULT = 65536
ARGON2_MEMORY_COST_MIN = 65536
ARGON2_MEMORY_COST_MAX = 65536
ARGON2_PARALLELISM = 4
ARGON2_HASH_LEN = 32
ARGON2_MEMORY_COST = ARGON2_MEMORY_COST_DEFAULT  # alias for external consumers


def _get_adaptive_memory_cost() -> int:
    """
    Return fixed memory cost for Argon2id.

    Previously adaptive (based on /proc/meminfo on Linux), but this caused
    password inconsistency across devices in portable mode because Android
    also uses sys.platform == 'linux' and may have less available RAM than
    desktop systems. A deterministic password generator must use fixed
    parameters to guarantee reproducibility regardless of device RAM.
    """
    return ARGON2_MEMORY_COST_DEFAULT  # always 65536 KB (64 MB)


class CryptoEngine:
    VERSION_TAG = "v1.3.0"   # Bisa tetap "v1.3.0" atau ubah ke "v1.3" jika perlu kompatibilitas

    @staticmethod
    def generate_password_deterministic(seed_bytes, allowed, length):
        charset_len = len(allowed)
        if charset_len == 0:
            raise ValueError("Character set cannot be empty")
        threshold = (256 // charset_len) * charset_len
        password_chars = []
        counter = 0
        while len(password_chars) < length:
            block = hashlib.sha256(
                seed_bytes + counter.to_bytes(4, "big")
            ).digest()
            for byte in block:
                if byte < threshold:
                    password_chars.append(allowed[byte % charset_len])
                    if len(password_chars) >= length:
                        break
            counter += 1
            if counter > 10000:
                raise RuntimeError(
                    "generate_password_deterministic: exhausted iteration limit"
                )
        return "".join(password_chars)

    @staticmethod
    def build_charset(upper=True, lower=True, numbers=True, symbols=True):
        allowed = ""
        if upper:
            allowed += string.ascii_uppercase
        if lower:
            allowed += string.ascii_lowercase
        if numbers:
            allowed += string.digits
        if symbols:
            allowed += "!@#$%^&*()_+-=[]{}|;:,.<>?/~"
        if not allowed:
            allowed = string.ascii_letters + string.digits
        return allowed

    @staticmethod
    def derive_password(
        master_password,
        service_salt,
        length,
        upper=True,
        lower=True,
        numbers=True,
        symbols=True,
    ):
        if not HAS_ARGON:
            raise RuntimeError("argon2-cffi is not installed")
        memory_cost = _get_adaptive_memory_cost()
        hash_bytes = hash_secret_raw(
            secret=master_password.encode("utf-8"),
            salt=service_salt.encode("utf-8"),
            time_cost=ARGON2_TIME_COST,
            memory_cost=memory_cost,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LEN,
            type=ARGON2_TYPE,
        )
        allowed = CryptoEngine.build_charset(upper, lower, numbers, symbols)
        return CryptoEngine.generate_password_deterministic(
            hash_bytes, allowed, length
        )

    @staticmethod
    def charset_size(upper, lower, numbers, symbols):
        charset = CryptoEngine.build_charset(upper, lower, numbers, symbols)
        return max(len(charset), 1)

    @staticmethod
    def entropy(length, charset_size):
        return length * math.log2(charset_size)