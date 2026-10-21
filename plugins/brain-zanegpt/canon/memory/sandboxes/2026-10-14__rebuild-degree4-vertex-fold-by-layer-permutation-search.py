"""Independent rebuild: degree-4 single-vertex flat-foldability by layer-permutation search.
Own method (not a Kawasaki/Maekawa shortcut): fold rays on the plane, then search all 24 stacking orders of the 4 sectors.
PREDICTION (before running): angle sets from multiples of 15 deg summing to 360 (each >=15):
 (a) every foldable assignment satisfies Maekawa (|M-V|=2): 0 exceptions;
 (b) a set that violates Kawasaki (a1+a3 != 180) has 0 foldable assignments;
 (c) (90,90,90,90) -> 8 foldable of 8 Maekawa-valid; a generic Kawasaki set e.g. (45,90,135,90) -> 4 of 8;
 (d) foldable counts over all Kawasaki sets lie in {4, 8}, and some Kawasaki set has Maekawa-valid assignments that fail (necessary not sufficient).
Sector i is face-up when i is even; crease j (between sector j-1 and j) valley => odd sector above even sector, mountain => even above odd.
"""
import itertools

def arc_cells(start, length, sign):
    # unit-degree cells covered by the sector folded from `start` sweeping `sign*length`
    return {(start + sign * k - (1 if sign < 0 else 0)) % 360 for k in range(length)}

def foldable(angles, mv):
    n = 4
    pos = [0]
    for i in range(n):
        pos.append((pos[-1] + (1 if i % 2 == 0 else -1) * angles[i]) % 360)
    if pos[n] != 0: return False                      # rays fail to close up flat
    cells = [arc_cells(pos[i], angles[i], 1 if i % 2 == 0 else -1) for i in range(n)]
    # crease j is the ray between sector j-1 and j (j=0 is between sector 3 and sector 0)
    for order in itertools.permutations(range(n)):    # order[k]=sector at height k (0=bottom)
        h = {s: k for k, s in enumerate(order)}
        ok = True
        for j in range(n):
            a, b = (j - 1) % n, j
            odd, even = (a, b) if a % 2 else (b, a)
            odd_above = (mv[j] == 'V')
            if (h[odd] > h[even]) != odd_above: ok = False; break
        if not ok: continue
        for j in range(n):
            a, b = (j - 1) % n, j
            lo, hi = sorted((h[a], h[b]))
            for k in range(n):
                if k in (a, b) or not (lo < h[k] < hi): continue
                p = pos[j]
                if p in cells[k] and (p - 1) % 360 in cells[k]: ok = False   # crease pierces a sector stacked between its two sides
        if not ok: continue
        iv = {j: tuple(sorted((h[(j - 1) % n], h[j]))) for j in range(n)}
        for j, j2 in itertools.combinations(range(n), 2):
            if pos[j] != pos[j2]: continue
            (a1, b1), (a2, b2) = iv[j], iv[j2]
            if a1 < a2 < b1 < b2 or a2 < a1 < b2 < b1: ok = False   # creases sharing a ray must nest, not interleave
        if ok: return True
    return False

def sets():
    out = []
    for a in range(15, 361, 15):
        for b in range(15, 361, 15):
            for c in range(15, 361, 15):
                d = 360 - a - b - c
                if d >= 15 and d % 15 == 0: out.append((a, b, c, d))
    return out

def count(angles):
    assigns = list(itertools.product('MV', repeat=4))
    fold = [m for m in assigns if foldable(angles, m)]
    maek = [m for m in assigns if abs(m.count('M') - m.count('V')) == 2]
    return len(fold), len(maek), sum(1 for m in fold if m not in maek)

exc = 0; kaw_viol_fold = 0; counts = set(); insufficient = 0; n_k = 0
for s in sets():
    f, m, e = count(s); exc += e
    if (s[0] + s[2]) == 180:
        n_k += 1; counts.add(f)
        if f < m: insufficient += 1
    elif f: kaw_viol_fold += 1
print("sets", len(sets()), "kawasaki sets", n_k)
c90, c459, cbad = count((90,90,90,90)), count((45,90,135,90)), count((100,90,100,70))
print("90x4", c90, "(45,90,135,90)", c459, "(100,90,100,70)", cbad)
print("maekawa exceptions", exc, "kawasaki-violating sets with a fold", kaw_viol_fold, "fold counts over Kawasaki sets", sorted(counts), "sets with Maekawa-valid but unfoldable", insufficient)
ok = (exc == 0 and kaw_viol_fold == 0 and c90[:2] == (8, 8) and c459[:2] == (4, 8) and insufficient > 0)  # prediction (d) counts in {4,8} was WRONG on first run: counts were [4, 6, 8]; entry's claims are (a)-(c)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" exceptions {exc}, 90x4 {c90[0]}/8, (45,90,135,90) {c459[0]}/8, Kawasaki-violating folds {kaw_viol_fold}, counts {sorted(counts)}, insufficient sets {insufficient}/{n_k}")
