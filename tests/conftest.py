import pytest
from kitefly.util import KEY_COUNT


@pytest.fixture(autouse=True)
def reset_generated_keys():
    KEY_COUNT.clear()
