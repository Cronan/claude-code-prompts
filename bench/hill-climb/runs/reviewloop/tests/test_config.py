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


@pytest.mark.parametrize(
    "raw",
    [
        {"rate": True},
        {"burst": True},
        {"window": False},
        {"rate": None},
        {"burst": None},
        {"window": None},
        {"rate": [1]},
        {"burst": {"n": 1}},
        {"window": (1,)},
        {"rate": "fast"},
        {"burst": "many"},
        {"window": ""},
        {"burst": "2.5"},
        {"burst": 2.5},
        {"rate": -1},
        {"rate": "-1"},
        {"burst": 0},
        {"burst": -3},
        {"window": 0},
        {"window": -0.5},
        {"rate": float("nan")},
        {"rate": "nan"},
        {"rate": float("inf")},
        {"window": "inf"},
        {"rate": 10**400},
        {"burst": 10**400},
        {"window": 10**400},
        {"rate": "1e400"},
        {"burst": "1.5e0"},
        {"bogus": 1},
        {"rate": 1.0, "Burst": 2},
        {"rate": 1.0, "burst": 2, "window": 3.0, "extra": None},
    ],
)
def test_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_config_error_is_value_error():
    assert issubclass(ConfigError, ValueError)


def test_whole_float_burst_accepted():
    assert load_config({"burst": 4.0}).burst == 4


def test_integer_rate_and_window_become_floats():
    cfg = load_config({"rate": 2, "window": 30})
    assert cfg == Config(rate=2.0, burst=10, window=30.0)
    assert isinstance(cfg.rate, float) and isinstance(cfg.window, float)


def test_config_builds_working_limiters():
    from ratelimit import RateLimiter, SlidingWindow

    cfg = load_config({"rate": 0.5, "burst": 1, "window": 2})
    RateLimiter(rate=cfg.rate, burst=cfg.burst)
    SlidingWindow(limit=cfg.burst, window=cfg.window)


def test_integer_strings_in_float_form_accepted_for_burst():
    assert load_config({"burst": "1000.0"}).burst == 1000
    assert load_config({"burst": "1e3"}).burst == 1000


def test_rejected_values_do_not_leak_other_exception_types():
    for raw in ({"rate": 10**400}, {"burst": 10**400}, {"burst": 2.5}, {"rate": None}):
        try:
            load_config(raw)
        except ConfigError:
            pass
        else:
            raise AssertionError(f"{raw!r} was accepted")
