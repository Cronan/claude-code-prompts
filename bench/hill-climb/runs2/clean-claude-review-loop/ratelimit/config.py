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
    raw_rate = raw.get("rate", 1.0)
    raw_burst = raw.get("burst", 10)
    raw_window = raw.get("window", 60.0)
    for name, value in (("rate", raw_rate), ("burst", raw_burst), ("window", raw_window)):
        if isinstance(value, bool):
            raise ConfigError(f"{name} must be a number, not bool")
    if isinstance(raw_burst, float) and not raw_burst.is_integer():
        raise ConfigError("burst must be a whole number")
    try:
        rate = float(raw_rate)
        burst = int(raw_burst)
        window = float(raw_window)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigError(f"bad value: {exc}") from exc
    if not math.isfinite(rate) or rate <= 0:
        raise ConfigError("rate must be positive and finite")
    if burst <= 0:
        raise ConfigError("burst must be positive")
    if not math.isfinite(window) or window <= 0:
        raise ConfigError("window must be positive and finite")
    return Config(rate=rate, burst=burst, window=window)
