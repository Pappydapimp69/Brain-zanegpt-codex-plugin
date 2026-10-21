"""Humor styles under localization: a structural toy model (NOT psychology of real people).

A joke is a payload needing a set of shared items. Content items (sound pairs S,
references R, observed situations E) when missing make the joke BLANK (harmless).
Norm items (power/closeness P, modesty M) when missing make a PARSEABLE joke be read
under the other audience's norms, which can turn a benign joke injurious.
Audience B holds each of A's items with probability overlap**alpha_type.
All numbers are stated assumptions, not measurements. Standard library, seeded.

PRE-REGISTERED PREDICTIONS (written before the first run; mixed-case hand estimates):
 P1  Model H, overlap 0.5, survival: observation 0.70-0.80, selfdep 0.45-0.55,
     tease 0.28-0.38, reference 0.21-0.29, wordplay 0.04-0.09.
 P2  mean(observation,selfdep) > mean(wordplay,reference) at every overlap 0.1..0.9.
 P3  at overlap 0.5, forcing every mechanism to ONE item of its main type, the
     per-type universality exponent alone explains 0.40-0.50 of the log-gap between
     observation and wordplay (the rest is the item COUNT).
 P4  BREAK: an observation that needs 3 locale-bound items (alpha 1.0) falls below a
     2-item reference (alpha 1.0) at every overlap but stays above standard wordplay.
 P5  tease injurious share (of jokes benign in A) at overlap 0.5 in 0.05-0.12; at
     0.9 <= 0.03; wordplay and reference injury exactly 0.
 P6  break-even injury cost c* (landing minus c*injury drops under wordplay's landing)
     at overlap 0.5: tease in 2-5, selfdep in 6-14, observation never.
 P7  register: the audience share expecting tu above which tu has less harm than
     usted for a teasing joke lies in 0.65-0.80.
 P8  that crossover is the same for self-deprecation (within 0.01) while the harm
     level of tu at share 0.5 is 0.25-0.35 of teasing's.
 P9  capping intensity at 0.25 makes tu harm exactly 0 at every audience share for
     teasing; a cap of 0.35 does not.
 P10 transcreating content items (0.8 per item) lifts wordplay at overlap 0.1 from
     below 0.01 to 0.60-0.68.
 P11 timing: a spoken punchline of 11 English syllables always fits the Spanish
     window; 14 syllables fits with probability 0.35-0.50.
 P12 styles at overlap 0.5 under the stated mixes: self-defeating lands >= affiliative,
     BUT that flips when the primary mechanism weight is 0.4; aggressive lands lowest
     and has the highest injury in all three weightings (0.4, 0.6, 0.8).
"""
import math, random

SEED = 20261010
N = 6000
OVERLAPS = [round(0.1 * k, 1) for k in range(1, 10)]
H_ALPHA = {"S": 2.0, "R": 1.0, "P": 0.6, "M": 0.6, "E": 0.4}   # smaller = more universal
CONTENT = {"S", "R", "E"}
NORM = {"P", "M"}
MECH = {
    "wordplay": {"S": 2},
    "reference": {"R": 2},
    "tease": {"P": 2, "E": 1},
    "selfdep": {"M": 1, "E": 1},
    "observation": {"E": 1},
}
TA = 0.5          # intensity above which a joke is hurtful in audience A
SHIFT_SD = 0.2    # norm shift per missing norm item
checks = []


def check(name, ok, detail):
    checks.append((name, bool(ok)))
    print(f"  [{'ok ' if ok else 'MISS'}] {name}: {detail}")


def analytic_land(spec, o, alpha=H_ALPHA):
    return math.prod((o ** alpha[t]) ** k for t, k in spec.items())


def sim(spec, o, alpha=H_ALPHA, imax=TA, n=N, seed=SEED, content_p=None):
    """Return dict land/blank/flat/inj rates. content_p overrides per-item content presence."""
    rng = random.Random(seed)
    c = {"land": 0, "blank": 0, "flat": 0, "inj": 0}
    for _ in range(n):
        i = rng.uniform(0.05, imax)
        blank = False
        missing_norm = 0
        for t, k in spec.items():
            for _ in range(k):
                p = (content_p if (content_p is not None and t in CONTENT) else o ** alpha[t])
                if rng.random() >= p:
                    if t in CONTENT:
                        blank = True
                    else:
                        missing_norm += 1
        if blank:
            c["blank"] += 1
        elif missing_norm == 0:
            c["land"] += 1
        else:
            shift = sum(rng.gauss(0, SHIFT_SD) for _ in range(missing_norm))
            c["inj" if i > TA + shift else "flat"] += 1
    return {k: v / n for k, v in c.items()}


print("== Part 1: survival (landing rate) per mechanism, Model H ==")
tab = {m: {o: sim(s, o) for o in OVERLAPS} for m, s in MECH.items()}
print("overlap " + " ".join(f"{m:>11}" for m in MECH))
for o in OVERLAPS:
    print(f"{o:7.1f} " + " ".join(f"{tab[m][o]['land']:11.3f}" for m in MECH))
worst = max(abs(tab[m][o]["land"] - analytic_land(s, o)) for m, s in MECH.items() for o in OVERLAPS)
print(f"  max |MC - analytic product| = {worst:.4f}")
rng_ok = {"observation": (0.70, 0.80), "selfdep": (0.45, 0.55), "tease": (0.28, 0.38),
          "reference": (0.21, 0.29), "wordplay": (0.04, 0.09)}
bad = {m: round(tab[m][0.5]["land"], 3) for m, (lo, hi) in rng_ok.items() if not lo <= tab[m][0.5]["land"] <= hi}
check("P1", not bad, f"o=0.5 land " + ", ".join(f"{m} {tab[m][0.5]['land']:.3f}" for m in rng_ok) + (f" OUT {bad}" if bad else ""))
gaps = [(tab["observation"][o]["land"] + tab["selfdep"][o]["land"]) / 2 - (tab["wordplay"][o]["land"] + tab["reference"][o]["land"]) / 2 for o in OVERLAPS]
check("P2", all(g > 0 for g in gaps), f"class gap min {min(gaps):.3f} max {max(gaps):.3f}")

print("== Part 1b: decomposition of the observation-vs-wordplay gap at overlap 0.5 ==")
lg = lambda spec, a=H_ALPHA: sum(k * a[t] * math.log(0.5) for t, k in spec.items())
total = lg(MECH["observation"]) - lg(MECH["wordplay"])
alpha_only = lg({"E": 1}) - lg({"S": 1})
share_alpha = alpha_only / total
print(f"  log gap total {total:.3f}; exponent-only {alpha_only:.3f}; share {share_alpha:.2f}")
check("P3", 0.40 <= share_alpha <= 0.50, f"exponent share {share_alpha:.2f} (item-count share {1 - share_alpha:.2f})")
uniform = {t: 1.0 for t in H_ALPHA}
u = {m: analytic_land(s, 0.5, uniform) for m, s in MECH.items()}
print("  uniform exponent (all 1.0) at 0.5: " + ", ".join(f"{m} {v:.3f}" for m, v in u.items()))

print("== Part 1c: BREAK scenario, locale-bound observation ==")
LOCAL_OBS = {"E": 3}
loc_alpha = dict(H_ALPHA, E=1.0)
below_ref, above_wp = [], []
for o in OVERLAPS:
    lo = analytic_land(LOCAL_OBS, o, loc_alpha)
    below_ref.append(lo < analytic_land({"R": 2}, o, loc_alpha))
    above_wp.append(lo > analytic_land({"S": 2}, o, loc_alpha))
glob_ref = analytic_land({"R": 1}, 0.5, dict(H_ALPHA, R=0.4))
print(f"  o=0.5: local obs {analytic_land(LOCAL_OBS, 0.5, loc_alpha):.3f}, std ref(2 items) {analytic_land({'R': 2}, 0.5):.3f}, "
      f"wordplay {analytic_land({'S': 2}, 0.5):.3f}, global 1-item reference {glob_ref:.3f}")
check("P4", all(below_ref) and all(above_wp), f"below reference at all o: {all(below_ref)}; above wordplay at all o: {all(above_wp)}; "
      f"label ordering reversed vs a global reference at 0.5: {analytic_land(LOCAL_OBS, 0.5, loc_alpha) < glob_ref}")

print("== Part 2: parse vs misread; injury and the cost ratio ==")
print("overlap  tease_inj selfdep_inj wordplay_inj reference_inj obs_inj")
for o in OVERLAPS:
    print(f"{o:7.1f} " + " ".join(f"{tab[m][o]['inj']:11.3f}" for m in ("tease", "selfdep", "wordplay", "reference", "observation")))
i5, i9 = tab["tease"][0.5]["inj"], tab["tease"][0.9]["inj"]
zero = all(tab[m][o]["inj"] == 0 for m in ("wordplay", "reference", "observation") for o in OVERLAPS)
check("P5", 0.05 <= i5 <= 0.12 and i9 <= 0.03 and zero, f"tease inj 0.5={i5:.3f} 0.9={i9:.3f}; content-only mechanisms zero injury: {zero}")


def cstar(m, o=0.5):
    inj = tab[m][o]["inj"]
    return float("inf") if inj == 0 else (tab[m][o]["land"] - tab["wordplay"][o]["land"]) / inj


cs = {m: cstar(m) for m in ("tease", "selfdep", "observation")}
print("  break-even cost ratio vs wordplay at 0.5: " + ", ".join(f"{m} {v:.2f}" for m, v in cs.items()))
check("P6", 2 <= cs["tease"] <= 5 and 6 <= cs["selfdep"] <= 14 and cs["observation"] == float("inf"),
      f"c* tease {cs['tease']:.2f}, selfdep {cs['selfdep']:.2f}, observation {cs['observation']}")

print("== Part 3: Spanish register (tu / usted / neutral) as a norm shift ==")
# shift added to felt intensity by register mismatch for a segment, then scaled by how
# register-dependent the mechanism is (rdep). Stated assumptions, derived from the
# direction of the open ledger tension only (usted can distance, tu can condescend).
SHIFT = {("tu", "usted_seg"): 0.25, ("usted", "tu_seg"): 0.10,
         ("neutral", "tu_seg"): 0.05, ("neutral", "usted_seg"): 0.05,
         ("tu", "tu_seg"): 0.0, ("usted", "usted_seg"): 0.0}
LANDMULT = {("usted", "tu_seg"): 0.7, ("neutral", "tu_seg"): 0.8, ("neutral", "usted_seg"): 0.8}
RDEP = {"tease": 1.0, "selfdep": 0.3, "observation": 0.0, "wordplay": 0.0, "reference": 0.0}
GRID = [0.05 + 0.005 * k for k in range(91)]   # intensities benign in A (<= 0.5)


def harm(strategy, f_tu, rdep, cap=TA):
    tot = 0.0
    for seg, w in (("tu_seg", f_tu), ("usted_seg", 1 - f_tu)):
        s = SHIFT[(strategy, seg)] * rdep
        pts = [i for i in GRID if i <= cap + 1e-9]
        tot += w * sum(1 for i in pts if i + s > TA + 1e-9) / len(pts)
    return tot


def crossover(rdep, cap=TA):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if harm("tu", mid, rdep, cap) > harm("usted", mid, rdep, cap):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


print("  f_tu  harm_tu harm_usted harm_neutral  (teasing)")
for f in (0.2, 0.4, 0.5, 0.6, 0.8, 0.9):
    print(f"  {f:.1f}  {harm('tu', f, 1):8.3f} {harm('usted', f, 1):10.3f} {harm('neutral', f, 1):12.3f}")
fs_t, fs_s = crossover(1.0), crossover(0.3)
print(f"  crossover share (tease) {fs_t:.3f}; (selfdep) {fs_s:.3f}")
check("P7", 0.65 <= fs_t <= 0.80, f"tease crossover {fs_t:.3f}")
ratio = harm("tu", 0.5, 0.3) / harm("tu", 0.5, 1.0)
check("P8", abs(fs_t - fs_s) <= 0.01 and 0.25 <= ratio <= 0.35, f"selfdep crossover {fs_s:.3f}; tu harm ratio selfdep/tease {ratio:.3f}")
obs_spread = max(abs(harm("tu", f, 0) - harm("usted", f, 0)) for f in (0.0, 0.5, 1.0))
print(f"  observation: register changes harm by {obs_spread:.3f} (payload is register-independent)")
cap25 = [harm("tu", f / 10, 1.0, cap=0.25) for f in range(11)]
cap35 = [harm("tu", f / 10, 1.0, cap=0.35) for f in range(11)]
check("P9", all(x == 0 for x in cap25) and max(cap35) > 0, f"cap 0.25 max harm {max(cap25):.3f}; cap 0.35 max harm {max(cap35):.3f}")
# net value with cost ratio 3 at 50/50 audience
for strat in ("tu", "usted", "neutral"):
    f = 0.5
    gain = sum(w * LANDMULT.get((strat, seg), 1.0) for seg, w in (("tu_seg", f), ("usted_seg", 1 - f)))
    print(f"  teasing net (gain - 3*harm) at share 0.5, {strat}: {gain - 3 * harm(strat, f, 1):.3f}")

print("== Part 4: repair moves (transcreate content, re-aim norms, bilingual, timing) ==")
TAU = 0.8
wp_lit = tab["wordplay"][0.1]["land"]
wp_tr = sim(MECH["wordplay"], 0.1, content_p=TAU)["land"]
print(f"  wordplay at 0.1: literal {wp_lit:.4f} -> transcreated {wp_tr:.3f}")
check("P10", wp_lit < 0.01 and 0.60 <= wp_tr <= 0.68, f"literal {wp_lit:.4f}, transcreated {wp_tr:.3f}")
tease_lit = sim(MECH["tease"], 0.3)
tease_tr = sim(MECH["tease"], 0.3, content_p=TAU)
tease_re = sim(MECH["tease"], 0.3, imax=0.25, content_p=TAU)
print(f"  tease at 0.3 land/inj: literal {tease_lit['land']:.3f}/{tease_lit['inj']:.3f}; "
      f"transcreated content {tease_tr['land']:.3f}/{tease_tr['inj']:.3f}; plus intensity cap 0.25 {tease_re['land']:.3f}/{tease_re['inj']:.3f}")
bi = analytic_land(MECH["wordplay"], 0.5 + 0.5 * 0.5)
print(f"  bilingual segment (overlap 0.5 -> 0.75) wordplay {bi:.3f} vs monolingual {analytic_land(MECH['wordplay'], 0.5):.3f}")
A, B, C = 0.90, 1.88, 1.87   # ratio range and mode (mean 1.55) as a stand-in triangular law
CAP_SYL = 2.8 * 7.7           # window x human Spanish rate, from the recalled hook figures


def fit(n):
    x = CAP_SYL / n
    if x >= B:
        return 1.0
    if x <= A:
        return 0.0
    return (x - A) ** 2 / ((B - A) * (C - A)) if x <= C else 1 - (B - x) ** 2 / ((B - A) * (B - C))


print("  punchline fit in Spanish window by English syllables: " + ", ".join(f"{n}:{fit(n):.2f}" for n in (8, 11, 12, 14, 17)))
check("P11", fit(11) == 1.0 and 0.35 <= fit(14) <= 0.50, f"fit(11)={fit(11):.2f} fit(14)={fit(14):.2f}")

print("== Part 5: HSQ four-style frame as mixtures of mechanisms (stand-in weights) ==")
PRIMARY = {"affiliative": "observation", "self-enhancing": "observation", "aggressive": "tease", "self-defeating": "selfdep"}


def style_stats(style, wprim, o=0.5):
    others = [m for m in MECH if m != PRIMARY[style]]
    w = {m: (1 - wprim) / len(others) for m in others}
    w[PRIMARY[style]] = wprim
    return (sum(w[m] * tab[m][o]["land"] for m in MECH), sum(w[m] * tab[m][o]["inj"] for m in MECH))


res = {}
for wp in (0.4, 0.6, 0.8):
    res[wp] = {s: style_stats(s, wp) for s in PRIMARY}
    print(f"  primary weight {wp}: " + "; ".join(f"{s} land {v[0]:.3f} inj {v[1]:.3f}" for s, v in res[wp].items()))
ok12 = (res[0.6]["self-defeating"][0] >= res[0.6]["affiliative"][0] and res[0.4]["self-defeating"][0] < res[0.4]["affiliative"][0]
        and all(min(res[w], key=lambda s: res[w][s][0]) == "aggressive" and max(res[w], key=lambda s: res[w][s][1]) == "aggressive" for w in res))
check("P12", ok12, "self-defeating>=affiliative at 0.6: " f"{res[0.6]['self-defeating'][0] >= res[0.6]['affiliative'][0]}, flips at 0.4: "
      f"{res[0.4]['self-defeating'][0] < res[0.4]['affiliative'][0]}, aggressive lowest land / highest inj at all weights")

held = sum(ok for _, ok in checks)
print(f"predictions held: {held}/{len(checks)}; missed: {[n for n, ok in checks if not ok]}")
print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} pre-registered predictions held; "
      f"wordplay 0.06 vs observation 0.76 at overlap 0.5; tease injury {i5:.2f}; tu/usted crossover at {fs_t:.2f} tu-expecting share")
