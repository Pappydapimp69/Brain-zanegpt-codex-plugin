import itertools, math
# Prediction (before run): 1D/2D points spaced 0.9*EPS apart chain a~b~c with a!~c.
# Cell size EPS/2 misses some within-EPS pairs in the 3x3 block; cell size EPS finds all
# pairs (like brute force); greedy keep-first dedupe through a correct hash still gives
# different survivor counts for different insertion orders (2 vs 3).
EPS = 1.0
pts = [(0.0, 0.0), (0.9, 0.0), (1.8, 0.0), (2.7, 0.0), (3.6, 0.0)]
def close(a, b): return math.hypot(a[0]-b[0], a[1]-b[1]) <= EPS
brute = {(i, j) for i, j in itertools.combinations(range(len(pts)), 2) if close(pts[i], pts[j])}
def hash_pairs(cell):
    g = {}
    for i, p in enumerate(pts):
        g.setdefault((math.floor(p[0]/cell), math.floor(p[1]/cell)), []).append(i)
    out = set()
    for i, p in enumerate(pts):
        cx, cy = math.floor(p[0]/cell), math.floor(p[1]/cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in g.get((cx+dx, cy+dy), []):
                    if j != i and close(p, pts[j]): out.add((min(i, j), max(i, j)))
    return out
small = hash_pairs(EPS/2); full = hash_pairs(EPS)
print("brute", len(brute), "cell=EPS/2", len(small), "cell=EPS", len(full))
def dedupe(order, cell):
    kept = []
    for i in order:
        if not any(close(pts[i], pts[k]) for k in kept): kept.append(i)
    return len(kept)
n_fwd = dedupe([0, 1, 2, 3, 4], EPS); n_mid = dedupe([1, 3, 0, 2, 4], EPS)
print("survivors fwd", n_fwd, "scrambled", n_mid)
ok = len(small) < len(brute) and full == brute and n_fwd != n_mid
print("RESULT: %s brute=%d small-cell=%d eps-cell=%d (all found) survivors %d vs %d by insertion order"
      % ("PASS" if ok else "FAIL", len(brute), len(small), len(full), n_fwd, n_mid))
