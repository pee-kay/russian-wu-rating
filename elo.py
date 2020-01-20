class Rating:
    def __init__(self):
        self.mu = 1500.0
        self.n = 0
        self.last_active = None

def rate_1vs1(r1, r2, drawn = False, k =  32, date = None):
    s = 0.5 if drawn else 1.0
    e = 1.0 / (1.0 + 10.0 ** ((r2.mu - r1.mu) / 400.0))

    new_r1 = Rating()
    new_r1.mu = r1.mu + k * (s - e)
    new_r1.n = r1.n + 1
    new_r1.last_active = date

    new_r2 = Rating()
    new_r2.mu = r2.mu + k * (e - s)
    new_r2.n = r2.n + 1
    new_r1.last_active = date
    return (new_r1, new_r2)