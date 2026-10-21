# Sandbox: a gag rule card (humiliated-not-harmed, victim-never-wins) filters WHICH
# gags are benign; escalation-needs-matching-distance limits HOW BIG. Do they cover
# each other? Beat is funny iff violation present AND benign-reason holds:
#   benign = card_ok AND severity <= distance_of_framing.
# Deterministic seeded generator, stdlib only.
import random

def gags(seed, n=400):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        out.append({"harm": r.choice(["humiliate", "injure"]),
                    "victim_wins": r.random() < 0.3,
                    "sev_pref": r.randint(1, 5)})
    return out

def card_ok(g, card):
    if not card:
        return True
    return g["harm"] == "humiliate" and not g["victim_wins"]

def run(sched, distance, card, card_partial=False, seed=7):
    """sched: list of severities per beat; distance: fn(beat_idx)->framing distance."""
    pool = gags(seed)
    shown = funny = 0
    for i, sev in enumerate(sched):
        for g in pool[i * 60:(i + 1) * 60]:
            if card_partial:           # card keeps only never-wins, drops the harm rule
                ok = not g["victim_wins"]
            else:
                ok = card_ok(g, card)
            if not ok:
                continue
            shown += 1
            # ground truth: injury or a winning victim is never benign (iteration 2 fix)
            if card_ok(g, True) and sev <= distance(i):
                funny += 1
    prec = funny / shown if shown else 0.0
    return funny, shown, prec

go_big = [1, 2, 3, 4, 5, 5]
mild = [1, 1, 2, 2, 2, 2]
grounded = lambda i: 2
matched = lambda i: min(5, 1 + i)      # framing distance dial turned up with the schedule

R = {}
R["nocard_grounded_big"] = run(go_big, grounded, card=False)
R["card_grounded_big"] = run(go_big, grounded, card=True)
R["card_grounded_mild"] = run(mild, grounded, card=True)
R["card_matched_big"] = run(go_big, matched, card=True)
R["partialcard_matched_big"] = run(go_big, matched, card=True, card_partial=True)  # breaker
for k, (f, s, p) in R.items():
    print("%-26s funny=%3d shown=%3d precision=%.3f" % (k, f, s, p))

# Prediction (before run): card lifts precision (nocard < card at matched distance) but
# does NOT rescue go-big at fixed grounded distance: card_grounded_big funny count stays
# below card_grounded_mild; matched distance restores go-big (>= 2x grounded-big funny);
# the partial card (breaker) drops precision below 1.0 even at matched distance.
ok = (R["card_grounded_big"][0] < R["card_grounded_mild"][0]
      and R["card_matched_big"][0] >= 2 * R["card_grounded_big"][0]
      and R["card_matched_big"][2] > R["nocard_grounded_big"][2]
      and R["partialcard_matched_big"][2] < 1.0)
print("RESULT: %s grounded-big=%d grounded-mild=%d matched-big=%d partial-card precision=%.3f"
      % ("PASS" if ok else "FAIL", R["card_grounded_big"][0], R["card_grounded_mild"][0],
         R["card_matched_big"][0], R["partialcard_matched_big"][2]))
