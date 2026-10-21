"""Gap: SEARCH/ranking/spell-correction-is-a-noisy-channel... + SEARCH/ranking/position-bias-corrupts-click-based-relevance...
(+ brainwork/E12 style evidence is not re-used; only the two kernels and the dictionary-vs-log contrast are exercised).
PREDICTION (before running): (1) dictionary-only corrector (uniform prior, shortest edit distance, alphabetical ties) is right on
well under 70% of popularity-weighted typos; noisy channel with the true log-frequency LM is right on >= 95%, including brand
words missing from the dictionary. (2) Training the LM on raw clicks over 6 rounds from a dictionary start leaves at least 3 of
the 8 ambiguous queries on the wrong top suggestion (exposure ratio 1/0.3 = 3.3x beats true popularity ratios below 3.3);
IPS-weighted clicks fix all 8 within 6 rounds. (3) BREAK: when the true ratio is >= 4 the raw-click loop recovers too, so the
trap only holds for ratios under the exposure ratio (here 3.33)."""
from fractions import Fraction as F
import math

# vocabulary: (word, true popularity, in_dictionary)
VOCAB = [("tesla", 900, True), ("tessla", 0, False), ("zalando", 400, False), ("zalondo", 0, False),
         ("nike", 800, True), ("mike", 300, True), ("bike", 150, True), ("hike", 120, True),
         ("lime", 500, True), ("like", 2000, True), ("lice", 40, True), ("line", 900, True),
         ("canva", 350, False), ("cansa", 5, False), ("casa", 300, True), ("cava", 120, True)]
POP = {w: p for w, p, _ in VOCAB}; INDICT = {w: d for w, _, d in VOCAB}

def ed(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[-1]

def typos(w):                           # deterministic single-deletion typos
    return sorted({w[:i] + w[i + 1:] for i in range(len(w))} - {w})
TESTS = []                               # (typo, intended, weight)
for w, p, _ in VOCAB:
    if p == 0: continue
    for t in typos(w): TESTS.append((t, w, F(p, len(typos(w)))))

def cands(q, words): return [w for w in words if ed(q, w) <= 2]
def correct_dict(q):
    cs = sorted(cands(q, [w for w in POP if INDICT[w]]), key=lambda w: (ed(q, w), w))
    return cs[0] if cs else None
LAM = 0.05
def correct_nc(q, lm):
    cs = cands(q, [w for w in POP if lm.get(w, 0) > 0])
    return max(cs, key=lambda w: (LAM ** ed(q, w) * lm[w], w)) if cs else None
def acc(fn):
    tot = sum(w for _, _, w in TESTS); good = sum(w for q, i, w in TESTS if fn(q) == i)
    return float(good / tot)

ok = True
a_dict = acc(correct_dict); a_nc = acc(lambda q: correct_nc(q, POP))
print(f"S1 dictionary corrector accuracy {a_dict:.3f}; noisy channel with true log LM {a_nc:.3f}")
brand_tests = [(q, i) for q, i, _ in TESTS if not INDICT[i]]
b_dict = sum(correct_dict(q) == i for q, i in brand_tests) / len(brand_tests)
b_nc = sum(correct_nc(q, POP) == i for q, i in brand_tests) / len(brand_tests)
print(f"S1b brand/out-of-dictionary typos: dictionary {b_dict:.2f} noisy channel {b_nc:.2f} ({len(brand_tests)} typos)")
miss_nc = a_nc < 0.95   # prediction (1) threshold; recorded
ok &= a_dict < 0.70 and a_nc >= a_dict + 0.15 and b_nc > b_dict

# S2 click loop on ambiguous queries: query -> (candidate list of two). exposure: rank1 1.0, rank2 0.3
EXPO = (F(1), F(3, 10))
AMBIG = [("nke", "nike", "mike"), ("lie", "like", "lime"), ("ln", "line", "lime"), ("hik", "hike", "bike"),
         ("tesl", "tesla", "tessla"), ("zalando"[:-1], "zalando", "zalondo"), ("cana", "canva", "casa"), ("cav", "cava", "casa")]
def loop(ips, rounds=6, ratio_override=None):
    wrong = 0
    for q, a_, b_ in AMBIG:
        truth, other = (a_, b_) if POP[a_] >= POP[b_] else (b_, a_)   # truth = the more popular candidate
        pop = dict(POP)
        pop[other] = max(pop[other], 1)
        if ratio_override: pop[truth] = pop[other] * F(ratio_override).limit_denominator(100)
        # start LM: dictionary-like flat prior, tie-broken so the OTHER word leads initially
        lm = {truth: F(1), other: F(1, 1) + F(1, 100)}
        for _ in range(rounds):
            order = sorted((truth, other), key=lambda w: (-lm[w], w))
            gain = {}
            for rank, w in enumerate(order):
                clicks = EXPO[rank] * F(pop[w], pop[truth] + pop[other])   # expected clicks, no sampling
                gain[w] = clicks / EXPO[rank] if ips else clicks
            tot = sum(gain.values())
            for w in lm: lm[w] = lm[w] + gain[w] / tot * 10
        top = max((truth, other), key=lambda w: (lm[w], w))
        wrong += top != truth
    return wrong
w_raw, w_ips = loop(False), loop(True)
print(f"S2 ambiguous queries wrong after 6 rounds: raw clicks {w_raw}/8, IPS {w_ips}/8")
ok &= w_raw >= 3 and w_ips == 0
# S3 BREAK: strongly separated popularity (ratio 4, 6) -> raw recovers?
for r in (1.5, 3, 4, 6):
    print(f"S3 true ratio {r}: raw wrong {loop(False, ratio_override=r)}/8, IPS wrong {loop(True, ratio_override=r)}/8")
raw_hi = loop(False, ratio_override=6); raw_mid = loop(False, ratio_override=1.5)
ok &= raw_hi == 0 and raw_mid >= 3
print("RESULT:", "PASS" if ok else "FAIL", f"(95% target missed: {miss_nc}) dictionary {a_dict:.2f} vs noisy channel {a_nc:.2f} accuracy; raw-click LM loop wrong {w_raw}/8 vs IPS {w_ips}/8; raw recovers once the true ratio exceeds the 3.33 exposure ratio")
