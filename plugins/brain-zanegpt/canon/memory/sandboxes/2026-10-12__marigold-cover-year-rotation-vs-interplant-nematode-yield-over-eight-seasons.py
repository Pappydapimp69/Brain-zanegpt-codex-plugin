"""Gap sandbox: ideas:GARDEN/companion-planting-claim-taxonomy says marigold nematode suppression works ONLY as a full-season
soil-occupying cover crop. brainwork E104 modelled one season's coverage curve (pool 0.77/0.59/0.26/0.07/0.006 of control at
5/10/25/50/95 percent coverage) but never asked the decision question: over several seasons, is a sacrificed cover-crop season worth it
against tomato every year or a 10 percent interplant?
Prediction (before run), start pool 2 (relative units), tomato multiplier 6 per season capped at 50, yield = 1/(1+pool/5), interplant
costs 10 percent yield: (1) tomato-only mean yield over 8 seasons < 0.2; (2) cover every 3rd season has the best mean yield of
{tomato-only, interplant-10, cover-1-in-3, cover-1-in-2} at that multiplier; (3) cover-1-in-2 is worse than 1-in-3 because it
sacrifices more seasons than the pool needs; (4) interplant-10 never beats tomato-only by more than 0.05 mean yield; (5) BREAK: with the
kill coefficient halved, cover-1-in-3 drops below cover-1-in-2 and the ranking flips."""
D, G, N = 120, 0.06, 8
def season_factor(cov, k):             # same daily-kill form as the E104 curve, relative to the unsuppressed growth
    return (max(1.0 - k * cov / (1 + G), 0.0)) ** D
K_FULL = 0.0473
chk = {c: season_factor(c, K_FULL) for c in (0.05, 0.10, 0.25, 0.50, 0.95)}
print("curve vs E104 (0.77,0.59,0.26,0.07,0.006): " + " ".join(f"{c:.2f}:{v:.3f}" for c, v in chk.items()))
def simulate(plan, R=6.0, cap=50.0, k=K_FULL, pool0=2.0, p50=5.0):
    pool, ys = pool0, []
    for s in range(N):
        kind = plan(s)
        if kind == "cover":
            pool *= season_factor(0.95, k); ys.append(0.0)
        else:
            cov = 0.10 if kind == "inter" else 0.0
            ys.append((1 / (1 + pool / p50)) * (0.9 if kind == "inter" else 1.0))
            pool = min(pool * R * season_factor(cov, k), cap)
    return sum(ys) / N
plans = {"tomato-only": lambda s: "t", "interplant-10": lambda s: "inter",
         "cover-1-in-3": lambda s: "cover" if s % 3 == 2 else "t", "cover-1-in-2": lambda s: "cover" if s % 2 == 1 else "t"}
res = {n: simulate(p) for n, p in plans.items()}
for n, v in res.items(): print(f"{n:15s} mean yield {v:.3f}")
res_half = {n: simulate(p, k=K_FULL / 2) for n, p in plans.items()}
print("BREAK kill halved: " + " ".join(f"{n}={v:.3f}" for n, v in res_half.items()))
res_low = {n: simulate(p, R=2.0) for n, p in plans.items()}
print("R=2 (weak multiplier): " + " ".join(f"{n}={v:.3f}" for n, v in res_low.items()))
p1 = res["tomato-only"] < 0.2
p2 = max(res, key=res.get) == "cover-1-in-3"
p3 = res["cover-1-in-2"] < res["cover-1-in-3"]
p4 = res["interplant-10"] - res["tomato-only"] <= 0.05
p5 = res_half["cover-1-in-3"] < res_half["cover-1-in-2"]
held = [p1, p2, p3, p4, p5]
print("held:", held)
print(f"RESULT: {'PASS' if all(held) else 'FAIL'} {sum(held)}/5 predictions held")
