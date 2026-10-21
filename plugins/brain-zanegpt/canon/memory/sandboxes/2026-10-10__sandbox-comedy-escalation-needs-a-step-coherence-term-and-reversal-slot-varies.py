"""Escalation model for an escalating-absurdity comedy arc with a final reversal.

Structure-only toy. It scores the SHAPE of a beat sequence under STATED audience
assumptions (habituation, adaptation level, an inverted-U expectation term). It says
nothing about real audiences or real people; every constant below is assumed.

PREDICTIONS (written before the first run; each is checked in code at the bottom):
  P1  contrast-driven audience (mu=1, Weber ratio): geometric total / linear total
      at N=6, I1=2, C=10 is >= 1.10 (predicted about 1.3).
  P2  level-driven audience (mu=0): flat-at-ceiling beats geometric by >= 30%.
  P3  with Weber contrast, the weight mu at which linear escalation overtakes
      flat-at-ceiling lies in [0.2, 0.6].
  P4  reversal placement, N=6 slots, default constants: best slot is 3 or 4,
      NOT the last slot.
  P5  best reversal slot is non-increasing as the expectation-build rate kappa
      rises (0.10, 0.25, 0.50): the "rule of three" is a kappa artefact.
  P6  BREAK: if the audience already expects the catch (P0=0.9) the reversal
      payoff drops by >= 70% versus P0=0.
  P7  doubling the ceiling C from 10 to 20 under geometric/Weber adds between
      10% and 35% to the arc total (log returns).
  P8  per-beat efficiency of a geometric arc (endpoint C=10) over N=2..8 peaks at
      N in {2,3}, and N=3 is not strictly better than N=2.
  P9  mild beats burn out first: retention of a constant mild sequence (I=2) at beat
      6 is 0.49+-0.05, intense (I=10) is 0.72+-0.05 (implementation check).
  P10 BREAK: a fixed-ratio (1.6x) arc clipped at C=10: the marginal payoff of beat 8
      is under 10% of the marginal payoff of beat 2 (beats past the ceiling are dead).
  P11 regret: no single schedule (flat, linear, geometric) is best under all four
      audience models (so the choice depends on the assumed audience).

PART 2 (added after Part 1 ran: Part 1 missed P1, P3, P4, P7, P11 because the plain
adaptation-contrast model rewards one jump straight to the ceiling; so Part 2 adds an
assumed coherence gate exp(-(rho/rho0)^2) on the log step rho=ln(I/A) and a fixed
normalisation. These Q-predictions were written BEFORE Part 2 was first run):
  Q1  gate on (rho0=0.8, contrast-W): flat-at-ceiling total is under 20% of the
      geometric total.
  Q2  gate on: geometric / linear total lies in [1.0, 1.25].
  Q3  gate on: per-beat efficiency of a geometric arc over N=2..8 peaks at N in {3,4}.
  Q4  gate on, fixed normalisation: C 10 -> 20 adds between 5% and 40% to the geometric arc.
  Q5  gate on: best reversal slot (N=6, kappa=0.25) is 4 or 5.
  Q6  BREAK: the gate cuts both ways. rho0=0.3 (very picky) cuts the geometric arc by
      >= 40% vs rho0=0.8, and a tolerant audience (rho0=3.0) lets flat-at-ceiling
      overtake geometric; the rho0 where flat = geometric lies in [1.0, 2.0].
  Q7  gate on, across the four audience models (level, mix, contrast-W, contrast-lin):
      at least 2 distinct best schedules.
"""
import math

C0 = dict(N=6, I1=2.0, a0=1.0, C=10.0, lam=0.2, alpha=0.5, I50=5.0)


def schedule(kind, N, I1, C):
    if kind == "flat":
        return [C] * N
    if kind == "linear":
        return [I1 + (C - I1) * k / (N - 1) for k in range(N)]
    if kind == "geometric":
        return [I1 * (C / I1) ** (k / (N - 1)) for k in range(N)]
    raise ValueError(kind)


def beat_responses(seq, mu, weber=True, lam=0.2, alpha=0.5, I50=5.0, a0=1.0, C=10.0, X0=0.0,
                   rho0=None, ref=None):
    """Per-beat response. Habituation: exp(-lam*X), X grows by w(I)=1/(1+I/I50)
    (weaker stimuli accumulate more). Contrast vs an adapting level A.
    rho0 (Part 2 only): coherence gate on the log step, exp(-(rho/rho0)^2).
    ref (Part 2 only): fixed normalisation constant instead of the per-run ceiling."""
    A, X, out = a0, X0, []
    for I in seq:
        r, A, X = _one(I, mu, weber, lam, alpha, I50, a0, C, A, X, rho0, ref)
        out.append(r)
    return out, A, X


def total(seq, mu, weber=True, **kw):
    return sum(beat_responses(seq, mu, weber, **kw)[0])


def reversal_value(A, P0, n, kappa, I_rev, a0, C, B=1.0):
    """Downward contrast of a drop to the mundane level against the adapted level A,
    scaled by an inverted-U expectation term S(P)=4P(1-P) (information-gap shape).
    The reversal is a new stimulus class, so no habituation is applied."""
    P = 1 - (1 - P0) * math.exp(-kappa * n)
    S = 4 * P * (1 - P)
    d = max(0.0, math.log(max(A, 1e-9) / max(I_rev, 1e-9))) / math.log(C / a0)
    return B * S * d, P, S


def arc_with_reversal(p, N, mu, kappa, P0=0.0, I1=2.0, a0=1.0, C=10.0, lam=0.2,
                      alpha=0.5, I50=5.0, kind="geometric", weber=True, rho0=None, ref=None):
    """N slots; the reversal sits in slot p (1-indexed) and the N-1 escalation beats
    follow a schedule that resumes after it. The drop pulls A down by alpha."""
    esc = schedule(kind, N - 1, I1, C)
    A, X, tot = a0, 0.0, 0.0
    nbefore = 0
    rev = 0.0
    ei = 0
    for slot in range(1, N + 1):
        if slot == p:
            rev, _, _ = reversal_value(A, P0, nbefore, kappa, a0, a0, C if ref is None else ref)
            tot += rev
            A += alpha * (a0 - A)
        else:
            r, A, X = _one(esc[ei], mu, weber, lam, alpha, I50, a0, C, A, X, rho0, ref)
            tot += r
            ei += 1
            if slot < p:
                nbefore += 1
    return tot, rev


def _one(I, mu, weber, lam, alpha, I50, a0, C, A, X, rho0=None, ref=None):
    I = max(0.0, min(C, I))
    R = C if ref is None else ref
    if weber:
        rho = math.log(max(I, 1e-9) / A)
        c = max(0.0, rho) / math.log(R / a0)
    else:
        rho = math.log(max(I, 1e-9) / A)
        c = max(0.0, I - A) / (R - a0)
    if rho0 is not None:
        c *= math.exp(-(max(0.0, rho) / rho0) ** 2)
    h = math.exp(-lam * X)
    r = h * ((1 - mu) * (I / R) + mu * c)
    return r, A + alpha * (I - A), X + 1.0 / (1.0 + I / I50)


def best_slot(kappa, mu=1.0, P0=0.0, **kw):
    vals = {p: arc_with_reversal(p, 6, mu, kappa, P0, **kw)[0] for p in range(2, 7)}
    return max(vals, key=lambda p: (vals[p], p)), vals


results = {}
log = []


def say(s):
    print(s)


# ---------- S1 schedules x audience models ----------
models = {"level(mu=0)": (0.0, True), "mix(mu=.5,W)": (0.5, True),
          "contrast-W(mu=1)": (1.0, True), "contrast-lin(mu=1)": (1.0, False)}
N, I1, C = C0["N"], C0["I1"], C0["C"]
tab = {}
say("S1 totals, N=6 I1=2 C=10 lam=.2 alpha=.5 (rows schedule, cols audience model)")
for k in ("flat", "linear", "geometric"):
    seq = schedule(k, N, I1, C)
    row = {}
    for m, (mu, wb) in models.items():
        row[m] = total(seq, mu, wb, lam=C0["lam"], alpha=C0["alpha"], I50=C0["I50"], a0=C0["a0"], C=C)
    tab[k] = row
    say("  %-10s " % k + "  ".join("%s=%.3f" % (m, v) for m, v in row.items()))
r3 = total(schedule("geometric", 3, I1, C), 1.0, True, lam=.2, alpha=.5, I50=5, a0=1, C=C)
say("  rule-of-three geometric N=3, contrast-W: total=%.3f per-beat=%.3f" % (r3, r3 / 3))
results["P1"] = tab["geometric"]["contrast-W(mu=1)"] / tab["linear"]["contrast-W(mu=1)"]
results["P2"] = tab["flat"]["level(mu=0)"] / tab["geometric"]["level(mu=0)"]
say("  P1 geo/lin (W)=%.3f ; P2 flat/geo (level)=%.3f" % (results["P1"], results["P2"]))

# regret
best = {m: max(tab, key=lambda k: tab[k][m]) for m in models}
say("  best schedule per model: %s" % best)
results["P11"] = len(set(best.values()))


# ---------- S2 crossover mu ----------
def diff(mu):
    f = total(schedule("flat", N, I1, C), mu, True, **{k: C0[k] for k in ("lam", "alpha", "I50", "a0")}, C=C)
    l = total(schedule("linear", N, I1, C), mu, True, **{k: C0[k] for k in ("lam", "alpha", "I50", "a0")}, C=C)
    return l - f


lo, hi = 0.0, 1.0
if diff(lo) < 0 < diff(hi):
    for _ in range(50):
        mid = (lo + hi) / 2
        if diff(mid) < 0:
            lo = mid
        else:
            hi = mid
    results["P3"] = (lo + hi) / 2
else:
    results["P3"] = None
say("S2 crossover mu (linear overtakes flat, Weber) = %s" % results["P3"])

# habituation-rate sweep, geometric vs linear vs flat under mu=.5
say("S2b lam sweep (mu=.5 Weber): geo/lin and flat/geo")
for lam in (0.0, 0.1, 0.2, 0.4, 0.8):
    g = total(schedule("geometric", N, I1, C), .5, True, lam=lam, alpha=.5, I50=5, a0=1, C=C)
    l = total(schedule("linear", N, I1, C), .5, True, lam=lam, alpha=.5, I50=5, a0=1, C=C)
    f = total(schedule("flat", N, I1, C), .5, True, lam=lam, alpha=.5, I50=5, a0=1, C=C)
    say("  lam=%.1f geo/lin=%.3f flat/geo=%.3f" % (lam, g / l, f / g))

# ---------- S3 reversal placement ----------
say("S3 reversal slot totals (geometric esc, contrast-W mu=1), N=6 slots")
bs = {}
for kappa in (0.10, 0.25, 0.50):
    b, vals = best_slot(kappa)
    bs[kappa] = b
    say("  kappa=%.2f best slot=%d  " % (kappa, b) + " ".join("p%d=%.3f" % (p, v) for p, v in vals.items()))
results["P4"] = bs[0.25]
results["P5"] = bs
# reversal-only value by slot for insight
say("  reversal-only payoff by slot at kappa=.25:")
rv = []
for p in range(2, 7):
    t, rr = arc_with_reversal(p, 6, 1.0, 0.25)
    rv.append((p, rr))
say("   " + " ".join("p%d=%.3f" % x for x in rv))

# break: anticipated reversal
r0 = arc_with_reversal(6, 6, 1.0, 0.25, P0=0.0)[1]
r9 = arc_with_reversal(6, 6, 1.0, 0.25, P0=0.9)[1]
results["P6"] = 1 - r9 / r0
say("S4 BREAK anticipated catch: reversal slot6 P0=0 -> %.3f ; P0=.9 -> %.3f ; drop=%.1f%%" % (r0, r9, 100 * results["P6"]))
say("  P0 sweep at slot 6:" + " ".join("P0=%.1f:%.3f" % (p0, arc_with_reversal(6, 6, 1.0, .25, P0=p0)[1]) for p0 in (0, .3, .5, .7, .9)))

# ---------- S5 ceiling ----------
say("S5 ceiling sweep (geometric, N=6, contrast-W)")
tc = {}
for Cc in (3, 5, 10, 20, 50):
    tc[Cc] = total(schedule("geometric", 6, 2.0, Cc), 1.0, True, lam=.2, alpha=.5, I50=5, a0=1, C=Cc)
    say("  C=%-3d total=%.3f" % (Cc, tc[Cc]))
results["P7"] = tc[20] / tc[10] - 1

# ---------- S6 rule of three: per-beat efficiency vs N ----------
say("S6 per-beat efficiency vs N (geometric endpoint C=10, contrast-W)")
eff = {}
for n in range(2, 9):
    t = total(schedule("geometric", n, 2.0, 10.0), 1.0, True, lam=.2, alpha=.5, I50=5, a0=1, C=10.0)
    eff[n] = t / n
    say("  N=%d total=%.3f per-beat=%.3f" % (n, t, eff[n]))
argm = max(eff, key=eff.get)
results["P8"] = (argm, eff[3] > eff[2] + 1e-9)

# ---------- S7 mild vs intense retention ----------
def retention(I, n=6):
    r, _, _ = beat_responses([I] * n, 0.0, True, lam=.2, alpha=.5, I50=5, a0=1, C=10.0)
    return r[-1] / r[0]


results["P9"] = (retention(2.0), retention(10.0))
say("S7 retention beat6/beat1: mild(I=2)=%.3f intense(I=10)=%.3f" % results["P9"])

# ---------- S8 ceiling collision ----------
seq = [min(10.0, 2.0 * 1.6 ** k) for k in range(10)]
cum = [sum(beat_responses(seq[:n], 1.0, True, lam=.2, alpha=.5, I50=5, a0=1, C=10.0)[0]) for n in range(1, 11)]
marg = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, 10)]
say("S8 BREAK ceiling collision, fixed ratio 1.6 clipped at 10: marginal per beat = " + " ".join("%.3f" % m for m in marg))
results["P10"] = marg[7] / marg[1]


# ================= PART 2: coherence gate =================
say("PART 2 (coherence gate rho0 on the log step; fixed normalisation ref=10)")
kw2 = dict(lam=.2, alpha=.5, I50=5.0, a0=1.0, C=10.0, ref=10.0)


def t2(kind, n, rho0, mu=1.0, weber=True, I1=2.0, C=10.0):
    d = dict(kw2)
    d["C"] = C
    return total(schedule(kind, n, I1, C), mu, weber, rho0=rho0, **d)


tg = {k: t2(k, 6, 0.8) for k in ("flat", "linear", "geometric")}
say("  rho0=.8 contrast-W totals: " + " ".join("%s=%.3f" % kv for kv in tg.items()))
results["Q1"] = tg["flat"] / tg["geometric"]
results["Q2"] = tg["geometric"] / tg["linear"]
eff2 = {n: t2("geometric", n, 0.8) / n for n in range(2, 9)}
say("  per-beat efficiency by N: " + " ".join("N%d=%.3f" % kv for kv in eff2.items()))
results["Q3"] = max(eff2, key=eff2.get)
c10 = t2("geometric", 6, 0.8, C=10.0)
c20 = t2("geometric", 6, 0.8, C=20.0)
c50 = t2("geometric", 6, 0.8, C=50.0)
say("  ceiling (fixed norm): C10=%.3f C20=%.3f C50=%.3f" % (c10, c20, c50))
results["Q4"] = c20 / c10 - 1
vals2 = {p: arc_with_reversal(p, 6, 1.0, 0.25, 0.0, rho0=0.8, ref=10.0)[0] for p in range(2, 7)}
results["Q5"] = max(vals2, key=lambda p: (vals2[p], p))
say("  reversal slot totals (gate on): " + " ".join("p%d=%.3f" % kv for kv in vals2.items()))
rho_tab = {}
for r0_ in (0.3, 0.5, 0.8, 1.2, 1.6, 2.0, 3.0):
    rho_tab[r0_] = (t2("flat", 6, r0_), t2("geometric", 6, r0_), t2("linear", 6, r0_))
    say("  rho0=%.1f flat=%.3f geo=%.3f lin=%.3f" % ((r0_,) + rho_tab[r0_]))
cross = None
prev = None
rs = [x / 20 for x in range(4, 80)]
for r0_ in rs:
    d = t2("flat", 6, r0_) - t2("geometric", 6, r0_)
    if prev is not None and prev < 0 <= d:
        cross = r0_
        break
    prev = d
results["Q6"] = (1 - rho_tab[0.3][1] / rho_tab[0.8][1], rho_tab[3.0][0] > rho_tab[3.0][1], cross)
say("  rho0 where flat overtakes geometric = %s" % cross)
best2 = {}
for m, (mu, wb) in models.items():
    vv = {k: t2(k, 6, 0.8, mu=mu, weber=wb) for k in ("flat", "linear", "geometric")}
    best2[m] = max(vv, key=vv.get)
    say("  %-20s %s" % (m, " ".join("%s=%.3f" % kv for kv in vv.items())))
results["Q7"] = len(set(best2.values()))
say("  best per model: %s" % best2)


# ---- exploratory (no prediction written; reported as observed) ----
say("EXPLORATORY E1 ceiling re-optimised: best total over N=2..12 per ceiling, gate on")
e1 = {}
for Cc in (5, 10, 20, 50, 100):
    tt = {n: t2("geometric", n, 0.8, C=float(Cc)) for n in range(2, 13)}
    nb = max(tt, key=tt.get)
    step = math.log(Cc / 2.0) / (nb - 1)
    e1[Cc] = (nb, tt[nb], step)
    say("  C=%-3d bestN=%d total=%.3f log-step/beat=%.2f (ratio %.2f)" % (Cc, nb, tt[nb], step, math.exp(step)))
say("EXPLORATORY E2 is the reversal last? best slot over (gate, kappa, P0) cells")
cells = []
for gate in (None, 0.8):
    for kap in (0.10, 0.25, 0.50):
        for p0 in (0.0, 0.5):
            vv = {p: arc_with_reversal(p, 6, 1.0, kap, p0, rho0=gate, ref=10.0)[0] for p in range(2, 7)}
            bp = max(vv, key=lambda p: (vv[p], p))
            cells.append(bp)
            say("  gate=%s kappa=%.2f P0=%.1f best slot=%d" % (gate, kap, p0, bp))
say("  last slot best in %d of %d cells" % (sum(1 for c in cells if c == 6), len(cells)))
results["E2"] = (sum(1 for c in cells if c == 6), len(cells))

# ---------- checks ----------
checks = []


def chk(name, ok, detail):
    checks.append(ok)
    say("  %s %s %s" % (name, "HELD" if ok else "MISSED", detail))


say("PREDICTION CHECKS")
chk("P1", results["P1"] >= 1.10, "geo/lin=%.3f" % results["P1"])
chk("P2", results["P2"] >= 1.30, "flat/geo=%.3f" % results["P2"])
chk("P3", results["P3"] is not None and 0.2 <= results["P3"] <= 0.6, "mu*=%s" % results["P3"])
chk("P4", results["P4"] in (3, 4), "best slot=%s" % results["P4"])
bk = results["P5"]
chk("P5", bk[0.10] >= bk[0.25] >= bk[0.50], "best slots by kappa=%s" % bk)
chk("P6", results["P6"] >= 0.70, "drop=%.1f%%" % (100 * results["P6"]))
chk("P7", 0.10 <= results["P7"] <= 0.35, "C10->20 adds %.1f%%" % (100 * results["P7"]))
chk("P8", results["P8"][0] in (2, 3) and not results["P8"][1], "argmax N=%s, N3>N2=%s" % results["P8"])
chk("P9", abs(results["P9"][0] - .49) <= .05 and abs(results["P9"][1] - .72) <= .05, "ret=%.3f/%.3f" % results["P9"])
chk("P10", results["P10"] < 0.10, "m8/m2=%.3f" % results["P10"])
chk("P11", results["P11"] >= 2, "distinct best schedules=%d" % results["P11"])
chk("Q1", results["Q1"] < 0.20, "flat/geo=%.3f" % results["Q1"])
chk("Q2", 1.0 <= results["Q2"] <= 1.25, "geo/lin=%.3f" % results["Q2"])
chk("Q3", results["Q3"] in (3, 4), "argmax N=%s" % results["Q3"])
chk("Q4", 0.05 <= results["Q4"] <= 0.40, "C10->20 adds %.1f%%" % (100 * results["Q4"]))
chk("Q5", results["Q5"] in (4, 5), "best slot=%s" % results["Q5"])
q6 = results["Q6"]
chk("Q6", q6[0] >= 0.40 and q6[1] and q6[2] is not None and 1.0 <= q6[2] <= 2.0,
    "picky cut=%.1f%% tolerant flat>geo=%s crossover=%s" % (100 * q6[0], q6[1], q6[2]))
chk("Q7", results["Q7"] >= 2, "distinct best schedules=%d" % results["Q7"])
held = sum(checks)
print("RESULT: %s %d/%d predictions held; escalation shape, ceiling and reversal slot depend on assumed audience constants" % (
    "PASS" if held == len(checks) else "FAIL", held, len(checks)))
