# Band card (floor+ceiling) vs ceiling-only card when the STATED distance is off by e from the true distance D.
# Funny iff D-3 <= s <= D. Prediction (before run): at e=0 band=1.00 > ceiling; at |e|=2 band falls to <=0.75 and the ceiling-only card
# falls less (its error only matters when stated > D); at e=+2 the two are within 0.10; at |e|>=4 band = 0.00 (zero overlap) while
# ceiling-only stays >=0.30 for e=-4 (understated). So band is NOT uniformly better: crossover at |e|~2. Hidden assumption: the writer's
# error is symmetric. Break: e=-4 understated: ceiling-only should beat band.
import random
def share(D, e, mode, N=400, seed=5, n=8, w=3):
    rng = random.Random(seed); S = D + e; f = 0
    for _ in range(N):
        for t in range(n):
            s = max(1, min(10, round(1 + t * 1.2 + rng.uniform(-2, 2))))
            s = min(s, S) if mode == "ceil" else min(max(s, S - w), S)
            f += D - w <= s <= D
    return f / (N * n)
D = 7
tab = {e: (share(D, e, "ceil"), share(D, e, "band")) for e in (-4, -3, -2, -1, 0, 1, 2, 3, 4)}
for e, (c, b) in tab.items(): print("e=%+d ceil %.2f band %.2f" % (e, c, b))
c0, b0 = tab[0]; c2, b2 = tab[2]; cm4, bm4 = tab[-4]; c4, b4 = tab[4]
ok = b0 > c0 and b2 <= 0.75 and abs(b2 - c2) <= 0.10 + 1e-9 and b4 == 0 and cm4 >= 0.30 and cm4 > bm4
print("RESULT:", "PASS" if ok else "FAIL", "D=7: e=0 band %.2f ceil %.2f; e=+2 band %.2f ceil %.2f; e=-4 band %.2f ceil %.2f; e=+4 band %.2f ceil %.2f" % (b0, c0, b2, c2, bm4, cm4, b4, c4))
