# ratelimit

Small keyed rate limiting library: a token bucket (`RateLimiter`) and a
sliding-window log (`SlidingWindow`), plus `load_config` for building
settings from parsed JSON or YAML.

Requirements the library must meet:

- Safe to call from many threads at once; a key never admits more than
  its limit however many threads contend for it.
- Rates below one request per second are supported (for example 0.5).
- Fails closed: if anything goes wrong internally, the request is denied.
- Invalid configuration (wrong types, non-positive numbers, unknown
  keys) is rejected with `ConfigError`.

Run the tests with `python -m pytest -q`.
