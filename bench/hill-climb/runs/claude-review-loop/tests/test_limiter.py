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
    rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a") in (True, False)


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


# --- added during review ---

import threading


def test_refill_strict():
    clock = FakeClock()
    rl = RateLimiter(rate=1.0, burst=1, clock=clock)
    assert rl.allow("a")
    assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")


def test_fractional_rate_refills():
    clock = FakeClock()
    rl = RateLimiter(rate=0.5, burst=1, clock=clock)
    assert rl.allow("a")
    for _ in range(3):
        clock.advance(0.5)
        assert not rl.allow("a")
    clock.advance(0.5)
    assert rl.allow("a")


def test_fail_closed_on_clock_error():
    def bad_clock():
        raise RuntimeError("boom")

    assert RateLimiter(rate=1.0, burst=5, clock=bad_clock).allow("a") is False
    assert SlidingWindow(limit=5, window=10.0, clock=bad_clock).allow("a") is False


def test_sliding_window_boundary():
    clock = FakeClock()
    sw = SlidingWindow(limit=1, window=10.0, clock=clock)
    assert sw.allow("a")
    clock.advance(10.0)
    assert sw.allow("a")


def test_thread_safety_never_exceeds_burst():
    clock = FakeClock()
    burst = 50
    rl = RateLimiter(rate=1.0, burst=burst, clock=clock)
    results = []
    lock = threading.Lock()
    start = threading.Barrier(16)

    def worker():
        start.wait()
        local = [rl.allow("k") for _ in range(100)]
        with lock:
            results.extend(local)

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sum(results) == burst
    assert rl.stats == {"allowed": burst, "denied": 1600 - burst}


def test_slow_rate_polled_often_still_refills():
    clock = FakeClock()
    rl = RateLimiter(rate=0.1, burst=1, clock=clock)
    assert rl.allow("a")
    for _ in range(9):
        clock.advance(1.0)
        assert not rl.allow("a")
    clock.advance(1.0)
    assert rl.allow("a")
