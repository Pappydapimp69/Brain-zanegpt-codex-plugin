"""Sandbox: does a keyword gate over prose need term RARITY, not overlap count?

Kernel under test: ideas:tooling/gating/keyword-match-over-prose
 claims: (1) raw overlap rewards long inputs, so raising the threshold makes the
 gate fire on BIGGER work, not more RELEVANT work; (2) weight by rarity
 (tf-idf vs the corpus) or match distinguishing nouns only.

PREDICTION (written before the first run; real data = 76 ledger headings read
from the linked cache, real unrelated text = Python stdlib source, plus the ideas
prose as a topical-confound control):
 P1 live-style raw gate (substring, floor 2, scaled bar) on UNRELATED stdlib
    code: fire rate climbs with diff size; FP(3200 words) - FP(50 words) >= 0.50.
 P2 raising a FIXED raw threshold 2 -> 4 lowers FP at 200 words but FP at 3200
    words stays >= 0.30, and planted-on-topic recall drops >= 0.30 (short
    headings cannot reach 4).
 P3 idf-mass gate (idf from held-out background) keeps recall >= 0.90 and has
    FP(3200) <= 0.10.
 P4 BREAK: idf computed over the headings alone (the literal 'corpus of open
    questions') is no better than raw: FP within 0.05 of raw at every size.
 P5 BREAK: idf calibrated on a different domain than the diff is drawn from
    does not hold the FP bound of P3 (FP(3200) > 0.10).
RUN-1 OUTCOME (recorded, not hidden): P1 ok, P2 FP(3200)>=.3 MISS (raw>=4 gave
 0.12 on code), P3 ok, P4 MISS (headings-only idf gave 0.28 vs raw 0.99 at 3200),
 P5 ok. Controls added after run 1, predicted before run 2:
 P6 a UNIFORM-weight gate needing half the heading's keywords (no rarity) has
    FP(3200) on code >= 0.30 while idf-mass at the same fraction is <= 0.10, so
    the gain is rarity and not only the fraction bar.
 P7 BREAK: a genuine edit that hits only the COMMON half of a heading's keywords
    (low-idf plant) is missed by idf-mass: recall <= 0.50 at every size, while
    the live gate keeps recall >= 0.90.
 P8 BREAK: one global idf cannot fix a topical diff: on ideas prose idf-mass
    FP(800) >= 0.20.
Added after run 2 (predicted before run 3):
 P9 FIX CANDIDATE: score per 200-word window (stride 100) and fire only if one
    WINDOW passes (co-location). On ideas prose at S=3200 whole-diff idf-mass
    FP is ~0.89; windowed idf-mass FP <= 0.50 with planted recall >= 0.90
    (the planted block is contiguous, so it fits one window).
Deterministic: no RNG, no clock; chunks are consecutive word windows.
"""
import math, os, re, sys, glob, sysconfig

HOME = os.path.expanduser("~")
LEDGER = os.path.join(HOME, ".brain/Tension/tension-ledger.md")
CLI = os.path.join(HOME, ".brain/Brain/bin/brain")
IDEAS = os.path.join(HOME, ".brain/ideas/idea-repository.md")
if not os.path.exists(IDEAS):
    IDEAS = "/home/user/ideas/idea-repository.md"

# ---- the live gate's keyword extraction, copied from its source (read only) ----
src = open(CLI, encoding="utf-8").read()
i = src.index("STOPWORDS = {"); j = src.index("}", i) + 1
ns = {}; exec(src[i:j], ns); STOP = ns["STOPWORDS"]

def subject(h):
    p = h.split(" · "); return " · ".join(p[2:]) if len(p) > 2 else h
def keywords(h):
    return {w for w in re.findall(r"[a-z][a-z-]{4,}", subject(h).lower()) if w not in STOP}

heads = [l[4:].strip() for l in open(LEDGER, encoding="utf-8") if l.startswith("### ")]
KW = {}
for h in heads:
    k = keywords(h)
    if len(k) >= 3: KW[h] = sorted(k)
TENS = sorted(KW)
ALLK = sorted({k for h in TENS for k in KW[h]})

def words_of(text): return text.lower().split()
def chunks(words, size, parity):
    out = []
    for n, s in enumerate(range(0, len(words) - size, size)):
        if n % 2 == parity: out.append(" ".join(words[s:s + size]))
    return out

# unrelated code corpus: stdlib sources, sorted, fixed cap
files = sorted(glob.glob(os.path.join(sysconfig.get_paths()["stdlib"], "*.py")))
code = []
for f in files:
    try: code += words_of(open(f, encoding="utf-8", errors="ignore").read())
    except OSError: pass
    if len(code) > 1_500_000: break
prose = words_of(open(IDEAS, encoding="utf-8").read())
SIZES = (50, 200, 800, 3200)

def df_table(texts):
    n = len(texts)
    return {k: (sum(1 for t in texts if k in t) + 1) / (n + 1) for k in ALLK}
def idf_from(df): return {k: math.log(1 / df[k]) for k in ALLK}

# ---- gates ----
def live(text, h):
    k = KW[h]; f = [x for x in k if x in text]
    return len(f) >= max(min(2, len(k)), (len(k) + 2) // 3)
def rawfix(t):
    return lambda text, h: sum(1 for x in KW[h] if x in text) >= t
def idfmass(idf, frac=0.5):
    def g(text, h):
        k = KW[h]; tot = sum(idf[x] for x in k)
        return sum(idf[x] for x in k if x in text) >= frac * tot
    return g

def uniform(frac):
    return lambda text, h: sum(1 for x in KW[h] if x in text) >= frac * len(KW[h])

def plant(text, h, idf, low=False):
    k = sorted(KW[h], key=lambda x: (idf[x] if low else -idf[x]))[: math.ceil(len(KW[h]) / 2)]
    return text + " " + " ".join(k)

def rates(gate, un, idf_for_plant, low=False):
    fp = sum(1 for c in un if any(gate(c, h) for h in TENS)) / len(un)
    pos = [(plant(c, h, idf_for_plant, low), h) for c in un[:12] for h in TENS]
    tp = sum(1 for c, h in pos if gate(c, h)) / len(pos)
    return fp, tp

def run(label, bg_cal, bg_eval, gates_fn):
    print(f"-- {label}")
    res = {}
    for S in SIZES:
        cal = chunks(bg_cal, S, 0); ev = chunks(bg_eval, S, 1)
        idf = idf_from(df_table(cal))
        for name, g in gates_fn(idf).items():
            fp, tp = rates(g, ev, idf)
            res[(name, S)] = (fp, tp)
    names = sorted({n for n, _ in res})
    for n in names:
        print(f"  {n:10s} " + "  ".join(f"S={S}: fp={res[(n,S)][0]:.2f} tp={res[(n,S)][1]:.2f}" for S in SIZES))
    return res

def gates(idf):
    return {"live": live, "raw>=2": rawfix(2), "raw>=4": rawfix(4), "idfmass.5": idfmass(idf, .5), "uniform.5": uniform(.5)}

print(f"headings used: {len(TENS)}  distinct keywords: {len(ALLK)}  code words: {len(code)}  prose words: {len(prose)}")
A = run("A in-domain: calibrate+eval on stdlib code", code, code, gates)
# B4: idf over the headings only
hdf = {k: (sum(1 for h in TENS if k in KW[h]) + 0.5) / (len(TENS) + 1) for k in ALLK}
hidf = {k: math.log(1 / hdf[k]) for k in ALLK}
print("-- B headings-only idf (the literal 'corpus of open questions')")
B = {}
for S in SIZES:
    ev = chunks(code, S, 1)
    B[S] = rates(idfmass(hidf, .5), ev, hidf)
print("  idf-heads  " + "  ".join(f"S={S}: fp={B[S][0]:.2f} tp={B[S][1]:.2f}" for S in SIZES))
C = run("C domain-mismatch: calibrate on ideas prose, eval on stdlib code", prose, code,
        lambda idf0: None) if False else None
# C: calibrate idf on prose, evaluate on code
print("-- C idf calibrated on prose, diff drawn from code")
Cres = {}
for S in SIZES:
    idfp = idf_from(df_table(chunks(prose, S, 0)))
    ev = chunks(code, S, 1)
    Cres[S] = rates(idfmass(idfp, .5), ev, idfp)
print("  idf-prose  " + "  ".join(f"S={S}: fp={Cres[S][0]:.2f} tp={Cres[S][1]:.2f}" for S in SIZES))
D = run("D topical control: calibrate+eval on ideas prose", prose, prose, gates)

# E: low-idf plant (genuine edit hitting only the common half of the keywords)
print("-- E low-idf plant on stdlib code (recall of a genuine but common-word edit)")
E = {}
for S in SIZES:
    cal = chunks(code, S, 0); ev = chunks(code, S, 1)
    idf = idf_from(df_table(cal))
    E[S] = {n: rates(g, ev, idf, low=True)[1] for n, g in (("live", live), ("idfmass.5", idfmass(idf, .5)))}
for n in ("live", "idfmass.5"):
    print(f"  {n:10s} " + "  ".join(f"S={S}: tp={E[S][n]:.2f}" for S in SIZES))

# F: windowed (co-located) scoring on topical prose at the biggest diff size
print("-- F windowed idf-mass (200-word windows, stride 100) vs whole-diff, ideas prose, S=3200")
S = 3200
cal = chunks(prose, 200, 0); idf = idf_from(df_table(cal))
ev = chunks(prose, S, 1)
base = idfmass(idf, .5)
def wgate(text, h):
    w = text.split()
    return any(base(" ".join(w[a:a + 200]), h) for a in range(0, max(1, len(w) - 100), 100))
Fw = rates(wgate, ev, idf)
Fb = rates(base, ev, idf)
print(f"  whole-diff fp={Fb[0]:.2f} tp={Fb[1]:.2f}   windowed fp={Fw[0]:.2f} tp={Fw[1]:.2f}")

# ---- checks ----
fl = {S: A[("live", S)][0] for S in SIZES}
checks = {}
checks["P1 live FP(3200)-FP(50)>=.5"] = fl[3200] - fl[50] >= 0.5
checks["P2 raw>=4 FP(200) < raw>=2 FP(200)"] = A[("raw>=4", 200)][0] < A[("raw>=2", 200)][0]
checks["P2 raw>=4 FP(3200)>=.3"] = A[("raw>=4", 3200)][0] >= 0.3
checks["P2 recall drop>=.3"] = A[("raw>=2", 200)][1] - A[("raw>=4", 200)][1] >= 0.3
checks["P3 idfmass recall>=.9"] = min(A[("idfmass.5", S)][1] for S in SIZES) >= 0.9
checks["P3 idfmass FP(3200)<=.1"] = A[("idfmass.5", 3200)][0] <= 0.1
checks["P4 heads-idf within .05 of raw"] = all(abs(B[S][0] - A[("raw>=2", S)][0]) <= 0.05 for S in SIZES)
checks["P5 mismatch FP(3200)>.1"] = Cres[3200][0] > 0.1
checks["P6 uniform.5 FP(3200)>=.3 and idfmass<=.1"] = A[("uniform.5", 3200)][0] >= 0.3 and A[("idfmass.5", 3200)][0] <= 0.1
checks["P7 idfmass low-plant recall<=.5 all sizes"] = all(E[S]["idfmass.5"] <= 0.5 for S in SIZES)
checks["P7 live low-plant recall>=.9"] = all(E[S]["live"] >= 0.9 for S in SIZES)
checks["P9 windowed FP<=.5 and tp>=.9 (prose S=3200)"] = Fw[0] <= 0.5 and Fw[1] >= 0.9
checks["P8 prose idfmass FP(800)>=.2"] = D[("idfmass.5", 800)][0] >= 0.2
for k, v in checks.items(): print(("  ok   " if v else "  MISS ") + k)
core = ["P1 live FP(3200)-FP(50)>=.5", "P2 raw>=4 FP(200) < raw>=2 FP(200)", "P2 recall drop>=.3",
        "P3 idfmass recall>=.9", "P3 idfmass FP(3200)<=.1", "P5 mismatch FP(3200)>.1",
        "P6 uniform.5 FP(3200)>=.3 and idfmass<=.1", "P7 idfmass low-plant recall<=.5 all sizes",
        "P7 live low-plant recall>=.9", "P8 prose idfmass FP(800)>=.2"]
core_ok = all(checks[c] for c in core)
missed = [k for k, v in checks.items() if not v]
print(f"RESULT: {'PASS' if core_ok else 'FAIL'} kernel core reproduced={core_ok}; live fp by size {[round(fl[S],2) for S in SIZES]}; "
      f"idfmass fp {[round(A[('idfmass.5',S)][0],2) for S in SIZES]}; low-idf-plant recall idfmass {round(E[800]['idfmass.5'],2)}; "
      f"my sub-predictions missed: {missed}")
