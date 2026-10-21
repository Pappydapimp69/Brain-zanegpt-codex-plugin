import random
# Model: a beat has severity s (1..5) and harm kind. Funny iff violation (s>=2)
# AND benign (s <= frame distance D) AND rule card allows (kind == humiliation, victim not the underdog).
def funny(s, kind, victim, D, card):
    if s < 2: return False
    if s > D: return False
    if card and (kind != "humiliation" or victim == "underdog"): return False
    return True
def beats(rng, n, card_aware, sched):
    out = []
    for s in sched:
        if card_aware: out.append((s, "humiliation", "bully"))
        else: out.append((s, rng.choice(["humiliation", "injury"]), rng.choice(["bully", "underdog"])))
    return out
def run(sched, dist, card, aware, seed=7, reps=50):
    rng = random.Random(seed); tot = ok = 0
    for _ in range(reps):
        for s, k, v in beats(rng, len(sched), aware, sched):
            D = dist(s); tot += 1; ok += funny(s, k, v, D, card)
    return ok / tot
big = [2, 3, 4, 5] * 3; mild = [2, 2, 3, 3] * 3; flat1 = [1, 1, 1, 1] * 3
r = {}
r["fixed2_bigsched_card"] = run(big, lambda s: 2, True, True)
r["fixed2_mild_card"] = run(mild, lambda s: 2, True, True)
r["matched_big_card"] = run(big, lambda s: s, True, True)
r["matched_big_nocard"] = run(big, lambda s: s, True, False)
r["matched_flat1_card_BREAK"] = run(flat1, lambda s: 5, True, True)
for k, v in r.items(): print(k, round(v, 3))
ok = (r["matched_big_card"] == 1.0 and r["fixed2_bigsched_card"] == 0.25 and r["fixed2_mild_card"] == 0.5
      and 0.2 < r["matched_big_nocard"] < 0.4 and r["matched_flat1_card_BREAK"] == 0.0)
print("RESULT: %s matched+card=%.2f fixed-big=%.2f nocard=%.2f violation-less=%.2f" % ("PASS" if ok else "FAIL",
      r["matched_big_card"], r["fixed2_bigsched_card"], r["matched_big_nocard"], r["matched_flat1_card_BREAK"]))
