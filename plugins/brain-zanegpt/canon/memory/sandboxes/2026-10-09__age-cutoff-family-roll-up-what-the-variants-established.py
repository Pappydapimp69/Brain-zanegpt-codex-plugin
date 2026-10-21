"""Roll-up sandbox for the age-cutoff family. Independent re-implementation of four headline findings.

PREDICTION (written before the first run; any item could come out wrong):
 F1  Contiguous windows, every lag pair a<b<=N, widths 1..P-1, averaged over P consecutive horizons from a
     base of 97: the 2-lag shadow average is flat (A[N]==A[N-1]) at EVERY multiple of P up to N=28, and
     nowhere else, for P=5..8; recorded anchors A[P],A[2P] = 7/2,17/2 (P6), 38/7,88/7 (P7), 8,18 (P8).
     A zero-offset base (horizon r instead of 97+r) changes the flat set (control).
 F2  Cover test = "every landing of the longer lag is a landing of the shorter lag". Set subset, bisect and an
     ascending merge agree exactly at P6,P7,P8 (base 241); a shared-iterator walk agrees when both lists share one
     order (both ascending or both descending) and gives a different count when only one list is reversed;
     a lengths-only cover and a residue-only cover both give different averages.
 F3  Contiguous always-on k-lag sets over lags 1..N: the horizons (T mod P) with zero shadows are {0} plus the
     last k-1 residues when P>=N, and only {0} when P<N, for k=2,3 over P=5..11, N=4..9 (bases 100 and 237).
     Control: a threshold-free "always {0,P-1}" rule must be wrong at the P<N cells.
 F4  3-lag sets, always-on fallback, contiguous (multiplier 1) versus scrambled (all unit multipliers): the
     residues of T mod P where contiguous shadows no more than scrambled form ONE cyclic interval containing
     residue 0 and containing the contiguous zero-shadow residues, at P=9,11,13 (lags 1..8, horizon base 300).
     Control: the block is keyed by lag universe, so widening to lags 1..12 changes it at some modulus, and both
     signs of (contiguous - scrambled) occur within one period (a single horizon cannot rank the families).
Model (taken from the family's own description, so the model definition is shared, the code is not): window set
B = {t : (m*t) mod P < w}; a press at tick t lands at t+L iff t is outside B or t+L is inside B; a pair/set of lags
is scanned in ascending order, 'cut' is the last lag that adds a landing not yet covered, 'last' is the largest
lag that lands at all, shadow = (last != cut).
"""
from fractions import Fraction as F
from itertools import combinations
from math import gcd
from bisect import bisect_left

# ---------------- set-based landings (used for F1, F2) ----------------
def lands_sets(P, m, w, T, lags):
    inB = lambda t: (m * t) % P < w
    return {L: {t + L for t in range(T) if (not inB(t)) or inB(t + L)} for L in lags}

def pair_shadow_sets(la, lb, cover):
    """la, lb: landing sets of a<b. returns 1 if shadow."""
    last = 'b' if lb else ('a' if la else None)
    covered = cover(la, lb)           # all b landings already in a
    cut = ('a' if la else None) if covered else 'b'
    return int(last != cut)

def total_by_N(P, T, w, Nmax):
    """prefix[N] = sum of pair shadows over a<b<=N (contiguous window width w, horizon T)."""
    lm = lands_sets(P, 1, w, T, range(1, Nmax + 1))
    col = [0] * (Nmax + 1)
    sub = lambda a, b: b <= a
    for b in range(2, Nmax + 1):
        col[b] = sum(pair_shadow_sets(lm[a], lm[b], sub) for a in range(1, b))
    pre = [0] * (Nmax + 1)
    for N in range(1, Nmax + 1):
        pre[N] = pre[N - 1] + col[N]
    return pre

def avg_table(P, base, Nmax):
    acc = [0] * (Nmax + 1)
    for r in range(P):
        for w in range(1, P):
            pre = total_by_N(P, base + r, w, Nmax)
            for N in range(Nmax + 1):
                acc[N] += pre[N]
    return [F(x, P) for x in acc]

def flats(A, P, Nmax):
    return [N for N in range(P, Nmax + 1) if A[N] == A[N - 1]]

def finding1():
    NMAX = 28
    anchors = {6: (F(7, 2), F(17, 2)), 7: (F(38, 7), F(88, 7)), 8: (F(8), F(18))}
    ok = True; notes = []
    for P in (5, 6, 7, 8):
        A = avg_table(P, 97, NMAX)
        got = flats(A, P, NMAX)
        want = [k * P for k in range(1, NMAX // P + 1)]
        good = got == want
        if P in anchors:
            good = good and (A[P], A[2 * P]) == anchors[P]
        A0 = avg_table(P, 0, NMAX)
        ctrl = flats(A0, P, NMAX) != want
        notes.append("P%d flats=%s avgP=%s avg2P=%s zero-offset-differs=%s" % (P, got, A[P], A[2 * P], ctrl))
        ok = ok and good and ctrl
    return ok, "F1 " + "; ".join(notes)

# ---------------- F2 cover implementations ----------------
def avg_with_cover(P, base, N, cover_fn, order):
    tot = 0
    for r in range(P):
        for w in range(1, P):
            lm = lands_sets(P, 1, w, base + r, range(1, N + 1))
            for a in range(1, N + 1):
                for b in range(a + 1, N + 1):
                    A_, B_ = lm[a], lm[b]
                    la, lb = order(sorted(A_), sorted(B_))
                    last = 'b' if B_ else ('a' if A_ else None)
                    covered = cover_fn(la, lb)
                    cut = ('a' if A_ else None) if covered else 'b'
                    tot += (last != cut)
    return F(tot, P)

def cov_set(la, lb): return set(lb) <= set(la)
def cov_bisect(la, lb):
    sa = sorted(la)
    for x in lb:
        i = bisect_left(sa, x)
        if i == len(sa) or sa[i] != x: return False
    return True
def cov_merge_asc(la, lb):
    i = 0
    for x in lb:
        while i < len(la) and la[i] < x: i += 1
        if i == len(la) or la[i] != x: return False
        i += 1
    return True
def cov_iter(la, lb):
    it = iter(la)
    return all(x in it for x in lb)
def cov_len(la, lb): return len(lb) <= len(la)
def cov_resid(P):
    return lambda la, lb: {x % P for x in lb} <= {x % P for x in la}

asc = lambda a, b: (a, b)
desc_both = lambda a, b: (a[::-1], b[::-1])
mismatch = lambda a, b: (a, b[::-1])

def finding2():
    BASE = 241; ok = True; notes = []
    for P in (6, 7, 8):
        N = P
        ref = avg_with_cover(P, BASE, N, cov_set, asc)
        res = {
            'bisect': avg_with_cover(P, BASE, N, cov_bisect, asc),
            'merge_asc': avg_with_cover(P, BASE, N, cov_merge_asc, asc),
            'iter_asc': avg_with_cover(P, BASE, N, cov_iter, asc),
            'iter_desc_both': avg_with_cover(P, BASE, N, cov_iter, desc_both),
        }
        brk = {
            'iter_mismatch': avg_with_cover(P, BASE, N, cov_iter, mismatch),
            'merge_mismatch': avg_with_cover(P, BASE, N, cov_merge_asc, mismatch),
            'len_only': avg_with_cover(P, BASE, N, cov_len, asc),
            'resid_only': avg_with_cover(P, BASE, N, cov_resid(P), asc),
        }
        agree = all(v == ref for v in res.values())
        broken = {k: v != ref for k, v in brk.items()}
        ok = ok and agree and all(broken.values())
        notes.append("P%d ref=%s agree=%s breaks=%s" % (P, ref, agree, {k: str(v) for k, v in brk.items()}))
    return ok, "F2 " + "; ".join(notes)

# ---------------- bitmask landings (used for F3, F4) ----------------
def window_mask(P, m, w, size):
    x = 0
    for t in range(size):
        if (m * t) % P < w: x |= 1 << t
    return x

def lands_mask(P, m, w, T, Nmax):
    Bm = window_mask(P, m, w, T + Nmax + 1)
    full = (1 << T) - 1
    out = {}
    for L in range(1, Nmax + 1):
        ok = (~Bm | (Bm >> L)) & full
        out[L] = ok << L
    return out

def set_shadow(land, lags):
    cov = 0; cut = 0; last = 0
    for L in lags:
        if land[L] & ~cov: cut = L
        cov |= land[L]
        if land[L]: last = L
    return int(last != cut)

def shadow_count(P, m, T, N, k):
    n = 0
    sets = list(combinations(range(1, N + 1), k))
    for w in range(1, P):
        land = lands_mask(P, m, w, T, N)
        for s in sets: n += set_shadow(land, s)
    return n, len(sets) * (P - 1)

def zero_residues(P, base, N, k):
    return sorted({(base + r) % P for r in range(P) if shadow_count(P, 1, base + r, N, k)[0] == 0})

def finding3():
    bad = []; cells = 0; wrong_unconditional = 0; below = 0
    for k in (2, 3):
        for N in range(4, 10):
            for P in range(5, 12):
                exp = sorted({0} | {P - j for j in range(1, k)}) if P >= N else [0]
                for base in (100, 237):
                    z = zero_residues(P, base, N, k); cells += 1
                    if z != exp: bad.append((k, N, P, base, z))
                    if P < N and base == 100:
                        below += 1
                        if z != sorted({0} | {P - j for j in range(1, k)}): wrong_unconditional += 1
    ok = not bad and below > 0 and wrong_unconditional == below
    return ok, "F3 cells=%d mismatches=%d first=%s below_threshold_cells=%d threshold_free_rule_wrong_on=%d" % (
        cells, len(bad), bad[:2], below, wrong_unconditional)

def is_cyclic_interval(S, P):
    S = set(S)
    if not S or len(S) == P: return True
    return sum(1 for r in range(P) if r in S and (r - 1) % P not in S) == 1

def lower_block(P, base, N, k=3):
    units = [m for m in range(1, P) if gcd(m, P) == 1]
    low = []; signs = set(); zero_c = []
    for r in range(P):
        T = base + r
        c, ct = shadow_count(P, 1, T, N, k)
        sh = tot = 0
        for m in units:
            a, b = shadow_count(P, m, T, N, k); sh += a; tot += b
        cr, sr = F(c, ct), F(sh, tot)
        if cr <= sr: low.append(T % P)
        signs.add((cr > sr) - (cr < sr))
        if c == 0: zero_c.append(T % P)
    return sorted(low), sorted(zero_c), signs

# blocks recorded by earlier family lessons at lags 1..12 (horizon base 600); my run uses base 300
RECORDED12 = {9: [0, 1, 7, 8], 11: [0, 1, 6, 7, 8, 9, 10], 13: [0, 1, 8, 9, 10, 11, 12]}

def finding4():
    ok = True; notes = []; changed = False
    for P in (9, 11, 13):
        low8, zero8, signs8 = lower_block(P, 300, 8)
        low12, zero12, _ = lower_block(P, 300, 12)
        iv = is_cyclic_interval(low8, P) and 0 in low8 and set(zero8) <= set(low8)
        both = (1 in signs8 and -1 in signs8)
        diff = low8 != low12
        changed = changed or diff
        notes.append("P%d lags1-8 block=%s zeros=%s interval0=%s both_signs=%s | lags1-12 block=%s differs=%s" % (
            P, low8, zero8, iv, both, low12, diff))
        rec = RECORDED12.get(P)
        match_rec = (low12 == rec)
        notes[-1] += " matches_recorded_lags1-12_block=%s" % match_rec
        ok = ok and iv and both and match_rec
    ok = ok and changed
    return ok, "F4 " + "; ".join(notes)

if __name__ == '__main__':
    results = []
    for fn in (finding1, finding2, finding3, finding4):
        good, msg = fn(); results.append(good); print(("PASS " if good else "FAIL ") + msg, flush=True)
    print("RESULT: %s findings=%s F1 flats at every multiple of P with zero-offset control, F2 cover impl agreement and order/length/residue breakers, F3 zero residues vs P>=N threshold, F4 lower-residue interval around 0" % (
        "PASS" if all(results) else "FAIL", results))
