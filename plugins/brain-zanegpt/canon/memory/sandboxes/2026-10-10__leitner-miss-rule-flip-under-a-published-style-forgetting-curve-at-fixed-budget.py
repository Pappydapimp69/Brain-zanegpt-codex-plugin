"""Leitner miss rule (reset-to-box-1 vs drop-one-box) under a published-style forgetting
curve, compared at a FIXED REVIEW BUDGET, with the flip mapped over learner parameters.

PREDICTION (written BEFORE the first run; every item could come out wrong):
  Setting: expected-value learner (no RNG, no clock), 8 item difficulties, 240 days,
  box gaps 1,2,4,8,16,32 days times a schedule scale m (swept) so both rules can be put
  on the same reviews-per-item budget; metric = mean expected retrievability over the
  horizon (primary) and at the last day (secondary). Basis for the curve is stated below.
  Base grid: power curve, lapse keep 0.5.
  P1. Flip exists: for the base grid at gain 0.6 the sign of
      delta = retention(drop-one) - retention(reset) at matched budget changes sign at
      least once when the learner's base stability scale s sweeps {0.5,1,2,4,8}.
  P2. Direction: reset wins (delta < 0) for the weakest learners (s = 0.5, gain 0.3) and
      drop-one wins (delta > 0) for the strongest (s = 8) at the same gain.
  P3. The earlier toy's pole (drop-one is cheaper for slow-strengthening learners, gain
      0.2) does NOT carry over to matched budget with a soft curve: at s = 1, gain 0.2
      delta <= 0 (reset at least as good).
  P4. Curve robustness: replacing the power curve by an exponential curve with the same
      90%-recall stability keeps the sign of delta in >= 80% of grid cells.
  P5. Size: |delta| <= 0.05 absolute mean retention in >= 80% of grid cells, i.e. the rule
      is a second-order choice next to the budget. (Built to BREAK this: the grid includes
      lapse keep 0.2 and wide difficulty spread, and the end-of-horizon metric.)
  Exact crossing s* at gain 0.6 predicted in [1, 4].

RUN 1 RESULT (recorded honestly; the script crashed on a print AFTER computing these):
  P1 FALSE (at gain 0.6, keep 0.5, delta is positive at EVERY s: +0.016 .. +0.007; no sign
  change, so drop-one-box is better at all five s). P2 FALSE (at gain 0.3 delta(s=0.5) was
  +0.008, not negative). P3 TRUE (delta(s=1, gain 0.2) = -0.005, reset better; but at
  s=0.5 and s>=2 the same gain gave +0.007..+0.026, so the sign is not monotone in s).
  P4 TRUE (power/exp sign agreement 153/169). The drop-one-box rule won at matched budget
  in most cells; reset won only in a small pocket (gain 0.2-0.3, s about 1, more so for
  lapse keep 0.2). My predicted 'weak learner -> reset, strong learner -> drop-one' map
  was wrong: the strong learner (s=8, gain 0.2) showed the LARGEST drop-one edge (+0.021).

PREDICTION 2 (written after run 1, BEFORE run 2; run 2 adds a finer schedule grid in the
  reset-favoured pocket and a hard-threshold recall variant that restores the earlier toy's
  semantics; P1-P5 keep their run-1 wording and are re-evaluated for the record):
  P6. Drop-one-box wins (delta > 0) in >= 85% of the main-grid cells at budget 13
      (power and exp, keep 0.5 and 0.2).
  P7. Every cell where reset wins at budget 13 has gain <= 0.3 and s <= 2 (the pocket is
      confined to slow-strengthening learners, never to fast ones).
  P8. Interpolation artefact check: with a 1.12x finer schedule grid the sign of delta at
      (s=1, gain 0.2, keep 0.5, power) stays negative.
  P9. Hard-threshold recall (success iff R >= 0.8; the earlier toy's deterministic
      semantics) gives a DIFFERENT sign map than expected-value recall in at least one of
      the cells (s=1; gain 0.2, 0.6, 1.0, 1.5): recall model choice matters for the flip.

RUN 2 RESULT (recorded honestly): FAIL. P1 F, P1b F, P2 F, P3 T, P4 T (0.91), P5 T
  (|delta| <= 0.04 in 355/355 cells), P6 T (drop-one wins 100/113 cells at budget 13),
  P7 FALSE (reset also won at keep 0.2 with gain 0.6-1.0, s 0.5-1, and at exp s=2, mostly
  by < 0.002, i.e. within the schedule-grid interpolation noise), P8 T (fine grid -0.0084).
  P9 was VACUOUS: the hard-threshold frontier (theta 0.8) is not monotone in reviews, my
  interpolation produced delta = 0.0 everywhere, so it said nothing. The run-2 'P9=True'
  came from that artefact and is withdrawn.

PREDICTION 3 (written after run 2, BEFORE run 3; run 3 replaces the threshold test by a
  step-rule comparison and a gentler threshold):
  P10. Hard-threshold recall (success iff R >= 0.6) at s=1, keep 0.5, cap 20 reviews/item:
      the sign of delta (best retention under the cap, drop-one minus reset) is not the
      same at all four gains 0.2, 0.6, 1.0, 1.5 (a flip inside that range, as in the old toy).
  The reported verdict for the main claim is carried by P1/P2/P6 as written; P7 stays
  as a recorded refutation.

Basis of the learner model (stated honestly, recalled from memory, not re-fetched):
  * Retrievability R(t,S): FSRS-style power law R = (1 + (19/81) t/S)^(-0.5), so R = 0.9
    at t = S. The power form is the shape reported for forgetting-curve fits in the
    FSRS line of work (and consistent with mixtures of exponentials, Anderson & Schooler
    1991 style); the exponential R = 0.9^(t/S) is the classic Ebbinghaus-style
    alternative and is run as the robustness curve.
  * Stability growth on a successful review follows the FSRS-like shape: growth is larger
    for lower retrievability at review (desirable difficulty), smaller for larger stability
    and larger for easier items:  S' = S * (1 + g * (1.4 - d) * S^-0.15 * h(R)),
    h(R) = (exp(1.5 (1-R)) - 1) / (exp(0.15) - 1)  (h = 1 at R = 0.9).
  * Lapse: S' = max(S0, keep * S) (stability partly kept; keep swept).
  * Item difficulty d in {0.1..0.9} (8 equal weights, noise-free heterogeneity),
    start stability S0 = s * (1.6 - 1.2 d).
  The constants are modelling choices, NOT fitted to data. No human recall data.
"""
import math

INT = [1, 2, 4, 8, 16, 32]
DIFFS = [0.1 + 0.8 * k / 7 for k in range(8)]
H = 240
SMAX = 3650.0


def make_curve(kind):
    if kind == "power":
        return lambda t, S: (1.0 + (19.0 / 81.0) * t / S) ** -0.5
    return lambda t, S: 0.9 ** (t / S)


def q(S):
    # state merging: log-bucket stability (about 6% steps) so histories that end at
    # nearly the same stability share one state (keeps the expected-value tree finite)
    return round(math.exp(round(math.log(S) * 16) / 16), 5)


def hR(R):
    return (math.exp(1.5 * (1 - R)) - 1) / (math.exp(0.15) - 1)


_CUM = {}


def cum(kind, S, Rf):
    k = (kind, S)
    c = _CUM.get(k)
    if c is None:
        c = [0.0]
        for t in range(H + 2):
            c.append(c[-1] + Rf(t, S))
        _CUM[k] = c
    return c  # c[n] = sum_{t<n} R(t,S)


def run_item(rule, m, s, g, keep, d, Rf, kind="power"):
    gaps = [max(1, int(round(x * m))) for x in INT]
    S0 = s * (1.6 - 1.2 * d)
    # states: due day -> {(box, Sq, last): p}
    sched = {gaps[0]: {(0, q(S0), 0): 1.0}}
    reviews = 0.0
    integ = 0.0  # sum over days of expected R
    final = 0.0
    day = 0
    pending = dict(sched)
    while pending:
        day = min(pending)
        if day > H:
            break
        states = pending.pop(day)
        for (box, S, last), p in states.items():
            c = cum(kind, S, Rf); integ += p * (c[day - last] - c[0])
            R = Rf(day - last, S)
            reviews += p
            # success
            Sn = min(SMAX, S * (1 + g * (1.4 - d) * S ** -0.15 * hR(R)))
            nb = min(5, box + 1)
            key = (nb, q(Sn), day)
            dd = day + gaps[nb]
            pending.setdefault(dd, {})
            pending[dd][key] = pending[dd].get(key, 0.0) + p * R
            # lapse
            Sl = max(S0, keep * S)
            nb = 0 if rule == "reset" else max(0, box - 1)
            key = (nb, q(Sl), day)
            dd = day + gaps[nb]
            pending.setdefault(dd, {})
            pending[dd][key] = pending[dd].get(key, 0.0) + p * (1 - R)
    for dd, states in pending.items():
        for (box, S, last), p in states.items():
            c = cum(kind, S, Rf); integ += p * (c[H - last + 1] - c[0])
            final += p * Rf(H - last, S)
    return reviews, integ / (H + 1), final


def run(rule, m, s, g, keep, kind):
    Rf = make_curve(kind)
    rv = av = fv = 0.0
    for d in DIFFS:
        a, b, c = run_item(rule, m, s, g, keep, d, Rf, kind)
        rv += a; av += b; fv += c
    n = len(DIFFS)
    return rv / n, av / n, fv / n


MS = [0.4 * 1.4 ** k for k in range(0, 10)]  # schedule scales ~0.4 .. 7.4


def frontier(rule, s, g, keep, kind):
    pts = [run(rule, m, s, g, keep, kind) for m in MS]
    return pts  # (reviews, avgR, finalR)


def at_budget(pts, B, idx):
    """linear interpolation of retention at reviews == B; pts ordered by m ascending
    (reviews descending). Returns None when B is outside the covered range."""
    for (r1, *a1), (r2, *a2) in zip(pts, pts[1:]):
        v1, v2 = a1[idx - 1], a2[idx - 1]
        if r2 <= B <= r1 and r1 != r2:
            w = (r1 - B) / (r1 - r2)
            return v1 + w * (v2 - v1)
    return None


def delta_cell(s, g, keep, kind, budgets):
    fa = frontier("reset", s, g, keep, kind)
    fb = frontier("minus1", s, g, keep, kind)
    out = []
    for B in budgets:
        ra, rb = at_budget(fa, B, 1), at_budget(fb, B, 1)
        fa2, fb2 = at_budget(fa, B, 2), at_budget(fb, B, 2)
        if None in (ra, rb, fa2, fb2):
            out.append(None)
        else:
            out.append((rb - ra, fb2 - fa2, ra, rb))
    return out


def run_item_thr(rule, m, s, g, keep, d, Rf, theta=0.8):
    gaps = [max(1, int(round(x * m))) for x in INT]
    S0 = s * (1.6 - 1.2 * d)
    S, box, last, due = S0, 0, 0, gaps[0]
    reviews = 0
    integ = 0.0
    day = due
    while day <= H:
        integ += sum(Rf(t - last, S) for t in range(last, day))
        R = Rf(day - last, S)
        reviews += 1
        if R >= theta:
            S = min(SMAX, S * (1 + g * (1.4 - d) * S ** -0.15 * hR(R)))
            box = min(5, box + 1)
        else:
            S = max(S0, keep * S)
            box = 0 if rule == "reset" else max(0, box - 1)
        last = day
        day = day + gaps[box]
    integ += sum(Rf(t - last, S) for t in range(last, H + 1))
    return reviews, integ / (H + 1)


def run_thr(rule, m, s, g, keep, kind):
    Rf = make_curve(kind)
    rv = av = 0.0
    for d in DIFFS:
        a, b = run_item_thr(rule, m, s, g, keep, d, Rf)
        rv += a; av += b
    n = len(DIFFS)
    return rv / n, av / n


def delta_thr(s, g, keep, B, theta, ratio=1.1):
    """Hard-threshold recall. The reviews-vs-retention frontier is not monotone here
    (loops of repeated lapses), so use a step rule: best retention among schedule scales
    whose reviews/item <= B, for each miss rule."""
    ms = [0.4 * ratio ** k for k in range(int(math.log(25 / 0.4) / math.log(ratio)))]
    best = []
    Rf = make_curve("power")
    for rule in ("reset", "minus1"):
        cand = []
        for m in ms:
            rv = av = 0.0
            for d in DIFFS:
                a_, b_ = run_item_thr(rule, m, s, g, keep, d, Rf, theta)
                rv += a_; av += b_
            if rv / len(DIFFS) <= B:
                cand.append(av / len(DIFFS))
        best.append(max(cand) if cand else None)
    if None in best:
        return None
    return best[1] - best[0]


def main():
    budgets = [6.0, 9.0, 13.0, 20.0]  # reviews per item over 240 days
    sgrid = [0.5, 1, 2, 4, 8]
    ggrid = [0.2, 0.3, 0.6, 1.0, 1.5, 2.5]
    print("Delta = mean-retention(drop-one) - mean-retention(reset) at matched reviews/item")
    print("(positive: drop-one better).  budgets", budgets, " horizon", H, "days")
    cells = {}
    for kind in ("power", "exp"):
        for keep in (0.5, 0.2):
            for g in ggrid:
                for s in sgrid:
                    cells[(kind, keep, g, s)] = delta_cell(s, g, keep, kind, budgets)
    for keep in (0.5, 0.2):
        print(f"-- power curve, lapse keep {keep}: delta (x1000) by s (cols) and gain (rows), budget 13")
        print("gain\\s " + " ".join(f"{s:>7}" for s in sgrid))
        for g in ggrid:
            row = []
            for s in sgrid:
                v = cells[("power", keep, g, s)][2]
                row.append("   n/a " if v is None else f"{v[0]*1000:7.1f}")
            print(f"{g:5.1f}  " + " ".join(row))

    # first-review retention at box-2 gap, a learner-level 'per-box retention' coordinate
    def r_box(s, b):
        Rf = make_curve("power")
        return sum(Rf(INT[b], s * (1.6 - 1.2 * d)) for d in DIFFS) / len(DIFFS)
    print("mean retrievability at the box gaps for a fresh item, by s:")
    for s in sgrid:
        print(f"  s={s}: " + " ".join(f"b{b}:{r_box(s,b):.2f}" for b in range(6)))

    # P1/P2: gain 0.6 base grid, budget 13
    def d_at(kind, keep, g, s, bi):
        v = cells[(kind, keep, g, s)][bi]
        return None if v is None else v[0]
    row06 = {s: d_at("power", 0.5, 0.6, s, 2) for s in sgrid}
    # gain 0.6 not on grid: add it
    for kind in ("power",):
        for s in sgrid:
            cells[(kind, 0.5, 0.6, s)] = cells.get((kind, 0.5, 0.6, s)) or delta_cell(s, 0.6, 0.5, kind, budgets)
    row06 = {s: d_at("power", 0.5, 0.6, s, 2) for s in sgrid}
    print("gain 0.6 keep 0.5 power, budget 13: delta by s:", {s: (None if v is None else round(v, 4)) for s, v in row06.items()})
    vals = [v for v in row06.values() if v is not None]
    p1 = len(vals) >= 3 and any(a < 0 < b or b < 0 < a for a, b in zip(vals, vals[1:]))
    g03 = {s: d_at("power", 0.5, 0.3, s, 2) for s in sgrid}
    p2 = g03[0.5] is not None and g03[8] is not None and g03[0.5] < 0 < g03[8]
    v31 = d_at("power", 0.5, 0.2, 1, 2)
    p3 = v31 is not None and v31 <= 0
    # P4: sign agreement power vs exp over all comparable cells and budgets
    agree = tot = 0
    for (kind, keep, g, s), lst in cells.items():
        if kind != "power":
            continue
        other = cells.get(("exp", keep, g, s))
        if other is None:
            continue
        for a, b in zip(lst, other):
            if a is None or b is None:
                continue
            tot += 1
            agree += (a[0] > 0) == (b[0] > 0)
    p4 = tot > 0 and agree / tot >= 0.8
    # P5: size
    small = tot2 = 0
    lg = []
    for (kind, keep, g, s), lst in cells.items():
        for v in lst:
            if v is None:
                continue
            tot2 += 1
            small += abs(v[0]) <= 0.05
            lg.append((abs(v[0]), kind, keep, g, s))
    p5 = tot2 > 0 and small / tot2 >= 0.8
    lg.sort(reverse=True)
    # run-2 additions
    neg = [(k[0], k[1], k[2], k[3]) for k, lst in cells.items() if lst[2] is not None and lst[2][0] <= 0]
    tot13 = sum(1 for lst in cells.values() if lst[2] is not None)
    p6 = tot13 > 0 and (tot13 - len(neg)) / tot13 >= 0.85
    p7 = all(g <= 0.3 and s_ <= 2 for (_, _, g, s_) in neg)
    print(f"P6 drop-one wins {tot13-len(neg)}/{tot13} cells at budget 13; reset-win cells (kind,keep,gain,s):", sorted(neg))
    global MS
    MS_save = MS
    MS = [0.4 * 1.12 ** k for k in range(20)] + [0.4 * 1.12 ** 19 * 1.4 ** k for k in range(1, 4)]
    fine = delta_cell(1, 0.2, 0.5, "power", [13.0])[0]
    MS = MS_save
    p8 = fine is not None and fine[0] < 0
    print("P8 fine-grid delta(s=1,gain .2,keep .5):", None if fine is None else round(fine[0], 4))
    thr_cells = {}
    for g in (0.2, 0.6, 1.0, 1.5):
        thr_cells[g] = delta_thr(1, g, 0.5, 20.0, 0.6)
    ev_sign = {g: (cells[("power", 0.5, g, 1)][2][0] > 0) if cells[("power", 0.5, g, 1)][2] else None for g in (0.2, 0.6, 1.0, 1.5)}
    th_sign = {g: (None if v is None else v > 0) for g, v in thr_cells.items()}
    p9 = None  # run-2 P9 was vacuous (see header); replaced by P10
    ths = [v for v in th_sign.values() if v is not None]
    p10 = len(ths) >= 3 and (True in ths) and (False in ths)
    floor = sorted([(round(lst[2][0], 4), k) for k, lst in cells.items() if lst[2] is not None and lst[2][0] < -0.002])
    print("reset-win cells beyond a 0.002 noise floor at budget 13:", floor)
    print("P10 threshold-recall (theta .6) delta by gain (s=1, keep .5, cap 20 reviews/item):", {g: (None if v is None else round(v, 4)) for g, v in thr_cells.items()})
    print("   expected-value sign (drop-one better?):", ev_sign, " threshold sign:", th_sign)
    # budget dependence for the pocket cell
    print("pocket cell (s=1,gain .2,keep .5,power) delta by budget [6,9,13,20]:",
          [None if v is None else round(v[0], 4) for v in cells[("power", 0.5, 0.2, 1)]])
    print(f"P4 sign agreement power/exp: {agree}/{tot} = {agree/max(tot,1):.2f}")
    print(f"P5 |delta|<=0.05 in {small}/{tot2} = {small/max(tot2,1):.2f}; largest:", [(round(a, 3),) + tuple(r) for a, *r in lg[:4]])
    # sign map over (s, g) for the power/keep0.5 grid at budget 13 and exp
    flips = []
    for kind in ("power", "exp"):
        for keep in (0.5, 0.2):
            for g in ggrid:
                vs = [(s, d_at(kind, keep, g, s, 2)) for s in sgrid]
                vs = [(s, v) for s, v in vs if v is not None]
                for (s1, v1), (s2, v2) in zip(vs, vs[1:]):
                    if (v1 < 0) != (v2 < 0):
                        # linear crossing in log2 s
                        x = math.log2(s1) + (math.log2(s2) - math.log2(s1)) * (-v1) / (v2 - v1)
                        flips.append((kind, keep, g, round(2 ** x, 2)))
    print("sign flips along s (kind, keep, gain, s*):", flips)
    # crossing at gain 0.6
    cross06 = [f[3] for f in flips if f[0] == "power" and f[1] == 0.5 and f[2] == 0.6]
    print("gain 0.6 crossing s*:", cross06)
    p1b = bool(cross06) and 1 <= cross06[0] <= 4
    # budget dependence of the winner (does the flip move with budget?)
    print("winner by budget (power,keep.5,gain .6):",
          {s: [None if v is None else ('drop' if v[0] > 0 else 'reset') for v in cells[("power", 0.5, 0.6, s)]] for s in sgrid})
    # end-of-horizon metric agreement
    e_agree = e_tot = 0
    for k, lst in cells.items():
        for v in lst:
            if v is None:
                continue
            e_tot += 1
            e_agree += (v[0] > 0) == (v[1] > 0)
    print(f"end-of-horizon vs mean-retention sign agreement: {e_agree}/{e_tot}")
    print(f"P1={p1} P1b(crossing in [1,4])={p1b} P2={p2} P3={p3} P4={p4} P5={p5}")
    print(f"P6={p6} P7={p7} P8={p8} P10={p10}")
    ok = p1 and p2 and p3 and p4 and p5 and p1b and p6 and p7 and p8 and p10
    print(f"RESULT: {'PASS' if ok else 'FAIL'} P1={p1} P1b={p1b} P2={p2} P3={p3} P4={p4} P5={p5} P6={p6} P7={p7} P8={p8} P10={p10}; "
          f"gain0.6 delta by s={ {s: (None if v is None else round(v, 4)) for s, v in row06.items()} }")


main()
