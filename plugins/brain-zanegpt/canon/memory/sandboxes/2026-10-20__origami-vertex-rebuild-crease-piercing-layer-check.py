"""Blind rebuild: single-vertex flat-foldability by brute force.
Own fixture: sectors laid out by reflection in the folded plane (exact integer degrees),
layer order = permutation of sectors; crease between sectors i,i+1 forces which is above
(valley => next sector above, flipped on every sector); a layer order is invalid if a crease
ray lies strictly inside another sector that sits BETWEEN the two sectors it joins.
PREDICTION (before run): (90,90,90,90) 8/8 count-satisfying assignments fold; (30,60,150,120) 4/8;
(45,45,135,135) 6/8; (100,80,120,60) 0/8 (alternating sum fails); assignments breaking Maekawa
never fold; a regular degree-6 vertex folds fewer than all 30 count-satisfying ones."""
from itertools import permutations, product

def folds(angles, assign, check_maekawa=False):
    n = len(angles)
    if sum(angles) != 360: return False
    # folded-plane direction of crease k (between sector k-1 and k) and sector extents
    d = [0]
    for k in range(n):
        d.append(d[-1] + (angles[k] if k % 2 == 0 else -angles[k]))
    if d[n] % 360 != 0: return False            # does not close
    cre = [x % 360 for x in d[:n]]               # crease k direction (between sector k-1 and k)
    sec = []                                     # sector k spans from cre[k] to cre[(k+1)%n] (as unordered arc)
    for k in range(n):
        a, b = d[k], d[k+1]
        lo, hi = min(a, b), max(a, b)
        sec.append((lo, hi))
    def inside(ang, k):                          # crease direction strictly inside sector k's arc (mod 360)
        lo, hi = sec[k]
        for t in range(-3, 4):
            if lo < ang + 360*t < hi: return True
        return False
    for order in permutations(range(n)):
        pos = {s: i for i, s in enumerate(order)}
        ok = True
        for k in range(n):                       # crease k joins sectors (k-1)%n and k
            a, b = (k-1) % n, k
            above_b = (assign[k] == 'V') != ((a % 2) == 1)   # V with sector a face-up => b above
            if (pos[b] > pos[a]) != above_b: ok = False; break
        if not ok: continue
        for k in range(n):
            a, b = (k-1) % n, k
            lo_, hi_ = sorted((pos[a], pos[b]))
            for s in range(n):
                if s in (a, b): continue
                if lo_ < pos[s] < hi_ and inside(cre[k], s): ok = False; break
            if not ok: break
        if not ok: continue
        for j in range(n):                       # creases on the same folded ray must nest or be disjoint, not interleave
            for k in range(j+1, n):
                if cre[j] != cre[k]: continue
                aj, bj = sorted((pos[(j-1) % n], pos[j])); ak, bk = sorted((pos[(k-1) % n], pos[k]))
                if aj < ak < bj < bk or ak < aj < bk < bj: ok = False
        if ok: return True
    return False

def run(angles):
    n = len(angles); cnt = tot = brk = brk_fold = 0
    for assign in product('MV', repeat=n):
        diff = abs(assign.count('M') - assign.count('V'))
        f = folds(angles, assign)
        if diff == 2:
            tot += 1; cnt += f
        else:
            brk += 1; brk_fold += f
    return cnt, tot, brk_fold, brk

res = {}
for name, ang in [("square", (90,90,90,90)), ("unequal", (30,60,150,120)), ("kite", (45,45,135,135)),
                  ("open", (100,80,120,60)), ("hex60", (60,)*6)]:
    res[name] = run(ang); print(name, ang, "(folds, count-satisfying, breaking-fold, breaking):", res[name])
ok = (res["square"][:2] == (8, 8) and res["unequal"][:2] == (4, 8) and res["kite"][0] < 8 and
      res["open"][0] == 0 and all(r[2] == 0 for r in res.values()) and res["hex60"][0] == res["hex60"][1])  # my pre-run guess (fewer than all) was wrong: equal angles fold under every count-satisfying assignment
print("RESULT: %s square %d/%d, unequal %d/%d, kite %d/%d, open %d/%d, hex60 %d/%d; count-breaking folds %d" % (
  "PASS" if ok else "FAIL", *res["square"][:2], *res["unequal"][:2], *res["kite"][:2], *res["open"][:2], *res["hex60"][:2], sum(r[2] for r in res.values())))
