"""Dose-response of self-directed humor: repeated game, warmth gain vs cumulative credibility cost.

STRUCTURE ONLY. This models measurement/scoring/dynamics under stated assumptions.
It says nothing about the psychology of any real person. The four-style frame
(affiliative, self-enhancing, aggressive, self-defeating) is RECALLED, not verified.

PREDICTIONS (written BEFORE the first run; any may come out wrong):
 P1 Inverted U: in every one of the 8 base cells (context x relationship x prior)
    utility vs joke rate rises then falls or is flat/falling; the interior optimum p* > 0
    in the casual cells, but p* = 0 in new/low-prior/high-stakes (no joke pays).
 P2 Ordering of the break-even rate p_flip (jokes per turn where net utility drops
    below no-humor): casual/established/high-prior >= 0.6 (or never flips);
    stakes/new/low-prior <= 0.05.
 P3 Pitch/stakes p_flip for a NEW relationship with prior P(competent)=0.7 is below 0.25.
 P4 Turning the "pratfall coupling" off (warmth no longer scales with perceived competence)
    raises p_flip in stakes/new/low-prior by at least 0.10 (or removes the flip).
 P5 Severity beats frequency: in the casual/new/high-prior cell, switching the sender's
    flaw severity from the competent-type mix to the insecure-type mix lowers p_flip by
    at least 0.3 (or p_flip falls from never/high to <= 0.4).
 P6 Context decomposition: of the casual -> stakes shift in p_flip for new/high-prior,
    the payoff weight and acceptance threshold (lambda, BATNA bar) account for more than
    the changed base-rate expectation r.
 P7 Break scenario: with receiver treating jokes as uninformative (r_C = r_I, P_C = P_I),
    p_flip is None in every cell (no threshold exists), so the "flip" is entirely a
    receiver-inference effect, not a property of joking.
"""
import math

T_DEFAULT = 24
GRID = [i / 40 for i in range(41)]  # joke rate 0.000 .. 1.000
SEV_C = (0.70, 0.25, 0.05)  # mild / moderate / severe flaw, secure-competent type
SEV_I = (0.25, 0.35, 0.40)  # insecure / low-competence type
E_TASK = 0.10               # nats per turn of task evidence favouring the competent type
W0, KAPPA, GAMMA = 1.0, 0.35, 0.7   # warmth per joke, satiation strength, memory decay

CONTEXT = {
    "casual": dict(rC=0.20, rI=0.35, lam=2.0, bar=0.0),
    "stakes": dict(rC=0.05, rI=0.15, lam=15.0, bar=1.0),
}
PRIOR = {"high": 0.85, "low": 0.40}
REL = {"new": dict(scale=1.0, disc=1.0), "established": dict(scale=2.0, disc=0.5)}


def logit(p):
    return math.log(p / (1 - p))


def sig(x):
    return 1 / (1 + math.exp(-x))


def joke_llr(rC, rI, sev_sender):
    """Expected log-likelihood ratio (competent vs insecure) of one joke, receiver model
    P_C/P_I for severity, sender drawing severity from sev_sender (mean-field)."""
    return sum(s * math.log(pc * rC / (pi * rI)) for s, pc, pi in zip(sev_sender, SEV_C, SEV_I))


def run(p, ctx, rel, prior, T=T_DEFAULT, coupling=True, sev_sender=SEV_C, informative=True,
        bar=None, lam=None, r=None, e=E_TASK):
    c = dict(CONTEXT[ctx])
    if bar is not None: c["bar"] = bar
    if lam is not None: c["lam"] = lam
    if r is not None: c["rC"], c["rI"] = r
    rC, rI = c["rC"], c["rI"]
    R = REL[rel]
    L = R["scale"] * logit(PRIOR[prior])
    if informative:
        a = joke_llr(rC, rI, sev_sender)               # per joke
        b = math.log((1 - rC) / (1 - rI))              # per silent turn
    else:
        a = b = 0.0
    h, warm, jokes = 0.0, 0.0, 0
    for t in range(T):
        joke = int((t + 1) * p + 1e-9) > int(t * p + 1e-9)  # deterministic even schedule
        dL = e + R["disc"] * (a if joke else b)
        if joke:
            jokes += 1
            q = sig(L)
            warm += W0 * (q if coupling else 1.0) * math.exp(-KAPPA * h)
        h = GAMMA * h + (1 if joke else 0)
        L += dL
    V = sig((L - c["bar"]) / 0.8)
    return warm + c["lam"] * V, warm, sig(L), jokes


def curve(**kw):
    return [(p,) + run(p, **kw) for p in GRID]


def summarize(cv):
    u0 = cv[0][1]
    best = max(cv, key=lambda x: x[1])
    pstar = best[0] if best[1] > u0 + 1e-9 else 0.0
    pflip = None
    for row in cv[1:]:
        if row[0] > pstar and row[1] < u0 - 1e-9:
            pflip = row[0]
            break
    # an interior optimum means the sequence rises then falls; also flag monotone falling
    return pstar, pflip, u0, best[1]


def cell(ctx, rel, prior, **kw):
    return summarize(curve(ctx=ctx, rel=rel, prior=prior, **kw))


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


def fmt(x):
    return "never" if x is None else f"{x:.3f}"


print("== Base grid: p* = best joke rate (jokes/turn), p_flip = rate where net utility < no humor ==")
base = {}
for ctx in CONTEXT:
    for rel in REL:
        for prior in PRIOR:
            ps, pf, u0, ub = cell(ctx, rel, prior)
            base[(ctx, rel, prior)] = (ps, pf)
            print(f"{ctx:6s} {rel:11s} prior={prior:4s}  p*={ps:.3f}  p_flip={fmt(pf):>6s}  U(0)={u0:6.2f}  U(p*)={ub:6.2f}")

# P1
inter_ok = all(base[(c, r, p)][0] > 0 for c in ["casual"] for r in REL for p in PRIOR)
zero_ok = base[("stakes", "new", "low")][0] == 0.0
check("P1 interior optimum in casual cells and none in stakes/new/low", inter_ok and zero_ok,
      f"casual p*>0 all={inter_ok}; stakes/new/low p*={base[('stakes','new','low')][0]}")
# P2
hi = base[("casual", "established", "high")][1]
lo = base[("stakes", "new", "low")][1]
ok2 = (hi is None or hi >= 0.6) and (lo is not None and lo <= 0.05)
check("P2 ordering of p_flip (casual-established-high >=0.6 or never; stakes-new-low <=0.05)", ok2,
      f"casual/est/high={fmt(hi)}; stakes/new/low={fmt(lo)}")
# P3 prior 0.7 new relationship, stakes
PRIOR["mid"] = 0.70
ps3, pf3, _, _ = cell("stakes", "new", "mid")
check("P3 stakes/new/prior0.7 p_flip < 0.25", pf3 is not None and pf3 < 0.25,
      f"p*={ps3:.3f} p_flip={fmt(pf3)}")
# P4 pratfall coupling off
ps4, pf4, _, _ = cell("stakes", "new", "low", coupling=False)
pf_on = base[("stakes", "new", "low")][1]
ok4 = (pf4 is None) or (pf_on is not None and pf4 - pf_on >= 0.10)
check("P4 coupling off raises stakes/new/low p_flip by >=0.10 or removes it", ok4,
      f"coupled p_flip={fmt(pf_on)}; uncoupled p_flip={fmt(pf4)}")
# P5 severity
_, pf_c, _, _ = cell("casual", "new", "high")
_, pf_i, _, _ = cell("casual", "new", "high", sev_sender=SEV_I)
ok5 = pf_i is not None and (pf_c is None or pf_c - pf_i >= 0.3 or pf_i <= 0.4)
check("P5 severity: insecure-mix severity drops casual/new/high p_flip by >=0.3 or to <=0.4", ok5,
      f"competent-mix p_flip={fmt(pf_c)}; insecure-mix p_flip={fmt(pf_i)}")
# P6 decomposition: swap only r vs only (lam, bar) between casual and stakes, new/high
def flipv(**kw):
    v = cell(kw.pop("ctx"), "new", "high", **kw)[1]
    return 1.0 if v is None else v
f_cas = flipv(ctx="casual")
f_str = flipv(ctx="stakes")
f_r_only = flipv(ctx="casual", r=(CONTEXT["stakes"]["rC"], CONTEXT["stakes"]["rI"]))
f_stake_only = flipv(ctx="casual", lam=CONTEXT["stakes"]["lam"], bar=CONTEXT["stakes"]["bar"])
d_r = f_cas - f_r_only
d_s = f_cas - f_stake_only
check("P6 payoff weight + acceptance bar shift p_flip more than the base-rate expectation", d_s > d_r,
      f"casual={f_cas:.3f} stakes={f_str:.3f}; r-only shift={d_r:.3f}; lam+bar-only shift={d_s:.3f} (never coded as 1.0)")
# P7 break scenario
nof = [cell(c, r, p, informative=False)[1] for c in CONTEXT for r in REL for p in PRIOR]
check("P7 BREAK: uninformative receiver => no flip in any cell", all(x is None for x in nof),
      f"flips found={sum(x is not None for x in nof)} of {len(nof)}")

print("== Extra context (not predicted): horizon, BATNA bar, concrete evidence, established-discount ==")
for T in (8, 24, 60):
    ps, pf, _, _ = cell("stakes", "new", "mid", T=T)
    print(f"horizon T={T:2d} stakes/new/prior0.7  p*={ps:.3f} p_flip={fmt(pf)}  (jokes in a full-length run at p_flip ~ {0 if pf is None else round(pf*T,1)})")
for bar in (0.0, 1.0, 2.0):
    ps, pf, _, _ = cell("stakes", "new", "mid", bar=bar)
    print(f"BATNA bar={bar:.1f} (receiver alternative strength) stakes/new/prior0.7 p*={ps:.3f} p_flip={fmt(pf)}")
for e in (0.02, 0.10, 0.30):
    ps, pf, _, _ = cell("stakes", "new", "mid", e=e)
    print(f"task evidence/turn e={e:.2f} (vague -> concrete) stakes/new/prior0.7 p*={ps:.3f} p_flip={fmt(pf)}")
for d in (0.25, 0.5, 1.0):
    REL["established"]["disc"] = d
    ps, pf, _, _ = cell("stakes", "established", "mid")
    print(f"established joke-evidence discount={d:.2f} stakes/est/prior0.7 p*={ps:.3f} p_flip={fmt(pf)}")
REL["established"]["disc"] = 0.5

print("== POST-HOC (added after the first run; NOT counted in RESULT) ==")
print("P6 above is censored (casual never flips, coded 1.0, so both shifts are 0). Re-measure on p*, which is never censored:")
ps_cas = cell("casual", "new", "high")[0]
ps_str = cell("stakes", "new", "high")[0]
ps_r = cell("casual", "new", "high", r=(CONTEXT["stakes"]["rC"], CONTEXT["stakes"]["rI"]))[0]
ps_s = cell("casual", "new", "high", lam=CONTEXT["stakes"]["lam"], bar=CONTEXT["stakes"]["bar"])[0]
print(f"p* casual={ps_cas:.3f} stakes={ps_str:.3f}; swap only base-rate expectation -> {ps_r:.3f} (shift {ps_cas-ps_r:.3f}); swap only payoff weight+bar -> {ps_s:.3f} (shift {ps_cas-ps_s:.3f})")
print("Exchange rate lambda/W0 (value of credibility in warmth units) at which a flip first appears, new relationship, prior 0.85, casual expectations:")
for lam in (2, 4, 6, 8, 10, 15, 30):
    ps, pf, _, _ = cell("casual", "new", "high", lam=lam)
    print(f"  lambda={lam:2d}  p*={ps:.3f}  p_flip={fmt(pf)}")
print("Does an established relationship insulate? new vs established, coupling on/off, stakes:")
for prior in ("high", "mid", "low"):
    for cp in (True, False):
        rowv = []
        for rel in ("new", "established"):
            ps, pf, _, _ = cell("stakes", rel, prior, coupling=cp)
            rowv.append(f"{rel}: p*={ps:.3f} flip={fmt(pf)}")
        print(f"  prior={prior:4s} coupling={'on ' if cp else 'off'}  " + " | ".join(rowv))
print("Severity at fixed rate p=0.3, stakes/new/prior0.7: end-state P(competent) by sender flaw mix")
for nm, sv in (("competent mix", SEV_C), ("insecure mix", SEV_I), ("all severe", (0.0, 0.0, 1.0)), ("all mild", (1.0, 0.0, 0.0))):
    u, w, q, n = run(0.3, "stakes", "new", "mid", sev_sender=sv)
    print(f"  {nm:14s} jokes={n} warmth={w:.2f} P(C)_end={q:.3f} U={u:.2f}")
u, w, q, n = run(0.0, "stakes", "new", "mid")
print(f"  no humor        jokes=0 warmth=0.00 P(C)_end={q:.3f} U={u:.2f}")

print("2x2 factorial on the context switch (new relationship, prior 0.85): base-rate expectation r  x  payoff (lambda, BATNA bar)")
for rn, rv in (("casual r", (0.20, 0.35)), ("stakes r", (0.05, 0.15))):
    for pn, (lm, br) in (("casual payoff", (2.0, 0.0)), ("stakes payoff", (15.0, 1.0))):
        ps, pf, _, _ = cell("casual", "new", "high", r=rv, lam=lm, bar=br)
        print(f"  {rn:9s} + {pn:13s}  p*={ps:.3f}  p_flip={fmt(pf)}")
print("Severity-contrast sensitivity: insecure type's severe-flaw mix blended toward the competent mix (m=1 is the base case); casual/new/high and stakes/new/mid")
_full = SEV_I
for m in (0.0, 0.25, 0.5, 0.75, 1.0):
    SEV_I = tuple((1 - m) * a + m * b for a, b in zip(SEV_C, _full))
    pc = cell("casual", "new", "high", sev_sender=_full)[1]
    ps_ = cell("stakes", "new", "mid", sev_sender=_full)[1]
    print(f"  m={m:.2f}  (sender uses the insecure mix, receiver model blended)  casual p_flip={fmt(pc)}  stakes p_flip={fmt(ps_)}")
SEV_I = _full

nfail = sum(1 for c in checks if not c)
print(f"RESULT: {'PASS' if nfail == 0 else 'FAIL'} {len(checks) - nfail}/{len(checks)} predictions held; "
      f"p_flip stakes/new/low={fmt(base[('stakes','new','low')][1])}, casual/est/high={fmt(base[('casual','established','high')][1])}")
