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


def _positive_number(name, value):
    """Return ``value`` as a positive finite float or raise ``ConfigError``.

    Accepts int, float and numeric str (parsed JSON/YAML may carry strings).
    Rejects bool, bytes, None and anything else, and rejects NaN and inf.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ConfigError(f"{name} must be a number, not {type(value).__name__}")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigError(f"bad value for {name}: {exc}") from exc
    if not math.isfinite(number):
        raise ConfigError(f"{name} must be finite")
    if number <= 0:
        raise ConfigError(f"{name} must be positive")
    return number


def _positive_int(name, value):
    """Return ``value`` as a positive int or raise ``ConfigError``.

    Like ``_positive_number`` but the value must be whole: 2.7 is rejected
    rather than truncated.
    """
    number = _positive_number(name, value)
    if not number.is_integer():
        raise ConfigError(f"{name} must be a whole number")
    return int(number)


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0.
    """
    if not isinstance(raw, dict):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(unknown, key=repr)}")
    rate = _positive_number("rate", raw.get("rate", 1.0))
    burst = _positive_int("burst", raw.get("burst", 10))
    window = _positive_number("window", raw.get("window", 60.0))
    return Config(rate=rate, burst=burst, window=window)
