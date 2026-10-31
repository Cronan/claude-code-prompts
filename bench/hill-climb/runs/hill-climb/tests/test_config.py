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


# --- Tests for the README requirement: invalid configuration is rejected ---


@pytest.mark.parametrize(
    "raw",
    [
        {"bogus": 1},
        {"rate": 1, "extra": 2},
        {"burst": 0},
        {"burst": -1},
        {"window": 0},
        {"window": -5},
        {"rate": -1},
        {"rate": "nan"},
        {"rate": "inf"},
        {"window": "nan"},
        {"burst": float("inf")},
        {"rate": True},
        {"burst": False},
        {"window": True},
        {"burst": 2.9},
        {"burst": "2.9"},
        {"burst": None},
        {"rate": [1]},
        {"window": {"a": 1}},
    ],
)
def test_invalid_config_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_integral_float_burst_accepted():
    assert load_config({"burst": 4.0}).burst == 4


def test_integral_numeric_string_burst_accepted():
    assert load_config({"burst": "4.0"}).burst == 4


@pytest.mark.parametrize("raw", [{"burst": b"4"}, {"rate": b"2"}, {"burst": "1_0"}, {"rate": "1_0"}])
def test_bytes_and_underscore_strings_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_non_dict_mapping_accepted():
    from collections import UserDict

    assert load_config(UserDict({"rate": 2})) == Config(rate=2.0, burst=10, window=60.0)
