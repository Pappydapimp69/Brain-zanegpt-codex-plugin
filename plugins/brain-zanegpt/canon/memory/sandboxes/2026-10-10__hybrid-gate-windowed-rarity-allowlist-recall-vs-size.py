"""Sandbox: can a HYBRID keyword gate (windowed co-location + rarity weighting +
per-tension allowlist or weakest-keyword floor) keep recall >= 0.9 on common-word
edits AND false fires <= 0.1 at 3200 words?  (Is the recall/precision tradeoff
of tension 'Should a relevance gate over prose trade recall of common-word
edits for precision on large diffs?' avoidable?)

Builds on 2026-10-10__rarity-weighted-gate-vs-raw-overlap-size-sweep.py
(memory entry sandbox-keyword-gate-rarity/E1; kernel
ideas:tooling/gating/keyword-match-over-prose). Same real headings (ledger,
read-only), same live-gate keyword extraction copied from the CLI source.

PREDICTION (written BEFORE the first run; any miss is reported, not hidden).
Corpora: stdlib source ('code'), the Python language-reference prose
('docs', unrelated prose) and the ideas repository prose ('ideas', topical
confound). Each corpus split in halves: first half calibrates idf, second half
supplies diffs. Windowed gates calibrate idf at the WINDOW scale.
 P1 REPLICATE: whole-diff idf-mass (half the heading's idf mass) on code has
    FP(3200) <= 0.10 and common-word-block recall <= 0.50.
 P2 WEAKEST-KEYWORD FLOOR (bar = idf mass of the heading's common half, W=200):
    common-block recall >= 0.90 (by construction) but FP(3200) > 0.10 on at
    least one of {docs, ideas}, and FP(3200) on ideas >= 0.80.
 P3 NARROWING WINDOWS: for the idf-half bar, narrowing W from 200 to 50 drops
    ideas FP(3200) to <= 0.10 but ALSO drops common-block recall below 0.90
    (the plant needs half the mass inside one window; common words cannot).
 P4 ORACLE ALLOWLIST (2 terms taken from the edit's own common half, pair must
    co-occur in one window), W=50, idf bar OR allowlist: common-block recall
    >= 0.90 and code FP(3200) <= 0.10, but ideas FP(3200) >= 0.20.
 P5 CURATOR-BLIND ALLOWLIST (2 terms rarest in the ledger, chosen without
    knowing how the edit is worded) added to the idf bar at W=50: common-block
    recall <= 0.60.
 P6 BREAK (dispersed edit): the same common keywords spread across the 3200-word
    diff instead of one block: every windowed gate with W <= 100 has recall
    <= 0.20; the whole-diff live gate keeps >= 0.90 (at FP >= 0.90 on code).
 P7 HEADLINE: count configs (W in 200/100/50/20 x bar in idf-half/floor x
    allowlist in none/curator/oracle) with block recall >= 0.90 AND FP(3200) <=
    0.10: >= 1 on code, >= 1 on docs, 0 on ideas; and with dispersed recall
    >= 0.90 as well: 0 on every corpus.
RUN-1 OUTCOME (recorded, not hidden; 4 window widths, 6 gates): P1 ok, P2 ok except
 ideas floor FP(3200)=0.74 (< 0.80), P3 ok on recall but ideas idf-W50 FP(3200)=0.20
 (> 0.10), P4 oracle code FP(3200)=0.24 (> 0.10), P5 MISS on docs (0.66 > 0.60), P6 ok,
 P7 MISS: feasible configs were code 2 / docs 0 / ideas 0 (floor bar at W=20 on code only).
 Added after run 1, predicted before run 2 (more realistic edits + one more lever):
 'floor2' = floor bar AND >= 2 distinct heading keywords in the window; W=10 added;
 plants 'common-spread4' / 'common-spread10' = the common keywords one every 4 / 10
 words (a sentence, not a contiguous block); counts of distinct tensions fired per
 diff.
 P8 floor2 at W=50: ideas FP(3200) in (0.10, 0.30] and code FP(3200) <= 0.05.
 P9 floor at W=20: spread4 recall <= 0.60 while floor at W=50 keeps spread4 recall
    >= 0.90 (narrowing the window to buy precision costs recall on sentence-shaped
    edits), on all three corpora.
 P10 floor at W=50 on ideas fires >= 0.5 distinct tensions per unplanted 3200-word diff.
 P11 floor2 at W=10 on ideas: FP(3200) <= 0.10 with block recall >= 0.90 but spread4
    recall <= 0.30 (precision reached only by requiring a contiguous block).
 P12 headline restated: no config is feasible (FP(3200) <= 0.10, recall >= 0.90 on
    block AND spread4) on ideas prose; the tradeoff is relocated to window width
    and edit shape, not removed.
Planted edits are synthetic and the recall of windowed gates is attributed to
the edit's own windows only (conservative); whole-diff baselines include
fires caused by the unplanted text (as the earlier sandbox did).
Deterministic: no RNG, no clock; chunks are consecutive word windows.
"""
import math, os, re, sys, glob, sysconfig

HOME = os.path.expanduser("~")
LEDGER = os.path.join(HOME, ".brain/Tension/tension-ledger.md")
CLI = os.path.join(HOME, ".brain/Brain/bin/brain")
IDEAS = os.path.join(HOME, ".brain/ideas/idea-repository.md")
if not os.path.exists(IDEAS):
    IDEAS = "/home/user/ideas/idea-repository.md"

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
KS = {h: frozenset(KW[h]) for h in TENS}
ALLK = sorted({k for h in TENS for k in KW[h]})
LEDGER_DF = {k: sum(1 for h in TENS if k in KS[h]) for k in ALLK}

def words_of(text): return text.lower().split()

files = sorted(glob.glob(os.path.join(sysconfig.get_paths()["stdlib"], "*.py")))
code = []
for f in files:
    try: code += words_of(open(f, encoding="utf-8", errors="ignore").read())
    except OSError: pass
    if len(code) > 1_500_000: break
topics = os.path.join(sysconfig.get_paths()["stdlib"], "pydoc_data", "topics.py")
docs = words_of(open(topics, encoding="utf-8", errors="ignore").read()) if os.path.exists(topics) else []
ideas = words_of(open(IDEAS, encoding="utf-8").read())

SIZES = (50, 200, 800, 3200)
WINS = (200, 100, 50, 20, 10)
GATES = [("idf", None), ("floor", None), ("floor2", None), ("idf", "cur"), ("idf", "orc"), ("floor", "cur"), ("floor", "orc"), ("floor2", "cur"), ("floor2", "orc")]
def gname(g): return g[0] + ("" if g[1] is None else "+" + g[1])

def present(text, ks=ALLK): return frozenset(k for k in ks if k in text)
def idf_at(cal, size):
    chunks = [" ".join(cal[s:s + size]) for s in range(0, len(cal) - size, size)]
    n = len(chunks)
    cnt = {k: 0 for k in ALLK}
    for c in chunks:
        for k in present(c): cnt[k] += 1
    return {k: math.log(1 / ((cnt[k] + 1) / (n + 1))) for k in ALLK}

class Corpus:
    def __init__(self, name, words):
        self.name = name
        m = len(words) // 2
        self.cal, self.ev = words[:m], words[m:]
        self.ref = idf_at(self.cal, 200)       # reference scale: defines which words are 'common' for plants
        self.idfW = {W: idf_at(self.cal, W) for W in WINS}
        self.idfS = {S: idf_at(self.cal, S) for S in SIZES}
        self.wcache = {}
        # thresholds per window scale, per gate bar
        self.thr = {}
        for W in WINS:
            idf = self.idfW[W]
            for h in TENS:
                ks = sorted(KW[h], key=lambda x: idf[x])
                tot = sum(idf[x] for x in ks)
                cm = sum(idf[x] for x in ks[:math.ceil(len(ks) / 2)])
                self.thr[(W, "idf", h)] = 0.5 * tot
                self.thr[(W, "floor", h)] = min(0.5 * tot, cm)
                self.thr[(W, "floor2", h)] = min(0.5 * tot, cm)
        self.common = {}; self.rare = {}; self.cur = {}; self.orc = {}
        for h in TENS:
            ks = sorted(KW[h], key=lambda x: (self.ref[x], x))
            half = math.ceil(len(ks) / 2)
            self.common[h] = ks[:half]
            self.rare[h] = ks[-half:]
            led = lambda x: (LEDGER_DF[x], -len(x), x)
            self.cur[h] = frozenset(sorted(KW[h], key=led)[:2])
            self.orc[h] = frozenset(sorted(self.common[h], key=led)[:2])

    def pres(self, start, size):
        key = (start, size)
        v = self.wcache.get(key)
        if v is None:
            v = present(" ".join(self.ev[start:start + size]))
            self.wcache[key] = v
        return v

def fires(C, W, inter, h, g):
    if not inter: return False
    bar, allow = g
    if allow is not None:
        a = (C.cur if allow == "cur" else C.orc)[h]
        if a <= inter: return True
    if bar == "floor2" and len(inter) < 2: return False
    idf = C.idfW[W]
    return sum(idf[k] for k in inter) >= C.thr[(W, bar, h)]

def window_starts(c, S, W):
    sz = min(W, S)
    stride = max(1, sz // 2)
    st = list(range(c, c + S - sz + 1, stride))
    if st[-1] != c + S - sz: st.append(c + S - sz)
    return sz, st

def chunk_starts(C, S):
    return list(range(0, len(C.ev) - S, max(50, S // 2)))

def plant_edits(C, c, S, h, kind):
    ks = {"common-block": C.common[h], "rare-block": C.rare[h], "common-scatter": C.common[h],
          "common-spread4": C.common[h], "common-spread10": C.common[h]}[kind]
    ed = {}
    if kind.startswith("common-spread"):
        gap = int(kind[len("common-spread"):])
        p0 = c + S // 2 - gap * len(ks) // 2
        for n, k in enumerate(ks): ed[p0 + n * gap] = k
    elif kind.endswith("block"):
        p0 = c + S // 2 - len(ks) // 2
        for n, k in enumerate(ks): ed[p0 + n] = k
    else:
        m = len(ks)
        for n, k in enumerate(ks): ed[c + (n + 1) * S // (m + 1)] = k
    return ed

def windowed_fire_edit(C, W, c, S, h, ed):
    """attributed to the edit: only windows that contain an edited word"""
    sz, st = window_starts(c, S, W)
    res = [False] * len(GATES)
    for s in st:
        idx = [p for p in ed if s <= p < s + sz]
        if not idx: continue
        ws = list(C.ev[s:s + sz])
        for p in idx: ws[p - s] = ed[p]
        txt = " ".join(ws)
        inter = frozenset(k for k in KW[h] if k in txt)
        for gi, g in enumerate(GATES):
            if not res[gi] and fires(C, W, inter, h, g): res[gi] = True
    return res

def evaluate(C):
    out = {}
    # ---- false fires on the unplanted text, by window scale and diff size
    for W in WINS:
        # per-window "any tension fires" vector, cached by start/size
        anyf = {}
        def win_any(s, sz):
            v = anyf.get((s, sz))
            if v is None:
                pr = C.pres(s, sz)
                v = [set() for _ in GATES]
                for h in TENS:
                    inter = pr & KS[h]
                    if not inter: continue
                    for gi, g in enumerate(GATES):
                        if fires(C, W, inter, h, g): v[gi].add(h)
                anyf[(s, sz)] = v
            return v
        for S in SIZES:
            cs = chunk_starts(C, S)
            hit = [0] * len(GATES); cnt = [0] * len(GATES)
            for c in cs:
                sz, st = window_starts(c, S, W)
                fl = [set() for _ in GATES]
                for s in st:
                    v = win_any(s, sz)
                    for gi in range(len(GATES)): fl[gi] |= v[gi]
                for gi in range(len(GATES)):
                    if fl[gi]: hit[gi] += 1
                    cnt[gi] += len(fl[gi])
            for gi, g in enumerate(GATES):
                out[("fp", W, S, gi)] = hit[gi] / len(cs)
                out[("cnt", W, S, gi)] = cnt[gi] / len(cs)
            out[("n", S)] = len(cs)
        # ---- recall of planted edits, attributed to the edit's own windows
        for S in SIZES:
            cs = chunk_starts(C, S)
            pick = cs[::max(1, len(cs) // 12)][:12]
            for kind in ("common-block", "common-spread4", "common-spread10", "common-scatter", "rare-block"):
                tp = [0] * len(GATES); tot = 0
                for c in pick:
                    for h in TENS:
                        r = windowed_fire_edit(C, W, c, S, h, plant_edits(C, c, S, h, kind))
                        tot += 1
                        for gi in range(len(GATES)):
                            if r[gi]: tp[gi] += 1
                for gi in range(len(GATES)): out[("tp", W, S, kind, gi)] = tp[gi] / tot
    # ---- whole-diff baselines (idf calibrated at the diff's own size; recall includes base fires)
    for S in SIZES:
        cs = chunk_starts(C, S)
        idf = C.idfS[S]
        base = {c: present(" ".join(C.ev[c:c + S])) for c in cs}
        def live(inter, h):
            k = KW[h]; return len(inter) >= max(min(2, len(k)), (len(k) + 2) // 3)
        def idfm(inter, h):
            return sum(idf[x] for x in inter) >= 0.5 * sum(idf[x] for x in KW[h])
        for nm, gf in (("live", live), ("wd-idf", idfm)):
            out[("wfp", nm, S)] = sum(1 for c in cs if any(gf(base[c] & KS[h], h) for h in TENS)) / len(cs)
            pick = cs[::max(1, len(cs) // 12)][:12]
            for kind in ("common-block", "common-scatter"):
                ok = tot = 0
                for c in pick:
                    for h in TENS:
                        ks = C.common[h]
                        ok += gf((base[c] & KS[h]) | frozenset(ks), h); tot += 1
                out[("wtp", nm, S, kind)] = ok / tot
    return out

CORP = {}
for nm, w in (("code", code), ("docs", docs), ("ideas", ideas)):
    CORP[nm] = Corpus(nm, w)
    print(f"corpus {nm}: {len(w)} words, eval chunks at 3200: {len(chunk_starts(CORP[nm], 3200))}", flush=True)
print(f"headings used: {len(TENS)}  distinct keywords: {len(ALLK)}")
R = {nm: evaluate(C) for nm, C in CORP.items()}


KINDS = ("common-block", "common-spread4", "common-spread10", "common-scatter", "rare-block")
for nm in CORP:
    print(f"== {nm}: whole-diff baselines (recall incl. base fires)")
    for g in ("live", "wd-idf"):
        print("  " + f"{g:7s} " + "  ".join(f"S={S}: fp={R[nm][('wfp',g,S)]:.2f} block={R[nm][('wtp',g,S,'common-block')]:.2f}" for S in SIZES))
for nm in CORP:
    for W in WINS:
        print(f"== {nm}  W={W}: fp by size 50/200/800/3200 | block recall @3200 | spread4 | spread10 | dispersed | rare-block | tensions fired per diff @3200")
        for gi, g in enumerate(GATES):
            print(f"  {gname(g):12s} fp " + " ".join(f"{R[nm][('fp',W,S,gi)]:.2f}" for S in SIZES)
                  + " | " + " | ".join(f"{R[nm][('tp',W,3200,k,gi)]:.2f}" for k in KINDS)
                  + f" | {R[nm][('cnt',W,3200,gi)]:.2f}")

def feasible(nm, kinds):
    out = []
    for W in WINS:
        for gi, g in enumerate(GATES):
            r = R[nm]
            ok = r[("fp", W, 3200, gi)] <= 0.10 and min(r[("tp", W, S, "common-block", gi)] for S in SIZES) >= 0.90
            for k in kinds: ok = ok and r[("tp", W, 3200, k, gi)] >= 0.90
            if ok: out.append((W, gname(g), round(r[("fp", W, 3200, gi)], 2)))
    return out
LEVELS = {"L1 block": (), "L2 block+spread4": ("common-spread4",), "L3 block+spread4+dispersed": ("common-spread4", "common-scatter")}
FEAS = {lv: {nm: feasible(nm, ks) for nm in CORP} for lv, ks in LEVELS.items()}
for lv in LEVELS:
    print(f"== feasible configs (fp(3200)<=.1 and recall>=.9 at 3200; block recall>=.9 at every size): {lv}")
    for nm in CORP: print(f"  {nm}: {len(FEAS[lv][nm])} {FEAS[lv][nm]}")
both = sorted(set(x[:2] for x in FEAS["L1 block"]["code"]) & set(x[:2] for x in FEAS["L1 block"]["docs"]) & set(x[:2] for x in FEAS["L1 block"]["ideas"]))
print("== L1-feasible on all three corpora at once:", both)
# best achievable ideas trade-off: lowest fp(3200) among configs with block recall >= .9, and highest block recall among fp<=.1
best_fp = min((R["ideas"][("fp", W, 3200, gi)], W, gname(g)) for W in WINS for gi, g in enumerate(GATES)
              if min(R["ideas"][("tp", W, S, "common-block", gi)] for S in SIZES) >= 0.9)
best_tp = max((R["ideas"][("tp", W, 3200, "common-block", gi)], W, gname(g)) for W in WINS for gi, g in enumerate(GATES)
              if R["ideas"][("fp", W, 3200, gi)] <= 0.10)
print(f"== ideas frontier: lowest fp(3200) with block recall>=.9 = {best_fp}; highest block recall with fp(3200)<=.1 = {best_tp}")

gi_of = {gname(g): gi for gi, g in enumerate(GATES)}
r = R
checks = {}
checks["P1 wd-idf code fp3200<=.1"] = r["code"][("wfp", "wd-idf", 3200)] <= 0.10
checks["P1 wd-idf code block recall<=.5 @3200"] = r["code"][("wtp", "wd-idf", 3200, "common-block")] <= 0.50
fl = gi_of["floor"]
checks["P2 floor W200 block recall>=.9 all corpora"] = all(r[n][("tp", 200, 3200, "common-block", fl)] >= 0.9 for n in CORP)
checks["P2 floor W200 fp3200>.1 on docs or ideas"] = max(r["docs"][("fp", 200, 3200, fl)], r["ideas"][("fp", 200, 3200, fl)]) > 0.10
checks["P2 floor W200 ideas fp3200>=.8 [run1 MISS: .74]"] = r["ideas"][("fp", 200, 3200, fl)] >= 0.80
ig = gi_of["idf"]
checks["P3 idf W50 ideas fp3200<=.1 [run1 MISS: .20]"] = r["ideas"][("fp", 50, 3200, ig)] <= 0.10
checks["P3 idf W50 block recall<.9"] = r["ideas"][("tp", 50, 3200, "common-block", ig)] < 0.90
og = gi_of["idf+orc"]
checks["P4 oracle W50 block recall>=.9"] = all(r[n][("tp", 50, 3200, "common-block", og)] >= 0.9 for n in CORP)
checks["P4 oracle W50 code fp3200<=.1 [run1 MISS: .24]"] = r["code"][("fp", 50, 3200, og)] <= 0.10
checks["P4 oracle W50 ideas fp3200>=.2"] = r["ideas"][("fp", 50, 3200, og)] >= 0.20
cg = gi_of["idf+cur"]
checks["P5 curator-blind W50 block recall<=.6 [run1 MISS on docs .66]"] = all(r[n][("tp", 50, 3200, "common-block", cg)] <= 0.60 for n in CORP)
checks["P6 windowed W<=100 dispersed recall<=.2 (all gates)"] = all(
    r[n][("tp", W, 3200, "common-scatter", gi)] <= 0.20 for n in CORP for W in (100, 50, 20, 10) for gi in range(len(GATES)))
checks["P6 whole-diff live dispersed recall>=.9, code fp>=.9"] = (
    r["code"][("wtp", "live", 3200, "common-scatter")] >= 0.9 and r["code"][("wfp", "live", 3200)] >= 0.9)
checks["P7 L1 feasible code>=1, docs>=1, ideas==0 [run1 MISS: docs 0]"] = (
    len(FEAS["L1 block"]["code"]) >= 1 and len(FEAS["L1 block"]["docs"]) >= 1 and len(FEAS["L1 block"]["ideas"]) == 0)
checks["P7 L3 feasible: 0 everywhere"] = all(len(FEAS["L3 block+spread4+dispersed"][n]) == 0 for n in CORP)
# added after run 1, predicted before run 2
f2 = gi_of["floor2"]
checks["P8 floor2 W50 ideas fp3200 in (.10,.30] and code fp3200<=.05"] = (
    0.10 < r["ideas"][("fp", 50, 3200, f2)] <= 0.30 and r["code"][("fp", 50, 3200, f2)] <= 0.05)
checks["P9 floor W20 spread4 recall<=.6 and floor W50 spread4 recall>=.9 (all corpora)"] = all(
    r[n][("tp", 20, 3200, "common-spread4", fl)] <= 0.6 and r[n][("tp", 50, 3200, "common-spread4", fl)] >= 0.9 for n in CORP)
checks["P10 ideas floor W50 tensions fired per 3200 diff >=.5"] = r["ideas"][("cnt", 50, 3200, fl)] >= 0.5
checks["P11 floor2 W10 ideas fp3200<=.1 with block recall>=.9, but spread4 recall<=.3"] = (
    r["ideas"][("fp", 10, 3200, f2)] <= 0.10 and r["ideas"][("tp", 10, 3200, "common-block", f2)] >= 0.9
    and r["ideas"][("tp", 10, 3200, "common-spread4", f2)] <= 0.3)
for k, v in checks.items(): print(("  ok   " if v else "  MISS ") + k)

missed = [k for k, v in checks.items() if not v]
headline = not both and len(FEAS["L3 block+spread4+dispersed"]["ideas"]) == 0 and len(FEAS["L2 block+spread4"]["ideas"]) == 0
print(f"RESULT: {'PASS' if headline else 'FAIL'} tradeoff-avoidable={bool(both)}; feasible counts L1 (code/docs/ideas)="
      f"{[len(FEAS['L1 block'][n]) for n in CORP]}, L2={[len(FEAS['L2 block+spread4'][n]) for n in CORP]}, "
      f"L3={[len(FEAS['L3 block+spread4+dispersed'][n]) for n in CORP]}; ideas frontier fp-at-recall>=.9={best_fp[0]:.2f} "
      f"recall-at-fp<=.1={best_tp[0]:.2f}; sub-predictions missed: {len(missed)}")
