"""Tests for the four README requirements: thread safety, sub-1/s rates,
fail closed, and invalid configuration rejected with ConfigError."""

import math
import threading

import pytest

from ratelimit import ConfigError, RateLimiter, SlidingWindow, load_config


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class SequenceClock:
    """Returns the given values in order, then repeats the last one."""

    def __init__(self, values):
        self.values = list(values)
        self.i = 0

    def __call__(self):
        v = self.values[min(self.i, len(self.values) - 1)]
        self.i += 1
        return v


class RaisingClock:
    def __init__(self):
        self.fail = True

    def __call__(self):
        if self.fail:
            raise RuntimeError("clock failure")
        return 0.0


# --- thread safety ---------------------------------------------------------


def _hammer(limiter, threads=32, calls=50):
    barrier = threading.Barrier(threads)
    results = []
    results_lock = threading.Lock()

    def worker():
        barrier.wait()
        mine = [limiter.allow("k") for _ in range(calls)]
        with results_lock:
            results.extend(mine)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return results


def test_concurrent_token_bucket_never_exceeds_burst():
    rl = RateLimiter(rate=0.001, burst=10, clock=FakeClock())
    results = _hammer(rl)
    assert sum(results) == 10
    assert rl.stats == {"allowed": 10, "denied": 32 * 50 - 10}


def test_concurrent_sliding_window_never_exceeds_limit():
    sw = SlidingWindow(limit=5, window=60.0, clock=FakeClock())
    results = _hammer(sw)
    assert sum(results) == 5
    assert len(sw._log["k"]) == 5


# --- sub-1/s rates -------------------------------------------------------


def test_fractional_rate_half():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    clock.advance(1.0)
    assert not rl.allow("a")
    clock.advance(0.9)
    assert not rl.allow("a")
    clock.advance(0.1)
    assert rl.allow("a")


def test_fractional_rate_no_drift_across_polls():
    clock = FakeClock()
    rl = RateLimiter(rate=0.1, burst=1, clock=clock)
    assert rl.allow("a")
    results = []
    for _ in range(10):
        clock.advance(1.0)
        results.append(rl.allow("a"))
    assert results == [False] * 9 + [True]


def test_clock_going_backwards_does_not_drain_tokens():
    clock = FakeClock(100.0)
    rl = RateLimiter(rate=1.0, burst=2, clock=clock)
    assert rl.allow("a")
    clock.t = 50.0
    assert rl.allow("a")
    assert rl._buckets["a"][0] >= 0.0


# --- fail closed ---------------------------------------------------------


def test_raising_clock_denies_and_counts_denial():
    clock = RaisingClock()
    rl = RateLimiter(rate=1.0, burst=3, clock=clock)
    assert rl.allow("a") is False
    assert rl.stats == {"allowed": 0, "denied": 1}
    assert rl._buckets == {}
    clock.fail = False
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]


def test_raising_clock_sliding_window_denies_and_keeps_state():
    clock = RaisingClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a") is False
    assert sw._log == {}
    clock.fail = False
    assert sw.allow("a") is True
    assert sw.allow("a") is False


def test_unhashable_key_denied():
    rl = RateLimiter(rate=1.0, burst=1, clock=FakeClock())
    sw = SlidingWindow(limit=1, window=1.0, clock=FakeClock())
    assert rl.allow([]) is False
    assert sw.allow([]) is False
    assert rl.stats["denied"] == 1


def test_nan_clock_reading_is_denied_and_not_stored():
    rl = RateLimiter(rate=1.0, burst=1, clock=SequenceClock([0.0, math.nan, 0.5, 1.0]))
    assert rl.allow("a") is True
    assert rl.allow("a") is False  # nan reading
    assert rl.allow("a") is False  # t=0.5, not refilled yet
    assert rl.allow("a") is True  # t=1.0
    assert all(math.isfinite(v) for v in rl._buckets["a"])

    sw = SlidingWindow(limit=1, window=10.0, clock=SequenceClock([0.0, math.nan, 1.0, 11.0]))
    assert sw.allow("a") is True
    assert sw.allow("a") is False  # nan reading
    assert sw.allow("a") is False  # t=1.0, still in window
    assert sw.allow("a") is True  # t=11.0
    assert all(math.isfinite(v) for v in sw._log["a"])


# --- invalid configuration -----------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        {"rate": math.nan},
        {"rate": "nan"},
        {"rate": "inf"},
        {"rate": math.inf},
        {"window": math.inf},
        {"window": math.nan},
        {"rate": True},
        {"rate": False},
        {"burst": True},
        {"burst": 2.7},
        {"burst": "2.5"},
        {"burst": 0.5},
        {"burst": None},
        {"rate": None},
        {"rate": b"1"},
        {"rate": [1]},
        {"burst": math.inf},
        {"rate": 10**400},
        {"rate": -0.0},
        {"rate": -1},
        {"burst": 0},
        {"window": 0},
        {"window": -1},
        {"x": 1},
        {1: 1, "x": 2},
        [],
        None,
        "rate=1",
    ],
)
def test_invalid_config_rejected(raw):
    with pytest.raises(ConfigError):
        load_config(raw)


def test_valid_config_forms_still_accepted():
    cfg = load_config({"rate": 0.5, "burst": 4.0, "window": "30"})
    assert cfg.rate == 0.5 and cfg.burst == 4 and cfg.window == 30.0
    assert isinstance(cfg.burst, int)


@pytest.mark.parametrize(
    "ctor",
    [
        lambda: RateLimiter(rate=math.nan, burst=1),
        lambda: RateLimiter(rate=0, burst=1),
        lambda: RateLimiter(rate=-1, burst=1),
        lambda: RateLimiter(rate="x", burst=1),
        lambda: RateLimiter(rate=1, burst=0),
        lambda: RateLimiter(rate=1, burst=0.5),
        lambda: RateLimiter(rate=1, burst=math.inf),
        lambda: RateLimiter(rate=True, burst=1),
        lambda: SlidingWindow(limit=0, window=1),
        lambda: SlidingWindow(limit=1, window=math.nan),
        lambda: SlidingWindow(limit=1, window=-5),
        lambda: SlidingWindow(limit=math.inf, window=10),
        lambda: SlidingWindow(limit=None, window=10),
    ],
)
def test_constructor_rejects_invalid_arguments(ctor):
    with pytest.raises(ConfigError):
        ctor()


def test_constructor_accepts_valid_arguments():
    rl = RateLimiter(rate=0.5, burst=3)
    assert rl.rate == 0.5 and rl.burst == 3
    sw = SlidingWindow(limit=2, window=10)
    assert sw.limit == 2 and sw.window == 10.0
