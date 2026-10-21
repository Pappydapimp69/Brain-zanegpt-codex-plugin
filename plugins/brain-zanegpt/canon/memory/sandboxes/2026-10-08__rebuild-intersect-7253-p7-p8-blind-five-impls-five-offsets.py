#!/usr/bin/env python3
"""Blind rebuild: does an "intersection size == size of b" cover test reproduce
the dict-membership period-average shadow counts at offset (base) 7253?

PREDICTION (written before the first run, never edited afterwards):
  Relations, not new numbers (only the calibration numbers given are known:
  P8 N=8 -> 8, P8 N=16 -> 18, P9 N=9 -> 100/9):
  1. For moduli 7 and 8 at base 7253 (and also at my other bases 29, 4999,
     9011, and hold-out modulus 9), the intersection-size cover test, the
     frozenset-subset test, the bitmask test and the arithmetic predicate
     all give per-(width,horizon,b) shadow count vectors IDENTICAL to the
     dict-membership reference, hence identical period averages at every
     N in 2..2P+1.  Reason: landings of one lag are t+L with distinct t, so
     they are duplicate-free sets, and len(A & B) == len(B)  <=>  B subset A.
  2. "Flat" is read as avg(N) == avg(N-1) (no increment from adding lag N).
     Prediction: over N in P-1..2P+1 the flat N are exactly [P, 2P] for
     P=7,8 at the large bases (4999, 7253, 9011).  Small base 29 and
     hold-out P=9 are NOT predicted (informational only).
  3. Intersection-size test is only valid on deduplicated collections: with a
     list b containing repeats, len(set(A) & set(B)) != len(b) although B is
     covered -> a false "uncovered".  Natural landings never repeat, so this
     does not bite the real model.  Empty b: intersection size 0 == 0 ->
     covered (vacuous), same as dict/subset/bitmask/arithmetic.
  4. Controls: base 0 (horizon T=r only) gives different averages than base
     7253; ignore-cover forced False gives 0 shadows at large base; ignore-
     cover forced True gives every pair a shadow, avg = (P-1)*N*(N-1)/2;
     sizes-only cover len(b) <= len(a) differs from dict for some N
     (break attempt succeeds).
  5. Calibration P8 N=8 -> 8, P8 N=16 -> 18, P9 N=9 -> 100/9 reproduced by the
     dict reference at base 7253 (if not, I will report the base that does).
  PASS criterion (fixed in advance): all four alternative cover tests equal
  dict everywhere on all fixtures, and flats == [P, 2P] for P=7,8 at 7253.

Model: period P, width w in 1..P-1, role B available at tick t iff t%P < w.
Press at tick t, lag L legal iff (t%P)>=w or ((t+L)%P)<w; lands at t+L.
Landing set(L,T) = {t+L : 0<=t<T, legal}.  b covered by a iff landings(b) is a
subset of landings(a).  cut lag = b if uncovered, else a if a lands anything
(else None); last-landing lag = b if b lands anything else a; shadow iff
last != cut.  Count over widths and pairs 1<=a<b<=N, horizons T=base+r,
r=0..P-1, divided by P (Fraction).
"""
import sys
import time
from bisect import bisect_left
from fractions import Fraction
from collections import Counter

T0 = time.time()


# ---------------------------------------------------------------- model prep
def legal(t, L, P, w):
    return (t % P) >= w or ((t + L) % P) < w


class Prep:
    """Per (P,w,base): legal press ticks per lag over the largest horizon."""

    def __init__(self, P, w, base, Lmax):
        self.P, self.w, self.base, self.Lmax = P, w, base, Lmax
        Tmax = base + P - 1
        self.legal_ts = {}
        self.bits = {}  # bit t set iff legal(t, L)
        for L in range(1, Lmax + 1):
            ts = [t for t in range(Tmax) if legal(t, L, P, w)]
            self.legal_ts[L] = ts
            s = 0
            for t in ts:
                s |= 1 << t
            self.bits[L] = s

    def lands(self, T):
        """list-of-landing ticks (ascending) for each lag at horizon T."""
        out = {}
        for L in range(1, self.Lmax + 1):
            ts = self.legal_ts[L]
            k = bisect_left(ts, T)
            out[L] = [t + L for t in ts[:k]]
        return out


# ----------------------------------------------------------- cover factories
# Each factory takes ctx dict {P,w,T,Lmax,lands} and returns cov(a,b)->bool
def f_dict(ctx):
    d = {L: {x: True for x in v} for L, v in ctx["lands"].items()}
    lands = ctx["lands"]

    def cov(a, b):
        da = d[a]
        return all(x in da for x in lands[b])
    return cov


def f_inter(ctx):
    s = {L: set(v) for L, v in ctx["lands"].items()}

    def cov(a, b):
        return len(s[a] & s[b]) == len(s[b])
    return cov


def f_frozen(ctx):
    s = {L: frozenset(v) for L, v in ctx["lands"].items()}

    def cov(a, b):
        return s[b] <= s[a]
    return cov


def f_bitmask(ctx):
    P, w, T = ctx["P"], ctx["w"], ctx["T"]
    prep = ctx["prep"]
    lowmask = (1 << T) - 1
    m = {L: (prep.bits[L] & lowmask) << L for L in range(1, ctx["Lmax"] + 1)}

    def cov(a, b):
        return (m[b] & ~m[a]) == 0
    return cov


def f_arith(ctx):
    P, w, T = ctx["P"], ctx["w"], ctx["T"]

    def cov(a, b):
        # every legal press t of lag b (landing x=t+b) must be a landing of a:
        # s=x-a in [0,T) and legal(s, a)
        d = b - a
        for t in range(T):
            if (t % P) >= w or ((t + b) % P) < w:  # legal b-press
                s = t + d
                if s >= T or not ((s % P) >= w or ((s + a) % P) < w):
                    return False
        return True
    return cov


def f_sizes(ctx):
    lands = ctx["lands"]

    def cov(a, b):
        return len(lands[b]) <= len(lands[a])
    return cov


def f_false(ctx):
    return lambda a, b: False


def f_true(ctx):
    return lambda a, b: True


IMPLS = {"dict": f_dict, "inter": f_inter, "frozen": f_frozen,
         "bitmask": f_bitmask, "arith": f_arith,
         "sizes": f_sizes, "ign_false": f_false, "ign_true": f_true}

EDGE_COUNT = Counter()


def is_shadow(cov, a_ne, b_ne):
    cut = (None if not a_ne else "a") if cov else "b"
    # represent as lag-identity labels
    last = "b" if b_ne else "a"
    return last != cut


def run(P, base, impl, preps=None):
    """returns dict (w,r,b)->count of shadowing a, for b in 2..2P+1"""
    Lmax = 2 * P + 1
    fac = IMPLS[impl]
    out = {}
    for w in range(1, P):
        prep = preps[w] if preps else Prep(P, w, base, Lmax)
        for r in range(P):
            T = base + r
            lands = prep.lands(T)
            ctx = {"P": P, "w": w, "T": T, "Lmax": Lmax, "lands": lands,
                   "prep": prep}
            cov = fac(ctx)
            for b in range(2, Lmax + 1):
                bne = len(lands[b]) > 0
                c = 0
                for a in range(1, b):
                    ane = len(lands[a]) > 0
                    if is_shadow(cov(a, b), ane, bne):
                        c += 1
                out[(w, r, b)] = c
    return out


def avgs(P, vec):
    """avg(N) for N=1..2P+1 as Fraction"""
    tot = Counter()
    for (w, r, b), c in vec.items():
        tot[b] += c
    res = {1: Fraction(0)}
    run_ = 0
    for N in range(2, 2 * P + 2):
        run_ += tot[N]
        res[N] = Fraction(run_, P)
    return res


def flats(P, av):
    return [N for N in range(P - 1, 2 * P + 2) if N >= 2 and av[N] == av[N - 1]
            and N >= P]


def fmt(av, P):
    return " ".join("%d:%s" % (N, av[N]) for N in range(P - 1, 2 * P + 2))


# ------------------------------------------------------------------- main
results = {}
fails = []
log = print

CORE = ["dict", "inter", "frozen", "bitmask"]
# (P, base): which impls to run beyond CORE
FIXTURE = []
for P in (7, 8):
    for base in (0, 29, 4999, 7253, 9011):
        FIXTURE.append((P, base))
for base in (0, 29, 7253):
    FIXTURE.append((9, base))
ARITH_OK = {(7, 29), (8, 29), (9, 29), (7, 0), (8, 0), (9, 0),
            (7, 4999), (8, 7253), (7, 7253)}
CONTROL = {(P, base) for (P, base) in FIXTURE if base in (29, 7253, 0)}

dict_av = {}
for (P, base) in FIXTURE:
    Lmax = 2 * P + 1
    preps = {w: Prep(P, w, base, Lmax) for w in range(1, P)}
    # natural landings must be duplicate-free
    for w in range(1, P):
        for r in (0, P - 1):
            for L, v in preps[w].lands(base + r).items():
                assert len(v) == len(set(v)), "dup landing!"
    vecs = {}
    names = list(CORE)
    if (P, base) in ARITH_OK:
        names.append("arith")
    if (P, base) in CONTROL:
        names += ["sizes", "ign_false", "ign_true"]
    for nm in names:
        vecs[nm] = run(P, base, nm, preps)
    ref = vecs["dict"]
    av = avgs(P, ref)
    dict_av[(P, base)] = av
    fl = flats(P, av)
    eq = {}
    for nm in names:
        if nm in ("dict",):
            continue
        eq[nm] = (vecs[nm] == ref)
    for nm in CORE[1:] + (["arith"] if "arith" in vecs else []):
        if not eq[nm]:
            fails.append("P%d base%d %s != dict" % (P, base, nm))
    # also all-N average equality (prefix sums)
    for nm in CORE[1:] + (["arith"] if "arith" in vecs else []):
        if avgs(P, vecs[nm]) != av:
            fails.append("P%d base%d %s avg != dict" % (P, base, nm))
    log("P=%d base=%d  t=%.1fs" % (P, base, time.time() - T0))
    log("   dict avg  " + fmt(av, P))
    log("   flats(avg[N]==avg[N-1], N>=P): %s   target [%d,%d]  avg(P)=%s"
        % (fl, P, 2 * P, av[P]))
    log("   vector-equal to dict: " + ", ".join(
        "%s=%s" % (k, v) for k, v in eq.items()))
    if (P, base) in CONTROL:
        for nm in ("sizes", "ign_false", "ign_true"):
            a2 = avgs(P, vecs[nm])
            log("   control %-9s avg %s  (equal to dict avgs: %s)"
                % (nm, fmt(a2, P), a2 == av))
    results[(P, base)] = {"flats": fl, "av": av}

# ----------------------------------------------------------- calibrations
log("CALIBRATION (dict, base 7253 and base 4999):")
calib_ok = True
for base in (7253, 4999, 9011):
    c1 = dict_av[(8, base)][8]
    c2 = dict_av[(8, base)][16] if (8, base) in dict_av else None
    log("  base %d: P8 N=8 -> %s, P8 N=16 -> %s" % (base, c1, c2))
c9 = dict_av[(9, 7253)][9]
log("  base 7253: P9 N=9 -> %s (expect 100/9)" % c9)
calib_ok = (dict_av[(8, 7253)][8] == 8 and dict_av[(8, 7253)][16] == 18
            and c9 == Fraction(100, 9))
log("  calibration matches given numbers: %s" % calib_ok)

# ------------------------------------------------------- base-0 control
for P in (7, 8):
    d0, d1 = dict_av[(P, 0)], dict_av[(P, 7253)]
    log("base-0 control P=%d: differs from base 7253: %s ; base0 avgs %s"
        % (P, d0 != d1, fmt(d0, P)))

# ------------------------------------------------------------ edge cases
log("EDGE CASES:")


def cov_variants(A, B):
    A, B = list(A), list(B)
    return {
        "dict": all(x in {y: 1 for y in A} for x in B),
        "inter": len(set(A) & set(B)) == len(set(B)),
        "frozen": frozenset(B) <= frozenset(A),
    }


edge_ok = True
for A, B in [([1, 2, 3], []), ([], []), ([], [5]), ([1, 2], [1, 2]),
             ([1, 2, 3], [2, 3]), ([1, 2], [2, 3])]:
    v = cov_variants(A, B)
    agree = len(set(v.values())) == 1
    edge_ok &= agree
    log("  A=%s B=%s -> %s agree=%s" % (A, B, v, agree))
# duplicates in b as a LIST: raw len(A & B) == len(b_list) breaks
A, Bl = [1, 2, 3], [1, 1, 2]
raw = len(set(A) & set(Bl)) == len(Bl)
truth = all(x in set(A) for x in Bl)
log("  dup-list b=%s: raw intersection-size says covered=%s, truth=%s "
    "(break expected when raw != truth)" % (Bl, raw, truth))
dup_break = (raw != truth)
# empty landing in the real model: base 0, r=0 -> T=0, everything empty
for impl in CORE + ["arith"]:
    v = run(7, 0, impl)
    EDGE_COUNT[impl] = sum(v.values())
log("  empty-landing (T=0 included, P=7 base 0) total shadows per impl: %s"
    % dict(EDGE_COUNT))
edge_ok &= len(set(EDGE_COUNT.values())) == 1

# ------------------------------------------------------------- verdict
flat_ok = all(results[(P, 7253)]["flats"] == [P, 2 * P] for P in (7, 8))
other_flat = {"P%d@%d" % k: v["flats"] for k, v in results.items()
              if v["flats"] != [k[0], 2 * k[0]]}
ctrl_ok = all(dict_av[(P, 0)] != dict_av[(P, 7253)] for P in (7, 8))
log("flats ok at 7253 for P=7,8: %s ; other fixtures with non-[P,2P] flats: %s"
    % (flat_ok, other_flat))
log("failures: %s ; edge_ok=%s dup_break=%s ctrl_base0_differs=%s elapsed=%.1fs"
    % (fails, edge_ok, dup_break, ctrl_ok, time.time() - T0))
ok = (not fails) and flat_ok and edge_ok
a7, a8 = dict_av[(7, 7253)], dict_av[(8, 7253)]
print("RESULT: %s intersect==dict==frozen==bitmask(==arith where run) on %d "
      "fixtures; flats@7253 P7=%s P8=%s; avg P7 N=7:%s N=14:%s; P8 N=8:%s "
      "N=16:%s; P9 N=9:%s; calib=%s base0_differs=%s other_flat_anomalies=%s"
      % ("PASS" if ok else "FAIL", len(FIXTURE), results[(7, 7253)]["flats"],
         results[(8, 7253)]["flats"], a7[7], a7[14], a8[8], a8[16],
         dict_av[(9, 7253)][9], calib_ok, ctrl_ok, other_flat))
