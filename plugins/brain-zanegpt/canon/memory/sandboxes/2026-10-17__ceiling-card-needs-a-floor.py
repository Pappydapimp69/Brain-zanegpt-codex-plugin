# Two-sided benign-violation band: a beat is funny iff D-3 <= severity <= D (severe harm needs distance, mild harm needs closeness).
# Cards: none; ceiling only (clamp s<=D, the harm-ceiling card); band (clamp s into [D-3, D]).
# Prediction (before run): at low distance D=3 the ceiling card is enough (band share within 0.05 of ceiling share) but at D=9
# the ceiling-only card scores <=0.55 funny share while the band card scores >=0.85; averaged over D=3..9 the band card beats
# ceiling by >=20 share points. Hidden assumption: mild beats at high distance are really unfunny (needs a floor).
# Break: a writer who states the band on the wrong side (floor D-3 -> D-6) should lose the gain.
import random
def share(D, mode, N=500, seed=11, wide=3, n=8):
    rng = random.Random(seed); f = 0
    for _ in range(N):
        for t in range(n):
            s = max(1, min(10, round(1 + t * 1.2 + rng.uniform(-2, 2))))
            if mode == "ceil": s = min(s, D)
            elif mode == "band": s = min(max(s, D - wide), D)
            elif mode == "wrongband": s = min(max(s, D - 2 * wide), D)
            if D - wide <= s <= D: f += 1
    return f / (N * n)
Ds = range(3, 10)
tab = {m: [share(D, m) for D in Ds] for m in ("none", "ceil", "band", "wrongband")}
for m, v in tab.items(): print(m, ["%.2f" % x for x in v])
avg = {m: sum(v) / len(v) for m, v in tab.items()}
lowgap = abs(tab["band"][0] - tab["ceil"][0]); c9, b9 = tab["ceil"][-1], tab["band"][-1]
print("avg", {k: round(x, 3) for k, x in avg.items()})
ok = lowgap <= 0.05 and c9 <= 0.55 and b9 >= 0.85 and avg["band"] - avg["ceil"] >= 0.20 and avg["wrongband"] < avg["band"] - 0.10
print("RESULT:", "PASS" if ok else "FAIL", "D=3 gap %.2f; D=9 ceil %.2f vs band %.2f; avg band %.2f ceil %.2f none %.2f wrongband %.2f" % (lowgap, c9, b9, avg["band"], avg["ceil"], avg["none"], avg["wrongband"]))
