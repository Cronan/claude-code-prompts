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
        raise ConfigError(f"unknown keys: {sorted(map(str, unknown))}")
    for key, value in raw.items():
        if isinstance(value, bool):
            raise ConfigError(f"{key} must be a number, not a bool")
    raw_burst = raw.get("burst", 10)
    if isinstance(raw_burst, float) and not raw_burst.is_integer():
        raise ConfigError("burst must be a whole number")
    try:
        rate = float(raw.get("rate", 1.0))
        burst = int(raw_burst)
        window = float(raw.get("window", 60.0))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"bad value: {exc}") from exc
    if not math.isfinite(rate) or rate <= 0:
        raise ConfigError("rate must be positive")
    if burst <= 0:
        raise ConfigError("burst must be positive")
    if not math.isfinite(window) or window <= 0:
        raise ConfigError("window must be positive")
    return Config(rate=rate, burst=burst, window=window)
