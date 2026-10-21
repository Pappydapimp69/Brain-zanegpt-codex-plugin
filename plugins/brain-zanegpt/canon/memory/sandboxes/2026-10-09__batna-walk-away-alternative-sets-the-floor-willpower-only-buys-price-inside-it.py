"""Sandbox: does bargaining power come from the walk-away alternative (BATNA), not willpower?

A MODEL shows the logic of a bargaining structure. It does NOT show how humans behave.

PREDICTIONS (written before the first run; each could come out wrong):
 P1 (exact alternating-offers DP, 100-unit pie, delta=0.9, 40 rounds, buyer has no alternative):
    seller payoff stays flat at about 52.6 (+-2) for seller alternative o_s <= 40, then
    follows 100 - 0.9*(100-o_s): 64 (+-1) at o_s=60 and 82 (+-1) at o_s=80. Raising an alternative
    that is below the no-alternative share buys nothing.
 P2 (concession agents; willpower = slow concession, BATNA = reservation price, 'toughness' cs):
    a tough seller's premium over a soft seller (same BATNA) is <= 8 when the buyer's walk-away
    ceiling is 40 and >= 25 when the ceiling is 100. Willpower converts to price only where the
    counterparty's alternative is weak.
 P3 (no zone of agreement, S_out > B_out): impasse for EVERY toughness level 0.02..0.9
    (willpower cannot create a deal). Seller then receives exactly its own alternative.
 P4 (negative control: both alternatives non-binding, floor 0 / ceiling 100): changing the seller
    alternative across 0..20 changes the price by 0 while toughness changes it by >= 20.
    (If this failed the model would be rigged toward BATNA.)
 P5 (first offer, sibling kernel): price rises monotonically with the seller's opening ask and is
    flat once the buyer ceiling binds.
 P6 (confounded population, fixed seed): naive correlation of toughness with payoff is >= 0.3 but
    falls by >= 50% once BATNA is held fixed (stratified); BATNA's own correlation stays >= 0.5.
P7 (added in iteration 2, AFTER P6 came out refuted in run 1 -- exploratory, not a pre-registered
    prediction): when counterparties have real alternatives (buyer ceilings 45-65 instead of 70-90)
    the within-BATNA willpower correlation drops by >= 30% relative to the P6 population.
All checks must hold for RESULT: PASS.

ITERATION LOG (kept honest):
 run 1: P1 missed (seller got 50 on the integer 100-grid, not 52.6+-2: rounding artifact, verified
        on a 10000-grid in run 2); P2 and P5 'failed/passed' for the wrong reason (60-round deadline
        made tough agents hit impasse); P5 tolerance did not allow price = ask at gap<=1; P6 refuted.
 run 2: fixed rounds 60 -> 400 (deadline kept as its own scenario S9), P1 evaluated on the fine grid,
        P5 tolerance ceiling+1. Predictions P1-P6 text left unchanged. P6 stays refuted.
"""
import math
import random


# ---------------- Layer A: exact alternating-offers with outside options (DP) -------------
def rubinstein(o_s, o_b, d_s=0.9, d_b=0.9, T=40, pie=100):
    """Return (seller, buyer) round-0 payoffs, seller proposes first.
    Either side may exit instead of accepting/proposing; on exit or final rejection both
    receive their own outside option (each goes to its alternative)."""
    # value[t][who] = (proposer payoff, responder payoff) in round-t units; who 0=seller 1=buyer
    opt = (o_s, o_b)
    disc = (d_s, d_b)
    nxt = None
    for t in range(T - 1, -1, -1):
        who = 0 if t % 2 == 0 else 1
        resp = 1 - who
        if nxt is None:
            r = opt[resp]                      # final round: reject == breakdown
        else:
            # responder's reject value: exit, or become proposer next round (discounted)
            r = max(opt[resp], disc[resp] * nxt[0])
        r_int = math.ceil(r - 1e-9)
        demand = pie - r_int
        if demand >= opt[who] and r_int <= pie:
            cur = (demand, r_int)              # proposer takes demand, responder gets r_int
        else:
            cur = (opt[who], opt[resp])        # proposer exits
        # store in terms of (proposer, responder); the next round's proposer is the other person
        nxt = cur
        last = cur
        last_who = who
    # t=0 proposer is the seller
    return last if last_who == 0 else (last[1], last[0])


# ---------------- Layer B: concession agents -------------------------------------------------
def concede(S_out, B_out, cs, cb, ask0=100.0, bid0=0.0, rounds=400):
    """Seller ask falls by cs*gap per round (floored at its alternative S_out); buyer bid rises by
    cb*gap (capped at its ceiling B_out = price at which its alternative is as good). Agreement
    when ask-bid <= 1 (price = ask). If both are at their limits and still apart: walk away.
    Impasse pays each side its own alternative. Returns (seller_payoff, buyer_payoff, dealt)."""
    ask, bid = ask0, bid0
    for _ in range(rounds):
        gap = ask - bid
        if gap <= 1.0:
            p = ask
            return (p, 100.0 - p, True)
        ask = max(S_out, ask - cs * gap)
        bid = min(B_out, bid + cb * gap)
        if ask >= bid and ask <= S_out + 1e-9 and bid >= B_out - 1e-9 and S_out > B_out:
            break
    return (S_out, 100.0 - B_out, False)


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else 0.0


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(("ok   " if ok else "FAIL ") + name + " :: " + detail)


# ---- S1 / P1: outside-option threshold (exact DP)
coarse = rubinstein(0, 0)[0]
print(f"S1 coarse 100-grid seller share with no alternative = {coarse} (integer-rounding artifact)")
PIE = 10000
base = rubinstein(0, 0, pie=PIE)[0] / 100
s1 = {o: round(rubinstein(o * 100, 0, pie=PIE)[0] / 100, 2) for o in (0, 20, 40, 52, 60, 80)}
print("S1 seller payoff by own alternative:", s1)
flat = all(abs(s1[o] - 52.6) <= 2 for o in (0, 20, 40))
bind = abs(s1[60] - 64) <= 1 and abs(s1[80] - 82) <= 1
mono = all(s1[a] <= s1[b] for a, b in zip((0, 20, 40, 52, 60), (20, 40, 52, 60, 80)))
check("P1 threshold", flat and bind and mono, f"base={base} flat={flat} binding={bind} monotone={mono}")

# ---- S2: boundary scenario: patience (cost of waiting) is also power -> narrows the claim
pat = rubinstein(0, 0, d_s=0.97, d_b=0.85, pie=PIE)[0] / 100
print(f"S2 patience-only seller (d_s=.97 vs d_b=.85, no alternatives): {pat} (vs {base} symmetric)")

# ---- S3 / P2: willpower premium vs counterparty's walk-away ceiling
cb = 0.15
prem = {}
for ceil_ in (40, 60, 80, 100):
    tough = concede(30, ceil_, 0.05, cb)[0]
    soft = concede(30, ceil_, 0.30, cb)[0]
    prem[ceil_] = tough - soft
    print(f"S3 buyer ceiling {ceil_}: tough={tough:.1f} soft={soft:.1f} premium={prem[ceil_]:.1f}")
check("P2 premium tracks counterparty alternative", prem[40] <= 8 and prem[100] >= 25,
      f"premium@40={prem[40]:.1f} premium@100={prem[100]:.1f}")

# ---- S4: head to head (reported, not a pass condition): tough/weak vs soft/strong
for ceil_ in (60, 80, 100):
    tw = concede(10, ceil_, 0.05, cb)[0]
    ss = concede(55, ceil_, 0.30, cb)[0]
    print(f"S4 buyer ceiling {ceil_}: tough+weakBATNA={tw:.1f} vs soft+strongBATNA={ss:.1f}")

# ---- S5 / P3: negative control, no ZOPA
res = [concede(70, 50, c, cb) for c in (0.02, 0.05, 0.1, 0.3, 0.6, 0.9)]
all_impasse = all(not r[2] for r in res)
exact = all(r[0] == 70 for r in res)
check("P3 no ZOPA => impasse for all toughness", all_impasse and exact,
      f"impasses={sum(1 for r in res if not r[2])}/6 seller_gets_own_alt={exact}")

# ---- S6 / P4: negative control, alternatives non-binding
by_alt = [concede(a, 100, 0.10, cb)[0] for a in (0, 5, 10, 20)]
by_tough = [concede(0, 100, c, cb)[0] for c in (0.05, 0.10, 0.20, 0.40)]
d_alt = max(by_alt) - min(by_alt)
d_tough = max(by_tough) - min(by_tough)
check("P4 non-binding BATNA changes nothing; willpower does", d_alt == 0 and d_tough >= 20,
      f"price spread across alt={d_alt:.2f} across toughness={d_tough:.1f}")

# ---- S7 / P5: first-offer anchor
anch = [(a, concede(30, 70, 0.05, cb, ask0=a)[0]) for a in (80, 100, 140, 200, 400)]
print("S7 opening ask -> price:", [(a, round(p, 1)) for a, p in anch])
ps = [p for _, p in anch]
mono5 = all(x <= y + 0.1 for x, y in zip(ps, ps[1:]))
check("P5 anchor monotone, capped by ceiling", mono5 and abs(ps[-1] - ps[-2]) < 1 and ps[-1] <= 70 + 1.5,
      f"prices={[round(p,1) for p in ps]}")

# ---- S9: deadline variant (willpower's cost): same tough seller under a 60-round deadline
dl = [(cl, concede(30, cl, 0.05, cb, rounds=60)) for cl in (40, 60, 80)]
print("S9 tough seller, 60-round deadline:", [(cl, round(r[0], 1), 'deal' if r[2] else 'IMPASSE') for cl, r in dl])

# ---- S8 / P6: confounded population, fixed seed. Tough people tend to be those WITH alternatives.
def population(ceilings):
    rng = random.Random(20261009)
    out = []
    for _ in range(400):
        S = rng.choice([10, 20, 30, 40, 50, 60])
        tough = 0.40 - 0.005 * S + rng.uniform(-0.04, 0.04)      # strong BATNA -> slower concession
        tough = min(max(tough, 0.02), 0.5)
        B = rng.choice(ceilings)
        out.append((S, tough, concede(S, B, tough, cb)[0]))
    return out


def analyse(rows):
    S_ = [r[0] for r in rows]
    T_ = [-r[1] for r in rows]
    Y_ = [r[2] for r in rows]
    by_s = {}
    for r in rows:
        by_s.setdefault(r[0], []).append(r)
    parts = [(len(g), corr([-x[1] for x in g], [x[2] for x in g])) for g in by_s.values()]
    return corr(T_, Y_), sum(n * c for n, c in parts) / sum(n for n, _ in parts), corr(S_, Y_)


rows = population([70, 80, 90])
naive, strat, cb_ = analyse(rows)
print(f"S8 naive willpower-payoff r={naive:.2f}; within-BATNA r={strat:.2f}; BATNA-payoff r={cb_:.2f}")
check("P6 apparent willpower effect is mostly the alternative", naive >= 0.3 and strat <= 0.5 * naive and cb_ >= 0.5,
      f"naive={naive:.2f} stratified={strat:.2f} batna_r={cb_:.2f}")

n2, s2, b2 = analyse(population([45, 55, 65]))
print(f"S10 counterparties with real alternatives (ceilings 45-65): naive={n2:.2f} within-BATNA={s2:.2f} BATNA r={b2:.2f}")
check("P7 (exploratory) real counterparty alternatives shrink willpower effect", s2 <= 0.7 * strat,
      f"within-BATNA willpower r {strat:.2f} -> {s2:.2f}")

if all(checks):
    print("RESULT: PASS %d/%d checks: outside option binds only above the no-option share; willpower premium %.1f->%.1f as buyer ceiling 40->100; no-ZOPA impasse 6/6; non-binding BATNA spread %.1f vs willpower spread %.1f; naive willpower r=%.2f -> %.2f within BATNA (model logic, not human behaviour)"
          % (sum(checks), len(checks), prem[40], prem[100], d_alt, d_tough, naive, strat))
else:
    print("RESULT: FAIL %d/%d checks held (see FAIL lines above)" % (sum(checks), len(checks)))
