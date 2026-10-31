import pytest

from ratelimit import Config, ConfigError, load_config


def test_defaults():
    assert load_config({}) == Config(rate=1.0, burst=10, window=60.0)


def test_values():
    cfg = load_config({"rate": "2.5", "burst": "4", "window": 30})
    assert cfg == Config(rate=2.5, burst=4, window=30.0)


def test_not_mapping():
    with pytest.raises(ConfigError):
        load_config([1, 2])


def test_bad_rate_type():
    with pytest.raises(ConfigError):
        load_config({"rate": "fast"})


def test_zero_rate():
    with pytest.raises(ConfigError):
        load_config({"rate": 0})


# --- added during review ---

def test_unknown_key():
    with pytest.raises(ConfigError):
        load_config({"rate": 1, "ratee": 2})


@pytest.mark.parametrize("raw", [
    {"burst": 0}, {"burst": -1}, {"window": 0}, {"window": -5},
    {"rate": float("nan")}, {"rate": float("inf")}, {"rate": True},
    {"burst": 4.5}, {"burst": None}, {"window": "soon"},
])
def test_rejects_bad_values(raw):
    with pytest.raises(ConfigError):
        load_config(raw)
