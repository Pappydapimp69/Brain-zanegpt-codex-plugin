#!/usr/bin/env python3
"""Blind rebuild: lossless age cutoff vs. largest valid lag when fallback role A is RESTRICTED.

PREDICTION (written before the first run, never edited afterwards):
  (1) In every scenario (A empty, single residue, periodic subsets of various periods, sparse /
      aperiodic tick sets, both press conventions X and Y) the brute-force minimal lossless
      cutoff equals the largest configured lag that has at least one valid press (0 if none),
      and equals the closed-form / bitmask-arithmetic answer. Zero mismatches.
  (2) The largest configured lag differs from that cutoff only when the largest configured lag
      itself has no valid press. Constructed breaker: B on ticks {0,1} mod 10, A empty,
      lags {1,7}: lag 1 valid, lag 7 not -> cutoff 1, max configured 7. The negative control
      'cutoff = max configured lag' must therefore FAIL (nonzero mismatches) on the breaker
      and on the random restricted-fallback pool.
  (3) With a random periodic NONEMPTY fallback the largest configured lag fails to have a valid
      press in a nonzero but minority fraction of cases (so 'almost always' is NOT exact; I
      guess roughly 1%-20% depending on density, higher when A is sparse and under convention X
      where A only fires at ticks B is off). It is exactly 0 when the largest lag is a multiple
      of the combined period (as long as some role is ever available).

MODEL (reconstructed from other lessons in the age-cutoff family, not from the target):
  Role B available on set Sb of ticks, fallback A on Sa. A press is made at tick t with a lag
  L from the configured lag set; it lands at t+L (must be inside the horizon).
  Convention X: hinted role = B if B(t) else A if A(t) else NO press.
  Convention Y: every tick presses, hinted role = B if B(t) else A.
  A press is VALID iff the hinted role is available at t+L.
  The age cutoff c drops any press with lag L > c.  A cutoff is lossless iff no valid press is
  dropped.  Minimal lossless cutoff = smallest c >= 0 with zero dropped valid presses.
"""
import random
import time
from math import gcd

T0 = time.time()


# ---------------------------------------------------------------- fixtures
def lcm(a, b):
    return a * b // gcd(a, b)


def periodic_set(period, residues, horizon):
    return {t for t in range(horizon) if (t % period) in residues}


def make_horizon(periods, maxlag):
    l = 1
    for p in periods:
        l = lcm(l, p)
    return 2 * l + maxlag + 2


# ---------------------------------------------------------------- impl 1: direct simulation
def sim_valid_presses(Sb, Sa, lags, T, conv):
    """Return list of (t, L) valid presses by literally simulating every tick."""
    out = []
    for t in range(T):
        inB = t in Sb
        inA = t in Sa
        if inB:
            role = Sb
        elif conv == 'X':
            if not inA:
                continue
            role = Sa
        else:
            role = Sa
        for L in lags:
            if t + L < T and (t + L) in role:
                out.append((t, L))
    return out


def sim_lossless_cutoff(Sb, Sa, lags, T, conv):
    valid = sim_valid_presses(Sb, Sa, lags, T, conv)
    for c in range(0, max(lags) + 1):
        dropped = sum(1 for (_, L) in valid if L > c)
        if dropped == 0:
            return c
    raise AssertionError("no lossless cutoff found")


# ---------------------------------------------------------------- impl 2: bitmask set arithmetic
def to_mask(S):
    m = 0
    for t in S:
        m |= 1 << t
    return m


def mask_valid_lag(Bm, Am, L, T, conv):
    full = (1 << T) - 1
    notB = full & ~Bm
    via_B = Bm & (Bm >> L)
    if conv == 'X':
        via_A = (Am & notB) & (Am >> L)
    else:
        via_A = notB & (Am >> L)
    return (via_B | via_A) & ((1 << max(T - L, 0)) - 1) != 0


def closed_form_cutoff(Sb, Sa, lags, T, conv):
    Bm, Am = to_mask(Sb), to_mask(Sa)
    good = [L for L in lags if mask_valid_lag(Bm, Am, L, T, conv)]
    return (max(good) if good else 0), good


# ---------------------------------------------------------------- third check: residues (periodic only)
def residue_valid_lag(Pb, Rb, Pa, Ra, L, conv):
    P = lcm(Pb, Pa)
    for r in range(P):
        inB = (r % Pb) in Rb
        inA = (r % Pa) in Ra
        landB = ((r + L) % Pb) in Rb
        landA = ((r + L) % Pa) in Ra
        if inB:
            if landB:
                return True
        elif conv == 'X':
            if inA and landA:
                return True
        else:
            if landA:
                return True
    return False


# ---------------------------------------------------------------- scenario generation
def rand_res(rng, P, dens_lo, dens_hi, allow_empty):
    k = max(0 if allow_empty else 1, round(P * rng.uniform(dens_lo, dens_hi)))
    k = min(k, P)
    return set(rng.sample(range(P), k))


def main():
    rng = random.Random(2026100877)
    st = dict(mism=0, ncase=0, zero=0, differs=0, differs_invalid=0, rmism=0, rchecked=0)

    def check(Sb, Sa, lags, T, conv, periodic=None):
        s = sim_lossless_cutoff(Sb, Sa, lags, T, conv)
        cf, good = closed_form_cutoff(Sb, Sa, lags, T, conv)
        st['ncase'] += 1
        if s != cf:
            st['mism'] += 1
        if s == 0:
            st['zero'] += 1
        mx = max(lags)
        if s != mx:
            st['differs'] += 1
            if mx not in good:
                st['differs_invalid'] += 1
        if periodic:
            Pb, Rb, Pa, Ra = periodic
            rg = [L for L in lags if residue_valid_lag(Pb, Rb, Pa, Ra, L, conv)]
            rc = max(rg) if rg else 0
            st['rchecked'] += 1
            if rc != s:
                st['rmism'] += 1
        return s

    # ---- Scenario 1: periodic B, restricted periodic fallback A of many shapes, both conventions
    A_kinds = ['empty', 'single', 'sparse', 'half', 'dense', 'full']
    for _ in range(3000):
        Pb = rng.randint(3, 12)
        Rb = rand_res(rng, Pb, 0.15, 0.7, False)
        kind = rng.choice(A_kinds)
        if kind == 'empty':
            Pa, Ra = 1, set()
        elif kind == 'full':
            Pa, Ra = 1, {0}
        else:
            Pa = rng.randint(2, 9)
            if kind == 'single':
                Ra = {rng.randrange(Pa)}
            elif kind == 'sparse':
                Ra = rand_res(rng, Pa, 0.1, 0.3, False)
            elif kind == 'half':
                Ra = rand_res(rng, Pa, 0.4, 0.6, False)
            else:
                Ra = rand_res(rng, Pa, 0.7, 0.95, False)
        n = rng.randint(1, 4)
        lags = sorted(rng.sample(range(1, 15), n))
        T = make_horizon([Pb, Pa], max(lags))
        Sb = periodic_set(Pb, Rb, T)
        Sa = periodic_set(Pa, Ra, T)
        for conv in ('X', 'Y'):
            check(Sb, Sa, lags, T, conv, (Pb, Rb, Pa, Ra))

    # ---- Scenario 2: sparse / aperiodic explicit tick sets (squares, powers of 2, random)
    T = 260
    squares = {i * i for i in range(17) if i * i < T}
    pow2 = {1 << i for i in range(9)}
    rndB = set(rng.sample(range(T), 90))
    rndA = set(rng.sample(range(T), 12))
    for name, Sb, Sa in [
        ('aperiodic-A-empty', squares, set()),
        ('aperiodic-A-pow2', squares, pow2),
        ('aperiodic-A-random12', rndB, rndA),
        ('aperiodic-A-single-tick', rndB, {5}),
        ('aperiodic-B-empty-A-empty', set(), set()),
        ('aperiodic-B-empty-A-sq', set(), squares),
    ]:
        for _ in range(250):
            lags = sorted(rng.sample(range(1, 30), rng.randint(1, 5)))
            for conv in ('X', 'Y'):
                check(Sb, Sa, lags, T, conv)

    # ---- Scenario 3: exhaustive small periodic: P=6, B windows (size<=3) x every A subset
    P = 6
    T6 = make_horizon([P], 8)
    exh = 0
    for bm in range(1, 1 << P):
        Rb = {r for r in range(P) if bm >> r & 1}
        if len(Rb) > 3:
            continue
        Sb = periodic_set(P, Rb, T6)
        for am in range(0, 1 << P):
            Ra = {r for r in range(P) if am >> r & 1}
            Sa = periodic_set(P, Ra, T6)
            for lags in ([1, 7], [2, 5, 8], [3, 6], [1, 4, 8], [7], [2, 3, 7]):
                for conv in ('X', 'Y'):
                    check(Sb, Sa, lags, T6, conv, (P, Rb, P, Ra))
                    exh += 1
    print(f"scenarios 1-3: cases={st['ncase']} (exhaustive part {exh}) cutoff0_cases={st['zero']}")

    # ---- Breaker: lags {1,7}, B = {0,1} mod 10, A empty -> cutoff 1 not 7
    Tb = make_horizon([10], 7)
    SbK = periodic_set(10, {0, 1}, Tb)
    brk_sim = sim_lossless_cutoff(SbK, set(), [1, 7], Tb, 'X')
    brk_cf, brk_good = closed_form_cutoff(SbK, set(), [1, 7], Tb, 'X')
    brk_sim_Y = sim_lossless_cutoff(SbK, set(), [1, 7], Tb, 'Y')
    valid = sim_valid_presses(SbK, set(), [1, 7], Tb, 'X')
    lost_at_1 = sum(1 for _, L in valid if L > 1)
    lost_at_0 = sum(1 for _, L in valid if L > 0)
    brk_ok = (brk_sim == 1 and brk_cf == 1 and brk_good == [1] and brk_sim_Y == 1
              and lost_at_1 == 0 and lost_at_0 > 0)
    # restricted but nonempty fallback that rescues lag 7 (A on residues {0,2} mod 7)
    SaR = periodic_set(7, {0, 2}, Tb)
    resc = sim_lossless_cutoff(SbK, SaR, [1, 7], Tb, 'X')
    resc_cf, _ = closed_form_cutoff(SbK, SaR, [1, 7], Tb, 'X')
    print(f"breaker: sim={brk_sim} closed={brk_cf} (Y: {brk_sim_Y}) maxconf=7 lost_at_cutoff1={lost_at_1} "
          f"lost_at_cutoff0={lost_at_0}; rescue by A={{0,2}} mod 7: sim={resc} closed={resc_cf}")

    # ---- Negative control: 'cutoff = max configured lag' must fail on breaker + restricted pool
    nc_breaker_fail = (brk_sim != 7)
    nc_pool_fail = st['differs']
    print(f"negative control (cutoff = max configured): fails on breaker={nc_breaker_fail}; "
          f"fails in {nc_pool_fail}/{st['ncase']} pool cases; of those {st['differs_invalid']} had "
          f"an INVALID max configured lag")

    # ---- Claim 3: how often does the largest configured lag lack a valid press under a random
    # PERIODIC NONEMPTY fallback?  bitmask arithmetic only, many cases.
    rng2 = random.Random(8675309)
    stats = {}
    exc_mult = 0
    mult_checked = 0
    for conv in ('X', 'Y'):
        for dens_name, lo, hi in [('sparse', 0.1, 0.3), ('half', 0.4, 0.6), ('dense', 0.7, 0.95)]:
            tot = bad = 0
            ex = None
            for _ in range(20000):
                Pb = rng2.randint(3, 12)
                Rb = rand_res(rng2, Pb, 0.15, 0.7, False)
                Pa = rng2.randint(2, 9)
                Ra = rand_res(rng2, Pa, lo, hi, False)
                lags = sorted(rng2.sample(range(1, 15), rng2.randint(1, 4)))
                T = make_horizon([Pb, Pa], max(lags))
                Bm = to_mask(periodic_set(Pb, Rb, T))
                Am = to_mask(periodic_set(Pa, Ra, T))
                tot += 1
                if not mask_valid_lag(Bm, Am, lags[-1], T, conv):
                    bad += 1
                    if ex is None:
                        ex = (Pb, sorted(Rb), Pa, sorted(Ra), lags[-1])
                Lm = lcm(Pb, Pa) * rng2.randint(1, 2)
                Tm = make_horizon([Pb, Pa], Lm)
                mult_checked += 1
                if not mask_valid_lag(to_mask(periodic_set(Pb, Rb, Tm)),
                                      to_mask(periodic_set(Pa, Ra, Tm)), Lm, Tm, conv):
                    exc_mult += 1
            stats[(conv, dens_name)] = (bad, tot, ex)
    tot_all = sum(v[1] for v in stats.values())
    bad_all = sum(v[0] for v in stats.values())
    for k, (b, t, ex) in stats.items():
        print(f"  claim3 conv={k[0]} A-density={k[1]:6s}: max-configured-lag has NO valid press in "
              f"{b}/{t} = {100*b/t:.2f}%  e.g. (Pb,Rb,Pa,Ra,maxlag)={ex}")
    print(f"  claim3 overall: {bad_all}/{tot_all} = {100*bad_all/tot_all:.2f}%; max lag = multiple of "
          f"combined period: exceptions {exc_mult}/{mult_checked}")

    p1 = (st['mism'] == 0 and st['rmism'] == 0)
    p2 = (brk_ok and nc_breaker_fail and nc_pool_fail > 0
          and st['differs'] == st['differs_invalid'])
    ok = p1 and p2
    print(f"mism={st['mism']}/{st['ncase']} residue_mism={st['rmism']}/{st['rchecked']} "
          f"maxconf_differs={st['differs']} all_with_invalid_max={st['differs'] == st['differs_invalid']} "
          f"runtime={time.time()-T0:.1f}s")
    print(f"RESULT: {'PASS' if ok else 'FAIL'} {st['ncase']} cases mism={st['mism']} "
          f"residue_mism={st['rmism']} breaker_cutoff={brk_sim}_vs_maxconf=7 "
          f"negctl_fails_pool={nc_pool_fail} claim3_maxlag_invalid_rate={100*bad_all/tot_all:.2f}% "
          f"({bad_all}/{tot_all}) multiple_of_period_exceptions={exc_mult}")


if __name__ == '__main__':
    main()
