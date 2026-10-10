from __future__ import annotations

from collections.abc import Iterator

import config
import pytest


@pytest.fixture(autouse=True)
def _clear_config_cache() -> Iterator[None]:
    config._cache.clear()
    yield
    config._cache.clear()
