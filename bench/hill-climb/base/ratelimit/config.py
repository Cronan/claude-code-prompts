"""Configuration loading.

Invalid configuration must be rejected with ``ConfigError`` rather than
silently producing a limiter that behaves unexpectedly.
"""

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
    try:
        rate = float(raw.get("rate", 1.0))
        burst = int(raw.get("burst", 10))
        window = float(raw.get("window", 60.0))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"bad value: {exc}") from exc
    if rate <= 0:
        raise ConfigError("rate must be positive")
    return Config(rate=rate, burst=burst, window=window)
