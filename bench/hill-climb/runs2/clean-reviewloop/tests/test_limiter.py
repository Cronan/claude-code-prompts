import threading

import pytest

from ratelimit import RateLimiter, SlidingWindow


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
    assert rl.allow("a")
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


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


class RaisingClock:
    def __call__(self):
        raise RuntimeError("clock broken")


class NanClock:
    def __call__(self):
        return float("nan")


class LockCheckingClock(FakeClock):
    """Records whether the limiter's lock was held when the clock was read."""

    def __init__(self, limiter_holder):
        super().__init__()
        self.holder = limiter_holder
        self.locked_on_read = []

    def __call__(self):
        self.locked_on_read.append(self.holder[0]._lock.locked())
        return self.t


def _hammer(limiter, key, threads, calls_per_thread):
    barrier = threading.Barrier(threads)
    admitted = []
    admitted_lock = threading.Lock()

    def worker():
        barrier.wait()
        count = sum(1 for _ in range(calls_per_thread) if limiter.allow(key))
        with admitted_lock:
            admitted.append(count)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(admitted)


def test_sub_one_per_second_rate():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    clock.advance(1.0)
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")
    assert not rl.allow("a")


def test_rate_limiter_concurrent_never_exceeds_burst():
    rl = RateLimiter(rate=1.0, burst=50, clock=FakeClock())
    assert _hammer(rl, "k", threads=16, calls_per_thread=100) == 50
    assert rl.stats["allowed"] == 50
    assert rl.stats["denied"] == 16 * 100 - 50


def test_sliding_window_concurrent_never_exceeds_limit():
    sw = SlidingWindow(limit=50, window=10.0, clock=FakeClock())
    assert _hammer(sw, "k", threads=16, calls_per_thread=100) == 50


def test_clock_read_under_lock():
    holder = []
    clock = LockCheckingClock(holder)
    for cls, kwargs in (
        (RateLimiter, {"rate": 1.0, "burst": 1}),
        (SlidingWindow, {"limit": 1, "window": 1.0}),
    ):
        clock.locked_on_read.clear()
        holder[:] = [cls(clock=clock, **kwargs)]
        holder[0].allow("a")
        holder[0].allow("a")
        assert clock.locked_on_read == [True, True]


@pytest.mark.parametrize(
    "make",
    [
        lambda clock: RateLimiter(rate=1.0, burst=1, clock=clock),
        lambda clock: SlidingWindow(limit=1, window=1.0, clock=clock),
    ],
    ids=["RateLimiter", "SlidingWindow"],
)
def test_fail_closed(make):
    lim = make(RaisingClock())
    assert lim.allow("a") is False
    assert lim.allow("a") is False

    for bad in (None, "12", object()):
        lim = make(lambda bad=bad: bad)
        assert lim.allow("a") is False

    lim = make(NanClock())
    assert lim.allow("a") is False
    assert lim.allow("a") is False

    lim = make(FakeClock())
    assert lim.allow(["unhashable"]) is False
    assert lim.allow("a") is True


def test_rate_limiter_exception_denials_counted():
    rl = RateLimiter(rate=1.0, burst=1, clock=RaisingClock())
    rl.allow("a")
    rl.allow("a")
    assert rl.stats == {"allowed": 0, "denied": 2}


def test_nan_clock_does_not_poison_bucket():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    rl.clock = NanClock()
    assert not rl.allow("a")
    rl.clock = clock
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


def test_reset_unhashable_raises_and_admits_nothing():
    rl = RateLimiter(rate=1.0, burst=1, clock=FakeClock())
    assert rl.allow("a")
    with pytest.raises(TypeError):
        rl.reset(["x"])
    assert not rl.allow("a")
    sw = SlidingWindow(limit=1, window=1.0, clock=FakeClock())
    assert sw.allow("a")
    with pytest.raises(TypeError):
        sw.reset(["x"])
    assert not sw.allow("a")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rate": float("nan"), "burst": 1},
        {"rate": float("inf"), "burst": 1},
        {"rate": "x", "burst": 1},
        {"rate": None, "burst": 1},
        {"rate": 1.0, "burst": float("nan")},
        {"rate": 1.0, "burst": float("inf")},
        {"rate": 1.0, "burst": "three"},
        {"rate": 1.0, "burst": None},
    ],
    ids=repr,
)
def test_rate_limiter_bad_parameters_fail_closed(kwargs):
    clock = FakeClock()
    rl = RateLimiter(clock=clock, **kwargs)
    for _ in range(3):
        assert rl.allow("a") is False
        clock.advance(1.0)
    assert rl.stats == {"allowed": 0, "denied": 3}


def test_rate_limiter_parameter_mutated_after_construction_fails_closed():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    rl.rate = "x"
    clock.advance(5.0)
    assert not rl.allow("a")
    rl.rate = 1.0
    assert rl.allow("a")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 1, "window": float("nan")},
        {"limit": 1, "window": float("inf")},
        {"limit": 1, "window": 0},
        {"limit": 1, "window": -1.0},
        {"limit": 1, "window": "10"},
        {"limit": 1, "window": None},
        {"limit": 0, "window": 1.0},
        {"limit": -1, "window": 1.0},
        {"limit": None, "window": 1.0},
    ],
    ids=repr,
)
def test_sliding_window_bad_parameters_fail_closed(kwargs):
    clock = FakeClock()
    sw = SlidingWindow(clock=clock, **kwargs)
    for _ in range(3):
        assert sw.allow("a") is False
        clock.advance(1.0)
