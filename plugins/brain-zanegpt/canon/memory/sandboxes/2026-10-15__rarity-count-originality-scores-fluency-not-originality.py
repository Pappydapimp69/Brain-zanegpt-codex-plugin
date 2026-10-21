"""Pass 4 sandbox (Ideation & originality): statistical-infrequency originality scoring.
Deterministic (seeded random.Random), stdlib only.
Idea universe: 300 categories, Zipf weights (s=1.1). Each respondent has a fluency F
(number of distinct ideas) and a hidden originality trait theta in [0,1]; they draw
ideas without replacement with weights p_k ** (1 - 0.8*theta) (high theta flattens
toward rare ideas). Scores computed against the pool's own frequencies:
  count5   : number of ideas given by <= 5% of the pool (Torrance-style rarity count)
  meanrar  : mean over the respondent's ideas of (1 - share of pool giving it)
  top2     : mean rarity of the respondent's two rarest ideas
"""
import random, math

K = 300
ZIPF = [1 / (k + 1) ** 1.1 for k in range(K)]

def respondent(rng, F, theta):
    w = [p ** (1 - 0.8 * theta) for p in ZIPF]
    chosen = set()
    while len(chosen) < F:
        r = rng.random() * sum(w[k] for k in range(K) if k not in chosen)
        acc = 0.0
        for k in range(K):
            if k in chosen:
                continue
            acc += w[k]
            if acc >= r:
                chosen.add(k); break
    return chosen

def pool(seed, n, corr=0.0):
    rng = random.Random(seed)
    people = []
    for _ in range(n):
        z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
        theta = 1 / (1 + math.exp(-z1))
        zf = corr * z1 + math.sqrt(1 - corr * corr) * z2
        F = max(2, min(25, round(11 + 5 * zf)))
        people.append((F, theta, respondent(rng, F, theta)))
    return people

def scores(people, ref=None):
    ref = ref if ref is not None else people
    n = len(ref)
    freq = {}
    for _, _, ideas in ref:
        for k in ideas:
            freq[k] = freq.get(k, 0) + 1
    out = []
    for F, th, ideas in people:
        share = [freq.get(k, 0) / n for k in ideas]
        rar = sorted(1 - s for s in share)
        count5 = sum(1 for s in share if s <= 0.05)
        out.append((F, th, count5, sum(rar) / len(rar), (rar[-1] + rar[-2]) / 2))
    return out

def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return 0.0  # constant score (saturated): carries no ranking information
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)

def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for t in range(i, j + 1):
            r[order[t]] = (i + j) / 2
        i = j + 1
    return r

def spearman(a, b):
    return pearson(ranks(a), ranks(b))

def report(tag, sc):
    F = [s[0] for s in sc]; th = [s[1] for s in sc]
    res = {}
    for name, idx in (('count5', 2), ('meanrar', 3), ('top2', 4)):
        v = [s[idx] for s in sc]
        res[name] = (pearson(v, F), pearson(v, th))
        print(f"{tag:22s} {name:8s} r(fluency) {res[name][0]:+.2f}  r(theta) {res[name][1]:+.2f}")
    return res

def avg(tag, n, seeds, corr=0.0):
    acc = {}
    for sd in seeds:
        sc = scores(pool(sd, n, corr))
        F = [x[0] for x in sc]; th = [x[1] for x in sc]
        for name, idx in (('count5', 2), ('meanrar', 3), ('top2', 4)):
            v = [x[idx] for x in sc]
            a = acc.setdefault(name, [0.0, 0.0, 1.0])
            rf, rt = pearson(v, F), pearson(v, th)
            a[0] += rf / len(seeds); a[1] += rt / len(seeds); a[2] = min(a[2], rt)
    for name, (rf, rt, mn) in acc.items():
        print(f"{tag:22s} {name:8s} mean r(fluency) {rf:+.2f}  mean r(theta) {rt:+.2f}  min r(theta) {mn:+.2f}")
    return {k: (v[0], v[1]) for k, v in acc.items()}

def main():
    big = pool(7, 200)
    report('seed 7 n=200', scores(big))
    # same first 20 people scored inside a 20-person pool vs inside the 200 pool
    small = big[:20]
    s20 = scores(small); s200 = scores(small, ref=big)
    rho_count = spearman([s[2] for s in s20], [s[2] for s in s200])
    rho_mean = spearman([s[3] for s in s20], [s[3] for s in s200])
    zero20 = sum(1 for s in s20 if s[2] == 0)
    print(f"20 people, own-pool vs 200-pool ranking: count5 spearman {rho_count:.2f}, meanrar spearman {rho_mean:.2f}; "
          f"count5 in 20-pool counts only unique ideas (5% of 20 = 1 person); people scoring 0 there: {zero20}/20")
    r200 = avg('n=200 x10 seeds', 200, range(100, 110))
    r20 = avg('n=20 x10 seeds', 20, range(200, 210))
    rc = avg('n=200 corr 0.5 x10 (break)', 200, range(300, 310), corr=0.5)
    ok = (r200['count5'][0] >= 0.6 and r200['count5'][1] < r200['count5'][0]
          and r200['meanrar'][1] >= 0.6 and abs(r200['meanrar'][0]) <= 0.2
          and rho_count < 0.8 and rc['count5'][1] >= 0.5)
    print(f"RESULT: {'PASS' if ok else 'FAIL'} n=200 mean of 10 seeds: rarity count r(fluency) {r200['count5'][0]:+.2f} vs r(originality) "
          f"{r200['count5'][1]:+.2f}; mean rarity r(fluency) {r200['meanrar'][0]:+.2f} vs r(originality) {r200['meanrar'][1]:+.2f}; "
          f"top2 {r200['top2'][0]:+.2f}/{r200['top2'][1]:+.2f}; 20-pool vs 200-pool count ranking spearman {rho_count:.2f} "
          f"(mean rarity {rho_mean:.2f}); n=20 pools mean rarity r(originality) {r20['meanrar'][1]:+.2f}; break corr 0.5: count r(originality) {rc['count5'][1]:+.2f}")

if __name__ == '__main__':
    main()
