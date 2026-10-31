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
