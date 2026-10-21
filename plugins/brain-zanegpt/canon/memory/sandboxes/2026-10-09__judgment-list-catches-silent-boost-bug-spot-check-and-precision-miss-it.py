"""Prediction (written before the first run):
 A tiny lexical engine (title/body/tags, tf x field boost) over a fixed 10-topic corpus. Two silent bugs, neither raises:
   BUG_A tags boost 0.5 -> 6 (decoys whose tags carry the query word outrank real hits; decoys exist for 3 of 10 topics: 3, 5, 8)
   BUG_B body boost 1 -> 5 (reorders primary/secondary hits inside the top 3, same set).
 P1: manually spot-checking the first 3 queries (topics 0,1,2) shows NO visible defect for BUG_A (top hit is right).
 P2: a 10-query judgment list flags BUG_A on nDCG@5 and MRR (>=1 drop each) and the list needs >= 4 queries to see it
     (first decoy topic is 3, so a list of 1-3 queries misses it).
 P3: BUG_B leaves precision@3 unchanged for all queries (same top-3 set) but lowers nDCG@5; MRR is unchanged or smaller.
 Built to break: P@3 as the only gate must MISS BUG_B; spot-check of the first 3 queries must MISS BUG_A.
Iteration note: run 1 used titles that named OTHER topics, so unrelated docs outranked real hits even with correct boosts
(good P@3=0.333) and BUG_B accidentally improved nDCG to 1.0; the fixture was wrong, not the claim. Run 2 uses neutral titles and a
secondary doc with higher body tf (5 vs 3) so the body-boost bug reorders main/secondary without changing the top-3 set.
Deterministic, stdlib only, no RNG."""
import math

TOPICS = ["alpha", "bravo", "cobalt", "delta", "ember", "fjord", "garnet", "harbor", "indigo", "juniper"]
DECOY = {3, 5, 8}

def corpus():
    docs = []
    for i, w in enumerate(TOPICS):
        docs.append(dict(id=f"{w}-main", title=f"{w} guide", body=f"{w} {w} {w} usage", tags="", g={w: 3}))
        docs.append(dict(id=f"{w}-second", title="notes", body=f"{w} {w} {w} {w} {w}", tags="", g={w: 2}))
        docs.append(dict(id=f"{w}-tangent", title="misc", body=f"{w} once", tags="", g={w: 1}))
        if i in DECOY:
            docs.append(dict(id=f"{w}-decoy", title="unrelated topic", body="nothing relevant here", tags=f"{w} {w} {w}", g={}))
    return docs

DOCS = corpus()
GOOD = dict(title=3.0, body=1.0, tags=0.5)

def search(q, boosts):
    scored = []
    for d in DOCS:
        s = sum(boosts[f] * d[f].split().count(q) for f in boosts)
        if s > 0: scored.append((-s, d["id"], d))
    return [d for _, _, d in sorted(scored, key=lambda x: (x[0], x[1]))]

def grade(d, q): return d["g"].get(q, 0)
def dcg(gs): return sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(gs))
def ndcg5(q, res):
    ideal = sorted((d["g"][q] for d in DOCS if q in d["g"]), reverse=True)[:5]
    return dcg([grade(d, q) for d in res[:5]]) / dcg(ideal)
def p3(q, res): return sum(grade(d, q) > 0 for d in res[:3]) / 3
def rr(q, res):
    for i, d in enumerate(res): 
        if grade(d, q) > 0: return 1 / (i + 1)
    return 0.0

def evalset(boosts, qs):
    r = [search(q, boosts) for q in qs]
    n = len(qs)
    return (sum(p3(q, x) for q, x in zip(qs, r)) / n, sum(rr(q, x) for q, x in zip(qs, r)) / n, sum(ndcg5(q, x) for q, x in zip(qs, r)) / n)

BUG_A = dict(GOOD, tags=6.0)
BUG_B = dict(GOOD, body=5.0)
TOL = 1e-9

def spot_ok(boosts, qs):  # eyeball: is the top hit a relevant doc for each query?
    return all(grade(search(q, boosts)[0], q) > 0 for q in qs)

print("S1 spot-check first 3 queries: good", spot_ok(GOOD, TOPICS[:3]), "bugA", spot_ok(BUG_A, TOPICS[:3]), "bugB", spot_ok(BUG_B, TOPICS[:3]))
base = evalset(GOOD, TOPICS)
a = evalset(BUG_A, TOPICS); b = evalset(BUG_B, TOPICS)
f = lambda t: "P@3=%.3f MRR=%.3f nDCG@5=%.3f" % t
print("S2 full 10-query list good ", f(base)); print("   bugA ", f(a)); print("   bugB ", f(b))
det_a = [k for k, (x, y) in zip(("P@3", "MRR", "nDCG"), zip(base, a)) if y < x - TOL]
det_b = [k for k, (x, y) in zip(("P@3", "MRR", "nDCG"), zip(base, b)) if y < x - TOL]
print("S3 detectors bugA", det_a, "bugB", det_b)
need = None
for n in range(1, 11):
    g, x = evalset(GOOD, TOPICS[:n]), evalset(BUG_A, TOPICS[:n])
    if x[2] < g[2] - TOL:
        need = n; break
print("S4 smallest judgment-list prefix that exposes bugA on nDCG@5:", need)
p1 = spot_ok(BUG_A, TOPICS[:3]) and spot_ok(GOOD, TOPICS[:3])
p2 = "nDCG" in det_a and "MRR" in det_a and need is not None and need >= 4
p3_ = ("P@3" not in det_b) and ("nDCG" in det_b)
ok = p1 and p2 and p3_
print(f"RESULT: {'PASS' if ok else 'FAIL'} spot-check_misses_bugA={p1}; bugA_detected_by={det_a} needs_{need}_queries; bugB_detected_by={det_b} (P@3 blind={ 'P@3' not in det_b})")
