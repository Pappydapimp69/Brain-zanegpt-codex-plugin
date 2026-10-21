# Each video needs (a) a verbatim trope/axis label (closed list; paraphrase rate p is rejected) and (b) a name not within
# edit distance 1 of any earlier name in the batch. Count generations per accepted video for a 16-video batch.
import random
SYL = ["ba","ko","mi","ru","ta","ne","so","li","pu","ze","fa","do"]
def lev1(a, b):
    if a == b: return True
    if abs(len(a)-len(b)) > 1: return False
    if len(a) == len(b): return sum(x != y for x, y in zip(a, b)) <= 1
    s, l = (a, b) if len(a) < len(b) else (b, a)
    return any(l[:i]+l[i+1:] == s for i in range(len(l)))
def batch(rng, k, p, syl, use_label, use_name):
    names, draws = [], 0
    while len(names) < k:
        draws += 1
        if use_label and rng.random() < p: continue
        n = "".join(rng.choice(SYL) for _ in range(syl))
        if use_name and any(lev1(n, m) for m in names): continue
        names.append(n)
        if draws > 5000: break
    return draws / k
def mean(f, N=300): return sum(f(random.Random(i)) for i in range(N)) / N
rows = {}
for lab, (ul, un) in {"none": (0, 0), "label only": (1, 0), "name only": (0, 1), "both": (1, 1)}.items():
    rows[lab] = mean(lambda r: batch(r, 16, .3, 3, ul, un)); print("%-10s draws per video %.2f" % (lab, rows[lab]))
two = mean(lambda r: batch(r, 16, .3, 2, 1, 1)); print("both, 2-syllable names %.2f" % two)
pred = rows["label only"] * rows["name only"]
ok = rows["both"] > rows["label only"] and rows["both"] > rows["name only"] and abs(rows["both"] - pred) / pred < .15 and two > 2 * rows["both"]
print("RESULT: %s draws per video none %.2f label %.2f name %.2f both %.2f (product %.2f); 2-syllable both %.2f" % (
    "PASS" if ok else "FAIL", rows["none"], rows["label only"], rows["name only"], rows["both"], pred, two))
