"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

import math
import numbers
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    rate: float
    burst: int
    window: float


KNOWN_KEYS = {"rate", "burst", "window"}


def _number(name, value):
    """Return ``value`` as a finite, positive float or raise ``ConfigError``.

    Accepts real numbers (not bool), ``Decimal`` and numeric strings, as
    produced by parsed JSON or YAML. Anything else, including None,
    containers, NaN, infinity and values too large for a float, is rejected.
    """
    if isinstance(value, bool) or not isinstance(value, (numbers.Real, Decimal, str)):
        raise ConfigError(f"{name} must be a number, got {type(value).__name__}")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigError(f"bad value for {name}: {exc}") from exc
    if not math.isfinite(result):
        raise ConfigError(f"{name} must be finite")
    if result <= 0:
        raise ConfigError(f"{name} must be positive")
    return result


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0.
    """
    if not isinstance(raw, Mapping):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(unknown, key=repr)}")
    rate = _number("rate", raw.get("rate", 1.0))
    burst = _number("burst", raw.get("burst", 10))
    window = _number("window", raw.get("window", 60.0))
    if not burst.is_integer():
        raise ConfigError("burst must be a whole number")
    return Config(rate=rate, burst=int(burst), window=window)
