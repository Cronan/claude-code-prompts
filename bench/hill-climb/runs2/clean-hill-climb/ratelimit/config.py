"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

import math
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    rate: float
    burst: int
    window: float


KNOWN_KEYS = {"rate", "burst", "window"}

# Numbers, exact numeric types a JSON/YAML parser may produce, and numeric
# strings (accepted for compatibility; see tests). bool is rejected
# separately because it is an int subclass.
ACCEPTED_TYPES = (int, float, str, Decimal, Fraction)


def load_config(raw):
    """Build a ``Config`` from a mapping such as parsed JSON or YAML.

    ``rate`` and ``window`` are in per-second / seconds; ``burst`` is a count.
    All three are optional and default to 1.0, 10 and 60.0.
    """
    if not isinstance(raw, dict):
        raise ConfigError("config must be a mapping")
    unknown = set(raw) - KNOWN_KEYS
    if unknown:
        raise ConfigError(f"unknown keys: {sorted(map(repr, unknown))}")
    for name in KNOWN_KEYS:
        if name not in raw:
            continue
        if isinstance(raw[name], bool):
            raise ConfigError(f"{name} must be a number, not bool")
        if not isinstance(raw[name], ACCEPTED_TYPES):
            raise ConfigError(
                f"{name} must be a number or numeric string, "
                f"not {type(raw[name]).__name__}"
            )
    raw_burst = raw.get("burst", 10)
    try:
        if not isinstance(raw_burst, str) and raw_burst != int(raw_burst):
            raise ConfigError("burst must be a whole number")
        rate = float(raw.get("rate", 1.0))
        burst = int(raw_burst)
        window = float(raw.get("window", 60.0))
    except ConfigError:
        raise
    except (TypeError, ValueError, OverflowError) as exc:
        raise ConfigError(f"bad value: {exc}") from exc
    if not math.isfinite(rate) or rate <= 0:
        raise ConfigError("rate must be a positive finite number")
    if burst <= 0:
        raise ConfigError("burst must be positive")
    if not math.isfinite(window) or window <= 0:
        raise ConfigError("window must be a positive finite number")
    return Config(rate=rate, burst=burst, window=window)
