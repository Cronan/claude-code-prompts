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


@pytest.mark.parametrize("key", ["rate", "burst", "window"])
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), True, False])
def test_rejects_non_finite_and_bool(key, bad):
    with pytest.raises(ConfigError):
        load_config({key: bad})


def test_rejects_fractional_burst():
    with pytest.raises(ConfigError):
        load_config({"burst": 2.9})


def test_rejects_huge_burst_as_config_error():
    with pytest.raises(ConfigError):
        load_config({"burst": 1e999})


def test_unknown_keys():
    with pytest.raises(ConfigError):
        load_config({"rate": 1, "rtae": 2})


def test_unknown_mixed_type_keys():
    with pytest.raises(ConfigError):
        load_config({1: 0, "a": 0})
