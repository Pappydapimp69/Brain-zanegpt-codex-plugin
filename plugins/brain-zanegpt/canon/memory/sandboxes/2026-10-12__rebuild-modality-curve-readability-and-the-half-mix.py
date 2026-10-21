"""Blind rebuild of seven#E66 (sound-to-sight curve shape vs readable depth).
Own fixture: exact MI between 4 equal bands and the modalities of k episodes
(k = 1, 3, 6) for the claimed curves PLUS the Fix's two variants (chest-deep
0.30 and 0.70) and a sweep of the chest-deep value; checks 'avoid 50/50 at any
stage: it is the least readable point' and the Fix 'move it to ~0.30 or 0.70'."""
import math
def H(ps): return -sum(p * math.log2(p) for p in ps if p > 0)
def mi(curve, k=1):
    # sufficient statistic: number of visual episodes among k (binomial)
    nb = len(curve); joint = {}
    for b, q in enumerate(curve):
        for v in range(k + 1):
            joint[(b, v)] = (1 / nb) * math.comb(k, v) * q**v * (1 - q)**(k - v)
    pv = {}
    for (b, v), p in joint.items(): pv[v] = pv.get(v, 0) + p
    return H([1 / nb] * nb) + H(pv.values()) - H(joint.values())
C = {"linear": [0, 1/3, 2/3, 1], "step": [0, 0, 1, 1], "banded": [0, .1, .5, .9],
     "flat": [.45] * 4, "fix0.30": [0, .1, .3, .9], "fix0.70": [0, .1, .7, .9]}
for name, c in C.items():
    print(f"{name:8} MI k=1 {mi(c):.3f}  k=3 {mi(c,3):.3f}  k=6 {mi(c,6):.3f}   P(deep|visual) {(c[2]+c[3])/sum(c) if sum(c) else 0:.3f}  early visuals/20 {10*(c[0]+c[1])/2:.2f}")
sweep = [(x / 20, mi([0, .1, x / 20, .9])) for x in range(1, 20)]
worst = min(sweep, key=lambda t: t[1])
print("chest-deep sweep (k=1):", " ".join(f"{x:.2f}:{m:.3f}" for x, m in sweep))
print(f"least readable chest-deep value: {worst[0]:.2f} (MI {worst[1]:.3f}); 0.50 is {mi(C['banded']):.3f}")
arith = abs(mi(C['banded']) - 0.470) < 5e-4 and abs(mi(C['linear']) - 0.541) < 5e-4 and mi(C['flat']) < 1e-9
fix30 = mi(C['fix0.30']) > mi(C['banded'])
fix70 = mi(C['fix0.70']) > mi(C['banded'])
half_worst = abs(worst[0] - 0.5) < 1e-9
print(f"claimed numbers reproduce: {arith}; fix 0.30 helps: {fix30}; fix 0.70 helps: {fix70}; 0.50 is the least readable value: {half_worst}")
print(f"RESULT: {'PASS' if (arith and fix30 and fix70 and half_worst) else 'FAIL'} banded 0.470 / 0.30 -> {mi(C['fix0.30']):.3f} / 0.70 -> {mi(C['fix0.70']):.3f}; worst chest-deep value {worst[0]:.2f}")
