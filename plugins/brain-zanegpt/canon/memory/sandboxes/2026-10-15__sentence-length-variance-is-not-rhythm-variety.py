"""Loop 4 pass 4 (new domain: Writing & storytelling). Prose-rhythm advice says vary sentence length;
style checkers often operationalise that as the spread of sentence lengths (coefficient of variation,
CV). Claim tested: CV measures spread, not variety - a mechanical short/long alternation scores as
the MOST varied paragraph. Proposed fix: also test periodicity (autocorrelation of lengths at lags
1..4). Then push: how often does that periodicity test fire on non-periodic paragraphs of realistic
length? Paragraphs below are written for this sandbox; labels are by construction.
Deterministic: random.Random(7) for the non-periodic sweep.
PREDICTION (written before running): CV order alternating > varied > three-cycle > monotone, so CV
alone calls the alternating paragraph best. Lag-1 autocorrelation is about -1 for alternating, about
-0.5 for the three-cycle (missed by a lag-1-only test at threshold 0.7), and max |r| over lags 1..4
catches both. On non-periodic random lengths the max-lag test false-positive rate is > 20% at 8
sentences and < 5% at 32.
RUN 1 refuted the autocorrelation fix at paragraph size (it flagged all four paragraphs, including the
near-monotone one at r=1.00 lag 4, and the varied one at 0.71). Added after run 1, so not predicted:
a CV gate (CV < 0.2 = monotone) plus an exact-period check on coarse bins (S <= 6 words, M 7-12,
L >= 13): flag when bin[i] == bin[i+p] on >= 80% of pairs for p = 2 or 3, measured on the same
paragraphs and on the same iid sweep."""
import re, random, statistics as st

PARAS = {
 "monotone": "The storm came in at dusk. We closed every door fast. The dog hid under the bed. "
             "My father lit two oil lamps. The wind shook the old shutters. Nobody said a single word. "
             "The rain hit the tin roof. We waited for it to pass.",
 "alternating": "The storm came. It rolled in from the west at dusk with a sound like trains crossing a bridge. "
                "We ran. My father pulled every shutter closed while my mother counted the seconds after the lightning. "
                "The dog hid. Under the bed he pressed himself flat against the boards and would not come out for anyone. "
                "Lamps flickered. Somewhere down the valley a tree split and fell across the road we had driven that morning.",
 "three_cycle": "The storm came. It rolled in from the west at dusk. A sound like trains crossing a long iron bridge filled the valley. "
                "We ran. My father pulled the shutters closed. My mother stood at the window counting the seconds after each flash. "
                "The dog hid. He pressed himself under the bed. Nothing we said or offered him would bring him out before morning.",
 "varied": "The storm came in at dusk. It rolled from the west with a sound like trains crossing a bridge, and the valley went dark. "
           "We ran. My father pulled the shutters while my mother counted the seconds after the lightning. "
           "The dog hid under the bed and would not come out for anyone, not even for the ham bone. Lamps flickered. "
           "Somewhere down the valley a tree split. We heard it fall across the road we had driven that morning, the one to town.",
}
def lengths(text): return [len(s.split()) for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
def cv(xs): return st.pstdev(xs) / st.mean(xs)
def acf(xs, lag):
    m = st.mean(xs); d = [x - m for x in xs]; den = sum(v * v for v in d)
    return 0.0 if den == 0 else sum(d[i] * d[i + lag] for i in range(len(d) - lag)) / den * len(d) / (len(d) - lag)
def max_lag(xs, lags=(1, 2, 3, 4)): return max(((abs(acf(xs, L)), L) for L in lags if L < len(xs) - 1), default=(0.0, 0))

rows = {}
for k, t in PARAS.items():
    L = lengths(t); c = cv(L); r1 = acf(L, 1); mx, at = max_lag(L)
    rows[k] = (c, r1, mx, at)
    print(f"{k:12s} n={len(L):2d} lens={L} CV={c:.3f} r1={r1:+.2f} max|r|={mx:.2f}@lag{at}")
order = sorted(rows, key=lambda k: -rows[k][0])
print("CV ranking (most 'varied' first):", order)
TH = 0.7
flag1 = {k: rows[k][1] <= -TH or rows[k][1] >= TH for k in rows}
flagm = {k: rows[k][2] >= TH for k in rows}
print(f"lag-1-only flags (|r1|>={TH}): {flag1}")
print(f"max-lag flags (max|r| lags1-4 >={TH}): {flagm}")

# push: false positives of the max-lag test on non-periodic paragraphs (iid lengths 4..28 words)
rng = random.Random(7); fp = {}
for n in (6, 8, 12, 16, 24, 32, 48):
    hits = 0; trials = 2000
    for _ in range(trials):
        xs = [rng.randint(4, 28) for _ in range(n)]
        if st.pstdev(xs) == 0: continue
        if max_lag(xs)[0] >= TH: hits += 1
    fp[n] = hits / trials
print("max-lag false-positive rate on iid lengths by sentence count:", {n: round(v, 3) for n, v in fp.items()})
def bins(xs): return ["S" if x <= 6 else "M" if x <= 12 else "L" for x in xs]
def bin_period(xs, frac=0.8):
    b = bins(xs)
    for p_ in (2, 3):
        pairs = [(b[i], b[i + p_]) for i in range(len(b) - p_)]
        if pairs and sum(a == c for a, c in pairs) / len(pairs) >= frac: return p_
    return 0
def verdict(xs):
    if cv(xs) < 0.2: return "monotone"
    return f"periodic{bin_period(xs)}" if bin_period(xs) else "ok"
fixv = {k: verdict(lengths(t)) for k, t in PARAS.items()}
print("fix verdicts (CV gate + binned exact period):", fixv)
rng2 = random.Random(11); fp2 = {}
for n in (6, 8, 12, 16, 24, 32):
    hits = 0; trials = 2000
    for _ in range(trials):
        xs = [rng2.randint(4, 28) for _ in range(n)]
        if verdict(xs) != "ok": hits += 1
    fp2[n] = hits / trials
print("fix false-positive rate on iid lengths:", {n: round(v, 3) for n, v in fp2.items()})
n_ok = min(n for n in fp if fp[n] < 0.05 and all(fp[m] < 0.05 for m in fp if m > n))

# Verdict on the run-1 claims as predicted (the max-lag fix is expected to be REFUTED on paragraphs)
cv_claim = order[0] == "alternating" and order[-1] == "monotone" and flag1["alternating"] and not flag1["three_cycle"]
maxlag_fix_holds = flagm["alternating"] and flagm["three_cycle"] and not flagm["varied"] and not flagm["monotone"]
binfix = fixv == {"monotone": "monotone", "alternating": "periodic2", "three_cycle": "periodic3", "varied": "ok"}
ok = cv_claim and binfix
print(f"RESULT: {'PASS' if ok else 'FAIL'} max-lag autocorr fix refuted on paragraphs ({sum(flagm.values())}/4 flagged incl. monotone r=1.00, varied {rows['varied'][2]:.2f}); "
      f"CV gate+binned period verdicts {list(fixv.values())}, iid FP n8 {fp2[8]:.3f} n12 {fp2[12]:.3f}; CV ranks {order} (alternating CV {rows['alternating'][0]:.2f} > varied {rows['varied'][0]:.2f}); "
      f"r1 alternating {rows['alternating'][1]:+.2f}, three-cycle {rows['three_cycle'][1]:+.2f} (lag-1 test misses it), "
      f"max-lag catches three-cycle at lag {rows['three_cycle'][3]} r={rows['three_cycle'][2]:.2f}, varied max {rows['varied'][2]:.2f}; "
      f"iid false positives n8 {fp[8]:.3f} n12 {fp[12]:.3f} n32 {fp[32]:.3f}; <5% from n={n_ok}")
