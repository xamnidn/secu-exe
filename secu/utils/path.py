from pathlib import Path
import os


def get_config_dir() -> Path:
    """Return the platform-appropriate configuration directory for SECU."""
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / "secu"
    return Path.home() / ".config" / "secu"
