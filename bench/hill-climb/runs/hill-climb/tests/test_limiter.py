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


# --- Tests for the README requirements -----------------------------------


def test_fractional_rate_refills_when_polled_faster_than_rate():
    # rate 0.5/s, burst 1: one request every two seconds, however often polled.
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    results = []
    for _ in range(20):
        clock.advance(0.25)
        results.append(rl.allow("a"))
    # 5 seconds elapsed at 0.5/s => exactly 2 further admissions, at t=2 and t=4.
    assert results.count(True) == 2
    assert results[7] is True and results[15] is True


def test_sub_second_polling_does_not_starve():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    results = []
    for _ in range(10):
        clock.advance(0.5)
        results.append(rl.allow("a"))
    assert results == [False, True] * 5


def test_refill_capped_at_burst():
    clock = FakeClock()
    rl = RateLimiter(rate=10.0, burst=2, clock=clock)
    assert rl.allow("a") and rl.allow("a")
    clock.advance(100.0)
    assert [rl.allow("a") for _ in range(3)] == [True, True, False]


def test_fails_closed_when_clock_raises():
    def broken_clock():
        raise RuntimeError("no clock")

    rl = RateLimiter(rate=1.0, burst=5, clock=broken_clock)
    assert rl.allow("a") is False
    sw = SlidingWindow(limit=5, window=10.0, clock=broken_clock)
    assert sw.allow("a") is False


def test_fails_closed_on_unhashable_key():
    rl = RateLimiter(rate=1.0, burst=5, clock=FakeClock())
    assert rl.allow(["unhashable"]) is False
    sw = SlidingWindow(limit=5, window=10.0, clock=FakeClock())
    assert sw.allow(["unhashable"]) is False


def test_sliding_window_exact_boundary_has_left_window():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(10.0)
    assert sw.allow("a")


def test_sliding_window_inside_window_still_counts():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(9.999)
    assert not sw.allow("a")


def _hammer(limiter, key, threads, calls_per_thread):
    import threading

    admitted = []
    barrier = threading.Barrier(threads)

    def worker():
        n = 0
        for _ in range(calls_per_thread):
            if limiter.allow(key):
                n += 1
        admitted.append(n)

    def start():
        barrier.wait()
        worker()

    ts = [threading.Thread(target=start) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(admitted)


def test_token_bucket_never_over_admits_under_contention():
    import time

    rl = RateLimiter(rate=0.000001, burst=500, clock=time.monotonic)
    total = _hammer(rl, "k", threads=16, calls_per_thread=400)
    assert total == 500
    assert rl.stats["allowed"] == 500
    assert rl.stats["allowed"] + rl.stats["denied"] == 16 * 400


def test_sliding_window_never_over_admits_under_contention():
    import time

    sw = SlidingWindow(limit=500, window=3600.0, clock=time.monotonic)
    total = _hammer(sw, "k", threads=16, calls_per_thread=400)
    assert total == 500


def test_sliding_window_boundary_with_fractional_timestamps():
    # now - window can round so a stamp exactly window old still counts.
    for i in range(1, 1000):
        clock = FakeClock(i * 0.1)
        sw = SlidingWindow(limit=1, window=10.0, clock=clock)
        assert sw.allow("a")
        clock.advance(10.0)
        assert sw.allow("a"), f"start={i * 0.1}"


def test_nan_clock_denies():
    nan_clock = lambda: float("nan")
    rl = RateLimiter(rate=1.0, burst=5, clock=nan_clock)
    assert [rl.allow("a") for _ in range(3)] == [False, False, False]
    sw = SlidingWindow(limit=5, window=10.0, clock=nan_clock)
    assert [sw.allow("a") for _ in range(3)] == [False, False, False]


class _YieldingKey:
    """A key whose hash yields the GIL, so an unlocked read-modify-write
    interleaves between threads. With the lock held, the yield happens inside
    the critical section and is harmless."""

    def __hash__(self):
        import time

        time.sleep(0)
        return 1

    def __eq__(self, other):
        return isinstance(other, _YieldingKey)


def test_token_bucket_lock_covers_read_modify_write():
    import time

    rl = RateLimiter(rate=0.000001, burst=200, clock=time.monotonic)
    total = _hammer(rl, _YieldingKey(), threads=8, calls_per_thread=100)
    assert total == 200
    assert rl.stats == {"allowed": 200, "denied": 600}


def test_sliding_window_lock_covers_read_modify_write():
    import time

    sw = SlidingWindow(limit=200, window=3600.0, clock=time.monotonic)
    total = _hammer(sw, _YieldingKey(), threads=8, calls_per_thread=100)
    assert total == 200


@pytest.mark.parametrize(
    "args",
    [
        (float("nan"), 3),
        ("1", 3),
        (-1.0, 3),
        (0, 3),
        (1.0, -1),
        (1.0, 2.5),
        (1.0, float("inf")),
        (True, 3),
        (1.0, True),
        (None, 3),
    ],
)
def test_rate_limiter_rejects_bad_constructor_args(args):
    with pytest.raises(ConfigError):
        RateLimiter(*args, clock=FakeClock())


@pytest.mark.parametrize(
    "args",
    [
        (2, -5),
        (2, float("nan")),
        (2, 0),
        ("2", 5.0),
        (-1, 5.0),
        (2.5, 5.0),
        (True, 5.0),
        (2, None),
    ],
)
def test_sliding_window_rejects_bad_constructor_args(args):
    with pytest.raises(ConfigError):
        SlidingWindow(*args, clock=FakeClock())


def test_zero_burst_and_zero_limit_deny_everything():
    assert RateLimiter(rate=1.0, burst=0, clock=FakeClock()).allow("a") is False
    assert SlidingWindow(limit=0, window=1.0, clock=FakeClock()).allow("a") is False


def _run_while_lock_held(limiter, clock, key, advance):
    """Start allow(key) while the test holds the limiter's lock, advance the
    clock, then release the lock and return allow's result."""
    import threading
    import time

    results = []
    limiter._lock.acquire()
    try:
        t = threading.Thread(target=lambda: results.append(limiter.allow(key)))
        t.start()
        time.sleep(0.05)  # let the thread reach (and block on) the lock
        clock.advance(advance)
    finally:
        limiter._lock.release()
    t.join(5)
    return results


def test_clock_is_read_under_the_lock():
    # A caller that waits for the lock must be stamped with the time it
    # acquired the lock, not the time it started waiting; otherwise the next
    # caller sees a stale ``last`` and refills a token that was just spent.
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert _run_while_lock_held(rl, clock, "a", 5.0) == [True]
    assert rl.allow("a") is False  # burst 1: the token spent at t=5 is gone

    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert _run_while_lock_held(sw, clock, "a", 5.0) == [True]
    clock.advance(5.0)  # 5 s after the admission: still inside the window
    assert sw.allow("a") is False


def test_rate_0_1_admits_exactly_on_time():
    clock = FakeClock()
    rl = RateLimiter(rate=0.1, burst=1, clock=clock)
    assert rl.allow("a")
    results = []
    for _ in range(20):
        clock.advance(1.0)
        results.append(rl.allow("a"))
    assert results.index(True) == 9  # t=10
    assert results.count(True) == 2  # t=10 and t=20


def test_huge_int_constructor_args_rejected():
    for args in [(10**400, 1), (1.0, 10**400)]:
        with pytest.raises(ConfigError):
            RateLimiter(*args, clock=FakeClock())
    with pytest.raises(ConfigError):
        SlidingWindow(10**400, 1.0, clock=FakeClock())


def test_long_window_does_not_expire_early():
    month = 30 * 24 * 3600.0
    clock = FakeClock(1_700_000_000.0)
    sw = SlidingWindow(limit=1, window=month, clock=clock)
    assert sw.allow("a")
    clock.advance(month - 0.002)
    assert sw.allow("a") is False
    clock.advance(0.002)
    assert sw.allow("a") is True


def test_stats_count_failed_calls_as_denied():
    rl = RateLimiter(rate=1.0, burst=5, clock=lambda: float("nan"))
    rl.allow("a")
    rl2 = RateLimiter(rate=1.0, burst=5, clock=FakeClock())
    rl2.allow(["unhashable"])
    assert rl.stats == {"allowed": 0, "denied": 1}
    assert rl2.stats == {"allowed": 0, "denied": 1}
