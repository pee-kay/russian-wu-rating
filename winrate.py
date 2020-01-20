class Rating:
    def __init__(self):
        self.mu = 0.0
        self.n = 0
        self.last_active = None

def rate_1vs1(r1, r2, drawn = False, date = None):
    new_r1 = Rating()
    new_r1.n = r1.n + 1
    new_r1.mu = (r1.mu * r1.n + (0 if drawn else 1)) / new_r1.n
    new_r1.last_active = date

    new_r2 = Rating()
    new_r2.n = r2.n + 1
    new_r2.mu = r2.mu * r2.n / new_r2.n
    new_r2.last_active = date

    return (new_r1, new_r2)