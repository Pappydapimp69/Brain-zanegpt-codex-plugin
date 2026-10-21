"""Opening a short pitch with a joke: does the change-first ordering rule survive a humor term?

STRUCTURE ONLY. Every constant is an assumption. This models scoring and dynamics of a toy
listener, never psychology of real people. The four-style humor frame is RECALLED, not verified.
Joke kinds here: self-directed (mild-mix and heavy-mix flaws) and an affiliative joke about the
shared situation, plus an affiliative joke carried inside the change beat itself.

Join under test: ideas PITCH/narrative-structure/lead-with-the-change (order rule: change beat
first, product later) and PITCH/technical-talks/motivation-and-one-idea (cut the orienting
opener) against ideas HUMOR-STYLES/dose/self-directed-joke-dose (a joke is a dose: warmth that
saturates, a credibility cost set by flaw severity and by the listener's expectation) and the
earlier dose sandbox (same flaw-severity evidence term, reused below).

PREDICTIONS (written BEFORE the first run; any may come out wrong). Cells = context
(casual, stakes) x prior belief (0.40, 0.85). Orders: CF change-first, AG agenda-first,
PF product-first. Pitch is 10 slots; a joke takes a slot and pushes out the last beat.
 P1 No joke: utility ordering CF > AG > PF in all 4 cells.
 P2 Uptake-only currency (acceptance probability V, warmth excluded): CF > PF under every one
    of 6 joke conditions in every cell (24/24). The humor term never flips the order there.
 P3 Combined currency (warmth + payoff weight * V): a joke added to the WRONG order (PF) beats
    CF with no joke in the 2 casual cells and in 0 stakes cells. i.e. the rule breaks where
    warmth is priced high relative to being believed.
 P4 In the 2 stakes cells the CF-PF gap in V with an opening self-directed joke stays within
    25 percent of the no-joke gap (order effect is roughly additive with the humor term).
 P5 For CF, an opening self-directed joke LOWERS combined utility in stakes/prior 0.40 and
    RAISES it in both casual cells.
 P6 Placement: for CF with a self-directed joke, a mid-pitch joke (slot 4) gives more absorbed
    content than an opening joke in 4/4 cells (an opening joke is an unframed beat before the
    change beat).
 P7 Attention flips the sign of the opening joke: at initial attention 0.35 the opening joke
    raises absorbed content of CF; at 0.95 it lowers it.
 P8 BREAK scenario: exhaustive grid (initial attention x prior x attention boost x change
    strength x tight horizon x 6 joke conditions x 3 positions), uptake-only: zero cases where
    PF with a joke beats CF with no joke.
"""
import math
from itertools import product

# --- flaw-severity evidence reused from the earlier dose model (assumed constants) ---
SEV_C = (0.70, 0.25, 0.05)
SEV_I = (0.25, 0.35, 0.40)
W0, KAPPA, GAMMA = 1.0, 0.35, 0.7
CONTEXT = {"casual": dict(rC=0.20, rI=0.35, lam=2.0, bar=0.0),
           "stakes": dict(rC=0.05, rI=0.15, lam=15.0, bar=1.0)}
AFF_DISC = 0.5            # affiliative joke is half as diagnostic of insecurity (assumed)
# --- pitch dynamics (assumed) ---
H = 10
D_UNF, D_FR = 0.14, 0.05  # attention lost per beat without / with a motivating frame
F_GAIN = 1.2              # frame strength per unit absorbed change beat
E_BASE, E_PROOF = 0.08, 0.9
KV, VREF = 0.35, 8.0      # weight and fixed reference of absorbed value in the uptake logit
J_ATT = 0.35              # fraction of the attention gap a joke refills
BLUR = 0.85               # carried joke blurs the change beat's frame
WARM_W = 1.0

# beat: (name, value v, frame dependence phi)
B = {"CHANGE": (2.0, 0.0), "BREAK": (1.0, 0.6), "OUTCOME": (1.0, 0.6), "PRODUCT": (2.0, 1.0),
     "FEAT1": (1.0, 1.0), "FEAT2": (1.0, 1.0), "PROOF": (2.0, 0.5), "OBJ": (1.0, 0.6),
     "ASK": (1.5, 1.0), "DETAIL": (0.5, 0.5), "AGENDA": (0.3, 0.0)}
CORE = ["CHANGE", "BREAK", "OUTCOME", "PRODUCT", "FEAT1", "FEAT2", "PROOF", "OBJ", "ASK"]


def order(name, tight):
    if name == "CF":
        seq = CORE[:]
    elif name == "PF":
        seq = ["PRODUCT", "FEAT1", "FEAT2", "PROOF", "CHANGE", "BREAK", "OUTCOME", "OBJ", "ASK"]
    else:  # AG: orienting opener first, then the change-first order
        seq = ["AGENDA"] + CORE
    if tight:   # ASK stays last and the spare beat is absent: a joke now displaces content
        seq = [s for s in seq if s != "ASK"][:H - 1] + ["ASK"]
    elif name != "AG":
        seq = seq + ["DETAIL"]
    return seq[:H]


def sig(x):
    return 1 / (1 + math.exp(-x))


def logit(p):
    return math.log(p / (1 - p))


def joke_llr(kind, ctx):
    rC, rI = CONTEXT[ctx]["rC"], CONTEXT[ctx]["rI"]
    if kind in ("aff", "carried"):
        return AFF_DISC * math.log(rC / rI)
    sev = SEV_C if kind == "self" else SEV_I
    return sum(s * math.log(pc * rC / (pi * rI)) for s, pc, pi in zip(sev, SEV_C, SEV_I))


def run(ord_name, kind=None, pos=None, ctx="stakes", prior=0.85, a0=0.85, jatt=J_ATT,
        fg=F_GAIN, tight=False, lam=None):
    """kind in {None,'self','heavy','aff','carried'}; pos 'open' | 'mid' | None."""
    c = CONTEXT[ctx]
    lam = c["lam"] if lam is None else lam
    seq = order(ord_name, tight)
    items = [(b, False) for b in seq]
    if kind in ("self", "heavy", "aff") and pos:
        idx = 0 if pos == "open" else 4
        items = (items[:idx] + [("JOKE", True)] + items[idx:])[:H]   # last beat is pushed out
    a, f, L, warm, h, vtot = a0, 0.0, logit(prior), 0.0, 0.0, 0.0
    ahist, bhist, whist = [], [], []

    def dose(a, L, warm, h, llr, atten=1.0):
        q = sig(L)
        warm += W0 * q * math.exp(-KAPPA * h)
        L += llr
        a = a + jatt * atten * (1 - a)
        return a, L, warm, h * GAMMA + 1.0
    for name, is_joke in items:
        d = D_UNF - (D_UNF - D_FR) * f
        if is_joke:
            a *= (1 - d)
            a, L, warm, h = dose(a, L, warm, h, joke_llr(kind, ctx))
        else:
            v, phi = B[name]
            ab = a * (0.5 + 0.5 * sig(L))
            vtot += v * (1 - phi + phi * f) * ab
            L += E_BASE * ab + (E_PROOF * ab if name == "PROOF" else 0.0)
            if name == "CHANGE":
                f = min(1.0, fg * ab)
                if kind == "carried":
                    f *= BLUR
            d = D_UNF - (D_UNF - D_FR) * f
            a *= (1 - d)
            h *= GAMMA
            if name == "CHANGE" and kind == "carried":
                a, L, warm, h = dose(a, L, warm, h, joke_llr(kind, ctx), 0.5)
        ahist.append(a); bhist.append(sig(L)); whist.append(warm)
    V = sig((L - c["bar"] + KV * (vtot - VREF)) / 0.8)
    return dict(U=WARM_W * warm + lam * V, V=V, warm=warm, vtot=vtot, belief=sig(L), att=a,
                ahist=ahist, bhist=bhist, whist=whist)


JOKES = [(None, None), ("self", "open"), ("self", "mid"), ("heavy", "open"), ("aff", "open"),
         ("carried", None)]
CELLS = [(cx, pr) for cx in ("casual", "stakes") for pr in (0.40, 0.85)]
checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


print("== Trajectory, CF vs PF, no joke vs opening self joke (stakes, prior 0.85): att/belief/warmth per slot ==")
for o in ("CF", "PF"):
    for k, p in ((None, None), ("self", "open")):
        r = run(o, k, p)
        print(f"  {o} {k or 'none':5s} att " + " ".join(f"{x:.2f}" for x in r["ahist"]) +
              f" | belief {r['belief']:.3f} warm {r['warm']:.3f} absorbed {r['vtot']:.2f} V {r['V']:.3f} U {r['U']:.3f}")

print("\n== P1 no-joke ordering ==")
ok = True
for cx, pr in CELLS:
    u = {o: run(o, ctx=cx, prior=pr)["U"] for o in ("CF", "AG", "PF")}
    good = u["CF"] > u["AG"] > u["PF"]
    ok &= good
    print(f"  {cx}/{pr}: CF {u['CF']:.3f} AG {u['AG']:.3f} PF {u['PF']:.3f}")
check("P1 CF>AG>PF without jokes in 4 cells", ok, "see lines above")

print("\n== P2 uptake-only (V) CF>PF under each joke condition ==")
n = tot = 0
bad = []
for cx, pr in CELLS:
    for k, p in JOKES:
        tot += 1
        vc, vp = run("CF", k, p, cx, pr)["V"], run("PF", k, p, cx, pr)["V"]
        if vc > vp:
            n += 1
        else:
            bad.append((cx, pr, k, p, round(vc, 3), round(vp, 3)))
check("P2 V ordering survives all joke conditions", n == tot == 24, f"{n}/{tot} hold; violations {bad[:3]}")

print("\n== P3 combined U: PF + joke vs CF + no joke ==")
casual_beats = stakes_beats = 0
for cx, pr in CELLS:
    base = run("CF", ctx=cx, prior=pr)["U"]
    best = max(((run("PF", k, p, cx, pr)["U"], k, p) for k, p in JOKES if k), key=lambda t: t[0])
    beat = best[0] > base
    print(f"  {cx}/{pr}: CF none {base:.3f}; best PF+joke {best[0]:.3f} ({best[1]},{best[2]}) -> {'PF wins' if beat else 'CF holds'}")
    if beat:
        if cx == "casual": casual_beats += 1
        else: stakes_beats += 1
check("P3 rule breaks in casual (2 cells) not stakes (0)", casual_beats == 2 and stakes_beats == 0,
      f"casual breaks {casual_beats}/2, stakes breaks {stakes_beats}/2")

print("\n== P4 stakes: CF-PF gap in V with opening self joke vs no joke ==")
ok = True
for pr in (0.40, 0.85):
    g0 = run("CF", ctx="stakes", prior=pr)["V"] - run("PF", ctx="stakes", prior=pr)["V"]
    g1 = run("CF", "self", "open", "stakes", pr)["V"] - run("PF", "self", "open", "stakes", pr)["V"]
    rel = abs(g1 - g0) / abs(g0)
    ok &= rel <= 0.25
    print(f"  prior {pr}: gap none {g0:.4f}, gap with open joke {g1:.4f}, change {rel*100:.1f}%")
check("P4 gap preserved within 25% in stakes", ok, "see lines above")

print("\n== P5 CF opening self joke vs none, combined U ==")
d = {}
for cx, pr in CELLS:
    d[(cx, pr)] = run("CF", "self", "open", cx, pr)["U"] - run("CF", ctx=cx, prior=pr)["U"]
    print(f"  {cx}/{pr}: delta U {d[(cx, pr)]:+.3f}")
ok5 = d[("stakes", 0.40)] < 0 and d[("casual", 0.40)] > 0 and d[("casual", 0.85)] > 0
check("P5 lowers in stakes/0.40, raises in both casual", ok5, f"deltas {[round(v, 3) for v in d.values()]}")

print("\n== P6 placement: absorbed content, mid vs open (CF, self joke) ==")
w = 0
for cx, pr in CELLS:
    vo, vm = run("CF", "self", "open", cx, pr)["vtot"], run("CF", "self", "mid", cx, pr)["vtot"]
    w += vm > vo
    print(f"  {cx}/{pr}: open {vo:.3f} mid {vm:.3f}")
check("P6 mid beats open in 4/4", w == 4, f"{w}/4")

print("\n== P7 attention flips the opening joke sign (CF absorbed content, stakes/0.85) ==")
dl = {}
for a0 in (0.35, 0.55, 0.75, 0.85, 0.95):
    dl[a0] = run("CF", "self", "open", a0=a0)["vtot"] - run("CF", a0=a0)["vtot"]
    print(f"  a0 {a0:.2f}: absorbed change {dl[a0]:+.3f}")
check("P7 raises at 0.35 and lowers at 0.95", dl[0.35] > 0 > dl[0.95], f"{dl[0.35]:+.3f} / {dl[0.95]:+.3f}")

print("\n== P8 BREAK: exhaustive grid, uptake-only, any PF+joke beating CF none ==")
cnt = tot8 = 0
first = None
by = {}
for a0, pr, ja, fg, tight, (k, p), cx in product((0.35, 0.55, 0.85, 0.95), (0.40, 0.85), (0.2, 0.35, 0.6, 0.9),
                                              (1.2, 0.6, 0.3), (False, True),
                                              [j for j in JOKES if j[0] and j[1]], ("casual", "stakes")):
    base = run("CF", ctx=cx, prior=pr, a0=a0, jatt=ja, fg=fg, tight=tight)["V"]
    alt = run("PF", k, p, cx, pr, a0, ja, fg, tight)["V"]
    tot8 += 1
    if alt > base:
        cnt += 1
        by[(fg, k, p)] = by.get((fg, k, p), 0) + 1
        if first is None:
            first = (a0, pr, ja, fg, tight, k, p, cx, round(alt, 3), round(base, 3))
print(f"  violations {cnt}/{tot8}; by (change strength, kind, pos): {sorted(by.items())[:6]}")
print(f"  first: {first}")
check("P8 no PF+joke beats CF none in V over the grid", cnt == 0, f"{cnt}/{tot8} violations")

print("\n== Join-break bookkeeping: exchange rate where warmth outweighs the order gap (stakes cells use lam sweep) ==")
for pr in (0.40, 0.85):
    # smallest payoff weight lam at which CF none >= best PF+joke in combined U (bisect on lam grid)
    star = None
    for lam in [x / 2 for x in range(1, 121)]:
        base = run("CF", ctx="stakes", prior=pr, lam=lam)["U"]
        best = max(run("PF", k, p, "stakes", pr, lam=lam)["U"] for k, p in JOKES if k)
        if base >= best:
            star = lam
            break
    print(f"  stakes prior {pr}: rule holds in combined currency from payoff weight lam >= {star} (warmth weight {WARM_W})")
for pr in (0.40, 0.85):
    star = None
    for lam in [x / 2 for x in range(1, 121)]:
        base = run("CF", ctx="casual", prior=pr, lam=lam)["U"]
        best = max(run("PF", k, p, "casual", pr, lam=lam)["U"] for k, p in JOKES if k)
        if base >= best:
            star = lam
            break
    print(f"  casual prior {pr}: rule holds in combined currency from lam >= {star}")

print("\n== POST-HOC (not counted in RESULT; written after seeing P4 and P8 fail) ==")
rows = {}
for a0, pr, ja, fg, tight, (k, p), cx in product((0.35, 0.55, 0.85, 0.95), (0.40, 0.85), (0.2, 0.35, 0.6, 0.9),
                                              (1.2, 0.6, 0.3), (False, True),
                                              [j for j in JOKES if j[0] and j[1]], ("casual", "stakes")):
    base = run("CF", ctx=cx, prior=pr, a0=a0, jatt=ja, fg=fg, tight=tight)["V"]
    alt = run("PF", k, p, cx, pr, a0, ja, fg, tight)["V"]
    for key in (("fg", fg), ("a0", a0), ("jatt", ja), ("ctx", cx), ("prior", pr), ("tight", tight)):
        t = rows.setdefault(key, [0, 0])
        t[1] += 1
        t[0] += alt > base
for key in sorted(rows, key=str):
    print(f"  violations when {key[0]}={key[1]}: {rows[key][0]}/{rows[key][1]}")
# threshold change strength fg*: smallest fg at which CF none beats PF + best joke in V, stakes prior 0.85, a0 0.85
for cx, pr in CELLS:
    star = None
    for fg10 in range(1, 25):
        fg = fg10 / 10
        base = run("CF", ctx=cx, prior=pr, fg=fg)["V"]
        best = max(run("PF", k, p, cx, pr, fg=fg)["V"] for k, p in JOKES if k and p)
        if base > best:
            star = fg
            break
    print(f"  {cx}/{pr}: CF none beats PF + best joke in V from change strength fg >= {star}")
# monotonicity of the lam threshold in the combined currency
for cx, pr in CELLS:
    flags = []
    for lam in [x / 2 for x in range(1, 121)]:
        base = run("CF", ctx=cx, prior=pr, lam=lam)["U"]
        best = max(run("PF", k, p, cx, pr, lam=lam)["U"] for k, p in JOKES if k)
        flags.append(base >= best)
    first = flags.index(True)
    print(f"  {cx}/{pr}: lam grid, rule holds at every lam after first hold: {all(flags[first:])}")
# the joke that costs least: carried vs open aff at CF stakes/0.4
for k, p in JOKES:
    r = run("CF", k, p, "stakes", 0.40)
    print(f"  CF stakes/0.4 {k or 'none'}/{p}: warm {r['warm']:.2f} V {r['V']:.3f} U {r['U']:.3f}")
# where do violations sit: attentive audience and modest refill vs cold audience or strong refill
zone = {"attentive+modest (a0>=0.85, jatt<=0.35)": [0, 0, 0.0], "cold or strong (a0<=0.55 or jatt>=0.6)": [0, 0, 0.0]}
for a0, pr, ja, fg, tight, (k, p), cx in product((0.35, 0.55, 0.85, 0.95), (0.40, 0.85), (0.2, 0.35, 0.6, 0.9),
                                              (1.2, 0.6, 0.3), (False, True),
                                              [j for j in JOKES if j[0] and j[1]], ("casual", "stakes")):
    zk = None
    if a0 >= 0.85 and ja <= 0.35: zk = "attentive+modest (a0>=0.85, jatt<=0.35)"
    elif a0 <= 0.55 or ja >= 0.6: zk = "cold or strong (a0<=0.55 or jatt>=0.6)"
    if zk is None: continue
    base = run("CF", ctx=cx, prior=pr, a0=a0, jatt=ja, fg=fg, tight=tight)["V"]
    alt = run("PF", k, p, cx, pr, a0, ja, fg, tight)["V"]
    zone[zk][1] += 1
    if alt > base:
        zone[zk][0] += 1
        zone[zk][2] = max(zone[zk][2], alt - base)
for zk, (c_, t_, m_) in zone.items():
    print(f"  {zk}: violations {c_}/{t_}, largest V margin {m_:.3f}")

npass = sum(checks)
print(f"RESULT: {'PASS' if npass == len(checks) else 'FAIL'} {npass}/{len(checks)} predictions held")
