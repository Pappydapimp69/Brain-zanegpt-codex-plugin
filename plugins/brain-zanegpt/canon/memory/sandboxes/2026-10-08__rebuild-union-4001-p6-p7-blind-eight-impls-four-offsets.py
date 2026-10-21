"""Blind rebuild: frozenset union-size cover test at offset 4001 vs dict membership.

PREDICTION (written before first run, never edited):
  * union-size test (len(fs(a)|fs(b)) == len(fs(a))) is exactly the subset test for finite
    sets, so union == dict == subset == bitmask == arithmetic predicate == sorted merge,
    bit-for-bit per (width, horizon, a, b), at offsets 37, 2999, 4001, 9001, moduli 6,7,8.
  * Averages at offset 4001 (N=P, 2P): P6 7/2 and 17/2; P7 38/7 and 88/7.
  * Calibration holds: P8 N=8 -> 8, N=16 -> 18, P9 N=9 -> 100/9.
  * 2-lag average flat (avg(N)==avg(N-1)) exactly at N=P and N=2P among N=P..2P+1
    (I expect N=P-1 not flat either; flats list [P,2P]) for P6,P7 (and probably P8).
  * Controls: base-0 differs from base 4001; ignore-cover reading A (nothing covered)
    gives 0 at base 4001; reading B (everything covered) gives nonzero (every pair with
    both lags landing, = (P-1)*C(N,2) total per horizon, i.e. avg (P-1)*C(N,2));
    sizes-only (len(b)<=len(a)) differs.
  * Naive len(set(a+b))==len(a) on lists with repeats is WRONG (differs); frozenset form is right.
  * Offsets beyond saturation give the same averages (invariant in base).
"""
import sys, time
from fractions import Fraction
from itertools import combinations
import random

t0 = time.time()

def landing_list(P, w, T, L):
    return [t + L for t in range(T) if (t % P) >= w or ((t + L) % P) < w]

# ---------- cover implementations: all take a bundle dict for lags a,b ----------
def cov_dict(S, a, b):
    da = dict.fromkeys(S['lst'][a], True)
    return all(x in da for x in S['lst'][b])

def cov_union(S, a, b):
    fa, fb = S['fs'][a], S['fs'][b]
    return len(fa | fb) == len(fa)

def cov_subset(S, a, b):
    return S['fs'][b] <= S['fs'][a]

def cov_bits(S, a, b):
    return (S['bm'][b] & ~S['bm'][a]) == 0

def cov_merge(S, a, b):
    A, B = S['lst'][a], S['lst'][b]
    i = 0; n = len(A)
    for x in B:
        while i < n and A[i] < x: i += 1
        if i >= n or A[i] != x: return False
    return True

def cov_union_dups(S, a, b):   # lists with repeats, frozenset union-size
    A, B = S['dup'][a], S['dup'][b]
    return len(frozenset(A) | frozenset(B)) == len(frozenset(A))

def cov_naive_dups(S, a, b):   # WRONG on purpose: len(set(a+b)) == len(a) on repeat lists
    A, B = S['dup'][a], S['dup'][b]
    return len(set(A + B)) == len(A)

def cov_sizes(S, a, b):        # control
    return len(S['lst'][b]) <= len(S['lst'][a])

def pred(P, w, T, L, s):
    return L <= s <= T - 1 + L and (((s - L) % P) >= w or (s % P) < w)

def cov_arith_fast(S, a, b):   # no sets: periodic reduction of the landing predicate
    P, w, T = S['P'], S['w'], S['T']
    hi = T - 1 + a
    lo = b
    if hi >= lo:
        end = min(hi, lo + P - 1)
        for s in range(lo, end + 1):
            if pred(P, w, T, b, s) and not pred(P, w, T, a, s): return False
    for s in range(max(hi + 1, b), T - 1 + b + 1):
        if pred(P, w, T, b, s): return False
    return True

def cov_arith_brute(S, a, b):
    P, w, T = S['P'], S['w'], S['T']
    for s in range(b, T - 1 + b + 1):
        if pred(P, w, T, b, s) and not pred(P, w, T, a, s): return False
    return True

def nonempty_arith(P, w, T, L):
    return any(pred(P, w, T, L, t + L) for t in range(min(T, P)))

COV = {'dict': cov_dict, 'union': cov_union, 'subset': cov_subset, 'bitmask': cov_bits,
       'merge': cov_merge, 'union_dups': cov_union_dups, 'arith_fast': cov_arith_fast}
NEG = {'naive_dups': cov_naive_dups, 'sizes_only': cov_sizes}

def shadow(covered, a_any, b_any, a, b):
    cut = b if not covered else (a if a_any else None)
    last = b if b_any else a
    return last != cut

def build(P, w, T, maxlag):
    S = {'P': P, 'w': w, 'T': T, 'lst': {}, 'fs': {}, 'bm': {}, 'dup': {}, 'any': {}}
    for L in range(1, maxlag + 1):
        l = landing_list(P, w, T, L)
        S['lst'][L] = l; S['fs'][L] = frozenset(l)
        m = 0
        for x in l: m |= 1 << x
        S['bm'][L] = m; S['dup'][L] = l + l[::-1]
        S['any'][L] = bool(l)
    return S

def run(P, base, impls, extra=(), mode='normal', Ns=None):
    """returns {impl: {(w,r): tuple of shadow bits over pairs a<b}} """
    maxlag = 2 * P + 1
    pairs = [(a, b) for b in range(2, maxlag + 1) for a in range(1, b)]
    out = {k: {} for k in list(impls) + list(extra)}
    for w in range(1, P):
        for r in range(P):
            T = base + r
            S = build(P, w, T, maxlag)
            for k in out:
                f = (COV.get(k) or NEG.get(k) or {'arith_brute': cov_arith_brute}[k])
                bits = []
                for (a, b) in pairs:
                    if mode == 'ignoreA': c = False
                    elif mode == 'ignoreB': c = True
                    else: c = f(S, a, b)
                    bits.append(shadow(c, S['any'][a], S['any'][b], a, b))
                out[k][(w, r)] = tuple(bits)
    return out, pairs

def vectors(res, pairs, P):
    """per-(w,r,b) shadow count vector"""
    vec = {}
    for (w, r), bits in res.items():
        d = {}
        for (a, b), s in zip(pairs, bits):
            d[b] = d.get(b, 0) + (1 if s else 0)
        vec[(w, r)] = d
    return vec

def averages(vec, P):
    """exact Fraction avg for N=2..2P+1 via prefix sums"""
    perb = {}
    for d in vec.values():
        for b, c in d.items(): perb[b] = perb.get(b, 0) + c
    tot = 0; av = {}
    for N in range(2, 2 * P + 2):
        tot += perb.get(N, 0)
        av[N] = Fraction(tot, P)
    return av

def flats(av, P):
    return [N for N in range(P - 1, 2 * P + 2) if N - 1 in av and av[N] == av[N - 1]]

def fmt(x): return str(x)

ok = True
fails = []
def check(cond, msg):
    global ok
    if not cond:
        ok = False; fails.append(msg)
    print(('  ok   ' if cond else '  FAIL ') + msg)

# ---------- unit tests of union-size vs subset on finite sets / lists ----------
print('== unit tests')
rng = random.Random(7)
bad = 0
for _ in range(20000):
    A = [rng.randrange(6) for _ in range(rng.randrange(0, 7))]
    B = [rng.randrange(6) for _ in range(rng.randrange(0, 7))]
    u = len(frozenset(A) | frozenset(B)) == len(frozenset(A))
    if u != (set(B) <= set(A)): bad += 1
check(bad == 0, 'union-size == subset on 20000 random lists with repeats/empties')
check(len(frozenset([]) | frozenset([3])) != len(frozenset([])), 'a empty, b nonempty -> NOT covered')
check(len(frozenset([]) | frozenset([])) == len(frozenset([])), 'both empty -> covered (vacuous)')
check(len(frozenset([1]) | frozenset([])) == 1, 'a nonempty, b empty -> covered')
naive_bad = sum(1 for _ in range(2000)
                if (lambda A, B: (len(set(A + B)) == len(A)) != (set(B) <= set(A)))(
                    [rng.randrange(4) for _ in range(5)], [rng.randrange(4) for _ in range(3)]))
check(naive_bad > 0, f'naive len(set(a+b))==len(a) on repeat lists is wrong in {naive_bad}/2000 draws (expected >0)')

# ---------- main runs ----------
impls = ['dict', 'union', 'subset', 'bitmask', 'arith_fast', 'merge', 'union_dups']
OFFS = [37, 2999, 4001, 9001]
AV = {}   # (P, base) -> averages of dict
for P in (6, 7, 8):
    for base in OFFS:
        use = impls if base in (37, 4001) else ['dict', 'union', 'subset', 'bitmask', 'arith_fast']
        extra = []
        if base == 37 or (base == 4001 and P == 6): extra.append('arith_brute')
        res, pairs = run(P, base, use, extra)
        ref = res['dict']
        for k, v in res.items():
            check(v == ref, f'P{P} base{base}: {k} == dict per-(w,r,pair) bits')
        vec = {k: vectors(v, pairs, P) for k, v in res.items()}
        check(all(vec[k] == vec['dict'] for k in vec), f'P{P} base{base}: per-(w,r,b) vectors identical across {len(res)} impls')
        av = {k: averages(vec[k], P) for k in vec}
        check(all(av[k] == av['dict'] for k in av), f'P{P} base{base}: averages identical all N=2..{2*P+1}')
        AV[(P, base)] = av['dict']
        five = [P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1]
        print(f'  P{P} base{base} avg at N={five}: {[fmt(av["dict"][N]) for N in five]}  flats={flats(av["dict"], P)}  [{time.time()-t0:.0f}s]')
        # union-vs-dict at the five N explicitly
        check([av['union'][N] for N in five] == [av['dict'][N] for N in five], f'P{P} base{base}: union avg == dict avg at five N')

# negatives at 4001
print('== negative controls at 4001')
for P in (6, 7):
    res, pairs = run(P, 4001, ['dict'], ['sizes_only', 'naive_dups'])
    for k in ('sizes_only', 'naive_dups'):
        same = res[k] == res['dict']
        av = averages(vectors(res[k], pairs, P), P)
        print(f'  P{P} {k}: avg(P)={av[P]} avg(2P)={av[2*P]} differs_from_dict_bits={not same}')
        check(not same, f'P{P} {k} control differs from dict')
    for mode in ('ignoreA', 'ignoreB'):
        r2, p2 = run(P, 4001, ['dict'], mode=mode)
        av = averages(vectors(r2['dict'], p2, P), P)
        print(f'  P{P} {mode}: avg(P)={av[P]} avg(2P)={av[2*P]} avg(2P+1)={av[2*P+1]}')
        if mode == 'ignoreA':
            check(all(v == 0 for v in av.values()), f'P{P} ignore-cover reading A (nothing covered) gives 0 for all N')
        else:
            exp = lambda N: Fraction((P - 1) * N * (N - 1) // 2)
            check(all(av[N] == exp(N) for N in av), f'P{P} ignore-cover reading B (all covered) = (P-1)*C(N,2) for all N, nonzero')
    r0, p0 = run(P, 0, ['dict', 'union'])
    check(r0['dict'] == r0['union'], f'P{P} base0: union == dict bits')
    av0 = averages(vectors(r0['dict'], p0, P), P)
    five = [P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1]
    print(f'  P{P} base-0 avg at five N: {[fmt(av0[N]) for N in five]} flats={flats(av0, P)} vs base4001 {[fmt(AV[(P,4001)][N]) for N in five]}')
    check([av0[N] for N in five] != [AV[(P, 4001)][N] for N in five], f'P{P} base-0 control differs from base 4001')

# ---------- claim numbers & calibration ----------
print('== claim numbers / calibration')
A6, A7, A8 = AV[(6, 4001)], AV[(7, 4001)], AV[(8, 4001)]
check(A6[6] == Fraction(7, 2) and A6[12] == Fraction(17, 2), f'P6 N=6,12 = {A6[6]}, {A6[12]} (claim 7/2, 17/2)')
check(A7[7] == Fraction(38, 7) and A7[14] == Fraction(88, 7), f'P7 N=7,14 = {A7[7]}, {A7[14]} (claim 38/7, 88/7)')
check(A8[8] == 8 and A8[16] == 18, f'calib P8 N=8,16 = {A8[8]}, {A8[16]} (8, 18)')
res9, pairs9 = run(9, 4001, ['dict', 'union'])
check(res9['dict'] == res9['union'], 'P9 4001 union == dict bits')
A9 = averages(vectors(res9['dict'], pairs9, 9), 9)
check(A9[9] == Fraction(100, 9), f'calib P9 N=9 = {A9[9]} (100/9)')
for P in (6, 7, 8):
    A = AV[(P, 4001)]
    fl = flats(A, P)
    print(f'  P{P} flats over N=P-1..2P+1: {fl}')
    if P in (6, 7):
        check(fl == [P, 2 * P], f'P{P} flats exactly [P,2P] = {[P, 2*P]}')
    for N in range(P - 1, 2 * P + 2):
        pass
    print(f'  P{P} full avg row N=2..{2*P+1}: {[fmt(A[N]) for N in range(2, 2*P+2)]}')
for P in (6, 7, 8):
    inv = all(AV[(P, b)] == AV[(P, 4001)] for b in OFFS)
    print(f'  P{P} averages invariant across offsets {OFFS}: {inv}')
    check(inv, f'P{P} offset invariance 37/2999/4001/9001')

print(f'elapsed {time.time()-t0:.1f}s')
summ = (f'union==dict(+subset,bitmask,arith,merge,dups) at offsets {OFFS} P6-8; '
        f'P6 {A6[6]},{A6[12]} P7 {A7[7]},{A7[14]} P8 {A8[8]},{A8[16]} P9 {A9[9]}; '
        f'flats P6 {flats(A6,6)} P7 {flats(A7,7)} P8 {flats(A8,8)}')
print('RESULT: ' + ('PASS ' if ok else 'FAIL ' + str(fails[:5]) + ' ') + summ)
