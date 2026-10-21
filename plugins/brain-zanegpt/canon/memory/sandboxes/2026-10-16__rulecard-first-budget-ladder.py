import random
# Ladder = one valid, benign beat at each severity 2..5 (distance matched to severity).
def valid(s, kind, victim): return kind == "humiliation" and victim == "bully"
def ladder_done(budget, card_first, allowed_sev, seed):
    rng = random.Random(seed); have = set()
    for _ in range(budget):
        s = rng.choice(allowed_sev)
        if card_first: kind, victim = "humiliation", "bully"
        else: kind, victim = rng.choice(["humiliation", "injury"]), rng.choice(["bully", "underdog"])
        if valid(s, kind, victim) and s >= 2: have.add(s)
    return have >= {2, 3, 4, 5}
def rate(budget, card_first, allowed=(1, 2, 3, 4, 5)):
    return sum(ladder_done(budget, card_first, allowed, sd) for sd in range(200)) / 200
r = {"first20": rate(20, True), "after20": rate(20, False), "after200_BREAK": rate(200, False),
     "first20_narrowcard": rate(20, True, (2, 3))}
for k, v in r.items(): print(k, v)
ok = r["first20"] >= 0.9 and r["after20"] < 0.3 and r["after200_BREAK"] > 0.95 and r["first20_narrowcard"] == 0.0
print("RESULT: %s ladder-complete first=%.2f after=%.2f after-big-budget=%.2f narrow-card=%.2f" % ("PASS" if ok else "FAIL",
      r["first20"], r["after20"], r["after200_BREAK"], r["first20_narrowcard"]))
