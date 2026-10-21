"""Blind rebuild: 2-lag period-average flats at N=P and N=2P, P11/P12, base 137.

PREDICTION (written before first run, never edited):
  - For P11 and P12 at base 137 (and other long bases 2003/7001), the exact-Fraction
    period average avg(N) (sum over r=0..P-1 of shadows at T=base+r, all widths, all pairs
    a<b<=N, divided by P) is non-decreasing in N, with avg(P)==avg(P-1)?? no -- flat means
    avg(N)==avg(N-1) at N=P and N=2P, and (I expect) no other flats in P-1..2P+1.
  - P12: avg(12)=25. P11: avg(12)=225/11, avg(11) strictly below 225/11 (flat is avg(11)==avg(10)
    in the sense avg(N)==avg(N-1); I expect avg(11)=avg(10) < avg(12)? -- I only commit to
    avg(11) < 225/11 and flats at N=11,22 for P11 and N=12,24 for P12).
  - Calibration: P8 N=8 -> 8, P8 N=16 -> 18, P9 N=9 -> 100/9.
  - Implementations (python sets, periodic-word tiling bitmask, per-bit bitmask) agree exactly.
  - P13 hold-out: I guess flats at 13 and 26 also appear (the pattern looks structural), but
    I am unsure; I will report whatever happens.
  - Controls: base-0 differs; ignore-cover forced False and forced True both differ.
"""
from fractions import Fraction
import sys, time

def legal_ok(t, L, P, w):
    return (t % P) >= w or ((t + L) % P) < w

# ---------- impl A: python sets ----------
def land_sets(P, w, T, N):
    return [None] + [set(t + L for t in range(T) if legal_ok(t, L, P, w)) for L in range(1, N + 1)]

# ---------- impl B: periodic word tiling ----------
def land_tile(P, w, T, N):
    k = -(-T // P)
    rep = ((1 << (P * k)) - 1) // ((1 << P) - 1)
    full = (1 << T) - 1
    out = [None]
    for L in range(1, N + 1):
        word = 0
        for i in range(P):
            if i >= w or ((i + L) % P) < w:
                word |= 1 << i
        out.append(((word * rep) & full) << L)
    return out

# ---------- impl C: per-bit ----------
def land_bit(P, w, T, N):
    out = [None]
    for L in range(1, N + 1):
        m = 0
        for t in range(T):
            if (t % P) >= w or ((t + L) % P) < w:
                m |= 1 << t
        out.append(m << L)
    return out

def subset_set(x, y): return x <= y
def subset_bit(x, y): return (x & ~y) == 0
def nonempty(x): return bool(x)

def shadow(la, lb, a, b, subset, cover_mode):
    if cover_mode == 'normal': covered = subset(lb, la)
    elif cover_mode == 'false': covered = False
    else: covered = True
    if not covered: cut = b
    else: cut = a if nonempty(la) else None
    last = b if nonempty(lb) else a
    return last != cut

def counts(P, base, N, impl, cover_mode='normal'):
    land = {'A': land_sets, 'B': land_tile, 'C': land_bit}[impl]
    subset = subset_set if impl == 'A' else subset_bit
    cnt = [0] * (N + 1)  # cnt[b]: shadows with larger lag b
    for w in range(1, P):
        for r in range(P):
            T = base + r
            ls = land(P, w, T, N)
            for b in range(2, N + 1):
                lb = ls[b]
                c = 0
                for a in range(1, b):
                    if shadow(ls[a], lb, a, b, subset, cover_mode): c += 1
                cnt[b] += c
    return cnt

def avgs(cnt, P):
    out, s = {}, 0
    for N in range(len(cnt)):
        s += cnt[N]; out[N] = Fraction(s, P)
    return out

def flats(av, lo, hi):
    return [N for N in range(lo, hi + 1) if av[N] == av[N - 1]]

def fs(x): return str(x)

def main():
    t0 = time.time()
    ok = True
    notes = []
    res = {}
    def run(P, base, impl, mode='normal'):
        N = 2 * P + 1
        key = (P, base, impl, mode)
        if key not in res: res[key] = avgs(counts(P, base, N, impl, mode), P)
        return res[key]

    # calibration (base 137, impl B)
    a8 = run(8, 137, 'B'); a9 = run(9, 137, 'B')
    cal = (a8[8] == 8, a8[16] == 18, a9[9] == Fraction(100, 9))
    print('calibration P8N8=%s P8N16=%s P9N9=%s ->' % (a8[8], a8[16], a9[9]), cal)
    ok &= all(cal)

    # agreement among impls
    agree = True
    plan = [(137, 'ABC'), (41, 'ABC'), (2003, 'AB'), (7001, 'B')]
    for P in (8, 9, 10, 11, 12, 13):
        for base, impls in plan:
            if base == 7001 and P > 12: pass
            ref = None
            for im in impls:
                a = run(P, base, im)
                if ref is None: ref = a
                elif a != ref:
                    agree = False; print('DISAGREE', P, base, im)
    print('impl agreement (same base):', agree, 'time %.1fs' % (time.time() - t0))
    ok &= agree

    # cross-base
    for P in (8, 9, 10, 11, 12, 13):
        same = all(run(P, b, 'B') == run(P, 137, 'B') for b in (41, 2003, 7001))
        print('P%d cross-base equal (41,137,2003,7001): %s' % (P, same))

    claim = {}
    for P in (10, 11, 12, 13):
        a = run(P, 137, 'B')
        print('\nP%d base137 averages N=%d..%d:' % (P, P - 1, 2 * P + 1))
        print('  ' + ', '.join('%d:%s' % (N, fs(a[N])) for N in range(P - 1, 2 * P + 2)))
        fl = flats(a, 2, 2 * P + 1)
        mono = all(a[N] >= a[N - 1] for N in range(2, 2 * P + 2))
        print('  flats (avg(N)==avg(N-1)), N in 2..2P+1:', fl, ' nondecreasing:', mono)
        claim[P] = (fl, mono)

    a11, a12 = run(11, 137, 'B'), run(12, 137, 'B')
    c = {}
    c['P12 flats 12&24'] = (12 in claim[12][0] and 24 in claim[12][0])
    c['P11 flats 11&22'] = (11 in claim[11][0] and 22 in claim[11][0])
    c['P12 N=12 avg 25'] = a12[12] == 25
    c['P11 N=12 avg 225/11'] = a11[12] == Fraction(225, 11)
    c['P11 N=11 < 225/11'] = a11[11] < Fraction(225, 11)
    c['nondecreasing P11,P12'] = claim[11][1] and claim[12][1]
    # exclusive flats within P-1..2P+1
    c['P11 flats only {11,22} in P..2P+1'] = [n for n in claim[11][0] if n >= 10] == [11, 22]
    c['P12 flats only {12,24} in P..2P+1'] = [n for n in claim[12][0] if n >= 11] == [12, 24]
    print()
    for k, v in c.items(): print('  check', k, v)
    ok &= all(c.values())

    # controls
    print('\nCONTROLS')
    for P in (11, 12):
        a = run(P, 137, 'B')
        b0 = run(P, 0, 'B'); f = run(P, 137, 'B', 'false'); tr = run(P, 137, 'B', 'true')
        for name, x in (('base-0', b0), ('cover-False', f), ('cover-True', tr)):
            diff = [N for N in range(P - 1, 2 * P + 2) if x[N] != a[N]]
            print('  P%d %s differs at %d/%d N; flats %s; avg(P)=%s avg(2P)=%s' % (
                P, name, len(diff), P + 3, flats(x, 2, 2 * P + 1), x[P], x[2 * P]))
            # control "passes the claim" would be a problem
            if x[P] == a[P] and x[2*P] == a[2*P] and not diff: ok = False; print('  control NOT differing!')
    # base-0 also with other impls for agreement
    ag0 = all(run(P, 0, 'A') == run(P, 0, 'B') == run(P, 0, 'C') for P in (11, 12))
    print('  base-0 impl agreement:', ag0); ok &= ag0

    print('\nruntime %.1fs' % (time.time() - t0))
    s = ('P12 avg(12)=%s avg(24)=%s flats %s; P11 avg(11)=%s avg(12)=%s flats %s; P13 flats %s; '
         'calib %s; impls agree %s' % (a12[12], a12[24], [n for n in claim[12][0] if n >= 11],
         a11[11], a11[12], [n for n in claim[11][0] if n >= 10], [n for n in claim[13][0] if n >= 12], cal, agree))
    print('RESULT: %s %s' % ('PASS' if ok else 'FAIL', s))

main()
