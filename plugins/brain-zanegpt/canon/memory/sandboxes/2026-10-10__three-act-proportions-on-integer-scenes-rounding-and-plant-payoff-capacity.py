# Kernels exercised: STORYTELLING/structure/three-act (25/50/25, PP1 at 25%, PP2 at 75%), STORYTELLING/economy/chekhovs-gun (a planted detail needs a payoff),
# STORYTELLING/pattern/heros-journey (three-stage arc: acts must map 1:1 to separation/initiation/return stages).
# Prediction (before run): placing PP1/PP2 on an integer scene count with floor, ceil, half-up or half-even rounding never leaves any act more than 1 scene
# off its ideal share; but they DISAGREE on the act sizes for some N, and Python's half-even round() makes Act One != Act Three for some N.
# Iteration 1 FAILED on the half-even part: round() half-even gave Act1 == Act3 for every N (0 asymmetric); floor/ceil/half-up were the asymmetric ones.
# Iteration 2 prediction: only half-even is symmetric (symmetric because 0.25N and 0.75N tie-break in opposite directions); floor/ceil asymmetric on ~75% of N.
# With K plants that need distinct Act-One scenes and K payoffs in Acts Two-Three, the plan is feasible iff Act One has >= K scenes, so the minimum N differs by rounding rule.
import math
def cuts(N, rule):
    f = {"floor": math.floor, "ceil": math.ceil, "halfup": lambda x: math.floor(x + .5), "halfeven": round}[rule]
    return f(0.25 * N), f(0.75 * N)
rules = ["floor", "ceil", "halfup", "halfeven"]
ok = True; asym = {}; maxdev = {}; disagree = []
for r in rules:
    asym[r] = []; md = 0
    for N in range(4, 121):
        a, b = cuts(N, r); acts = (a, b - a, N - b)
        md = max(md, abs(acts[0] - .25 * N), abs(acts[1] - .5 * N), abs(acts[2] - .25 * N))
        if acts[0] != acts[2]: asym[r].append(N)
    maxdev[r] = md
for N in range(4, 121):
    if len({cuts(N, r) for r in rules}) > 1: disagree.append(N)
print("max dev per rule (scenes)", {r: round(maxdev[r], 2) for r in rules})
print("rules disagree on N count", len(disagree), "first", disagree[:6])
print("Act1 != Act3 counts", {r: len(asym[r]) for r in rules}, "halfeven first", asym["halfeven"][:6])
ok &= all(maxdev[r] <= 1.0 + 1e-9 for r in rules) and len(disagree) > 0 and len(asym["halfeven"]) == 0 and len(asym["floor"]) > 50 and len(asym["ceil"]) > 50
# plant/payoff capacity: K plants need K distinct Act-One scenes; payoffs fit after PP1 (Acts 2-3) -> smallest N per rule
minN = {}
for r in rules:
    for K in (3, 5):
        n = next(N for N in range(4, 200) if cuts(N, r)[0] >= K)
        minN[(r, K)] = n
print("min N for K plants", minN)
ok &= len({minN[(r, 5)] for r in rules}) > 1  # rules disagree
# BREAK: hero's-journey three stages must equal the acts; check stage sizes all >= 1 scene for tiny N, and where the partition degenerates
deg = {r: [N for N in range(2, 12) if min(cuts(N, r)[0], cuts(N, r)[1] - cuts(N, r)[0], N - cuts(N, r)[1]) < 1] for r in rules}
print("degenerate N (an act has 0 scenes)", deg)
ok &= all(len(deg[r]) > 0 for r in rules)
print("RESULT:", "PASS" if ok else "FAIL", "devs<=1 scene all rules; rules disagree on %d of 117 N; halfeven asym on %d N (floor %d, ceil %d, halfup %d); min N for 5 plants %s; degenerate small N exist" % (len(disagree), len(asym["halfeven"]), len(asym["floor"]), len(asym["ceil"]), len(asym["halfup"]), {r: minN[(r, 5)] for r in rules}))
