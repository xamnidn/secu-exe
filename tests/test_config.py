from secu.core.config_manager import ConfigManager


def test_device_id():
    cfg = ConfigManager()
    device_id = cfg.get_device_id()
    assert len(device_id) == 64
