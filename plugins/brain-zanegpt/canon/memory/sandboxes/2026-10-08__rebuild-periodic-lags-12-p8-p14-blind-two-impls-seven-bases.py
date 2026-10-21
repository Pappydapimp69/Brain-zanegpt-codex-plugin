#!/usr/bin/env python3
"""Blind rebuild: contiguous 2-lag shadow count periodic in T at lag range N=12 across unrelated bases.

MODEL (reconstructed from sibling lessons in memory/projects/local__*age-cutoff*; see report):
  * period P (8..14); contiguous window B_w = { t : t mod P < w }, width w = 1..P-1.
  * always-on fallback.  A press at tick t with lag L is legal iff t is outside B_w
    (fallback hint, always available) or t+L is inside B_w (primary hint must be available at landing).
  * the horizon is T: presses t = 0..T-1 are made, landing ticks t+L are NOT truncated at T.
  * lag set = any 2-subset {a<b} of lags 1..N (C(N,2) sets).
  * landings(L) = { t+L : press t legal }.  coverage cutoff = last lag (ascending) whose landings are not
    all already served by earlier lags; last-landing lag = largest lag with any landing.
    The set is SHADOWED iff last-landing lag != coverage cutoff.
  * count(T) = number of (width w, 2-lag set) pairs shadowed at horizon T.
CLAIM UNDER TEST: count(T) == count(T+P) (3 full periods of T) for every base, and the one-period total
  sum_{r<P} count(base+r) is identical across bases (N=12: P14 538, P12 300).

PREDICTION (written BEFORE the first run of the claim run; never edited afterwards):
  * Calibration against OTHER lessons' numbers (N=7 totals 64,99,145,200,265,336,413; N=9 71,100,150,214,295,
    391,504; N=10/11/14 rows; N=P and N=2P averages; base-0 control 38,64,100) reproduces exactly.
  * True model N=12: ZERO periodicity violations at all bases 13,100,300,777,1000,4096,9973 over 3 full periods
    (risk: the smallest base 13 might still be inside the warm-up; I expect it to pass because the recorded
    warm-up onset was about T=7..10).  One-period totals for P8..P14 identical across all bases and equal to
    129,155,181,225,300,406,538 (so P14=538 and P12=300 both reproduce).
  * direct-simulation implementation A and bitmask implementation B agree on every count they both compute.
  * Varying N: totals are non-decreasing in N and base-independent for N=8 and N=16 too, except that a tiny base
    may violate periodicity when N is large compared with the base (N=16 at base 13 is the risky cell).
  * Negative controls: (1) counter-reset variant (effective horizon T mod 500) MUST violate periodicity and be
    base-dependent; (2) wrong-period variant (windows of period P+1 but compared at lag P) MUST violate;
    (3) tiny horizons T=1..4 at base 0 must violate (recorded in a sibling lesson); (4) landings truncated at
    horizon T is a risk prediction: I expect it NOT to violate at large bases (subset failures are monotone and
    saturate) but to be base-dependent only at small horizons.
  * Expected: RESULT: PASS.
"""
import sys, time
from itertools import combinations
from fractions import Fraction

PS = list(range(8, 15))
BASES_CLAIM = (100, 300, 777)
BASES_MINE = (13, 1000, 4096, 9973)
BASES = (13, 100, 300, 777, 1000, 4096, 9973)
BASES_A = (13, 100, 300, 777, 1000)          # direct simulation only on the smaller bases (cost)
N_MAIN = 12
t0 = time.time()

# ---------------------------------------------------------------- implementation A: direct simulation
def legal(t, L, P, w):
    if (t % P) < w:                      # primary window available at press tick -> hinted role is primary
        return ((t + L) % P) < w         # legal only if primary still available at landing
    return True                          # fallback hinted: always available

def shadow_pair_A(landA, landB, a, b):
    """generic cutoff walk over lags (a<b): returns True iff last-landing lag != coverage cutoff."""
    served = set()
    cut = 0
    last = 0
    for L, land in ((a, landA), (b, landB)):
        if land:
            last = L
        if not land <= served:           # adds an unserved landing
            cut = L
        served = served | land if L == a else served
    return last != cut

def counts_A(P, N, base, nT):
    """returns {T: count} for T in base..base+nT-1 by literal simulation (incremental landing sets)."""
    res = {T: 0 for T in range(base, base + nT)}
    lags = range(1, N + 1)
    pairs = list(combinations(lags, 2))
    for w in range(1, P):
        land = {L: set() for L in lags}
        for t in range(base):
            for L in lags:
                if legal(t, L, P, w):
                    land[L].add(t + L)
        for T in range(base, base + nT):
            c = 0
            for a, b in pairs:
                # specialised two-lag walk (same logic as shadow_pair_A, without copying big sets)
                lb = land[b]
                if lb and lb <= land[a]:
                    c += 1
            res[T] += c
            for L in lags:
                if legal(T, L, P, w):
                    land[L].add(T + L)
    return res

def shadow_pair_A_generic_check(P, N, T):
    """cross-check: the specialised subset shortcut equals the generic cutoff walk (small T only)."""
    bad = 0
    for w in range(1, P):
        land = {L: {t + L for t in range(T) if legal(t, L, P, w)} for L in range(1, N + 1)}
        for a, b in combinations(range(1, N + 1), 2):
            sp = bool(land[b]) and land[b] <= land[a]
            if sp != shadow_pair_A(land[a], land[b], a, b):
                bad += 1
    return bad

# ---------------------------------------------------------------- implementation B: bitmask / arithmetic
class MaskBank:
    """periodic landing-residue bitmasks: landing x (tick) legal iff cond(x mod P) with press t=x-L."""
    def __init__(self, P, Nmax, M, Q=None):
        self.P = P
        Q = Q or P
        self.full = {}
        for w in range(1, P):
            for L in range(1, Nmax + 1):
                bits = ['0'] * (M + L + 1)
                for x in range(M + L + 1):
                    inB_press = ((x - L) % Q) < w
                    inB_land = (x % Q) < w
                    if (not inB_press) or inB_land:
                        bits[x] = '1'
                self.full[(w, L)] = int(''.join(reversed(bits)), 2)

    def landing(self, w, L, T, truncate=False):
        lo = (1 << L)
        hi = 1 << (T + L)            # presses t=0..T-1 -> landings x in [L, T+L)
        m = self.full[(w, L)] & (hi - lo)
        if truncate:                 # CONTROL: drop landings at or after the horizon
            m &= (1 << T) - 1
        return m

def count_B(bank, N, T, truncate=False):
    P = bank.P
    c = 0
    pairs = list(combinations(range(1, N + 1), 2))
    for w in range(1, P):
        ms = {L: bank.landing(w, L, T, truncate) for L in range(1, N + 1)}
        for a, b in pairs:
            mb = ms[b]
            if mb and (mb & ~ms[a]) == 0:
                c += 1
    return c

# ---------------------------------------------------------------- helpers
def profile_B(bank, N, base, nT, f=count_B, **kw):
    return {T: f(bank, N, T, **kw) for T in range(base, base + nT)}

def check_periodic(prof, P, base):
    """3 full periods of T: count(T)==count(T+P) for T=base..base+3P-1 ; returns (checks, violations)."""
    v = 0
    for T in range(base, base + 3 * P):
        if prof[T] != prof[T + P]:
            v += 1
    return 3 * P, v

def one_period_total(prof, P, base):
    return sum(prof[T] for T in range(base, base + P))

# ---------------------------------------------------------------- calibration (other lessons' numbers)
def calibrate():
    ok = True
    rec = {  # one-period totals at base 3001-ish, from sibling lessons
        7: [64, 99, 145, 200, 265, 336, 413],
        9: [71, 100, 150, 214, 295, 391, 504],
        10: [87, 108, 150, 215, 299, 401, 524],
        11: [109, 127, 159, 215, 300, 405, 534],
        14: [143, 205, 255, 290, 339, 418, 539],
    }
    banks = {P: MaskBank(P, 28, 3100 + 2 * 14 + 40) for P in PS}
    for N, row in rec.items():
        got = [sum(count_B(banks[P], N, 3001 + r) for r in range(P)) for P in PS]
        print(f"calib N={N}: got={got} recorded={row} match={got == row}")
        ok &= (got == row)
    # average at N=P (flat) : P8 8, P9 100/9, P10 15, P11 215/11, P12 25 ; N=2P: 18,220/9,65/2,460/11,53,854/13,161/2
    avgP = [8, Fraction(100, 9), 15, Fraction(215, 11), 25]
    avg2P = [18, Fraction(220, 9), Fraction(65, 2), Fraction(460, 11), 53, Fraction(854, 13), Fraction(161, 2)]
    gP = [Fraction(sum(count_B(banks[P], P, 3001 + r) for r in range(P)), P) for P in PS[:5]]
    g2P = [Fraction(sum(count_B(banks[P], 2 * P, 3001 + r) for r in range(P)), P) for P in PS]
    print(f"calib avg N=P: {[str(x) for x in gP]} match={gP == avgP}")
    print(f"calib avg N=2P: {[str(x) for x in g2P]} match={g2P == avg2P}")
    ok &= (gP == avgP) and (g2P == avg2P)
    # base-0 control (recorded averages at N=P differ: 19/4, 64/9, 10)
    g0 = [Fraction(sum(count_B(banks[P], P, r) for r in range(P)), P) for P in (8, 9, 10)]
    r0 = [Fraction(19, 4), Fraction(64, 9), Fraction(10)]
    print(f"calib base-0 N=P avgs: {[str(x) for x in g0]} recorded {[str(x) for x in r0]} match={g0 == r0}")
    ok &= (g0 == r0)
    # implementation A against the same recorded numbers (N=7, base 300) and generic-walk cross check
    gA = []
    for P in PS:
        pa = counts_A(P, 7, 300, P)
        gA.append(sum(pa.values()))
    print(f"calib A N=7 base300: {gA} match={gA == rec[7]}")
    ok &= (gA == rec[7])
    gen_bad = sum(shadow_pair_A_generic_check(P, 9, T) for P in (8, 11, 14) for T in (3, 20, 41))
    print(f"calib generic cutoff walk vs subset shortcut mismatches: {gen_bad}")
    ok &= (gen_bad == 0)
    return ok

# ---------------------------------------------------------------- main claim run
def main():
    cal_ok = calibrate()
    print(f"[{time.time()-t0:.1f}s] calibration ok={cal_ok}")

    banks = {P: MaskBank(P, 16, max(BASES) + 4 * 14 + 4) for P in PS}
    print(f"[{time.time()-t0:.1f}s] banks built")

    results = {}                         # (N, base, P) -> (checks, viol, total, profile)
    for N in (N_MAIN, 8, 16):
        for base in BASES:
            for P in PS:
                prof = profile_B(banks[P], N, base, 4 * P)
                ch, v = check_periodic(prof, P, base)
                results[(N, base, P)] = (ch, v, one_period_total(prof, P, base), prof)
        print(f"[{time.time()-t0:.1f}s] B done N={N}")

    # implementation A (direct sim) on small bases, N=12 ; plus N=8,16 at bases 100,300
    mism = 0
    a_cells = 0
    a_viol = 0
    a_checks = 0
    for base in BASES_A:
        for P in PS:
            pa = counts_A(P, N_MAIN, base, 4 * P)
            pb = results[(N_MAIN, base, P)][3]
            for T in pa:
                a_cells += 1
                if pa[T] != pb[T]:
                    mism += 1
            ch, v = check_periodic(pa, P, base)
            a_checks += ch
            a_viol += v
    print(f"[{time.time()-t0:.1f}s] A(N=12) done: cells={a_cells} A_vs_B_mismatch={mism} A_checks={a_checks} A_viol={a_viol}")
    for N in (8, 16):
        for base in (100, 300):
            for P in PS:
                pa = counts_A(P, N, base, 4 * P)
                pb = results[(N, base, P)][3]
                for T in pa:
                    a_cells += 1
                    if pa[T] != pb[T]:
                        mism += 1
    print(f"[{time.time()-t0:.1f}s] A(N=8,16) done: total A cells={a_cells} A_vs_B_mismatch={mism}")

    # ---- report main claim
    total_checks = 0
    total_viol = 0
    viol_cells = []
    for base in BASES:
        for P in PS:
            ch, v, _, _ = results[(N_MAIN, base, P)]
            total_checks += ch
            total_viol += v
            if v:
                viol_cells.append((base, P, v))
    claim_style = sum(P for P in PS) * len(BASES_CLAIM)     # one check per residue, 3 bases = 231
    print(f"N=12 checks={total_checks} (7 bases x 3 periods x sum(P)=77) violations={total_viol} viol_cells={viol_cells}")
    print(f"claim-style count: 3 bases x sum(P)=77 -> {claim_style}; mine over the claim bases only: "
          f"{sum(results[(N_MAIN,b,P)][0] for b in BASES_CLAIM for P in PS)} (3 periods each)")
    totals_by_base = {b: [results[(N_MAIN, b, P)][2] for P in PS] for b in BASES}
    for b in BASES:
        print(f"  N=12 base {b:5d}: totals P8..P14 = {totals_by_base[b]}")
    ref = totals_by_base[BASES[0]]
    base_indep = all(totals_by_base[b] == ref for b in BASES)
    print(f"N=12 totals identical across all {len(BASES)} bases: {base_indep}; P12={ref[4]} P14={ref[6]}")
    claim_numbers = (ref[6] == 538 and ref[4] == 300)
    print(f"P14==538 and P12==300: {claim_numbers}")

    # ---- N variation
    print("N variation (one-period totals P8..P14 per base; violations):")
    nvar_ok = True
    nvar_summary = []
    for N in (8, 12, 16):
        tb = {b: [results[(N, b, P)][2] for P in PS] for b in BASES}
        vb = {b: sum(results[(N, b, P)][1] for P in PS) for b in BASES}
        same = all(tb[b] == tb[BASES[0]] for b in BASES)
        same_ex13 = all(tb[b] == tb[100] for b in BASES if b != 13)
        print(f"  N={N}: ref(base100)={tb[100]} identical_all_bases={same} identical_excluding_13={same_ex13} "
              f"violations_by_base={vb}")
        nvar_summary.append((N, tb[100], same, vb))
    n8, n12, n16 = (s[1] for s in nvar_summary)
    mono = all(x <= y <= z for x, y, z in zip(n8, n12, n16))
    print(f"  totals non-decreasing in N (8<=12<=16) for all P: {mono}")

    # ---- negative controls
    print("negative controls:")
    # (1) counter reset: effective horizon T mod 500
    M = 500
    def reset_count(bank, N, T):
        return count_B(bank, N, T % M)
    ctl_reset_v = 0
    ctl_reset_tot = {}
    for base in BASES:
        for P in PS:
            prof = profile_B(banks[P], N_MAIN, base, 4 * P, f=reset_count)
            ch, v = check_periodic(prof, P, base)
            ctl_reset_v += v
            ctl_reset_tot.setdefault(base, []).append(one_period_total(prof, P, base))
    reset_indep = all(ctl_reset_tot[b] == ctl_reset_tot[BASES[0]] for b in BASES)
    print(f"  (1) reset horizon T mod {M}: violations={ctl_reset_v} totals_base_independent={reset_indep}")
    # (2) wrong period: windows period P+1 compared at lag P
    ctl_wp_v = 0
    ctl_wp_checks = 0
    for P in PS:
        bankw = MaskBank(P, N_MAIN, 300 + 4 * P + 4, Q=P + 1)
        for base in (100, 300):
            prof = profile_B(bankw, N_MAIN, base, 4 * P)
            ch, v = check_periodic(prof, P, base)
            ctl_wp_v += v
            ctl_wp_checks += ch
    print(f"  (2) windows period P+1, compared at lag P: violations={ctl_wp_v} of {ctl_wp_checks}")
    # (3) tiny horizons
    tiny_viol = 0
    tiny_checks = 0
    for P in PS:
        prof = profile_B(banks[P], N_MAIN, 1, 4 + P)
        for T in range(1, 5):
            tiny_checks += 1
            if prof[T] != prof[T + P]:
                tiny_viol += 1
    print(f"  (3) tiny horizons T=1..4: violations={tiny_viol} of {tiny_checks}")
    # (4) truncated landings
    ctl_tr_v = 0
    ctl_tr_tot = {}
    for base in BASES:
        for P in PS:
            prof = profile_B(banks[P], N_MAIN, base, 4 * P, truncate=True)
            ch, v = check_periodic(prof, P, base)
            ctl_tr_v += v
            ctl_tr_tot.setdefault(base, []).append(one_period_total(prof, P, base))
    tr_indep = all(ctl_tr_tot[b] == ctl_tr_tot[BASES[0]] for b in BASES)
    tr_indep_ex13 = all(ctl_tr_tot[b] == ctl_tr_tot[100] for b in BASES if b != 13)
    print(f"  (4) landings truncated at horizon: violations={ctl_tr_v} totals_identical_all_bases={tr_indep} "
          f"identical_excluding_13={tr_indep_ex13} totals(base100)={ctl_tr_tot[100]}")

    controls_ok = (ctl_reset_v > 0 and not reset_indep) and ctl_wp_v > 0 and tiny_viol > 0
    true_ok = (total_viol == 0 and a_viol == 0 and mism == 0 and base_indep and claim_numbers)
    print(f"summary: cal_ok={cal_ok} true_ok={true_ok} controls_ok={controls_ok} elapsed={time.time()-t0:.1f}s")
    ok = cal_ok and true_ok and controls_ok
    print(f"RESULT: {'PASS' if ok else 'FAIL'} N=12 checks={total_checks} violations={total_viol} "
          f"bases={list(BASES)} totals(P8..P14)={ref} base_independent={base_indep} P14={ref[6]} P12={ref[4]} "
          f"A_vs_B_mismatch={mism} control_reset_viol={ctl_reset_v} control_wrongperiod_viol={ctl_wp_v} "
          f"control_tiny_viol={tiny_viol} control_trunc_viol={ctl_tr_v}")

if __name__ == "__main__":
    main()
