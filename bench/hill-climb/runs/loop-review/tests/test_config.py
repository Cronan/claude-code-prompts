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


# --- regression tests added by the hardening review ---


@pytest.mark.parametrize(
    "raw",
    [
        {"burst": 0},
        {"burst": -3},
        {"burst": 2.7},
        {"burst": True},
        {"burst": "x"},
        {"burst": None},
        {"rate": -1},
        {"rate": True},
        {"rate": "inf"},
        {"rate": "nan"},
        {"rate": None},
        {"rate": [1]},
        {"window": 0},
        {"window": -5},
        {"window": "inf"},
        {"window": False},
        {"rte": 5},
        {"rate": 1.0, "extra": 1},
    ],
)
def test_invalid_config_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_sub_one_per_second_rate_accepted():
    assert load_config({"rate": 0.5}) == Config(rate=0.5, burst=10, window=60.0)


def test_integral_float_burst_accepted():
    assert load_config({"burst": 4.0}).burst == 4
