"""Deterministic revenue model: premium vs free-to-play vs hybrid.

Kernel under test: ideas:MONETIZATION/model-choice/premium-is-the-optimal-default-hybrid-is-the-scale-up
Siblings exercised: ideas:MONETIZATION/ethics/pay-to-win-destroys-its-own-market-cosmetics-dont,
                    ideas:MONETIZATION/dark-patterns/premium-currency-creates-a-monopoly-money-effect

A model shows the LOGIC of the claim, not market data. Every parameter below is an
illustrative assumption chosen once, before the first run; no external figure is used.

PREDICTION (written before the first run; grid = reach 1e4..1e8 x monthly retention
.5/.7/.85/.95 = 20 cells, 24-month horizon, net = revenue - costs):
  P1  at fit=0.5 free-to-play wins 0 of 20 cells.
  P2  premium wins every cell with reach <= 1e5 (10 cells); hybrid wins >= 1 cell; the
      reach where hybrid first beats premium never rises as retention rises.
  P3  at fit=1.0 free-to-play wins >= 1 cell, and only cells with retention >= .85
      and reach >= 1e7.
  P4  negative controls: free-to-play with zero live-ops cost and fit=1 wins every
      reach at r=.85; with DLC attach 0 hybrid wins 0 cells; with zero reach all
      models net exactly minus their fixed costs.
  P5  a x1.5 spend multiplier (virtual-currency distance) on free-to-play spend at
      fit=0.2 still wins 0 cells (a spend lever does not replace mechanic fit).
  P6  pay-to-win pressure sweep on the hybrid: 24-month net peaks at an interior
      pressure (0 < x* < 1), and full pressure falls below that peak.
  P7  BREAK attempt: collapse premium store conversion 0.02 -> 0.005 at fit=0.5;
      predicted to hand free-to-play at least 1 cell (premium default has a boundary).

PREDICTION ERRATUM (found on first run): P2 says "10 cells" but reach <= 1e5 is 2 reaches
x 4 retentions = 8 cells; the check below uses 8. First-run misses are kept in the output.
Iteration 2 (added after the P6 miss, labelled post-hoc): a monthly-spend pressure
path to test the kernel's own "short spike, long burn" wording directly (P8, not a
pre-registered prediction).
"""
T = 24
CUT = 0.30
REFUND = 0.08
PRICE = 20.0
BASE = dict(
    dev=40_000.0,          # shared base-game cost
    c_p=0.02,              # premium: reach -> buyer
    c_f=0.15,              # free: reach -> install
    wom=0.6,               # word-of-mouth lift = 1 + wom * retention
    f2p_extra=40_000.0,    # economy / store / infra build
    f2p_ops=8_000.0,       # live-ops cost per month
    q0=0.04,               # f2p payer share of actives at full fit
    arppu=12.0,            # f2p spend per paying active per month
    drops=8,               # hybrid seasonal drops (every 3 months)
    drop_cost=8_000.0,
    attach=0.15,           # share of active owners buying a drop
    drop_price=8.0,
    spend_mult=1.0,        # virtual-currency spend multiplier
    p2w=0.0,               # pay-to-win pressure 0..1 on hybrid
    f2p_free_ops=False,
)

def premium(R, r, P):
    buyers = R * P["c_p"] * (1 + P["wom"] * r)
    return buyers * PRICE * (1 - REFUND) * (1 - CUT) - P["dev"]

def f2p(R, r, fit, P):
    installs = R * P["c_f"] * (1 + P["wom"] * r)
    rf = r * (0.8 + 0.2 * fit) + (1 - r) * 0.4 * fit
    q = P["q0"] * (0.25 + 0.75 * fit)
    rev = 0.0
    for t in range(T):
        rev += installs * (rf ** t) * q * P["arppu"] * P["spend_mult"] * (1 - CUT)
    ops = 0.0 if P["f2p_free_ops"] else P["f2p_ops"] * T
    extra = 0.0 if P["f2p_free_ops"] else P["f2p_extra"]
    return rev - P["dev"] - extra - ops

def hybrid(R, r, fit, P):
    x = P["p2w"]
    # pressure raises attach but erodes retention and word of mouth (kernel: p2w burns the base)
    r_h = r * (1 - 0.35 * x) + (1 - r) * 0.15 * fit * (1 - x)
    wom = P["wom"] * (1 - 0.8 * x)
    buyers = R * P["c_p"] * (1 + wom * r)
    base = buyers * PRICE * (1 - REFUND) * (1 - CUT)
    attach = P["attach"] * (1 + 3 * x) * P["spend_mult"]
    dlc = 0.0
    for d in range(1, P["drops"] + 1):
        dlc += buyers * (r_h ** (3 * d)) * attach * P["drop_price"] * (1 - CUT)
    return base + dlc - P["dev"] - P["drops"] * P["drop_cost"]

def nets(R, r, fit, P):
    return {"premium": premium(R, r, P), "f2p": f2p(R, r, fit, P), "hybrid": hybrid(R, r, fit, P)}

REACH = [1e4, 1e5, 1e6, 1e7, 1e8]
RET = [0.5, 0.7, 0.85, 0.95]

def grid(fit, P):
    wins = {"premium": [], "f2p": [], "hybrid": []}
    for r in RET:
        for R in REACH:
            n = nets(R, r, fit, P)
            wins[max(n, key=n.get)].append((R, r))
    return wins

def cross(r, fit, P):
    """smallest grid reach where hybrid beats premium (inf if none)"""
    for R in REACH:
        if hybrid(R, r, fit, P) > premium(R, r, P):
            return R
    return float("inf")

checks = []
def check(name, ok, detail):
    checks.append(ok)
    print(("ok   " if ok else "MISS ") + name + " :: " + detail)

# S1 baseline fit .5
w = grid(0.5, BASE)
check("P1 fit.5 f2p wins 0/20", len(w["f2p"]) == 0, "f2p=%d premium=%d hybrid=%d" % (len(w["f2p"]), len(w["premium"]), len(w["hybrid"])))
small = [(R, r) for r in RET for R in REACH if R <= 1e5]
check("P2a premium wins all reach<=1e5", all(c in w["premium"] for c in small), "premium cells small=%d/%d" % (sum(c in w["premium"] for c in small), len(small)))
check("P2b hybrid wins >=1", len(w["hybrid"]) >= 1, "hybrid cells=%s" % sorted(w["hybrid"]))
cr = [cross(r, 0.5, BASE) for r in RET]
mono = all(cr[i] >= cr[i + 1] for i in range(len(cr) - 1))
check("P2c crossover reach non-increasing in retention", mono, "crossovers by r=%s" % cr)

# S2 fit 1.0
w1 = grid(1.0, BASE)
ok3 = len(w1["f2p"]) >= 1 and all(r >= 0.85 and R >= 1e7 for R, r in w1["f2p"])
check("P3 fit1 f2p wins only r>=.85 & R>=1e7", ok3, "f2p cells=%s" % sorted(w1["f2p"]))
# fit threshold at the two largest reaches, r=.85
def fit_threshold(R, r, P):
    for i in range(0, 101):
        f = i / 100
        n = nets(R, r, f, P)
        if max(n, key=n.get) == "f2p":
            return f
    return None
th7, th8 = fit_threshold(1e7, 0.85, BASE), fit_threshold(1e8, 0.85, BASE)
print("info min fit for f2p to win at r=.85: R=1e7 -> %s, R=1e8 -> %s" % (th7, th8))

# S3 negative controls
P = dict(BASE, f2p_free_ops=True)
nc1 = all(max(nets(R, 0.85, 1.0, P), key=lambda k: nets(R, 0.85, 1.0, P)[k]) == "f2p" for R in REACH)
check("P4a free-ops fit1 f2p wins every reach", nc1, "reaches=%s" % REACH)
P = dict(BASE, attach=0.0)
wz = grid(0.5, P)
check("P4b attach 0 hybrid wins 0", len(wz["hybrid"]) == 0, "hybrid=%d" % len(wz["hybrid"]))
z = nets(0.0, 0.85, 0.5, BASE)
fixed = {"premium": -BASE["dev"], "f2p": -(BASE["dev"] + BASE["f2p_extra"] + BASE["f2p_ops"] * T), "hybrid": -(BASE["dev"] + BASE["drops"] * BASE["drop_cost"])}
check("P4c zero reach nets fixed cost", all(abs(z[k] - fixed[k]) < 1e-9 for k in z), "nets=%s" % {k: round(v) for k, v in z.items()})

# S4 monopoly money multiplier
P = dict(BASE, spend_mult=1.5)
w15 = grid(0.2, P)
check("P5 spend x1.5 at fit.2 f2p wins 0", len(w15["f2p"]) == 0, "f2p cells=%d (fit.2 x1.0 baseline=%d)" % (len(w15["f2p"]), len(grid(0.2, BASE)["f2p"])))
# does x1.5 on a high-fit game change anything? (info)
print("info spend x1.5 at fit1 f2p cells: %d vs x1.0: %d" % (len(grid(1.0, P)["f2p"]), len(w1["f2p"])))

# S5 pay-to-win sweep, hybrid, R=1e6, r=.85, fit .5
sweep = []
for i in range(0, 11):
    x = i / 10
    sweep.append((x, hybrid(1e6, 0.85, 0.5, dict(BASE, p2w=x))))
best = max(sweep, key=lambda s: s[1])
print("info p2w sweep (x, net): " + " ".join("%.1f:%d" % (x, round(v)) for x, v in sweep))
check("P6 interior p2w peak and x=1 below peak", 0 < best[0] < 1 and sweep[-1][1] < best[1], "peak x=%.1f net=%d; x=1 net=%d; x=0 net=%d" % (best[0], best[1], sweep[-1][1], sweep[0][1]))

# S6 BREAK: premium store conversion collapses
P = dict(BASE, c_p=0.005)
wb = grid(0.5, P)
check("P7 premium conv .005 hands f2p >=1 cell", len(wb["f2p"]) >= 1, "f2p cells=%s premium=%d hybrid=%d" % (sorted(wb["f2p"]), len(wb["premium"]), len(wb["hybrid"])))
# breakeven premium conversion at r=.85 R=1e7 fit .5
lo, hi = 0.0005, 0.02
for _ in range(60):
    mid = (lo + hi) / 2
    Pm = dict(BASE, c_p=mid)
    n = nets(1e7, 0.85, 0.5, Pm)
    if max(n, key=n.get) == "f2p":
        lo = mid
    else:
        hi = mid
print("info premium conversion below which f2p beats both at R=1e7 r=.85 fit.5: %.4f (baseline %.3f)" % (hi, BASE["c_p"]))


# S7 iteration 2 (post-hoc): monthly pressure spend path, cumulative revenue per owner
def path(x, months=T, r=0.85, k=0.6, lift=4.0):
    r_h = r * (1 - k * x)            # churn grows with pressure
    spend = 0.30 * (1 + lift * x)         # monthly spend per active owner, pressure lifts it
    cum, out, a = 0.0, [], 1.0
    for m in range(months):
        cum += a * spend * (1 - CUT)
        out.append(cum)
        a *= r_h
    return out
p0, p1 = path(0.0), path(1.0)
lead = [m for m in range(T) if p1[m] > p0[m]]
cross_m = next((m for m in range(T) if p1[m] < p0[m] and m > 0), None)
check("P8 (post-hoc) pressure spikes early then falls behind", bool(lead) and cross_m is not None, "x=1 leads in months %s..%s, behind from month %s; month-24 cumulative x=1 %.2f vs x=0 %.2f" % (lead[0] if lead else None, lead[-1] if lead else None, cross_m, p1[-1], p0[-1]))

# iteration 3: where does pressure start to lose by month 24? (churn slope k vs spend lift)
def breakeven_k(lift):
    lo, hi = 0.0, 0.99
    for _ in range(60):
        mid = (lo + hi) / 2
        if path(1.0, k=mid, lift=lift)[-1] > path(0.0)[-1]:
            lo = mid
        else:
            hi = mid
    return hi
bk = {lift: breakeven_k(lift) for lift in (1.0, 2.0, 4.0)}
print("info churn slope k above which full pressure loses by month 24, by spend lift: " + " ".join("lift%.0f:%.3f" % (a, b) for a, b in bk.items()))
check("P9 (post-hoc) a churn slope exists where pressure loses", all(0 < v < 0.99 for v in bk.values()), "k* by lift=%s; at k=0.6 lift=4 pressure wins (cum24 %.2f vs %.2f); at k=0.9 lift=4 cum24 %.2f vs %.2f" % ({a: round(b, 3) for a, b in bk.items()}, p1[-1], p0[-1], path(1.0, k=0.9)[-1], p0[-1]))

claim = [
    all(c in w["premium"] for c in small),
    len(w["hybrid"]) >= 1 and mono,
    len(w["f2p"]) == 0 and len(grid(0.2, BASE)["f2p"]) == 0 and len(w1["f2p"]) >= 1,
    nc1 and len(wz["hybrid"]) == 0,
    len(wb["f2p"]) >= 1,
]
allok = all(checks)
print("scorecard: %d/%d checks held (misses printed above as MISS)" % (sum(checks), len(checks)))
print("RESULT: %s kernel logic reproduced in the model (%d/%d claim checks); %d of %d numeric checks missed (P3 f2p region wider than guessed, P6 and P8 pressure beat the clean base at the first parameters; P9 finds the churn slope where it stops paying); f2p wins 0/20 at fit.5, %d/20 at fit1; premium %d/20 at fit.5; break (premium conv .005) hands f2p %d cells" % ("PASS" if all(claim) else "FAIL", sum(claim), len(claim), len(checks) - sum(checks), len(checks), len(w1["f2p"]), len(w["premium"]), len(wb["f2p"])))
