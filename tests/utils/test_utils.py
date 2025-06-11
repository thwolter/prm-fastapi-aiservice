class DummyRequest:
    def __init__(self, param=None):
        self.param = param


def test_override_settings_resets_after_use(monkeypatch):
    from src.core import config

    original = config.settings.REDIS_URL
    # Directly patch the REDIS_URL for testing
    monkeypatch.setattr(config.settings, "REDIS_URL", "redis://example:6380")
    assert config.settings.REDIS_URL == "redis://example:6380"
    # Reset
    monkeypatch.setattr(config.settings, "REDIS_URL", original)
    assert config.settings.REDIS_URL == original
