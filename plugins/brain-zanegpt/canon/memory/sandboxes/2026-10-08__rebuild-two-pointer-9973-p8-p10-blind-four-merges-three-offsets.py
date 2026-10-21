"""Blind rebuild: sorted-landing-list two-pointer merge cover test at offset 9973.

PREDICTION (written before the first run, never edited):
  * Shadow = (b covered by a) and (b lands something) -- derived by hand from the
    cut/last-landing definitions.  Cover decided by early-exit merge over ascending
    landing lists == set-subset (dict) == bitmask (b & ~a == 0) == arithmetic
    membership predicate, for every (width, horizon, b), all offsets.
  * At base 9973, lags a,b in 1..N, horizons T=9973+r r=0..P-1, divided by P:
      P8 : N=8 -> 8,      N=16 -> 18
      P9 : N=9 -> 100/9,  N=18 -> 220/9
      P10: N=10 -> 15,    N=20 -> 65/2
  * Flats over N=P-1..2P+1 are exactly [P, 2P].  "Flat" is ambiguous, so I declare
    two readings before running: flat_prev(N): avg(N)==avg(N-1); flat_next(N):
    avg(N)==avg(N+1) (N<=2P).  PASS needs at least one reading to give exactly [P,2P]
    for all three P.  (I expect flat_prev, i.e. lag N adds nothing on average.)
  * Lag range assumed 1..N (a>=1).  Degenerate convention: if b covered and a empty,
    cut=None, last=a -> counted as shadow (only matters at tiny T, i.e. controls).
  * Controls: base-0 differs from the claimed numbers/flats; ignore-cover forced False
    (shadow never) and forced True (shadow iff b nonempty) and length-only
    (covered := len(b)<=len(a)) do NOT reproduce the numbers/flats.
  * Edge: merge returns True for empty b, False for b longer than a (duplicate-free
    lists), False whenever b[-1] > a[-1]; all landing lists strictly ascending.
  * Runtime under ~3 min.
"""
import sys, time, random
from fractions import Fraction
from bisect import bisect_left

T0 = time.perf_counter()
PS = (8, 9, 10)
CLAIM = {8: (Fraction(8), Fraction(18)), 9: (Fraction(100, 9), Fraction(220, 9)),
         10: (Fraction(15), Fraction(65, 2))}
OFFSETS = (9973, 3571, 6007, 43)   # my own fixture (3571/6007/43 beyond 9973)
BASE0 = 0


# ---------------- landing sets ----------------
def legal(P, w, L, t):
    return (t % P) >= w or ((t + L) % P) < w


def landing_list(P, w, L, T):
    return [t + L for t in range(T) if legal(P, w, L, t)]


# ---------------- cover implementations over ascending lists ----------------
def cover_set(a, b):                      # dict/set reference
    return set(b) <= set(a)


def cover_walkb(a, b):                    # walk b, advance a, early exit
    i, n = 0, len(a)
    for x in b:
        while i < n and a[i] < x:
            i += 1
        if i == n or a[i] != x:
            return False
    return True


def cover_classic(a, b):                  # classic two-index merge with prechecks
    if not b:
        return True
    if len(b) > len(a) or b[-1] > a[-1] or b[0] < a[0]:
        return False
    i = j = 0
    na, nb = len(a), len(b)
    while j < nb:
        if i >= na:
            return False
        if a[i] < b[j]:
            i += 1
        elif a[i] == b[j]:
            i += 1; j += 1
        else:
            return False                  # a passed b[j] -> b[j] missing
    return True


def cover_desc(a, b):                     # merge from the descending end
    i, j = len(a) - 1, len(b) - 1
    while j >= 0:
        if i < 0:
            return False
        if a[i] > b[j]:
            i -= 1
        elif a[i] == b[j]:
            i -= 1; j -= 1
        else:
            return False
    return True


def cover_bisect(a, b):                   # bisect-based, galloping lower bound
    lo, n = 0, len(a)
    for x in b:
        lo = bisect_left(a, x, lo)
        if lo == n or a[lo] != x:
            return False
    return True


MERGES = {"walkb": cover_walkb, "classic": cover_classic, "desc": cover_desc,
          "bisect": cover_bisect}


def shadow_flag(covered, a_ne, b_ne):
    cut = ('b' if not covered else ('a' if a_ne else None))
    last = 'b' if b_ne else 'a'
    return last != cut


# ---------------- vector builders ----------------
def vec_lists(P, base, coverfn, mode=None):
    """mode None: real cover; 'F'/'T': forced; 'len': length-only."""
    vec = {}
    nmax = 2 * P + 1
    for w in range(1, P):
        for r in range(P):
            T = base + r
            L = {l: landing_list(P, w, l, T) for l in range(1, nmax + 1)}
            for b in range(2, nmax + 1):
                c = 0
                lb = L[b]
                for a in range(1, b):
                    la = L[a]
                    if mode == 'F':
                        cov = False
                    elif mode == 'T':
                        cov = True
                    elif mode == 'len':
                        cov = len(lb) <= len(la)
                    else:
                        cov = coverfn(la, lb)
                    if shadow_flag(cov, bool(la), bool(lb)):
                        c += 1
                vec[(w, r, b)] = c
    return vec


def vec_mask(P, base):
    vec = {}
    nmax = 2 * P + 1
    for w in range(1, P):
        pats = {}
        for l in range(1, nmax + 1):
            pats[l] = sum(1 << rho for rho in range(P) if rho >= w or ((rho + l) % P) < w)
        for r in range(P):
            T = base + r
            k = -(-T // P) if T else 0
            rep = ((1 << (P * k)) - 1) // ((1 << P) - 1) if k else 0
            M = {}
            for l in range(1, nmax + 1):
                m = (pats[l] * rep) & ((1 << T) - 1)
                M[l] = m << l
            for b in range(2, nmax + 1):
                c = 0
                for a in range(1, b):
                    cov = (M[b] & ~M[a]) == 0
                    if shadow_flag(cov, M[a] != 0, M[b] != 0):
                        c += 1
                vec[(w, r, b)] = c
    return vec


def vec_arith(P, base):
    """No lists: enumerate b's landings by arithmetic, test membership in a by predicate."""
    vec = {}
    nmax = 2 * P + 1
    for w in range(1, P):
        for r in range(P):
            T = base + r
            for b in range(2, nmax + 1):
                c = 0
                b_ne = any(legal(P, w, b, t) for t in range(T))
                for a in range(1, b):
                    a_ne = any(legal(P, w, a, t) for t in range(T))
                    cov = True
                    for t in range(T):
                        if legal(P, w, b, t):
                            x = t + b - a            # candidate source tick for lag a
                            if not (0 <= x < T and legal(P, w, a, x)):
                                cov = False
                                break
                    if shadow_flag(cov, a_ne, b_ne):
                        c += 1
                vec[(w, r, b)] = c
    return vec


def averages(P, vec):
    nmax = 2 * P + 1
    col = {b: 0 for b in range(2, nmax + 1)}
    for (w, r, b), c in vec.items():
        col[b] += c
    tot, run = {1: 0}, 0
    for N in range(2, nmax + 1):
        run += col[N]
        tot[N] = run
    return {N: Fraction(tot[N], P) for N in range(2, nmax + 1)}


def flats(P, avg):
    prev = [N for N in range(P - 1, 2 * P + 2) if N - 1 in avg and avg[N] == avg[N - 1]]
    nxt = [N for N in range(P - 1, 2 * P + 1) if N + 1 in avg and avg[N] == avg[N + 1]]
    return prev, nxt


def claim_ok(P, avg):
    return (avg[P], avg[2 * P]) == CLAIM[P]


def flats_ok(P, avg):
    pr, nx = flats(P, avg)
    return pr == [P, 2 * P] or nx == [P, 2 * P]


# ---------------- edge tests ----------------
def edge_tests():
    ok = True
    msgs = []
    for name, f in list(MERGES.items()) + [("set", cover_set)]:
        checks = [
            (f([], []), True), (f([1, 2], []), True), (f([], [3]), False),
            (f([1, 2, 3], [1, 2, 3, 4]), False),          # b longer than a
            (f([1, 5, 9], [1, 5, 10]), False),             # b max beyond a max
            (f([1, 5, 9], [1, 5, 9]), True), (f([1, 2, 3, 4], [2, 4]), True),
            (f([2, 4, 6], [1]), False), (f([2, 4, 6], [3, 4]), False),
            (f([1, 3, 5], [5]), True), (f([1, 3, 5], [7]), False),
        ]
        for k, (got, exp) in enumerate(checks):
            if got != exp:
                ok = False
                msgs.append(f"{name} edge#{k}")
    rnd = random.Random(12345)
    for _ in range(4000):
        a = sorted(rnd.sample(range(40), rnd.randint(0, 20)))
        if rnd.random() < 0.5 and a:
            b = sorted(rnd.sample(a, rnd.randint(0, len(a))))
        else:
            b = sorted(rnd.sample(range(40), rnd.randint(0, 12)))
        ref = cover_set(a, b)
        for name, f in MERGES.items():
            if f(a, b) != ref:
                ok = False
                msgs.append(f"{name} fuzz {a} {b}")
                break
    # early exit really exits early: instrumented walk on a big mismatch at the front
    class Cnt(list):
        reads = 0
        def __getitem__(self, i):
            Cnt.reads += 1
            return list.__getitem__(self, i)
    big_a = Cnt(range(1, 100000, 2)); big_b = Cnt([2] + list(range(3, 100000, 2)))
    cover_walkb(big_a, big_b)
    if Cnt.reads > 10:
        ok = False; msgs.append("no early exit")
    return ok, msgs


def landing_sanity(P, base):
    bad = 0
    for w in range(1, P):
        for l in range(1, 2 * P + 2):
            for r in range(P):
                x = landing_list(P, w, l, base + r)
                if any(x[i] >= x[i + 1] for i in range(len(x) - 1)):
                    bad += 1
    return bad


def main():
    ok_edge, msgs = edge_tests()
    print("edge tests:", ok_edge, msgs)
    allok = ok_edge
    summary = {}
    for P in PS:
        print(f"--- P{P}")
        dup = landing_sanity(P, 9973)
        print(f"  duplicate/ascending violations (9973): {dup}")
        allok &= (dup == 0)
        for base in OFFSETS:
            t1 = time.perf_counter()
            ref = vec_lists(P, base, cover_set)
            vs = {n: vec_lists(P, base, f) for n, f in MERGES.items()}
            vm = vec_mask(P, base)
            same = {n: v == ref for n, v in vs.items()}
            same["mask"] = vm == ref
            if base in (9973, 43):                       # arithmetic impl is slow: 2 offsets
                va = vec_arith(P, base) if (base == 43 or P == 8 or True) else None
                same["arith"] = va == ref
            avg = averages(P, ref)
            vals = (avg[P], avg[2 * P])
            pr, nx = flats(P, avg)
            allsame = all(same.values())
            allok &= allsame
            print(f"  base {base}: impls==dict {same}  avg(P),avg(2P)={vals[0]},{vals[1]}"
                  f" claim_ok={claim_ok(P, avg)} flat_prev={pr} flat_next={nx}"
                  f" [{time.perf_counter()-t1:.1f}s]")
            if base == 9973:
                summary[P] = (vals, pr, nx, claim_ok(P, avg), flats_ok(P, avg))
                allok &= claim_ok(P, avg) and flats_ok(P, avg)
                print("   avg N=P-1..2P+1:", [str(avg[N]) for N in range(P - 1, 2 * P + 2)])
            else:
                print(f"   (offset {base}) claim_ok={claim_ok(P, avg)} flats_ok={flats_ok(P, avg)}")
        # controls (at 9973 for ignore/len; base-0 uses real cover)
        cb = vec_lists(P, BASE0, cover_walkb)
        ab = averages(P, cb)
        print(f"  CONTROL base-0: avg(P),avg(2P)={ab[P]},{ab[2*P]} claim_ok={claim_ok(P, ab)}"
              f" flats={flats(P, ab)} flats_ok={flats_ok(P, ab)}")
        ctrl_differs = not (claim_ok(P, ab) and flats_ok(P, ab))
        for nm, mode in (("ignore-cover=False", 'F'), ("ignore-cover=True", 'T'), ("length-only", 'len')):
            cv = vec_lists(P, 9973, None, mode)
            ac = averages(P, cv)
            same_ref = cv == vec_lists(P, 9973, cover_set) if False else None
            repro = claim_ok(P, ac) and flats_ok(P, ac)
            print(f"  CONTROL {nm}: avg(P),avg(2P)={ac[P]},{ac[2*P]} flats={flats(P, ac)} reproduces={repro}")
            ctrl_differs &= not repro
        print(f"  controls all differ: {ctrl_differs}")
        allok &= ctrl_differs
    el = time.perf_counter() - T0
    key = "; ".join(f"P{P}: N=P {summary[P][0][0]}, N=2P {summary[P][0][1]}, flats {summary[P][1] if summary[P][3] and summary[P][1]==[P,2*P] else summary[P][2]}"
                    for P in PS)
    print(f"elapsed {el:.1f}s")
    print(f"RESULT: {'PASS' if allok else 'FAIL'} merge(walkb/classic/desc/bisect)==set==mask==arith; {key}; controls differ; {el:.0f}s")


main()
