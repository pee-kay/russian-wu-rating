class Rating:
    def __init__(self, mu=1500.0, n=0, date=None):
        self.mu = mu
        self.n = n
        self.last_active = date


def rate_1vs1(r1, r2, drawn=False, k=32, date=None):
    s = 0.5 if drawn else 1.0
    e = 1.0 / (1.0 + 10.0**((r2.mu - r1.mu) / 400.0))

    new_r1 = Rating(r1.mu + k * (s - e), r1.n + 1, date)
    new_r2 = Rating(r2.mu + k * (e - s), r2.n + 1, date)
    return (new_r1, new_r2)


def rate_2vs2(r1, r2, p1, p2, drawn=False, k=16, date=None):
    s = 0.5 if drawn else 1.0
    e = 1.0 / (1.0 + 10.0**((r2.mu + p2.mu - r1.mu - p1.mu) / 400.0))

    new_r1 = Rating(r1.mu + k * (s - e), r1.n + 1, date)
    new_r2 = Rating(r2.mu + k * (e - s), r2.n + 1, date)
    new_p1 = Rating(p1.mu + k * (s - e), p1.n + 1, date)
    new_p2 = Rating(p2.mu + k * (e - s), p2.n + 1, date)
    return (new_r1, new_r2, new_p1, new_p2)
