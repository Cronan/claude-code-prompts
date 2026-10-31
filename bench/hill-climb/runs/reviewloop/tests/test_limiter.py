import threading
import time

import pytest

from ratelimit import ConfigError, RateLimiter, SlidingWindow


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


def test_burst_then_deny():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=3, clock=clock)
    assert [rl.allow("a") for _ in range(4)] == [True, True, True, False]


def test_keys_independent():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert rl.allow("b")
    assert not rl.allow("a")


def test_refill():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    rl.allow("a")
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")
    assert not rl.allow("a")


def test_reset():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert not rl.allow("a")
    rl.reset("a")
    assert rl.allow("a")


def test_stats_counts():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    rl.allow("a")
    rl.allow("a")
    assert rl.stats == {"allowed": 1, "denied": 1}


def test_sliding_window_basic():
    clock = FakeClock()
    sw = SlidingWindow(limit=2, window=10.0, clock=clock)
    assert sw.allow("a")
    assert sw.allow("a")
    assert not sw.allow("a")
    clock.advance(11.0)
    assert sw.allow("a")


def test_sliding_window_reset():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    sw.reset("a")
    assert sw.allow("a")


# --- sub-1/s rates -----------------------------------------------------------


def test_fractional_rate_refills_after_two_seconds():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    for _ in range(19):
        clock.advance(0.1)
        assert not rl.allow("a"), clock.t
    clock.advance(0.1)  # t == 2.0
    assert rl.allow("a")
    assert not rl.allow("a")


def test_fractional_refill_not_lost_by_polling():
    clock = FakeClock()
    rl = RateLimiter(rate=0.25, burst=1, clock=clock)
    assert rl.allow("a")
    # Poll far more often than the refill interval; the fraction must accumulate.
    for _ in range(39):
        clock.advance(0.1)
        assert not rl.allow("a")
    clock.advance(0.1)  # t == 4.0
    assert rl.allow("a")


def test_refill_caps_at_burst():
    clock = FakeClock()
    rl = RateLimiter(rate=10.0, burst=2, clock=clock)
    assert rl.allow("a")
    assert rl.allow("a")
    clock.advance(100.0)
    assert [rl.allow("a") for _ in range(3)] == [True, True, False]


def test_clock_going_backwards_grants_nothing():
    clock = FakeClock(10.0)
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    clock.t = 0.0
    assert not rl.allow("a")
    clock.t = 10.5
    assert not rl.allow("a")
    clock.t = 11.0
    assert rl.allow("a")


# --- fail closed ------------------------------------------------------------


def _boom():
    raise RuntimeError("clock broken")


def test_rate_limiter_fails_closed_on_clock_error():
    rl = RateLimiter(rate=1.0, burst=5, clock=_boom)
    assert rl.allow("a") is False
    assert rl.stats == {"allowed": 0, "denied": 1}


def test_sliding_window_fails_closed_on_clock_error():
    sw = SlidingWindow(limit=5, window=10.0, clock=_boom)
    assert sw.allow("a") is False


def test_rate_limiter_fails_closed_on_bad_clock_value():
    rl = RateLimiter(rate=1.0, burst=5, clock=lambda: "now")
    assert rl.allow("a") is False
    rl = RateLimiter(rate=1.0, burst=5, clock=lambda: float("nan"))
    assert rl.allow("a") is False


def test_sliding_window_fails_closed_on_bad_clock_value():
    sw = SlidingWindow(limit=5, window=10.0, clock=lambda: None)
    assert sw.allow("a") is False


def test_rate_limiter_fails_closed_on_unhashable_key():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=5, clock=clock)
    assert rl.allow(["unhashable"]) is False
    assert rl.allow("a")  # still works afterwards


def test_sliding_window_fails_closed_on_unhashable_key():
    clock = FakeClock()
    sw = SlidingWindow(limit=5, window=10.0, clock=clock)
    assert sw.allow({"k": 1}) is False
    assert sw.allow("a")


# --- constructor validation ---------------------------------------------------


@pytest.mark.parametrize(
    "rate, burst",
    [
        (0, 1),
        (-1.0, 1),
        (1.0, 0),
        (1.0, -1),
        (None, 1),
        (1.0, None),
        ("1", 1),
        (1.0, "1"),
        (True, 1),
        (1.0, True),
        (1.0, 1.5),
        (float("nan"), 1),
        (float("inf"), 1),
    ],
)
def test_rate_limiter_rejects_bad_construction(rate, burst):
    with pytest.raises(ConfigError):
        RateLimiter(rate=rate, burst=burst, clock=FakeClock())


@pytest.mark.parametrize(
    "limit, window",
    [
        (0, 10.0),
        (-1, 10.0),
        (1, 0),
        (1, -10.0),
        (None, 10.0),
        (1, None),
        ("1", 10.0),
        (1, "10"),
        (True, 10.0),
        (1, True),
        (1.5, 10.0),
        (1, float("nan")),
        (1, float("inf")),
    ],
)
def test_sliding_window_rejects_bad_construction(limit, window):
    with pytest.raises(ConfigError):
        SlidingWindow(limit=limit, window=window, clock=FakeClock())


def test_limiters_reject_non_callable_clock():
    with pytest.raises(ConfigError):
        RateLimiter(rate=1.0, burst=1, clock=5)
    with pytest.raises(ConfigError):
        SlidingWindow(limit=1, window=1.0, clock=None)


def test_whole_float_burst_is_accepted():
    rl = RateLimiter(rate=1.0, burst=2.0, clock=FakeClock())
    assert rl.burst == 2
    sw = SlidingWindow(limit=2.0, window=10, clock=FakeClock())
    assert sw.limit == 2


# --- sliding window boundaries ------------------------------------------------


def test_sliding_window_exact_boundary_leaves_window():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(9.999)
    assert not sw.allow("a")
    clock.advance(0.001)  # exactly window seconds since the first request
    assert sw.allow("a")


def test_sliding_window_keys_independent():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    assert sw.allow("b")
    assert not sw.allow("a")
    assert not sw.allow("b")


# --- thread safety ----------------------------------------------------------


class _BarrierClock:
    """Constant clock that yields the GIL on every read to widen races."""

    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        time.sleep(0)
        return self.t


def _hammer(limiter, key, threads, calls_per_thread):
    results = []
    lock = threading.Lock()
    start = threading.Barrier(threads)

    def worker():
        local = 0
        start.wait()
        for _ in range(calls_per_thread):
            if limiter.allow(key):
                local += 1
        with lock:
            results.append(local)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(results)


@pytest.mark.parametrize("round_", range(5))
def test_rate_limiter_concurrent_admits_exactly_burst(round_):
    rl = RateLimiter(rate=0.001, burst=50, clock=_BarrierClock())
    admitted = _hammer(rl, "k", threads=16, calls_per_thread=100)
    assert admitted == 50
    assert rl.stats == {"allowed": 50, "denied": 16 * 100 - 50}


@pytest.mark.parametrize("round_", range(5))
def test_sliding_window_concurrent_admits_exactly_limit(round_):
    sw = SlidingWindow(limit=50, window=1000.0, clock=_BarrierClock())
    admitted = _hammer(sw, "k", threads=16, calls_per_thread=100)
    assert admitted == 50


def test_rate_limiter_concurrent_many_keys():
    rl = RateLimiter(rate=0.001, burst=3, clock=_BarrierClock())
    counts = {}
    lock = threading.Lock()

    def worker(i):
        key = f"k{i % 8}"
        for _ in range(50):
            if rl.allow(key):
                with lock:
                    counts[key] = counts.get(key, 0) + 1

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(32)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert counts == {f"k{i}": 3 for i in range(8)}
    assert rl.stats["allowed"] == 24
    assert rl.stats["allowed"] + rl.stats["denied"] == 32 * 50


def test_reset_races_with_allow_without_error():
    clock = _BarrierClock()
    rl = RateLimiter(rate=0.001, burst=1, clock=clock)
    sw = SlidingWindow(limit=1, window=1000.0, clock=clock)
    stop = threading.Event()
    calls = 500

    def resetter():
        while not stop.is_set():
            rl.reset("k")
            sw.reset("k")
            time.sleep(0)

    t = threading.Thread(target=resetter)
    t.start()
    try:
        results = [(rl.allow("k"), sw.allow("k")) for _ in range(calls)]
    finally:
        stop.set()
        t.join()
    assert all(isinstance(a, bool) and isinstance(b, bool) for a, b in results)
    # Nothing was lost: every call was counted exactly once.
    assert rl.stats["allowed"] + rl.stats["denied"] == calls
    assert rl.stats["allowed"] >= 1
    # State is consistent once the resetter has stopped.
    rl.reset("k")
    sw.reset("k")
    assert [rl.allow("k") for _ in range(2)] == [True, False]
    assert [sw.allow("k") for _ in range(2)] == [True, False]


# --- clock pathologies and numeric edge cases -------------------------------


@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_rate_limiter_non_finite_clock_denies_without_poisoning_state(bad):
    clock = FakeClock(1.0)
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    clock.t = bad
    assert rl.allow("a") is False
    clock.t = 2.0
    assert rl.allow("a")
    assert rl.stats == {"allowed": 2, "denied": 1}


@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan")])
def test_sliding_window_non_finite_clock_denies_without_poisoning_state(bad):
    clock = FakeClock(1.0)
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.t = bad
    assert sw.allow("a") is False
    clock.t = 11.0
    assert sw.allow("a")


def test_backward_clock_step_does_not_lock_key_out():
    clock = FakeClock(1000.0)
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    clock.t = 0.0
    assert not rl.allow("a")
    clock.t = 1001.0  # one second after the admission, by the original baseline
    assert rl.allow("a")


def test_polling_does_not_shift_exact_refill_boundary():
    # 0.2/s polled every 0.1s: incremental float accumulation would drift and
    # deny at t == 5.0; refilling from the last admission must not.
    clock = FakeClock()
    rl = RateLimiter(rate=0.2, burst=1, clock=clock)
    assert rl.allow("a")
    for i in range(1, 50):
        clock.t = round(i * 0.1, 10)
        assert not rl.allow("a"), clock.t
    clock.t = 5.0
    assert rl.allow("a")


def test_huge_integer_arguments_raise_config_error():
    with pytest.raises(ConfigError):
        RateLimiter(rate=10**400, burst=1, clock=FakeClock())
    with pytest.raises(ConfigError):
        RateLimiter(rate=1.0, burst=10**400, clock=FakeClock())
    with pytest.raises(ConfigError):
        SlidingWindow(limit=10**400, window=1.0, clock=FakeClock())
    with pytest.raises(ConfigError):
        SlidingWindow(limit=1, window=10**400, clock=FakeClock())
