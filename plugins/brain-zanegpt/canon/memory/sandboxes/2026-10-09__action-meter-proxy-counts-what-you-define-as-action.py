# Deterministic sandbox (no RNG, no real timing). Hunger decay models:
#   timer  : 1.0 per wall-clock minute
#   action : 0.1 per COUNTED action
#   hybrid : w*timer + (1-w)*action, both normalised so a 10 act/min goal-runner pays the same base cost
# Food value 20. All rates parameterised.
T_RATE, A_RATE, FOOD = 1.0, 0.1, 20.0

def cost(model, minutes, counted, w=0.2):
    t, a = T_RATE * minutes, A_RATE * counted
    return {"timer": t, "action": a, "hybrid": w * t + (1 - w) * a}[model] / FOOD

def play(goal, moves, apm):  # goal actions, non-goal moves, total actions/min
    minutes = (goal + moves) / apm
    return minutes

checks = []
# S1 reproduce kernel: same 100 goal actions, explorer 2/min vs speedrunner 10/min, only goal actions exist
ex, sp = play(100, 0, 2), play(100, 0, 10)
r = {m: cost(m, ex, 100) / cost(m, sp, 100) for m in ("timer", "action")}
r["hybrid"] = cost("hybrid", ex, 100) / cost("hybrid", sp, 100)
print("S1 same-goal ratios", {k: round(v, 2) for k, v in r.items()})
checks.append(abs(r["timer"] - 5.0) < 1e-9 and abs(r["action"] - 1.0) < 1e-9 and abs(r["hybrid"] - 1.8) < 1e-9)

# S2 idler: 10 idle minutes, zero actions
idle = {m: cost(m, 10, 0) for m in ("timer", "action", "hybrid")}
print("S2 idler cost/10min", idle)
checks.append(idle["action"] == 0 and abs(idle["hybrid"] - 0.1) < 1e-9)

# S3 BREAK: explorer also makes 300 non-goal moves (walking/looking) at 10 act/min; speedrunner makes none.
# If every action is counted, the 'neutral' action meter taxes exploration by movement.
ex3 = play(100, 300, 10); sp3 = play(100, 0, 10)
all_counted = cost("action", ex3, 400) / cost("action", sp3, 100)
print("S3 action-meter ratio when ALL actions counted:", round(all_counted, 2))
checks.append(abs(all_counted - 4.0) < 1e-9)  # neutrality fails: 4x penalty

# S4 fix attempt: count goal actions only -> exploration free again, but a pure wanderer (0 goal, 400 moves) pays nothing
goal_only = cost("action", ex3, 100) / cost("action", sp3, 100)
wander = cost("action", play(0, 400, 10), 0)
print("S4 goal-only ratio", round(goal_only, 2), "wanderer cost", wander)
checks.append(goal_only == 1.0 and wander == 0.0)

# S5 hybrid on goal-only counting: sweep timer weight, find window where explorer ratio<=2 AND wanderer cost >= 0.05 food
ok = []
for wi in range(0, 101, 5):
    w = wi / 100
    ratio = cost("hybrid", ex3, 100, w) / cost("hybrid", sp3, 100, w)
    wcost = cost("hybrid", play(0, 400, 10), 0, w)
    if ratio <= 2.0 and wcost >= 0.05: ok.append(w)
print("S5 feasible timer weights (ratio<=2, wanderer>=0.05):", ok)
kernel_band = [w for w in (0.1, 0.2) if w in ok]
print("S5 kernel's 10-20% band still feasible:", kernel_band)
checks.append(kernel_band == [0.1, 0.2])  # band survives under goal-only counting
print("RESULT: %s kernel numbers reproduce (5.0/1.0/1.8, idler 0.1); neutrality breaks when all actions count (4.0x); goal-only counting frees pure wanderers (0.0) but a hybrid band %s (incl. 10-20%%) restores both limits" % ("PASS" if all(checks) else "FAIL", ok))
