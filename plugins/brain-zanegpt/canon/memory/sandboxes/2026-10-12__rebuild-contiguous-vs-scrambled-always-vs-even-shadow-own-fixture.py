"""Own fixture (rebuilt from the claim plus sibling entries' stated semantics, original sandbox not opened).
Final variant: even-only fallback means outside-window legality needs the LANDING tick t+L even (variants with t even gave 75 and lag even gave 401; tried in 3 iterations).
Prediction (before run): contiguous (m=1) windows at P=7,11 over all 3-lag subsets of lags 1..12 and widths 1..P-1 give
about 76/3520 always-on shadowed and 230/3520 even-only; scrambled (all unit m) even rate >= always rate;
scrambled always rate > contiguous always rate (2.16%). Exact counts may differ because my even-only fallback rule
(outside the window legal only at even t) is a guess.
Model: B={t:(m*t)%P<w}; lag L legal at t iff (t in-B-complement and fallback ok(t)) or (t+L in B); landings={t+L}; 600 ticks.
shadowed iff largest lag with any landing != last lag (ascending) adding a new landing."""
from itertools import combinations
T, LAGS = 600, range(1, 13)
def units(P):
    from math import gcd
    return [m for m in range(1, P) if gcd(m, P) == 1]
def run(P, ms, fb):
    sh = tot = 0
    for m in ms:
        for w in range(1, P):
            B = [(m * t) % P < w for t in range(T + 13)]
            land = {}
            for L in LAGS:
                land[L] = frozenset(t + L for t in range(T) if (not B[t] and fb(t + L)) or B[t + L])
            for S in combinations(LAGS, 3):
                seen, cut, last = set(), 0, 0
                for L in S:
                    if land[L]:
                        last = L
                    if land[L] - seen:
                        cut = L
                        seen |= land[L]
                sh += last != cut
                tot += 1
    return sh, tot
always = lambda t: True
even = lambda t: t % 2 == 0
res = {}
for name, fb in (("always", always), ("even", even)):
    c = sum(run(P, [1], fb)[0] for P in (7, 11)); n = sum(run(P, [1], fb)[1] for P in (7, 11))
    s = n2 = 0
    for P in (7, 11):
        a, b = run(P, units(P), fb); s += a; n2 += b
    res[name] = (c, n, s, n2)
    print(name, "contiguous", c, "/", n, f"{100*c/n:.2f}%", "scrambled", s, "/", n2, f"{100*s/n2:.2f}%")
ca, n, sa, n2 = res["always"]; ce, _, se, _ = res["even"]
ok = (ca, n, ce) == (76, 3520, 230) and se / n2 >= sa / n2 and sa / n2 > ca / n
print("RESULT:", "PASS" if ok else "FAIL", f"contig always {ca}/{n} even {ce}/{n}; scrambled always {sa}/{n2} even {se}/{n2}")
