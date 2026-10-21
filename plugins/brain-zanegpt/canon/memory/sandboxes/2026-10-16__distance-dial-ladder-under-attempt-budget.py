import random
# Severe harm wants distance, mild harm wants closeness: target distance(s) = s. Funny = s * max(0, 1 - |d - s| / 3).
def f(s, d): return s * max(0.0, 1 - abs(d - s) / 3)
RUNGS = (2, 3, 4, 5)
def completed(budget, card_first, seed):
    rng = random.Random(seed); have = set()
    for _ in range(budget):
        s = rng.choice((1, 2, 3, 4, 5))
        ok = True if card_first else (rng.random() < 0.5 and rng.random() < 0.5)  # humiliation of a bully
        if ok and s >= 2: have.add(s)
    return have
def mean_score(dist, budget, card_first, reps=200):
    return sum(sum(f(s, dist(s)) for s in completed(budget, card_first, sd)) for sd in range(reps)) / reps
dials = {"matched": lambda s: s, "near": lambda s: 1, "far": lambda s: 5, "mid": lambda s: 3}
r = {k: mean_score(v, 20, True) for k, v in dials.items()}
r["matched_cardafter20"] = mean_score(dials["matched"], 20, False)
r["matched_cardafter200"] = mean_score(dials["matched"], 200, False)  # BREAK: big budget removes the order penalty
r["full_ladder_matched"] = sum(f(s, s) for s in RUNGS)
for k, v in r.items(): print(k, round(v, 2))
ok = (r["matched"] >= 0.9 * 14 and r["near"] < 4 and 6 < r["far"] < 10 and 0.5 * r["matched"] < r["matched_cardafter20"] < 0.8 * r["matched"]  # first-run bound of 25% was wrong: partial ladders still score
      and r["matched_cardafter200"] > 0.95 * 14)
print("RESULT: %s mean ladder score matched=%.2f near=%.2f far=%.2f mid=%.2f; card-after budget20=%.2f budget200=%.2f" % (
    "PASS" if ok else "FAIL", r["matched"], r["near"], r["far"], r["mid"], r["matched_cardafter20"], r["matched_cardafter200"]))
