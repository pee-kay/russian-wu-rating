import math

MAX_RD = 350.0
MAX_RD_SQ = MAX_RD * MAX_RD
C_SQUARE = MAX_RD_SQ * 0.9 / (365 * 1.5)
Q = math.log(10) / 400


class Rating:
    def __init__(self, mu=1500.0, n=0, rdSq=MAX_RD_SQ, date=None):
        self.mu = mu
        self.n = n
        self.rdSq = rdSq
        self.last_active = date

    def getRdSq(self, date=None):
        if date is None:
            return self.rdSq

        if self.last_active is None:
            return MAX_RD_SQ

        dt = (date - self.last_active).days
        if dt < 0:
            return self.rdSq
        return min(self.rdSq + dt * C_SQUARE, MAX_RD_SQ)


def rate_1vs1(r1, r2, drawn=False, k=32, date=None):
    s = 0.5 if drawn else 1.0
    rd1Sq = r1.getRdSq(date)
    rd2Sq = r2.getRdSq(date)
    grd1_2 = 1.0 / math.sqrt(1 + 3 * Q * Q * rd2Sq / (math.pi * math.pi))
    grd2_1 = 1.0 / math.sqrt(1 + 3 * Q * Q * rd1Sq / (math.pi * math.pi))
    e1_2 = 1.0 / (1.0 + 10.0 ** (grd1_2 * (r2.mu - r1.mu) / 400.0))
    e2_1 = 1.0 / (1.0 + 10.0 ** (grd2_1 * (r1.mu - r2.mu) / 400.0))
    d1Sq = 1.0 / (Q * Q * grd1_2 * grd1_2 * e1_2 * (1 - e1_2))
    d2Sq = 1.0 / (Q * Q * grd2_1 * grd2_1 * e2_1 * (1 - e2_1))

    new_rd1Sq = 1.0 / (1.0 / rd1Sq + 1.0 / d1Sq)
    new_r1 = Rating(r1.mu + Q * grd1_2 * (s - e1_2) *
                    new_rd1Sq, r1.n + 1, new_rd1Sq, date)

    new_rd2Sq = 1 / (1 / rd2Sq + 1/d2Sq)
    new_r2 = Rating(r2.mu + Q * grd2_1 * (1 - s - e2_1) *
                    new_rd2Sq, r2.n + 1, new_rd2Sq, date)
    return (new_r1, new_r2)
