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


def test_sliding_window_exact_edge_has_left_window():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(9.999)
    assert not sw.allow("a")
    clock.advance(0.001)
    assert clock.t == 10.0
    assert sw.allow("a")


def test_clock_going_backwards_does_not_drain_or_lock_out():
    clock = FakeClock(t=100.0)
    rl = RateLimiter(rate=1.0, burst=2, clock=clock)
    assert rl.allow("a")
    clock.t = 0.0
    # One token left; stepping back must not take it away.
    assert rl.allow("a")
    assert not rl.allow("a")
    # Refill is measured from the latest time seen, not from the step back.
    clock.t = 100.5
    assert not rl.allow("a")
    clock.t = 101.0
    assert rl.allow("a")


def test_sliding_window_reset():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    sw.reset("a")
    assert sw.allow("a")


def test_fractional_rate():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    assert not rl.allow("a")
    clock.advance(1.0)
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


class RaisingClock:
    def __call__(self):
        raise RuntimeError("clock failure")


def test_fail_closed_on_clock_error():
    rl = RateLimiter(rate=1.0, burst=5, clock=RaisingClock())
    assert rl.allow("a") is False
    sw = SlidingWindow(limit=5, window=10.0, clock=RaisingClock())
    assert sw.allow("a") is False


def _hammer(limiter, key, threads, calls_per_thread):
    import threading

    results = []
    results_lock = threading.Lock()
    start = threading.Barrier(threads)

    def worker():
        start.wait()
        local = 0
        for _ in range(calls_per_thread):
            if limiter.allow(key):
                local += 1
        with results_lock:
            results.append(local)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return sum(results)


def test_token_bucket_concurrent_never_exceeds_burst():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=50, clock=clock)
    assert _hammer(rl, "a", threads=8, calls_per_thread=100) == 50
    assert rl.stats == {"allowed": 50, "denied": 750}


def test_sliding_window_concurrent_never_exceeds_limit():
    clock = FakeClock()
    sw = SlidingWindow(limit=50, window=10.0, clock=clock)
    assert _hammer(sw, "a", threads=8, calls_per_thread=100) == 50


class YieldingKey:
    """A key whose hash gives up the GIL.

    Every dict read and write of the per-key state hashes the key, so a
    limiter that does not hold its lock across read-compute-write will
    interleave threads between the read and the write and admit more
    than the limit. With the lock held the yield is harmless.
    """

    def __hash__(self):
        import time

        time.sleep(0.0002)
        return 1

    def __eq__(self, other):
        return isinstance(other, YieldingKey)


def test_token_bucket_concurrent_with_yielding_key():
    key = YieldingKey()
    rl = RateLimiter(rate=1.0, burst=20, clock=FakeClock())
    assert _hammer(rl, key, threads=8, calls_per_thread=10) == 20
    assert rl.stats == {"allowed": 20, "denied": 60}


def test_sliding_window_concurrent_with_yielding_key():
    key = YieldingKey()
    sw = SlidingWindow(limit=20, window=10.0, clock=FakeClock())
    assert _hammer(sw, key, threads=8, calls_per_thread=10) == 20


class TickingClock:
    """Clock that advances by ``step`` on every read, from any thread."""

    def __init__(self, step):
        self.t = 0.0
        self.step = step
        self._lock = __import__("threading").Lock()

    def __call__(self):
        with self._lock:
            self.t += self.step
            return self.t


def test_token_bucket_concurrent_refill_never_exceeds_budget():
    # 8 threads x 100 calls = 800 reads of the clock, each advancing 0.01s,
    # so the run spans 8.0s at rate 10/s: 10 burst + 80 refilled = 90 at most.
    clock = TickingClock(step=0.01)
    rl = RateLimiter(rate=10.0, burst=10, clock=clock)
    allowed = _hammer(rl, "a", threads=8, calls_per_thread=100)
    assert 10 <= allowed <= 90


def test_sliding_window_concurrent_refill_never_exceeds_budget():
    # Clock spans 8.0s in 0.01s steps; window 1.0s, limit 5: at most 5 per
    # window and at most 9 windows touched, so never more than 45.
    clock = TickingClock(step=0.01)
    sw = SlidingWindow(limit=5, window=1.0, clock=clock)
    allowed = _hammer(sw, "a", threads=8, calls_per_thread=100)
    assert 5 <= allowed <= 45
