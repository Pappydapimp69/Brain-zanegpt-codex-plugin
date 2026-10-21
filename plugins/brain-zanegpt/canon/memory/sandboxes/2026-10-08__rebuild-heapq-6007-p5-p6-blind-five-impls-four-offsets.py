#!/usr/bin/env python3
"""Blind rebuild: heapq merge-dedupe length cover test vs dict reference.

PREDICTION (written before first run, never edited):
  * heapq.merge+groupby length-compare cover test is equivalent to dict/frozenset/
    bitmask/arithmetic cover tests: per-(width,horizon,b) shadow count vectors
    identical for every offset tried (37, 4001, 6007, 9973) and moduli 5,6,7,
    including empty-landing edge cases at tiny T.
  * Offset 6007, horizons T=6007+r, r=0..P-1: P5 averages 2 (N=5) and 26/5 (N=10);
    P6 averages 7/2 (N=6) and 17/2 (N=12).
  * The 2-lag average (avg over horizons of shadow count, summed over widths and
    pairs a<b<=N) is flat (avg(N)==avg(N-1)) exactly at N=P and N=2P among
    N in P..2P+1, so flats == [P, 2P] for P=5,6 (and probably 7) at 6007.
  * Controls: base-0 differs from base 6007; ignore-cover forced False gives 0
    (every b is its own cut and last-landing lag); forced True gives "all pairs"
    (large, not 0); sizes-only cover (len(b)<=len(a)) differs.
  * Calibration with my model: P8 N=8 -> 8, N=16 -> 18, P9 N=9 -> 100/9.
  * Overall expectation: PASS. Uncertain whether other offsets reproduce the exact
    same averages (may depend on offset residue mod P); that is reported only.

Model: period P, width w in 1..P-1; press at tick t with lag L is legal iff
(t%P)>=w or ((t+L)%P)<w; lands at t+L, 0<=t<T, no truncation at horizon.
b covered by a iff landings(b) subset of landings(a).
cut lag = b if b uncovered else (a if a lands anything else None);
last-landing lag = b if b lands else (a if a lands else None); shadow iff differ.
"""
import heapq
import sys
import time
from fractions import Fraction
from itertools import groupby
from multiprocessing import Pool


def legal(t, L, P, w):
    return (t % P) >= w or ((t + L) % P) < w


def landings(T, L, P, w):
    return [t + L for t in range(T) if legal(t, L, P, w)]  # strictly increasing


# --- cover tests -------------------------------------------------------------
def cover_heap(la, lb):
    merged = [k for k, _ in groupby(heapq.merge(la, lb))]
    return len(merged) == len(la)


def cover_dict(la, lb):
    d = {x: True for x in la}
    return all(x in d for x in lb)


def cover_fset(sa, sb):
    return sb <= sa


def cover_mask(ma, mb):
    return (mb & ~ma) == 0


def cover_arith(T, a, b, P, w):
    # every legal press of lag b has a legal lag-a press landing on the same tick
    for t in range(T):
        if legal(t, b, P, w):
            t2 = t + b - a
            if not (0 <= t2 < T and legal(t2, a, P, w)):
                return False
    return True


def shadow(cov, na, nb):
    cut = 'b' if not cov else ('a' if na else None)
    last = 'b' if nb else ('a' if na else None)
    return last != cut


METHODS = ['heap', 'dict', 'fset', 'mask', 'arith']
CONTROLS = ['cF', 'cT', 'size']


def run(P, base, methods=METHODS, rng=None, nmax=None):
    """Return dict: method/control -> {N: Fraction avg}, plus mismatch counts."""
    nmax = nmax or 2 * P + 1
    rr = range(P) if rng is None else rng
    vecs = {m: {} for m in methods + CONTROLS}
    for w in range(1, P):
        for r in rr:
            T = base + r
            L = {l: landings(T, l, P, w) for l in range(1, nmax + 1)}
            S = {l: frozenset(L[l]) for l in L}
            M = {}
            for l in L:
                m = 0
                for x in L[l]:
                    m |= 1 << x
                M[l] = m
            for m in vecs:
                vecs[m][(w, r)] = [0] * (nmax + 1)
            for b in range(2, nmax + 1):
                for a in range(1, b):
                    na, nb = bool(L[a]), bool(L[b])
                    covs = {}
                    if 'heap' in methods:
                        covs['heap'] = cover_heap(L[a], L[b])
                    if 'dict' in methods:
                        covs['dict'] = cover_dict(L[a], L[b])
                    if 'fset' in methods:
                        covs['fset'] = cover_fset(S[a], S[b])
                    if 'mask' in methods:
                        covs['mask'] = cover_mask(M[a], M[b])
                    if 'arith' in methods:
                        covs['arith'] = cover_arith(T, a, b, P, w)
                    covs['cF'] = False
                    covs['cT'] = True
                    covs['size'] = len(L[b]) <= len(L[a])
                    for m, c in covs.items():
                        if shadow(c, na, nb):
                            vecs[m][(w, r)][b] += 1
    out = {}
    for m, v in vecs.items():
        avg = {}
        for N in range(2, nmax + 1):
            tot = sum(sum(vec[2:N + 1]) for vec in v.values())
            avg[N] = Fraction(tot, len(rr))
        # note: sum over widths of sum over r / len(rr) == average over horizons
        out[m] = (avg, v)
    return out


def job(args):
    P, base, methods, rng = args
    t0 = time.time()
    res = run(P, base, methods, rng)
    ref = res['dict'][1] if 'dict' in methods else res['fset'][1]
    mism = {m: sum(1 for k in ref if res[m][1][k] != ref[k]) for m in methods}
    avgs = {m: res[m][0] for m in res}
    return (P, base, mism, avgs, time.time() - t0)


def flats(avg, P):
    return [N for N in range(P, 2 * P + 2) if avg[N] == avg[N - 1]]


def fr(x):
    return str(x)


def main():
    ok = True
    notes = []
    # ---- empty-landing edge cases (tiny T, base 0) ----
    edge_bad = 0
    for P in (5, 6):
        for w in range(1, P):
            for T in range(0, 4):
                for a in range(1, 2 * P + 2):
                    for b in range(a + 1, 2 * P + 2):
                        la, lb = landings(T, a, P, w), landings(T, b, P, w)
                        c = {cover_heap(la, lb), cover_dict(la, lb),
                             cover_fset(frozenset(la), frozenset(lb)),
                             cover_arith(T, a, b, P, w)}
                        if len(c) != 1:
                            edge_bad += 1
    # direct empties
    assert cover_heap([], []) is True and cover_heap([1, 2], []) is True
    assert cover_heap([], [3]) is False
    print('edge: empty-landing mismatches (T=0..3, P5/6, all w, all pairs):', edge_bad)
    if edge_bad:
        ok = False

    # ---- calibration (frozenset only, offset 6007) ----
    cal = {}
    for P, Ns in ((8, (8, 16)), (9, (9,))):
        cal[P] = run(P, 6007, ['fset'], None, nmax=max(Ns))['fset'][0]
    c8, c16, c9 = cal[8][8], cal[8][16], cal[9][9]
    print('calibration (6007): P8 N=8 ->', c8, ' P8 N=16 ->', c16, ' P9 N=9 ->', c9,
          '(want 8, 18, 100/9)')
    cal_ok = (c8 == 8 and c16 == 18 and c9 == Fraction(100, 9))
    if not cal_ok:
        ok = False
        notes.append('calibration mismatch')

    # ---- main jobs ----
    jobs = []
    for base in (6007, 4001, 9973, 37):
        for P in (5, 6):
            jobs.append((P, base, METHODS, None))
    for base in (6007, 37):
        jobs.append((7, base, METHODS, None))
    for P in (5, 6, 7):
        jobs.append((P, 0, METHODS, None))  # base-0 control
    with Pool(4) as pool:
        results = pool.map(job, jobs, chunksize=1)
    R = {(P, base): (mism, avgs, dt) for P, base, mism, avgs, dt in results}

    all_equal = True
    for (P, base), (mism, avgs, dt) in sorted(R.items()):
        bad = {m: c for m, c in mism.items() if c}
        if bad:
            all_equal = False
        ref = avgs['dict']
        same_all_N = all(avgs[m][N] == ref[N] for m in METHODS for N in ref)
        if not same_all_N:
            all_equal = False
        five = [P - 1, P, 2 * P - 1, 2 * P, 2 * P + 1]
        print(f'P{P} base={base} ({dt:.0f}s) vec-mismatch={mism} allN-avg-equal={same_all_N}')
        print('   avg at N=%s: %s' % (five, [fr(avgs["heap"][N]) for N in five]),
              ' heap==dict at five:', all(avgs['heap'][N] == avgs['dict'][N] for N in five),
              ' flats:', flats(avgs['heap'], P))
    if not all_equal:
        ok = False
        notes.append('implementations disagree')

    # ---- claim numbers at 6007 ----
    claim = {(5, 5): Fraction(2), (5, 10): Fraction(26, 5),
             (6, 6): Fraction(7, 2), (6, 12): Fraction(17, 2)}
    claim_ok = True
    for (P, N), v in claim.items():
        got = R[(P, 6007)][1]['heap'][N]
        print(f'claim P{P} N={N}: heap={got} claim={v} {"OK" if got == v else "NO"}')
        claim_ok &= (got == v)
    flat_ok = all(flats(R[(P, 6007)][1]['heap'], P) == [P, 2 * P] for P in (5, 6))
    print('flats at 6007 == [P,2P] for P5,P6:', flat_ok,
          '| P7:', flats(R[(7, 6007)][1]['heap'], 7))
    other_off = {base: {P: [fr(R[(P, base)][1]['heap'][N]) for N in (P, 2 * P)] +
                        [flats(R[(P, base)][1]['heap'], P)]
                    for P in (5, 6)} for base in (4001, 9973, 37)}
    print('other offsets (avg at P, 2P, flats):', other_off)
    if not (claim_ok and flat_ok):
        ok = False
        notes.append('claim numbers/flats not reproduced')

    # ---- controls ----
    # base-0
    diff0 = {P: R[(P, 0)][1]['heap'] != R[(P, 6007)][1]['heap'] for P in (5, 6)}
    print('base-0 averages P5 N=5,10:', [fr(R[(5, 0)][1]['heap'][N]) for N in (5, 10)],
          'P6 N=6,12:', [fr(R[(6, 0)][1]['heap'][N]) for N in (6, 12)],
          '| differs from 6007:', diff0, '| base-0 flats P5/P6:',
          flats(R[(5, 0)][1]['heap'], 5), flats(R[(6, 0)][1]['heap'], 6))
    ctrl_ok = all(diff0.values())
    for P in (5, 6):
        a = R[(P, 6007)][1]
        cf = [a['cF'][N] for N in (P, 2 * P)]
        ct = [a['cT'][N] for N in (P, 2 * P)]
        sz = [a['size'][N] for N in (P, 2 * P)]
        print(f'P{P} 6007 ignore-cover(False)={[fr(x) for x in cf]} '
              f'ignore-cover(True)={[fr(x) for x in ct]} sizes-only={[fr(x) for x in sz]} '
              f'sizes flats={flats(a["size"], P)}')
        ctrl_ok &= all(x == 0 for x in cf)
        ctrl_ok &= (sz != [a['heap'][N] for N in (P, 2 * P)] or
                    any(a['size'][N] != a['heap'][N] for N in range(2, 2 * P + 2)))
        ctrl_ok &= (ct != [a['heap'][N] for N in (P, 2 * P)])
    print('controls behave as predicted:', ctrl_ok)
    if not ctrl_ok:
        ok = False
        notes.append('controls not as predicted')

    summary = ('heapq==dict==fset==mask==arith per-vector at 6007/4001/9973/37 (P5,P6) and 6007/37 (P7); '
               f'6007: P5 N5={R[(5,6007)][1]["heap"][5]} N10={R[(5,6007)][1]["heap"][10]}, '
               f'P6 N6={R[(6,6007)][1]["heap"][6]} N12={R[(6,6007)][1]["heap"][12]}, '
               f'flats P5={flats(R[(5,6007)][1]["heap"],5)} P6={flats(R[(6,6007)][1]["heap"],6)}; '
               f'calib {c8},{c16},{c9}; edge_mismatch={edge_bad}')
    if notes:
        summary += ' NOTES: ' + '; '.join(notes)
    print('RESULT: %s %s' % ('PASS' if ok else 'FAIL', summary))


if __name__ == '__main__':
    main()
