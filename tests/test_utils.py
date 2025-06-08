import types
import pytest

from tests.fixtures.env import override_settings
from src.core.config import settings


class DummyRequest:
    def __init__(self, param=None):
        self.param = param


def test_override_settings_resets_after_use():
    original = settings.REDIS_URL
    gen = override_settings(DummyRequest('redis://example:6380'))
    next(gen)
    assert settings.REDIS_URL == 'redis://example:6380'
    with pytest.raises(StopIteration):
        next(gen)
    assert settings.REDIS_URL == original
