"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

import math
from collections.abc import Mapping
from dataclasses import dataclass


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    rate: float
    burst: int
    window: float


KNOWN_KEYS = {"rate", "burst", "window"}


def _to_float(name, value):
    """Accept an int, float or numeric str; reject everything else.

    bool is a subclass of int and bytes would satisfy ``float()``; neither is
    a configuration number. ``float()`` also accepts ``"1_0"``, which no JSON
    or YAML parser emits, so underscores are rejected.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ConfigError(f"{name} must be a number or numeric string")
    if isinstance(value, str) and "_" in value:
        raise ConfigError(f"bad value for {name}: {value!r}")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigError(f"bad value for {name}: {exc}") from exc
    if not math.isfinite(result):
        raise ConfigError(f"{name} must be a finite number")
    return result


def _positive_float(name, value):
    result = _to_float(name, value)
    if result <= 0:
        raise ConfigError(f"{name} must be positive")
    return result


def _positive_int(name, value):
    as_float = _to_float(name, value)
    if not as_float.is_integer():
        raise ConfigError(f"{name} must be a whole number")
    if as_float <= 0:
        raise ConfigError(f"{name} must be positive")
    if isinstance(value, int):
        return value
    return int(as_float)


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0. Values may be
    numbers or numeric strings (as parsed config often yields); bools,
    non-positive, non-finite and non-integral ``burst`` values are rejected.
    Unknown keys are rejected.
    """
    if not isinstance(raw, Mapping):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(map(str, unknown))}")
    rate = _positive_float("rate", raw.get("rate", 1.0))
    burst = _positive_int("burst", raw.get("burst", 10))
    window = _positive_float("window", raw.get("window", 60.0))
    return Config(rate=rate, burst=burst, window=window)
