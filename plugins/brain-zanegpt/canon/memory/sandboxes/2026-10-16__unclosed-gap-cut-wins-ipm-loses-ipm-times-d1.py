import random
# Three cuts of one fixable-fail ad. Information gap opens at 3 s. Curiosity slows drop-off while it is open.
# master30 closes the gap at 28 s; trunc15 never closes it (cut by clock); beat15 closes it at 13 s.
CUTS = {"master30": (30, 28), "trunc15": (15, None), "beat15": (15, 13)}
def reach_end(length, close, r, rng_free=False):
    s = 1.0
    for t in range(length):
        gap_open = t >= 3 and (close is None or t < close)
        rate = r * (0.5 if gap_open else 1.0)
        s *= (1 - rate)
    return s
def true_vals(r, install_bait, d1_base, d1_pen):
    out = {}
    for n, (L, c) in CUTS.items():
        unresolved = c is None
        ipm = 1000 * reach_end(L, c, r) * 0.08 * (install_bait if unresolved else 1.0)
        d1 = d1_base - (d1_pen if unresolved else 0)
        out[n] = (ipm, d1)
    return out
def pick(meas, rule):
    return max(meas, key=lambda k: meas[k][0] * (meas[k][1] if rule == "ipm*d1" else 1))
def noisy(rng, tv, imps=2000):
    m = {}
    for n, (ipm, d1) in tv.items():
        inst = sum(rng.random() < ipm/1000 for _ in range(imps)); ret = sum(rng.random() < d1 for _ in range(inst))
        m[n] = (1000*inst/imps, ret/inst if inst else 0)
    return m
def scenario(label, r, bait, pen, N=300, seed=3):
    rng = random.Random(seed); tv = true_vals(r, bait, 0.30, pen)
    best = max(tv, key=lambda k: tv[k][0]*tv[k][1]); wins = {"ipm": 0, "ipm*d1": 0}
    for _ in range(N):
        m = noisy(rng, tv)
        for rule in wins: wins[rule] += pick(m, rule) == best
    print("%-34s true best=%-8s IPM-only right %3d%%  IPM*D1 right %3d%%" % (label, best, 100*wins["ipm"]//N, 100*wins["ipm*d1"]//N))
    return best, wins["ipm"]/N, wins["ipm*d1"]/N
a = scenario("bait +40% installs, D1 -0.12", 0.03, 1.4, 0.12)
b = scenario("bait +40% installs, D1 -0.00 (breaker)", 0.03, 1.4, 0.0)
c = scenario("no bait boost, D1 -0.12", 0.03, 1.0, 0.12)
ok = a[2] - a[1] > 0.3 and abs(b[2]-b[1]) < 0.15
print("RESULT: %s IPM*D1 beats IPM-only by %.2f when unclosed gap costs D1 (best=%s); gap %.2f with no D1 cost" % ("PASS" if ok else "FAIL", a[2]-a[1], a[0], b[2]-b[1]))
