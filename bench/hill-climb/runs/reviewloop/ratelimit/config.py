"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

import math
import numbers
from dataclasses import dataclass


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    rate: float
    burst: int
    window: float


KNOWN_KEYS = {"rate", "burst", "window"}


def _parse_number(name, value, allow_str):
    """Return ``value`` as a finite float or raise ``ConfigError``.

    Accepts real numbers (not bools) and, when ``allow_str`` is set, numeric
    strings. Everything else, including None, containers, NaN, infinity and
    integers too large for a float, is rejected.
    """
    if isinstance(value, bool):
        raise ConfigError(f"{name} must be a number, got bool")
    if isinstance(value, str):
        if not allow_str:
            raise ConfigError(f"{name} must be a number, got str")
        try:
            number = float(value.strip())
        except ValueError as exc:
            raise ConfigError(f"{name} must be a number, got {value!r}") from exc
    elif isinstance(value, numbers.Real):
        try:
            number = float(value)
        except (OverflowError, ValueError, TypeError) as exc:
            raise ConfigError(f"{name} is out of range: {value!r}") from exc
    else:
        raise ConfigError(f"{name} must be a number, got {type(value).__name__}")
    if not math.isfinite(number):
        raise ConfigError(f"{name} must be finite, got {value!r}")
    return number


def coerce_float(name, value, allow_str=False):
    """Coerce ``value`` to a positive finite float or raise ``ConfigError``."""
    number = _parse_number(name, value, allow_str)
    if number <= 0:
        raise ConfigError(f"{name} must be positive, got {value!r}")
    return number


def coerce_int(name, value, allow_str=False):
    """Coerce ``value`` to a positive int or raise ``ConfigError``.

    Whole-number floats (and, with ``allow_str``, strings such as ``"4"`` or
    ``"1e3"``) are accepted; fractional values are rejected.
    """
    number = _parse_number(name, value, allow_str)
    if not number.is_integer():
        raise ConfigError(f"{name} must be a whole number, got {value!r}")
    if number <= 0:
        raise ConfigError(f"{name} must be positive, got {value!r}")
    return int(number)


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0. Numeric strings
    are accepted. Any other key, a non-numeric value, a bool, a non-finite or
    non-positive number, or a fractional ``burst`` raises ``ConfigError``.
    """
    if not isinstance(raw, dict):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        names = ", ".join(sorted(repr(k) for k in unknown))
        raise ConfigError(f"unknown config keys: {names}")
    rate = coerce_float("rate", raw.get("rate", 1.0), allow_str=True)
    burst = coerce_int("burst", raw.get("burst", 10), allow_str=True)
    window = coerce_float("window", raw.get("window", 60.0), allow_str=True)
    return Config(rate=rate, burst=burst, window=window)
