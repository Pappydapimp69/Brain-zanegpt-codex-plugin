"""Rebuild of seven E57 (cap flicker per sliding 1 s window, never by average rate).
Own fixture: two different generators -- Poisson (exponential gaps) and a bursty
two-state Markov generator (bursts at 6/s, quiet at 0.3/s) -- seeds 7/11/13, 120 s,
mean rates 1.0/1.5/2.0 per second. A flash is a PAIR of opposing transitions
(WCAG definition), each flash lasting 80 ms, so a window can hold the tail of a flash.
Predictions written before running:
 P1 irregular flicker at a mean of 1.0/s (below E57's 1.5) still breaks 3-per-window for both generators.
 P2 a greedy start-time cap keeps every window <= 3 FLASHES when counted as full transition pairs (expect hold).
 P3 the cap keeps >= 0.70 of flashes at 2.0/s for both generators (E57: 0.75 for its generator).
"""
import random

DUR, T = 0.08, 120.0

def poisson(rate, seed):
    rng, t, out = random.Random(seed), 0.0, []
    while True:
        t += rng.expovariate(rate)
        if t >= T: return out
        out.append(t)

def bursty(rate, seed):
    # two states; burst 6/s, quiet q; time share in burst chosen so the mean equals rate
    rng, t, out = random.Random(seed), 0.0, []
    q, b = 0.3, 6.0
    share = (rate - q) / (b - q)
    state_end, burst = 0.0, False
    while t < T:
        if t >= state_end:
            burst = rng.random() < share
            state_end = t + rng.expovariate(1 / 0.8)
        t += rng.expovariate(b if burst else q)
        if t < T: out.append(t)
    return out

def worst_window(starts):
    # count transitions (on at s, off at s+DUR); a flash = 2 transitions; worst over windows starting at any transition
    tr = sorted([s for s in starts] + [s + DUR for s in starts])
    best, j = 0, 0
    for i in range(len(tr)):
        while tr[i] - tr[j] >= 1.0: j += 1
        best = max(best, i - j + 1)
    return best / 2  # flashes = transition pairs

def cap(starts):
    kept = []
    for s in starts:
        recent = [k for k in kept if s - k < 1.0]
        if len(recent) < 3: kept.append(s)
    return kept

rows, p1, p2, kept20 = [], True, True, []
for name, gen in (("poisson", poisson), ("bursty", bursty)):
    for rate in (1.0, 1.5, 2.0):
        for seed in (7, 11, 13):
            s = gen(rate, seed); c = cap(s)
            w, wc = worst_window(s), worst_window(c)
            if rate == 1.0 and seed == 7: p1 &= w > 3
            p2 &= wc <= 3
            if rate == 2.0: kept20.append((name, len(c) / len(s)))
            rows.append((name, rate, seed, w, wc))
        print(f"{name:7s} rate {rate}: worst raw " + "/".join(f"{r[3]:.1f}" for r in rows[-3:]) +
              "  capped " + "/".join(f"{r[4]:.1f}" for r in rows[-3:]))
for n, k in kept20: print(f"{n} keeps {k:.3f} at 2.0/s")
p3 = all(k >= 0.70 for _, k in kept20)
checks = [("P1 1.0/s irregular breaks the rule", p1), ("P2 cap <= 3 flashes counted as pairs", p2), ("P3 cap keeps >= 0.70 at 2/s", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; worst raw at 1.0/s poisson {rows[0][3]:.1f} bursty {rows[9][3]:.1f}; "
      f"worst capped {max(r[4] for r in rows):.1f}; kept at 2/s " + "/".join(f"{k:.2f}" for _, k in kept20))
