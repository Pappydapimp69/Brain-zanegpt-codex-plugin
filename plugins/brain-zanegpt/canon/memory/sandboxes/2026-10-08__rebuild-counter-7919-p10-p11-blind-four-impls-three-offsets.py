#!/usr/bin/env python3
"""Blind rebuild: Counter multiset-difference cover test vs dict reference.

PREDICTION (written before the first run, never edited):
  * Interpretation of the four numbers: P=10 -> avg(N=P)=15, avg(N=2P)=65/2;
    P=11 -> avg(N=P)=215/11, avg(N=2P)=460/11.  (Guess; the run decides.)
  * At every offset (7919, plus my own 4003 and 10007) the per-width/per-horizon
    shadow counts from Counter(b)-Counter(a)==empty, dict membership,
    frozenset subset and an int-bitmask test are identical, so the period-average
    shadow count is identical at every N in 2..2P+1 for P=10 and P=11.
  * Flat points (avg(N)==avg(N-1)) over N=P-1..2P+1 are exactly [P, 2P] for
    both moduli.
  * Controls: base-0 differs from the offset runs; "cover always uncovered"
    (cut lag forced to b) gives exactly 0; the literal "never uncovered"
    (cover always true, cut=a, last=b) instead marks EVERY pair a shadow, so I
    expect it NOT to be 0 (the 0 prediction only fits the forced-uncovered
    reading); sizes-only cover (len compare) differs from the true cover.
  * Calibration: P8 N=8 -> 8, P8 N=16 -> 18, P9 N=9 -> 100/9.
"""
import sys
import time
from collections import Counter
from fractions import Fraction
from multiprocessing import Pool

OFFSETS = (7919, 4003, 10007)
IMPLS = ("dict", "counter", "frozenset", "bitmask")


def landing_list(P, w, T, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]


def legal_bitmask(P, w, T, L):
    """Bit t set iff press at tick t with lag L is legal; built from a P-periodic
    pattern repeated over T bits (independent construction from landing_list)."""
    pat = 0
    for r in range(P):
        if r >= w or ((r + L) % P) < w:
            pat |= 1 << r
    reps = T // P + 1
    full = 0
    for _ in range(reps):
        full = (full << P) | pat
    # pattern bits for residue r sit at positions r, r+P, ... ; (full<<P)|pat keeps this
    return full & ((1 << T) - 1)


def shadow(a, b, cov, na, nb):
    cut = b if not cov else (a if na > 0 else None)
    last = b if nb > 0 else a
    return last != cut


def run_job(args):
    """Returns {variant: {(w,r): [cnt_by_b...]}} for one (P, base)."""
    P, base, variants = args
    Nmax = 2 * P + 1
    out = {v: {} for v in variants}
    for w in range(1, P):
        for r in range(P):
            T = base + r
            lands = {L: landing_list(P, w, T, L) for L in range(1, Nmax + 1)}
            n = {L: len(lands[L]) for L in lands}
            masks = {L: legal_bitmask(P, w, T, L) << L for L in lands}
            dicts = counters = fsets = None
            if "dict" in variants:
                dicts = {L: dict.fromkeys(lands[L], True) for L in lands}
            if "counter" in variants:
                counters = {L: Counter(lands[L]) for L in lands}
            if "frozenset" in variants:
                fsets = {L: frozenset(lands[L]) for L in lands}
            for v in variants:
                cnt = [0] * (Nmax + 1)
                for b in range(2, Nmax + 1):
                    c = 0
                    for a in range(1, b):
                        if v == "dict":
                            da = dicts[a]
                            cov = all(x in da for x in lands[b])
                        elif v == "counter":
                            cov = not (counters[b] - counters[a])
                        elif v == "frozenset":
                            cov = fsets[b] <= fsets[a]
                        elif v == "bitmask":
                            cov = (masks[b] & ~masks[a]) == 0
                        elif v == "sizes":
                            cov = n[b] <= n[a]
                        elif v == "always_covered":
                            cov = True
                        elif v == "always_uncovered":
                            cov = False
                        else:
                            raise ValueError(v)
                        if shadow(a, b, cov, n[a], n[b]):
                            c += 1
                    cnt[b] = c
                out[v][(w, r)] = cnt
    return out


def averages(res, P):
    Nmax = 2 * P + 1
    perb = [0] * (Nmax + 1)
    for cnt in res.values():
        for b in range(2, Nmax + 1):
            perb[b] += cnt[b]
    avg = {}
    run = 0
    for N in range(2, Nmax + 1):
        run += perb[N]
        avg[N] = Fraction(run, P)
    return avg


def flats(avg, P):
    return [N for N in range(P - 1, 2 * P + 2) if avg[N] == avg[N - 1]]


def fmt(f):
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def main():
    t0 = time.time()
    jobs = []
    keys = []
    for P in (10, 11):
        for off in OFFSETS:
            jobs.append((P, off, IMPLS + ("sizes", "always_covered", "always_uncovered")))
            keys.append((P, off))
        jobs.append((P, 0, ("dict", "sizes")))
        keys.append((P, 0))
    # calibration
    for P in (8, 9):
        jobs.append((P, 7919, ("dict",)))
        keys.append((P, 7919))
    # largest jobs first
    order = sorted(range(len(jobs)), key=lambda i: -(jobs[i][0] * (jobs[i][1] + 1)))
    with Pool(4) as pool:
        results = pool.map(run_job, [jobs[i] for i in order], chunksize=1)
    res = {keys[i]: results[j] for j, i in enumerate(order)}
    print(f"compute done in {time.time()-t0:.1f}s")

    ok = True
    notes = []
    # calibration
    cal = {
        (8, 8): Fraction(8), (8, 16): Fraction(18), (9, 9): Fraction(100, 9)}
    for (P, N), want in cal.items():
        got = averages(res[(P, 7919)]["dict"], P)[N]
        good = got == want
        print(f"calibration P{P} N={N}: got {fmt(got)} want {fmt(want)} {'ok' if good else 'MISMATCH'}")
        ok &= good

    claim = {(10, "P"): Fraction(15), (10, "2P"): Fraction(65, 2),
             (11, "P"): Fraction(215, 11), (11, "2P"): Fraction(460, 11)}
    for P in (10, 11):
        for off in OFFSETS:
            r = res[(P, off)]
            # exact per-(w,r,b) equality of all four cover implementations
            for impl in IMPLS[1:]:
                same = r[impl] == r["dict"]
                print(f"P{P} off={off}: per-(w,r,b) counts {impl} == dict : {same}")
                ok &= same
            av = {i: averages(r[i], P) for i in r}
            for impl in IMPLS[1:]:
                same = av[impl] == av["dict"]
                ok &= same
            d = av["dict"]
            print(f"P{P} off={off}: avg N=P-1..2P+1 = " +
                  ", ".join(f"{N}:{fmt(d[N])}" for N in range(P - 1, 2 * P + 2)))
            fl = flats(d, P)
            print(f"P{P} off={off}: flats over N=P-1..2P+1 = {fl}  (expect {[P, 2*P]})")
            ok &= fl == [P, 2 * P]
            cP, c2P = d[P], d[2 * P]
            ok &= cP == claim[(P, "P")] and c2P == claim[(P, "2P")]
            print(f"P{P} off={off}: avg(N=P)={fmt(cP)} (claim {fmt(claim[(P,'P')])}), "
                  f"avg(N=2P)={fmt(c2P)} (claim {fmt(claim[(P,'2P')])})")
            # controls
            for ctl in ("sizes", "always_covered", "always_uncovered"):
                a = av[ctl]
                diff = [N for N in range(2, 2 * P + 2) if a[N] != d[N]]
                print(f"  control {ctl}: avg(P)={fmt(a[P])} avg(2P)={fmt(a[2*P])} "
                      f"differs from dict at {len(diff)} of {2*P} N")
            ok &= av["always_uncovered"][2 * P] == 0 and all(
                v == 0 for v in av["always_uncovered"].values())
            ok &= av["sizes"] != d
        # base-0 control
        z = averages(res[(P, 0)]["dict"], P)
        zs = averages(res[(P, 0)]["sizes"], P)
        d = averages(res[(P, 7919)]["dict"], P)
        diffz = [N for N in range(2, 2 * P + 2) if z[N] != d[N]]
        print(f"P{P} base-0 control: avg(P)={fmt(z[P])} avg(2P)={fmt(z[2*P])} "
              f"differs from offset-7919 at {len(diffz)} N; flats={flats(z, P)}")
        ok &= bool(diffz)
        # offsets agree with each other
        ok &= averages(res[(P, 4003)]["dict"], P) == d == averages(res[(P, 10007)]["dict"], P)
        print(f"P{P} offsets 4003/7919/10007 give identical average vectors: "
              f"{averages(res[(P,4003)]['dict'],P)==d==averages(res[(P,10007)]['dict'],P)}")

    # summary numbers
    s = {}
    for P in (10, 11):
        d = averages(res[(P, 7919)]["dict"], P)
        s[P] = (fmt(d[P]), fmt(d[2 * P]))
    ac = averages(res[(10, 7919)]["always_covered"], 10)
    print(f"always_covered (cover=True, cut=a,last=b) P10 avg(N=P)={fmt(ac[10])} (all pairs shadow)")
    print(f"total time {time.time()-t0:.1f}s")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} Counter==dict==frozenset==bitmask at offsets {OFFSETS}; "
          f"P10 avg(N=10)={s[10][0]}, avg(N=20)={s[10][1]}; P11 avg(N=11)={s[11][0]}, avg(N=22)={s[11][1]}; "
          f"flats [P,2P]; forced-uncovered ignore-cover=0, sizes-only and base-0 differ")


if __name__ == "__main__":
    main()
