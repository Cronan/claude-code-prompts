from decimal import Decimal
from fractions import Fraction

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


def test_unknown_key():
    with pytest.raises(ConfigError):
        load_config({"rate": 1, "bogus": 2})


def test_unknown_keys_of_mixed_types():
    with pytest.raises(ConfigError):
        load_config({1: 2, "x": 3})


@pytest.mark.parametrize(
    "raw",
    [
        {"rate": -1},
        {"burst": 0},
        {"burst": -3},
        {"window": 0},
        {"window": -0.5},
        {"rate": True},
        {"burst": False},
        {"window": True},
        {"rate": None},
        {"burst": None},
        {"window": [1]},
        {"rate": {"x": 1}},
        {"rate": "nan"},
        {"rate": float("nan")},
        {"rate": "inf"},
        {"rate": float("inf")},
        {"window": "nan"},
        {"window": float("inf")},
        {"burst": float("inf")},
        {"burst": float("nan")},
        {"burst": 2.9},
        {"burst": "fast"},
        {"burst": Decimal("2.9")},
        {"burst": Decimal("2.5")},
        {"burst": Fraction(5, 2)},
        {"burst": Decimal("nan")},
        {"rate": b"2"},
        {"burst": b"2"},
        {"window": b"2"},
        {"rate": bytearray(b"2")},
    ],
)
def test_invalid_values_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_integral_float_burst_accepted():
    assert load_config({"burst": 4.0}).burst == 4


def test_integral_decimal_and_fraction_burst_accepted():
    assert load_config({"burst": Decimal("4")}).burst == 4
    assert load_config({"burst": Fraction(8, 2)}).burst == 4
    assert load_config({"rate": Decimal("0.5")}).rate == 0.5
