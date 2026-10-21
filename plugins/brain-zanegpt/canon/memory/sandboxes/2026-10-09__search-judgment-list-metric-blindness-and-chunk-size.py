# Deterministic toy search stack (no RNG). Exercises three kernels:
#  A judgment list vs eyeballing, B metric blind spots, C chunk size.
import math
from collections import Counter
NT, SIG, PARA = 8, 8, 24
def sig(t): return [f"t{t}w{i}" for i in range(SIG)]
FILL = [f"f{i}" for i in range(10)]
def para(t):  # signature words cycle in order, filler between -> w0 and w5 sit 5 positions apart
    out = []
    for i in range(PARA):
        out.append(sig(t)[(i // 2) % SIG] if i % 2 == 0 else FILL[(i * 3 + t) % len(FILL)])
    return out
def doc_tokens(d): return [w for k in (0, 0, 1, 2) for w in para((d + k) % NT)]  # primary topic written twice, 2 later topics once
DOCS = {d: doc_tokens(d) for d in range(NT)}
def grade(d, t):  # 2 if t is the doc's FIRST topic, 1 if later topic, 0 otherwise
    return 2 if t == d else 1 if t in {(d + 1) % NT, (d + 2) % NT} else 0
QUERIES = [(t, [sig(t)[0], sig(t)[5]]) for t in range(NT)]
DF = Counter(w for d in DOCS.values() for w in set(d))
def idf(w): return math.log(1 + NT / DF[w]) if DF[w] else 0.0
def tfidf(units, q):
    c = Counter(units); return sum((1 + math.log(c[w])) * idf(w) for w in q if c[w])
def rank_whole(q, decoy=0.0, tags=None):
    s = {d: tfidf(DOCS[d], q) / math.sqrt(len(DOCS[d])) for d in DOCS}
    if tags:  # buggy boost on an irrelevant field (decoy tags)
        for d, tg in tags.items(): s[d] += decoy * sum(1 for w in q if w in tg)
    return sorted(DOCS, key=lambda d: (-s[d], d))
def dcg(gr): return sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(gr))
def ndcg(rk, t, k=3):
    gr = [grade(d, t) for d in rk[:k]]; ideal = sorted((grade(d, t) for d in DOCS), reverse=True)[:k]
    return dcg(gr) / dcg(ideal)
def pk(rk, t, k=3): return sum(grade(d, t) > 0 for d in rk[:k]) / k
def mrr(rk, t): return next((1 / (i + 1) for i, d in enumerate(rk) if grade(d, t) > 0), 0.0)
def avg(f, ranker): return sum(f(ranker(q), t) for t, q in QUERIES) / len(QUERIES)
res = []

# ---- A: boosted decoy field. The ranker never errors; spot-check of first 3 queries vs full list.
tags = {(t + 4) % NT: set(sig(t)[:2]) for t in (5, 6, 7)}   # decoy tags on a non-relevant doc, affecting only queries 5-7
good = lambda q: rank_whole(q)
bug = lambda q: rank_whole(q, decoy=50.0, tags=tags)
spot_same = all(bug(q)[0] == good(q)[0] for t, q in QUERIES[:3])
nd_g, nd_b = avg(lambda r, t: ndcg(r, t), good), avg(lambda r, t: ndcg(r, t), bug)
print(f"A spot-check(first 3) same top1: {spot_same}; full-list nDCG@3 good {nd_g:.3f} bug {nd_b:.3f}")
res.append(("A", nd_b < nd_g))
res.append(("A-spot-blind", spot_same))

# ---- B: two regressions on top of the good ranker; each metric is blind to one of them.
def swap_best(q):  # reorder top3 so grade-2 doc is last: still all relevant
    r = good(q); top = sorted(r[:3], key=lambda d: grade(d, [t for t, qq in QUERIES if qq == q][0])); return top + r[3:]
def demote_first(q):  # push the first hit to rank 2 behind a NON-relevant doc... keeps P@3 equal
    r = good(q); t = [t for t, qq in QUERIES if qq == q][0]
    non = next(d for d in r if grade(d, t) == 0)
    rest = [d for d in r if d != non]; return [non] + rest
print("B metric   base   swap-best  demote-first")
for name, f in (("P@3", pk), ("MRR", mrr), ("nDCG@3", ndcg)):
    print(f"  {name:7} {avg(f, good):.3f}  {avg(f, swap_best):.3f}      {avg(f, demote_first):.3f}")
pk_blind = avg(pk, swap_best) == avg(pk, good); mrr_blind = avg(mrr, swap_best) == avg(mrr, good)
nd_sees_swap = avg(ndcg, swap_best) < avg(ndcg, good); mrr_sees_demote = avg(mrr, demote_first) < avg(mrr, good)
pk_sees_demote = avg(pk, demote_first) < avg(pk, good)
res += [("B", pk_blind and mrr_blind and nd_sees_swap and mrr_sees_demote and pk_sees_demote)]

# ---- C: chunking. Hit = top-1 doc has grade>0; chunk score = best chunk. size in tokens, overlap 25%.
def rank_chunks(q, size):
    step = max(1, int(size * 0.75)); sc = {}
    for d, toks in DOCS.items():
        sc[d] = max(tfidf(toks[i:i + size], q) for i in range(0, max(1, len(toks) - size + 1), step))
    return sorted(DOCS, key=lambda d: (-sc[d], d))
print("C size   P@1(any relevant)  top1==primary-topic doc")
c_res = {}
for size in (3, 12, 30, 72):
    rk = lambda q, s=size: rank_chunks(q, s)
    p1 = sum(grade(rk(q)[0], t) > 0 for t, q in QUERIES) / NT
    pri = sum(rk(q)[0] == t for t, q in QUERIES) / NT
    c_res[size] = (p1, pri); print(f"  {size:3}    {p1:.3f}             {pri:.3f}")
whole = sum(rank_whole(q)[0] == t for t, q in QUERIES) / NT
print(f"  whole-doc primary-topic top1 {whole:.3f}")
res.append(("C-small-chunks-lose-repetition-signal", c_res[3][1] < 0.5 and c_res[12][1] < 0.5))
res.append(("C-chunks-spanning-the-repeat-match-whole-doc", c_res[30][1] == whole and c_res[72][1] == whole))
print(res)
print(f"RESULT: {'PASS' if all(ok for _, ok in res) else 'FAIL'} " + "; ".join(f"{n}={ok}" for n, ok in res))
