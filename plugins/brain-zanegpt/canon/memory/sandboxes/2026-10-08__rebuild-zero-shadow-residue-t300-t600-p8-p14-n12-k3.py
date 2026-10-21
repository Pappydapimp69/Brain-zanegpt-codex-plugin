#!/usr/bin/env python3
"""Blind rebuild: contiguous always-on zero shadowing is a T mod P residue effect.

PREDICTION (written before the first run of the claim, never edited afterwards)
-------------------------------------------------------------------------------
Model (taken from OTHER lessons of the age-cutoff family, not from the target):
  ticks t = 0..T-1; role B ("contiguous" window) available at t iff t mod P < w
  for every width w = 1..P-1; fallback A always available; the hint at t is B if
  available else A; a press of lag L at tick t is legal iff t is outside B or
  t+L is inside B; its landing is t+L (landings past the horizon allowed).
  Lag universe 1..12, every 3-lag set (C(12,3)=220, so P8 has 1540 cases, P14 2860).
  A set is SHADOWED iff the largest legal lag differs from the coverage cutoff
  (the largest lag adding a landing tick not served by a smaller lag of the set).
Mechanism I expect: with free landings the only T-dependence is the top edge; a
  legal press of the largest lag at t in [T-(L3-L2), T) lands where no smaller lag
  lands, so it un-shadows the set.  At T mod P == 0 the last tick has residue P-1
  (outside every window, always legal) so the count is 0 at residue 0.
Predictions:
  1. count(T) depends only on T mod P once T >= ~P+12 (equal for T and T+P, and
     equal across the 300s, 600s and 1000s ranges), at P 8,12,14,15 and hold-outs 9,10,13.
  2. P8 is zero only at residue 0 and its peak over residues is 184 (N=12, 3-lag).
  3. P14 is zero exactly at residues {0,12,13}.
  4. The T300-range table equals the T600-range table by residue; count(300) > 0 for
     P8 (300%8=4) and P14 (300%14=6) while count(600)=0 for both.
  5. Calibration on other lessons at T=600, lags 1..12, 3-lag sets: P7 26, P9 93,
     P11 50, P13 126, P16 308, P17 635, P18 825, P19 308, P21 504; zero at P6,8,10,12,14,15,20;
     P15 profile from T=300: 0,55,155,291,364,390,363,287,175,90,40,14,3,0,0.
  6. Controls: T->T+1 shift changes counts; small T (< P+12) is not yet periodic;
     clipped landings (landing < T) remove the top edge, so counts become constant in T
     (no residue structure, P8 not zero only at residue 0).
  7. Other lag universes N != 12 do not reproduce the calibration numbers.
-------------------------------------------------------------------------------
"""
import sys, time
from itertools import combinations

t0 = time.time()
N_DEFAULT = 12


# ---------- implementation A: direct simulation with explicit sets ----------
def count_direct(T, P, N=N_DEFAULT, k=3, clip=False):
    lags = range(1, N + 1)
    combs = list(combinations(lags, k))
    total = shadow = 0
    for w in range(1, P):
        S = {}
        for L in lags:
            s = set()
            for t in range(T):
                inB = (t % P) < w
                if (not inB) or (((t + L) % P) < w):
                    u = t + L
                    if clip and u >= T:
                        continue
                    s.add(u)
            S[L] = s
        for c in combs:
            total += 1
            legal = [L for L in c if S[L]]
            if not legal:
                continue
            largest_legal = max(legal)
            cutoff = None
            seen = set()
            for L in c:  # ascending
                if S[L] - seen:
                    cutoff = L
                seen |= S[L]
            if cutoff != largest_legal:
                shadow += 1
    return shadow, total


# ---------- implementation B: bigint bitmask / periodic arithmetic ----------
_rep_cache = {}


def _rep(P, T):
    key = (P, T)
    if key not in _rep_cache:
        k = T // P + 1
        _rep_cache[key] = (((1 << (P * k)) - 1) // ((1 << P) - 1), (1 << T) - 1)
    return _rep_cache[key]


def count_mask(T, P, N=N_DEFAULT, k=3, clip=False):
    lags = range(1, N + 1)
    combs = list(combinations(lags, k))
    rep, full = _rep(P, T)
    total = shadow = 0
    for w in range(1, P):
        M = {}
        for L in lags:
            pat = 0
            for r in range(P):
                if r >= w or ((r + L) % P) < w:
                    pat |= 1 << r
            legal_ticks = (rep * pat) & full  # bit t set iff press at t legal
            m = legal_ticks << L  # bit u set iff landing u served
            if clip:
                m &= full
            M[L] = m
        for c in combs:
            total += 1
            nz = [L for L in c if M[L]]
            if not nz:
                continue
            acc = 0
            cutoff = None
            for L in c:
                if M[L] & ~acc:
                    cutoff = L
                acc |= M[L]
            if cutoff != max(nz):
                shadow += 1
    return shadow, total


def table(P, Ts, f=count_mask, **kw):
    return {T: f(T, P, **kw)[0] for T in Ts}


def main():
    ok = {}
    notes = []
    mods = [8, 12, 14, 15]
    holds = [9, 10, 13]
    allm = mods + holds
    big = list(range(290, 340)) + list(range(590, 640)) + list(range(1000, 1101))

    # bitmask tables over many horizons
    tab = {}
    for P in allm:
        tab[P] = {T: count_mask(T, P)[0] for T in list(range(1, 3 * P + 25)) + big}
    print("bitmask tables built %.1fs" % (time.time() - t0), flush=True)

    # cross-implementation agreement (direct sim) on a subset
    mism = 0
    ncheck = 0
    for P in allm:
        Ts = list(range(1, 3 * P + 25, 5 if P not in mods else 2))
        Ts += [300 + i for i in range(P)] + [600 + i for i in range(P)]
        if P in mods:
            Ts += [1000 + i for i in range(P)]
        for T in Ts:
            a = count_direct(T, P)[0]
            ncheck += 1
            if a != tab[P][T]:
                mism += 1
                print("MISMATCH", P, T, a, tab[P][T])
    # also clip mode agreement
    for P in (8, 14):
        for T in (61, 300, 305, 600, 603):
            if count_direct(T, P, clip=True)[0] != count_mask(T, P, clip=True)[0]:
                mism += 1
    ok["impls_agree"] = mism == 0
    print("direct-vs-bitmask checks=%d mismatches=%d  %.1fs" % (ncheck, mism, time.time() - t0), flush=True)

    # periodicity: count(T)==ref[T mod P] for all large T
    per_viol = {}
    ref = {}
    for P in allm:
        ref[P] = {r: tab[P][600 + ((r - 600) % P)] for r in range(P)}
        v = 0
        for T in big:
            if tab[P][T] != ref[P][T % P]:
                v += 1
        # T vs T+P over the whole tabulated small+big range for T>=P+12
        for T in sorted(tab[P]):
            if T >= P + 12 and (T + P) in tab[P] and tab[P][T] != tab[P][T + P]:
                v += 1
        per_viol[P] = v
    ok["periodic_all"] = all(v == 0 for v in per_viol.values())
    print("periodicity violations by P:", per_viol)

    def prof(P, base):  # residue -> count for T in base..base+P-1
        return {(base + i) % P: tab[P][base + i] for i in range(P)}

    zeros = {P: sorted(r for r, c in ref[P].items() if c == 0) for P in allm}
    peaks = {P: max(ref[P].values()) for P in allm}
    argpk = {P: sorted(r for r, c in ref[P].items() if c == peaks[P]) for P in allm}
    print("zero residues:", zeros)
    print("peak counts  :", peaks, "at residues", argpk)
    ok["p8_zero_only_0"] = zeros[8] == [0]
    ok["p8_peak_184"] = peaks[8] == 184
    ok["p14_zero_0_12_13"] = zeros[14] == [0, 12, 13]

    same = True
    for P in allm:
        p3, p6, p10 = prof(P, 300), prof(P, 600), prof(P, 1000)
        if not (p3 == p6 == p10):
            same = False
    ok["t300_eq_t600_by_residue"] = same
    nz = tab[8][300] > 0 and tab[14][300] > 0 and tab[8][600] == 0 and tab[14][600] == 0
    ok["t300_nonzero_t600_zero"] = nz
    print("T300/T600/T1200 values: P8 %s P14 %s" % ((tab[8][300], tab[8][600]), (tab[14][300], tab[14][600])))
    print("P8 table by residue :", [ref[8][r] for r in range(8)])
    print("P14 table by residue:", [ref[14][r] for r in range(14)])
    print("P12 table by residue:", [ref[12][r] for r in range(12)])
    print("P15 table by residue:", [ref[15][r] for r in range(15)])

    # ---- calibration on OTHER lessons (all at T=600, lags 1..12, 3-lag, free landings)
    calib_T600 = {6: 0, 7: 26, 8: 0, 9: 93, 10: 0, 11: 50, 12: 0, 13: 126, 14: 0, 15: 0,
                  16: 308, 17: 635, 18: 825, 19: 308, 20: 0, 21: 504}
    cal_bad = {P: (count_mask(600, P)[0], v) for P, v in calib_T600.items() if count_mask(600, P)[0] != v}
    ok["calib_T600_all16"] = not cal_bad
    p15_rec = [0, 55, 155, 291, 364, 390, 363, 287, 175, 90, 40, 14, 3, 0, 0]
    p15_mine = [tab[15][300 + i] for i in range(15)]
    ok["calib_P15_profile"] = p15_mine == p15_rec
    ok["calib_P14_T1200_14_T300_251"] = count_mask(1200, 14)[0] == 14 and tab[14][300] == 251 and tab[8][300] == 184
    print("calibration T600 mismatches:", cal_bad, "| P15 profile ok:", ok["calib_P15_profile"], p15_mine)
    print("P14 T1200:", count_mask(1200, 14)[0], "P14 max over period:", peaks[14])
    ok["calib_totals"] = (count_mask(600, 8)[1], count_mask(600, 14)[1], count_mask(600, 9)[1]) == (1540, 2860, 1760)

    # ---- alternatives: other lag universes / set sizes (rejected?)
    alt = {}
    for N in (8, 10, 11, 12, 13, 14, 16):
        mism_n = sum(1 for P in (7, 9, 11, 13, 16, 18, 21) if count_mask(600, P, N=N)[0] != calib_T600[P]) if N != 12 else 0
        r8 = [count_mask(600 + i, 8, N=N)[0] for i in range(8)]  # T=600+i -> residue i
        r14 = [count_mask(600 + i, 14, N=N)[0] for i in range(14)]
        alt[N] = (mism_n, max(r8), [(600 + i) % 8 for i, c in enumerate(r8) if c == 0], [(600 + i) % 14 for i, c in enumerate(r14) if c == 0])
        print("N=%d calib_mismatch(of 7 moduli)=%d P8 peak=%d P8 zeros=%s P14 zeros=%s" % ((N,) + alt[N]))
    for k in (2, 4):
        r9 = count_mask(600, 9, k=k)
        print("k=%d P9@600 shadow/total=%s (recorded 3-lag: 93/1760; recorded 4-lag: 363/3960)" % (k, r9))
    ok["only_N12_calibrates"] = alt[12][0] == 0 and all(alt[n][0] > 0 for n in alt if n != 12)
    ok["N12_unique_p8_184"] = [n for n in alt if alt[n][1] == 184] == [12]

    # ---- negative controls
    # (a) shift by one tick
    shift = {P: sum(1 for r in range(P) if ref[P][r] != ref[P][(r + 1) % P]) for P in allm}
    ok["ctrl_shift1_changes"] = all(v > 0 for v in shift.values())
    # (b) small T not yet periodic
    smallviol = {P: sum(1 for T in range(1, P + 12) if (T + P) in tab[P] and tab[P][T] != tab[P][T + P]) for P in allm}
    ok["ctrl_small_T_not_periodic"] = all(v > 0 for v in smallviol.values())
    # (c) clipped landings: residue structure should vanish
    clip = {}
    for P in (8, 14):
        c = [count_mask(600 + i, P, clip=True)[0] for i in range(P)]
        clip[P] = c
    ok["ctrl_clipped_flat_no_zero_residue"] = all(len(set(c)) == 1 and c[0] > 0 for c in clip.values())
    print("control shift1 residue changes:", shift)
    print("control small-T non-periodic T count:", smallviol)
    print("control clipped (T=600..): P8", clip[8], "P14", clip[14][:5], "... all equal:",
          {P: len(set(c)) == 1 for P, c in clip.items()})

    must = ["impls_agree", "periodic_all", "p8_zero_only_0", "p8_peak_184", "p14_zero_0_12_13",
            "t300_eq_t600_by_residue", "t300_nonzero_t600_zero", "calib_T600_all16", "calib_P15_profile",
            "ctrl_shift1_changes", "ctrl_small_T_not_periodic", "ctrl_clipped_flat_no_zero_residue"]
    for kx, v in ok.items():
        print("  %-36s %s%s" % (kx, v, "" if kx in must else "   (informational)"))
    passed = all(ok[m] for m in must)
    print("elapsed %.1fs" % (time.time() - t0))
    print("RESULT: %s impls_agree=%s periodic_all=%s P8_zero=%s P8_peak=%d P14_zero=%s T300_eq_T600=%s "
          "P8_T300=%d P14_T300=%d calib_T600=%s onlyN12=%s zeros12=%s zeros15=%s" % (
              "PASS" if passed else "FAIL", ok["impls_agree"], ok["periodic_all"], zeros[8], peaks[8],
              zeros[14], ok["t300_eq_t600_by_residue"], tab[8][300], tab[14][300],
              ok["calib_T600_all16"], ok["only_N12_calibrates"], zeros[12], zeros[15]))


main()
