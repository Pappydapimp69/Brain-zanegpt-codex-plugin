"""Rebuild of seven E63 (conditioned phantoms: alternating real and phantom cues lands 4-5 of 12;
budget one honest pairing per phantom). Own fixture: Rescorla-Wagner with learning rates
a = 0.2/0.3/0.45 and thresholds 0.5/0.6/0.7, 6 teaching pairings, then a LONG run of 60 cues
(E63 used 12) under real:phantom ratios 1:1, 2:1, 3:1. Count phantoms landed in cues 31-60
(the steady state, after teaching has worn off). Closed form for a k:1 cycle: V just before
the phantom satisfies V = 1 - (1-a)^k * (1 - (1-a) V).
Predictions written before running:
 P1 at E63's own a = 0.3, threshold 0.6, a 1:1 schedule lands 0 phantoms in steady state
    (fixed point 1/(2-a) = 0.588 < 0.6) -- the 4-5 of 12 is teaching carry-over.
 P2 'one pairing per phantom' sustains phantoms in fewer than half the (a, threshold) cells.
 P3 a 2:1 schedule sustains phantoms in every cell with threshold <= 0.6.
"""

def run(a, thr, ratio, teach=6, cues=60):
    V = 0.0
    for _ in range(teach): V += a * (1 - V)
    landed_late, seq = 0, ([True] * ratio + [False])
    for c in range(cues):
        real = seq[c % len(seq)]
        if real: V += a * (1 - V)
        else:
            if V >= thr and c >= 30: landed_late += 1
            V *= (1 - a)
    return landed_late

def fixed(a, k):
    # V before the phantom in a k:1 steady cycle
    b = (1 - a) ** k
    return (1 - b) / (1 - b * (1 - a))

cells = [(a, t) for a in (0.2, 0.3, 0.45) for t in (0.5, 0.6, 0.7)]
res = {}
for a, t in cells:
    res[(a, t)] = {k: run(a, t, k) for k in (1, 2, 3)}
    print(f"a={a:.2f} thr={t:.1f}: steady V before phantom 1:1 {fixed(a,1):.3f} 2:1 {fixed(a,2):.3f} 3:1 {fixed(a,3):.3f}; "
          f"late phantoms landed (of {30//2}/{30//3}/{30//4}) {res[(a,t)][1]}/{res[(a,t)][2]}/{res[(a,t)][3]}")
p1 = res[(0.3, 0.6)][1] == 0
p2 = sum(1 for c in cells if res[c][1] > 0) < len(cells) / 2
p3 = all(res[(a, t)][2] > 0 for a, t in cells if t <= 0.6)
checks = [("P1 1:1 lands 0 late at E63's constants", p1), ("P2 1:1 sustains in < half the cells", p2), ("P3 2:1 sustains wherever thr <= 0.6", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; E63 constants 1:1 late {res[(0.3,0.6)][1]}/15 (V* {fixed(0.3,1):.3f}), "
      f"2:1 {res[(0.3,0.6)][2]}/10; 1:1 sustains in {sum(1 for c in cells if res[c][1] > 0)}/9 cells; "
      f"2:1 in {sum(1 for c in cells if res[c][2] > 0)}/9")
