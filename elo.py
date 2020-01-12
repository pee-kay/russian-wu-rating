class Rating:
    def __init__(self):
        self.mu = 1500.0

def rate_1vs1(r1, r2, drawn = False, k = 10.0):
    s = 0.5 if drawn else 1.0
    e1 = 1.0 / (1.0 + 10.0 ** ((r2.mu - r1.mu) / 400.0))
    e2 = 1.0 / (1.0 + 10.0 ** ((r1.mu - r2.mu) / 400.0))

    new_r1 = Rating()
    new_r1.mu = r1.mu + k * (s - e1)

    new_r2 = Rating()
    new_r2.mu = r2.mu + k * (1.0 - s - e2)
    return (new_r1, new_r2)