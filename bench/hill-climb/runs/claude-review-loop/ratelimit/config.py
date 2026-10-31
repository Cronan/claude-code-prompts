"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

import math
from dataclasses import dataclass


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    rate: float
    burst: int
    window: float


KNOWN_KEYS = {"rate", "burst", "window"}


def _positive_float(name, value):
    if isinstance(value, bool):
        raise ConfigError(f"{name} must be a number, not bool")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"bad value for {name}: {exc}") from exc
    if not math.isfinite(result):
        raise ConfigError(f"{name} must be finite")
    if result <= 0:
        raise ConfigError(f"{name} must be positive")
    return result


def _positive_int(name, value):
    if isinstance(value, bool):
        raise ConfigError(f"{name} must be an integer, not bool")
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise ConfigError(f"{name} must be a whole number")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"bad value for {name}: {exc}") from exc
    if result <= 0:
        raise ConfigError(f"{name} must be positive")
    return result


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0.
    """
    if not isinstance(raw, dict):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(map(str, unknown))}")
    rate = _positive_float("rate", raw.get("rate", 1.0))
    burst = _positive_int("burst", raw.get("burst", 10))
    window = _positive_float("window", raw.get("window", 60.0))
    return Config(rate=rate, burst=burst, window=window)
