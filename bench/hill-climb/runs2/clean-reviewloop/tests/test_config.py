import types
from decimal import Decimal

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


@pytest.mark.parametrize("raw", [None, "rate=1", 1, {"rate", "burst"}], ids=repr)
def test_other_non_mappings_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_non_dict_mapping_accepted():
    cfg = load_config(types.MappingProxyType({"rate": 0.5}))
    assert cfg == Config(rate=0.5, burst=10, window=60.0)


def test_decimal_and_lenient_strings_accepted():
    cfg = load_config({"rate": Decimal("0.5"), "burst": " 5 ", "window": "1_0"})
    assert cfg == Config(rate=0.5, burst=5, window=10.0)


def test_bad_rate_type():
    with pytest.raises(ConfigError):
        load_config({"rate": "fast"})


def test_zero_rate():
    with pytest.raises(ConfigError):
        load_config({"rate": 0})


def test_sub_one_per_second_rate_accepted():
    assert load_config({"rate": 0.5}).rate == 0.5


@pytest.mark.parametrize(
    "raw",
    [
        {"rate": True},
        {"burst": False},
        {"window": None},
        {"rate": [1]},
        {"burst": {"n": 1}},
        {"rate": "fast"},
        {"burst": ""},
        {"rate": b"1"},
        {"rate": Decimal("NaN")},
        {"rate": Decimal("-1")},
        {"rate": -1},
        {"burst": 0},
        {"window": -0.5},
        {"rate": float("nan")},
        {"rate": "nan"},
        {"window": float("inf")},
        {"window": "inf"},
        {"rate": "1e999"},
        {"burst": float("inf")},
        {"rate": 10**400},
        {"burst": 10**400},
        {"burst": 2.7},
        {"burst": "2.5"},
        {"bogus": 1},
        {"rate": 1, "extra": 2},
        {1: 0, "x": 0},
    ],
    ids=repr,
)
def test_invalid_config_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_integral_float_burst_accepted():
    assert load_config({"burst": 4.0}).burst == 4
