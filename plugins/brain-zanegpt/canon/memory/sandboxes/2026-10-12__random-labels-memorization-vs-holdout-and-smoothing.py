"""Prediction (before run): a high-capacity memorizer (1-nearest-neighbour) reaches 100% train accuracy on hash-derived
RANDOM labels but ~50% (45-55%) on a held-out set; on a learnable rule (sign of x0+x1) with 10% label noise it has train
100% and test ~ 0.80-0.90; a smoothed version (k=15 neighbours, the capacity-control analogue of dropout/regularization)
raises test accuracy over k=1 on the noisy rule by >=4 points and fits random labels LESS (train < 100%). With a tiny
one-region training set (3 points, as in brain/E116's 3-query judgment list) train is 100% yet held-out falls to the base
rate. BREAK: smoothing must not rescue random labels (test stays ~50%).
No RNG: points and labels come from sha256 of (seed, index)."""
import hashlib, math
def u(seed, i, j):
    h = hashlib.sha256(f"{seed}:{i}:{j}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 2**32
def pts(seed, n): return [(u(seed, i, 0) * 2 - 1, u(seed, i, 1) * 2 - 1) for i in range(n)]
def rand_lab(seed, n): return [int(u(seed, i, 9) < .5) for i in range(n)]
def rule_lab(P, seed, noise=.1):
    return [int((x + y) > 0) ^ int(u(seed, i, 7) < noise) for i, (x, y) in enumerate(P)]
def knn(Ptr, Ytr, p, k):
    d = sorted(range(len(Ptr)), key=lambda i: ((Ptr[i][0]-p[0])**2 + (Ptr[i][1]-p[1])**2, i))[:k]
    return int(sum(Ytr[i] for i in d) * 2 > k)
def acc(Ptr, Ytr, P, Y, k): return sum(knn(Ptr, Ytr, p, k) == y for p, y in zip(P, Y)) / len(P)
# leave-self-in train accuracy: a point is its own nearest neighbour
tr, te = pts(1, 200), pts(2, 400)
out = {}
# S1 random labels
yr, yt = rand_lab(11, 200), rand_lab(12, 400)
out["rand_k1"] = (acc(tr, yr, tr, yr, 1), acc(tr, yr, te, yt, 1))
out["rand_k15"] = (acc(tr, yr, tr, yr, 15), acc(tr, yr, te, yt, 15))
# S2 noisy rule; test labels clean-rule (noise 0) as truth
ys, yst = rule_lab(tr, 21), rule_lab(te, 22, 0.0)
out["rule_k1"] = (acc(tr, ys, tr, ys, 1), acc(tr, ys, te, yst, 1))
out["rule_k15"] = (acc(tr, ys, tr, ys, 15), acc(tr, ys, te, yst, 15))
# S3 tiny one-region training set: 3 points all in x>0,y>0 quadrant with label 1; test spans the plane, rule truth
tiny = [(0.3, 0.4), (0.5, 0.2), (0.6, 0.7)]; yt3 = [1, 1, 1]
out["tiny"] = (acc(tiny, yt3, tiny, yt3, 1), acc(tiny, yt3, te, yst, 1))
for k, v in out.items(): print(k, "train %.3f test %.3f" % v)
base = sum(yst) / len(yst)
ok = (out["rand_k1"][0] == 1.0 and .45 <= out["rand_k1"][1] <= .55
      and out["rule_k1"][0] == 1.0 and .80 <= out["rule_k1"][1] <= .90
      and out["rule_k15"][1] - out["rule_k1"][1] >= .04
      and out["rand_k15"][0] < 1.0 and .45 <= out["rand_k15"][1] <= .55
      and out["tiny"][0] == 1.0 and abs(out["tiny"][1] - max(base, 1 - base)) > 0.0 and out["tiny"][1] <= .60)
print("RESULT:", "PASS" if ok else "FAIL", "random labels k1 train %.2f test %.2f; noisy rule k1 test %.2f -> k15 test %.2f; k15 random train %.2f test %.2f; tiny-set train %.2f test %.2f (class share %.2f)"
      % (out["rand_k1"] + (out["rule_k1"][1], out["rule_k15"][1]) + out["rand_k15"] + out["tiny"] + (base,)))
