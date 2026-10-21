# Origami single-vertex flat-foldability by brute force. Sectors s_0..s_{n-1} with angles a_i (sum 360) are
# separated by creases c_i (between s_{i-1} and s_i, c_0 between s_{n-1} and s_0). Fold flat: folded crease
# directions f_0=0, f_{i+1}=f_i +/- a_i alternating; it closes only if f_n = 0 mod 360 (Kawasaki's theorem).
# Layering: sector i faces up if i is even. At a valley (seen from the top) the face-down sector of the pair
# lies ABOVE the face-up one, at a mountain below. A sector whose folded span strictly covers a crease
# direction may not sit between the two sectors of that crease. Creases folded onto the same ray must nest (no interleaved layer intervals).
# Exhaustive over M/V assignments and layer orders.
# PREDICTION (before run): a 90-degree degree-4 vertex folds in all 8 of the 8 assignments with |M-V|=2 and in none
# of the other 8; for the unequal Kawasaki vertex (30,60,150,120) fewer than all 8 Maekawa-count assignments
# fold (I expect 6 of 8 to 4 of 8), and no assignment violating |M-V|=2 ever folds on any tested vertex.
import itertools
def folded(angles):
    f = [0]; sgn = 1
    for a in angles:
        f.append((f[-1] + sgn * a) % 360); sgn = -sgn
    return f
def closes(angles):
    return folded(angles)[-1] % 360 == 0
def covers(span, d):
    lo, hi, = span
    return lo < d < hi if lo <= hi else (d > lo or d < hi)   # span given as arc start->end ccw
def spans(angles):
    f = folded(angles); out = []
    for i, a in enumerate(angles):
        start, end = (f[i], f[i + 1]) if i % 2 == 0 else (f[i + 1], f[i])   # ccw arc from start to end
        out.append((start % 360, end % 360))
    return out, f
def arc_covers(span, d):
    s, e = span; d %= 360
    if s <= e: return s < d < e
    return d > s or d < e
def foldable(angles, mv):
    n = len(angles)
    if not closes(angles): return False
    sp, f = spans(angles)
    for order in itertools.permutations(range(n)):
        pos = {s: p for p, s in enumerate(order)}           # larger = higher
        ok = True
        for i in range(n):
            lo_s, hi_s = (i - 1) % n, i                    # crease i between s_{i-1} and s_i
            down = hi_s if hi_s % 2 == 1 else lo_s
            up = lo_s if down == hi_s else hi_s
            if (mv[i] == "V") != (pos[down] > pos[up]): ok = False; break
            a, b = sorted((pos[lo_s], pos[hi_s]))
            for t in range(n):
                if t in (lo_s, hi_s): continue
                if a < pos[t] < b and arc_covers(sp[t], f[i]): ok = False; break
            if not ok: break
        if ok:
            iv = [tuple(sorted((pos[(i - 1) % n], pos[i]))) for i in range(n)]   # layer interval of each crease
            for i in range(n):
                for j in range(i + 1, n):
                    if f[i] == f[j]:                       # creases folded onto the same ray must nest or be disjoint
                        (a1, b1), (a2, b2) = iv[i], iv[j]
                        if a1 < a2 < b1 < b2 or a2 < a1 < b2 < b1: ok = False
            if ok: return True
    return False
def census(angles):
    n = len(angles); res = {"maekawa_fold": 0, "maekawa_total": 0, "other_fold": 0}
    for mv in itertools.product("MV", repeat=n):
        m = mv.count("M"); v = n - m
        is_mae = abs(m - v) == 2
        fold = foldable(angles, mv)
        if is_mae:
            res["maekawa_total"] += 1; res["maekawa_fold"] += fold
        else:
            res["other_fold"] += fold
    return res
cases = {"square90": [90, 90, 90, 90], "unequal4": [30, 60, 150, 120], "unequal4b": [45, 45, 135, 135],
         "not_kawasaki": [100, 80, 120, 60], "deg6": [60] * 6}
out = {}
for name, a in cases.items():
    out[name] = census(a); print(name, a, "closes", closes(a), out[name])
ok = (out["square90"]["maekawa_fold"] == 8 and out["square90"]["other_fold"] == 0
      and out["not_kawasaki"]["maekawa_fold"] == 0
      and 4 <= out["unequal4"]["maekawa_fold"] < 8
      and all(v["other_fold"] == 0 for v in out.values()))
print(f"RESULT: {'PASS' if ok else 'FAIL'} Maekawa-count assignments that fold: " +
      ", ".join(f"{k} {v['maekawa_fold']}/{v['maekawa_total']}" for k, v in out.items()) +
      f"; folding assignments breaking |M-V|=2: {sum(v['other_fold'] for v in out.values())}")
