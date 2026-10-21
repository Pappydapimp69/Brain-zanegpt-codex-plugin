"""Blind rebuild: run-length INTERVAL lag cover at offset 8209 (and other offsets).

PREDICTION (written before the first run, never edited):
  * Interval-run cover == dict-set cover == bitmask cover on every
    (width, horizon, b) shadow vector, for all offsets tried (incl. 43, 3571, 9001, 8209).
  * "Flat" = N in P-1..2P+1 where avg(N) == avg(N-1) (adding lag b=N adds no shadows on average).
    For offset 8209 and P in {8,9,10} the flats are exactly [P, 2P].
  * Averages: N=P -> 8, 100/9, 15 (P=8,9,10); N=2P -> 18, 220/9, 65/2.
  * Base-0 control (T=r, r<P) differs from these numbers.
  * Ignore-subset rule (uncovered forced False, and also forced True) does NOT reproduce them.
  * Length-only rule (uncovered iff |landings b| > |landings a|) does NOT reproduce them.
  * Other long offsets (3571, 9001) give the same numbers as 8209 (implementation- and offset-independent
    at long horizons); tiny offset 43 may or may not.
"""
import sys, time, random
from fractions import Fraction
from bisect import bisect_right

# ---------- model ----------
def legal(t, L, P, w):
    return (t % P) >= w or ((t + L) % P) < w

# ---------- implementation 1: dict/set ----------
class DictImpl:
    def __init__(s, P, w, T, Lmax):
        s.S = [None] + [set(t + L for t in range(T) if legal(t, L, P, w)) for L in range(1, Lmax + 1)]
    def size(s, L): return len(s.S[L])
    def nonempty(s, L): return len(s.S[L]) > 0
    def covered(s, a, b): return s.S[b] <= s.S[a]

# ---------- implementation 2: run-length intervals ----------
def build_runs(P, w, T, L):
    """maximal runs [start,end] of consecutive landings (landings come in increasing order)."""
    runs = []
    for t in range(T):
        if legal(t, L, P, w):
            x = t + L
            if runs and runs[-1][1] + 1 == x:
                runs[-1][1] = x
            else:
                runs.append([x, x])
    return runs

def runs_contained_twoptr(B, A):
    """every run of B lies inside a single run of A (A maximal runs). two-pointer."""
    j = 0
    nA = len(A)
    for (s, e) in B:
        while j < nA and A[j][1] < s:
            j += 1
        if j >= nA or A[j][0] > s or A[j][1] < e:
            return False
    return True

def runs_contained_bisect(B, A):
    starts = [r[0] for r in A]
    for (s, e) in B:
        i = bisect_right(starts, s) - 1
        if i < 0 or A[i][1] < e:
            return False
    return True

class RunImpl:
    def __init__(s, P, w, T, Lmax, use_bisect=False):
        s.R = [None] + [build_runs(P, w, T, L) for L in range(1, Lmax + 1)]
        s.cont = runs_contained_bisect if use_bisect else runs_contained_twoptr
    def size(s, L): return sum(e - st + 1 for st, e in s.R[L])
    def nonempty(s, L): return len(s.R[L]) > 0
    def covered(s, a, b): return s.cont(s.R[b], s.R[a])

# ---------- implementation 3: bitmask / arithmetic ----------
class MaskImpl:
    def __init__(s, P, w, T, Lmax):
        full_tile_cnt = T // P + 1
        rep = ((1 << (P * full_tile_cnt)) - 1) // ((1 << P) - 1)  # 1 at every multiple of P
        lim = (1 << T) - 1
        s.M = [None]
        for L in range(1, Lmax + 1):
            pat = 0
            for res in range(P):
                if res >= w or ((res + L) % P) < w:
                    pat |= 1 << res
            legal_mask = (pat * rep) & lim
            s.M.append(legal_mask << L)
    def size(s, L): return bin(s.M[L]).count("1")
    def nonempty(s, L): return s.M[L] != 0
    def covered(s, a, b): return (s.M[b] & ~s.M[a]) == 0

# ---------- shadow logic ----------
def shadow_vec(impl, Lmax, rule="true"):
    """vec[b] = number of a<b that are shadows (b in 2..Lmax); rule controls the 'uncovered' test."""
    vec = [0] * (Lmax + 1)
    for b in range(2, Lmax + 1):
        nb = impl.nonempty(b)
        c = 0
        for a in range(1, b):
            na = impl.nonempty(a)
            if rule == "true": unc = not impl.covered(a, b)
            elif rule == "ign_false": unc = False
            elif rule == "ign_true": unc = True
            elif rule == "len": unc = impl.size(b) > impl.size(a)
            else: raise ValueError(rule)
            cut = b if unc else (a if na else None)
            last = b if nb else a
            if last != cut: c += 1
        vec[b] = c
    return vec

def averages(vecs, P, Lmax):
    """vecs: dict (w,r)->vec. returns avg[N] for N=2..Lmax as Fraction (sum over widths, mean over r)."""
    tot = [0] * (Lmax + 1)
    for v in vecs.values():
        run = 0
        for N in range(2, Lmax + 1):
            run += v[N]
            tot[N] += run
    return {N: Fraction(tot[N], P) for N in range(2, Lmax + 1)}

def flats(avg, P):
    return [N for N in range(P - 1, 2 * P + 2) if N - 1 >= 2 and avg[N] == avg[N - 1]]

def run_case(P, base, impls, rules=("true",), verbose=False):
    Lmax = 2 * P + 1
    vecs = {k: {} for k in impls}  # impl name -> rule -> (w,r)->vec
    out = {}
    for name in impls:
        out[name] = {rule: {} for rule in rules}
    for w in range(1, P):
        for r in range(P):
            T = base + r
            for name, mk in impls.items():
                im = mk(P, w, T, Lmax)
                for rule in rules:
                    out[name][rule][(w, r)] = shadow_vec(im, Lmax, rule)
    return out

# ---------- unit/edge tests of the run machinery ----------
def edge_tests():
    # builder: adjacent landings merge, gap of exactly one tick splits
    assert runs_contained_twoptr([], [[1, 3]]) and runs_contained_bisect([], [[1, 3]])  # empty b covered
    assert runs_contained_twoptr([], []) and runs_contained_bisect([], [])
    assert not runs_contained_twoptr([[1, 1]], []) and not runs_contained_bisect([[1, 1]], [])
    A = [[1, 3], [5, 7]]  # gap of exactly one tick (4) between runs
    assert not runs_contained_twoptr([[3, 5]], A) and not runs_contained_bisect([[3, 5]], A)
    assert runs_contained_twoptr([[1, 3], [5, 7]], A) and runs_contained_bisect([[1, 3], [5, 7]], A)
    assert not runs_contained_twoptr([[4, 4]], A) and not runs_contained_bisect([[4, 4]], A)
    assert runs_contained_twoptr([[7, 7]], A) and not runs_contained_twoptr([[7, 8]], A)  # touches end of A
    assert not runs_contained_bisect([[7, 8]], A) and not runs_contained_twoptr([[0, 1]], A)
    # random cross-check vs sets, with genuinely maximal runs
    rng = random.Random(7)
    def rand_runs():
        xs = sorted(rng.sample(range(40), rng.randint(0, 25)))
        rs = []
        for x in xs:
            if rs and rs[-1][1] + 1 == x: rs[-1][1] = x
            else: rs.append([x, x])
        return rs, set(xs)
    for _ in range(4000):
        (Ra, Sa), (Rb, Sb) = rand_runs(), rand_runs()
        e = Sb <= Sa
        assert runs_contained_twoptr(Rb, Ra) == e == runs_contained_bisect(Rb, Ra)
    # builder vs sets on small cases incl. horizon-end touching and T=0
    for P in (3, 4, 5):
        for w in range(1, P):
            for T in range(0, 3 * P + 2):
                for L in range(1, 2 * P + 2):
                    S = sorted(t + L for t in range(T) if legal(t, L, P, w))
                    rr = build_runs(P, w, T, L)
                    flat = [x for s, e in rr for x in range(s, e + 1)]
                    assert flat == S
                    for i in range(len(rr) - 1): assert rr[i + 1][0] - rr[i][1] >= 2  # maximal
    print("edge tests ok")

PCLAIM = {8: (Fraction(8), Fraction(18)), 9: (Fraction(100, 9), Fraction(220, 9)), 10: (Fraction(15), Fraction(65, 2))}

def main():
    t0 = time.time()
    edge_tests()
    all_ok = True
    notes = []
    offsets = [8209, 3571, 9001, 43, 0]
    for base in offsets:
        for P in (8, 9, 10):
            impls = {
                "dict": lambda P, w, T, L: DictImpl(P, w, T, L),
                "runs": lambda P, w, T, L: RunImpl(P, w, T, L),
                "runs_bisect": lambda P, w, T, L: RunImpl(P, w, T, L, True),
                "mask": lambda P, w, T, L: MaskImpl(P, w, T, L),
            }
            rules = ("true", "ign_false", "ign_true", "len")
            if base not in (8209, 0, 43):
                rules = ("true",)
            out = run_case(P, base, impls, rules)
            Lmax = 2 * P + 1
            # per-(w,r,b) vector equality across impls, every rule
            for rule in rules:
                for name in ("runs", "runs_bisect", "mask"):
                    if out[name][rule] != out["dict"][rule]:
                        all_ok = False
                        notes.append(f"VEC MISMATCH base={base} P={P} rule={rule} impl={name}")
            avgs = {rule: averages(out["dict"][rule], P, Lmax) for rule in rules}
            avg_runs = averages(out["runs"]["true"], P, Lmax)
            assert avg_runs == avgs["true"]
            fl = flats(avgs["true"], P)
            a = avgs["true"]
            claim = PCLAIM[P]
            hold = (a[P], a[2 * P]) == claim and fl == [P, 2 * P]
            line = f"base={base:5d} P={P:2d} true: avg[P]={a[P]} avg[2P]={a[2*P]} flats={fl} claim_holds={hold}"
            for rule in rules[1:]:
                ar = avgs[rule]
                line += f" | {rule}: avg[P]={ar[P]} avg[2P]={ar[2*P]} flats={flats(ar,P)}"
            print(line, flush=True)
            if base == 8209:
                if not hold: all_ok = False; notes.append(f"claim fails at 8209 P={P}")
                for rule in rules[1:]:
                    ar = avgs[rule]
                    if (ar[P], ar[2 * P]) == claim and flats(ar, P) == [P, 2 * P]:
                        all_ok = False; notes.append(f"control {rule} reproduces claim P={P}")
            if base == 0:
                if hold: notes.append(f"base-0 control ALSO reproduces claim P={P}")
            if base in (3571, 9001):
                if not hold: notes.append(f"offset {base} P={P} differs from claim")
            if base == 43 and not hold: notes.append(f"small offset 43 P={P} differs")
            if P == 8 and base == 8209:
                print("calibration P8 N=8:", a[8], "N=16:", a[16], "P9 N=9 checked in its own row")
        print(f"  elapsed {time.time()-t0:.1f}s", flush=True)
    print("notes:", notes)
    summary = f"intervals==dict==mask on all vectors={all_ok}; elapsed {time.time()-t0:.0f}s; notes={len(notes)}"
    print("RESULT: " + ("PASS " if all_ok else "FAIL ") + summary)

if __name__ == "__main__":
    main()
