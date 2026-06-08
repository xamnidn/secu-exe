import hashlib
import json
import secrets
from pathlib import Path

from secu.utils.path import get_config_dir


class ConfigManager:
    def __init__(self):
        self.config_dir = get_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.device_file = self.config_dir / "device.json"

    def get_device_id(self):
        try:
            if self.device_file.exists():
                data = json.loads(self.device_file.read_text())
                device_id = data.get("device_id")
                if device_id and len(device_id) == 64:
                    try:
                        bytes.fromhex(device_id)
                        return device_id
                    except ValueError:
                        pass

            device_id = secrets.token_hex(32)
            self.device_file.write_text(
                json.dumps({"device_id": device_id}, indent=2)
            )
            return device_id
        except Exception:
            return hashlib.sha256(str(Path.home()).encode()).hexdigest()
