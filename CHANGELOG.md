# CHANGELOG -- SECU v1.3.0 Patch

### Fixed
- Removed adaptive memory cost (`_get_adaptive_memory_cost`) to ensure portable
  mode produces identical passwords on all platforms regardless of available RAM.
  Android (which uses Linux kernel) could previously generate different passwords
  than Windows/macOS due to lower MemAvailable values triggering a reduced
  memory cost parameter.
- Raised `ARGON2_MEMORY_COST_MIN` from 32768 to 65536 (32 MB → 64 MB) to meet
  OWASP hard minimum for Argon2id.

### Changed
- `_get_adaptive_memory_cost()` now returns a fixed 65536 KB (64 MB) instead of
  sampling `/proc/meminfo` on Linux/Android. This guarantees deterministic output
  in portable mode across all platforms.

## New Files

### `secu/utils/normalizer.py`
- **Purpose:** Cross-cutting utility for deterministic service name normalization.
- **Contents:**
  - `ServiceNormalizer` class with `DELIMITER = ':'` constant.
  - `normalize(raw: str) -> str`: applies strip, Unicode NFC, lowercase, control-character rejection, and delimiter rejection.
  - `preview(raw: str) -> str`: safe wrapper that returns an empty string instead of raising exceptions (for UI live preview).
- **Rationale:** Ensures identical inputs produce identical salts across all platforms, preventing subtle Unicode or whitespace differences from breaking password determinism.

## Modified Files

### `secu/utils/__init__.py`
- **Change:** Added `from .normalizer import ServiceNormalizer`.
- **Rationale:** Exposes the normalizer through the package namespace so `main_view.py` can import it cleanly.

### `secu/core/crypto_engine.py`
- **Changes:**
   - Replaced hardcoded `ARGON2_MEMORY_COST = 65536` with three constants: `ARGON2_MEMORY_COST_DEFAULT` (65536), `ARGON2_MEMORY_COST_MIN` (32768), and `ARGON2_MEMORY_COST_MAX` (65536).
   - Added `_get_adaptive_memory_cost() -> int` function that reads `/proc/meminfo` on Linux to determine available RAM, then uses 1/8 of that value, clamped to [32 MB, 64 MB].
  - Updated `derive_password()` to call `_get_adaptive_memory_cost()` for the `memory_cost` parameter.
- **Rationale:** Prevents out-of-memory crashes on low-end devices (e.g., 2 GB RAM VMs) while preserving OWASP-recommended 64 MB on systems with sufficient memory.
- **Fallback:** Windows and macOS systems without `/proc/meminfo` silently use the default 64 MB.

### `secu/ui/views/main_view.py`
- **Changes:**
  - Added import: `from secu.utils.normalizer import ServiceNormalizer`.
  - Added `self._service_var = tk.StringVar(value=self.PLACEHOLDER_SERVICE)` to track service input.
  - Wired `textvariable=self._service_var` into `entry_service`.
  - Added `self._preview_label` (tk.Label) below the service entry field to display the normalized form in real time.
  - Added `_update_preview(self, *args)` method, bound via `trace_add("write", ...)` to update the preview label dynamically.
  - Modified `generate_logic()`:
    - Replaced raw `service.strip()` with `ServiceNormalizer.normalize(raw_service)`.
    - Added `try/except (TypeError, ValueError)` block that shows a `messagebox.showwarning` dialog if the service name contains invalid characters (e.g., `:`) or is empty.
    - Salt is now built from the normalized `service_name` instead of raw input.
  - Updated `apply_theme()` to theme the new `_preview_label`.
- **Rationale:** Blocks salt injection attacks via the `:` delimiter and gives users immediate visual feedback on how their input will be normalized, reducing human error.

### `secu/ui/views/help_view.py`
- **Changes:**
  - Appended a new "CLIPBOARD SECURITY" section to `HELP_TEXT`.
  - The section explains:
    - SECU's built-in 10-second auto-clear and random-data overwrite.
    - OS-level risks: Windows Clipboard History, macOS Universal Clipboard, third-party managers (Ditto, CopyQ, Klipper, GPaste).
    - Additional risks from screenshot tools, screen recorders, and keyloggers.
    - Actionable recommendations: disable OS clipboard history, avoid third-party managers, lock screen after use, use full-disk encryption.
- **Rationale:** Transparency about the limits of application-level clipboard security. Empowers users to take additional OS-level precautions.

## Testing Checklist

- [ ] Normalization: `' Google.COM ' -> 'google.com'`
- [ ] Unicode NFC: composed characters normalize identically on Windows and Linux.
- [ ] Rejection: `'my:bank'` triggers an error dialog before generation.
- [ ] Adaptive memory: on a 2 GB RAM VM, memory cost should be ~32 MB; on 16 GB, it should be 64 MB.
- [ ] Help view: the clipboard disclaimer renders correctly in the UI.
- [ ] Determinism: identical inputs on different OSes produce identical passwords.
