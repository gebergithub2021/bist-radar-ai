from bist_radar.core.config import AppConfig


def test_default_configuration() -> None:
    config = AppConfig()

    assert config.app_name == "BIST Radar AI"
    assert config.version == "0.1.0"