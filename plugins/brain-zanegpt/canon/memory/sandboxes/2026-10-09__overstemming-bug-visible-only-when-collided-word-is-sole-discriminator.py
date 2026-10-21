"""Run 1 (kept for honesty): FAILED with every drop 0.000 because ids sort relevant-first ('0x' < '0y'), so the tie
breaker silently put the relevant doc on top after truncation made the two docs tie. Run 2 adds a tie-break parameter.
Prediction (written before run 1): a 4-char truncation analyzer (temper/tempest -> temp) never errors; a judgment list
reports an MRR drop only for queries where the collided word is the sole discriminator between the relevant doc and a decoy
(drop > 0.2 on those queries), and reports 0.000 drop for queries that also carry a disambiguating non-colliding term. The
drop on the full list scales with the share of sole-discriminator queries (0 of 6 -> 0, 3 of 6 -> about half the sole-query
drop, 6 of 6 -> full), and a list that omits that query class cannot see the bug at any list length. Stdlib, no RNG."""
import math
from collections import Counter

PAIRS = [("temper", "tempest"), ("grind", "grinder"), ("polish", "polishing"), ("press", "pressing"), ("weave", "weaving"), ("drill", "drilling")]
CTX = ["kiln", "loom", "forge", "mill", "vat", "lathe"]
def corpus():
    docs = []
    for i, (x, y) in enumerate(PAIRS):
        docs.append((f"{i}x", f"{CTX[i]} {x} note"))       # relevant for query word x
        docs.append((f"{i}y", f"{CTX[i]} {y} note"))       # decoy: same context, differs only by the collided word
    return docs
def tok(s, stem): return [w[:4] if stem else w for w in s.split()]
TIE = {'favor': lambda d: d, 'against': lambda d: ('!' + d) if d.endswith('y') else d}
def mrr(queries, stem, tie='favor'):
    docs = corpus(); N = len(docs)
    toks = {d: Counter(tok(t, stem)) for d, t in docs}
    df = Counter(w for c in toks.values() for w in c)
    idf = lambda w: math.log(1 + N / (1 + df.get(w, 0)))
    tot = 0
    for qtext, rel in queries:
        q = tok(qtext, stem)
        sc = sorted(((-sum(idf(w) * toks[d][w] for w in q), TIE[tie](d), d) for d, _ in docs))
        rank = [d for _, _, d in sc].index(rel) + 1
        tot += 1 / rank
    return tot / len(queries)
sole = [(PAIRS[i][0], f"{i}x") for i in range(6)]                         # query = the colliding word alone
withctx = [(f"{CTX[i]} {PAIRS[i][0]}", f"{i}x") for i in range(6)]       # + context word, but decoy shares context too
withunique = [(f"{PAIRS[i][0]} note {CTX[i]}", f"{i}x") for i in range(6)]
res = {}
for tie in ('favor', 'against'):
  for name, qs in (("sole", sole), ("with_shared_context", withctx)):
    res[name, tie] = (mrr(qs, False, tie), mrr(qs, True, tie)); print(tie, name, "ok=%.3f overstemmed=%.3f" % res[name, tie])
# mixed lists: k sole-discriminator queries + (6-k) queries whose relevant doc has a unique extra token
def mixed(k):
    qs = sole[:k]
    for i in range(k, 6):
        qs.append((PAIRS[i][0] + " " + "u%d" % i, f"{i}x"))
    return qs
def mrr_mixed(k, stem, tie='against'):
    docs = [(d, t) for d, t in corpus()]
    docs = [(d, t + (" u%d" % int(d[0]) if d.endswith("x") and int(d[0]) >= k else "")) for d, t in docs]
    N = len(docs); toks = {d: Counter(tok(t, stem)) for d, t in docs}
    df = Counter(w for c in toks.values() for w in c); idf = lambda w: math.log(1 + N / (1 + df.get(w, 0)))
    tot = 0
    for qtext, rel in mixed(k):
        sc = sorted(((-sum(idf(w) * toks[d][w] for w in tok(qtext, stem)), TIE[tie](d), d) for d, _ in docs))
        tot += 1 / ([d for _, _, d in sc].index(rel) + 1)
    return tot / 6
drops = {}
for k in (0, 3, 6):
    g, b = mrr_mixed(k, False), mrr_mixed(k, True); drops[k] = g - b
    print("sole queries=%d/6 MRR ok=%.3f overstemmed=%.3f drop=%.3f" % (k, g, b, drops[k]))
c0 = all(res[n, 'favor'][0] - res[n, 'favor'][1] < 0.01 for n in ("sole", "with_shared_context"))   # favoring tie-break hides it
sw, sc_ = res["sole", "against"], res["with_shared_context", "against"]
c1 = sw[0] - sw[1] > 0.2
c2 = sc_[0] - sc_[1] > 0.2
c3 = drops[0] < 0.01 and drops[6] > 0.2 and drops[0] < drops[3] < drops[6]
print("checks favoring_tiebreak_hides_bug=%s sole_visible_when_tie_against=%s shared_context_still_visible=%s scales_with_share=%s" % (c0, c1, c2, c3))
print("RESULT: %s tie favors relevant: drop 0.000 for both; tie against: sole %.3f->%.3f, shared-context %.3f->%.3f; mixed-list drop 0/6=%.3f 3/6=%.3f 6/6=%.3f"
      % ("PASS" if (c0 and c1 and c3) else "FAIL", *sw, *sc_, drops[0], drops[3], drops[6]))
