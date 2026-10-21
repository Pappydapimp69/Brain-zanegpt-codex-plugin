from itertools import combinations
TROPES, AXES, ENGINES, SKELS = 6, 5, 8, 2
KIT, FRESH = 10, 4            # 16 feature slots: kit 10, engine-skeleton 1, trope 1, fresh 4
def batch(R, axes, kit_rot=0):
    slots = [(e, s) for e in range(ENGINES) for s in range(SKELS)]      # 16 distinct engine-skeleton slots
    per = {t: 0 for t in range(TROPES)}; vids = []
    for i, es in enumerate(slots):                                       # greedy: cap per trope, distinct cells
        for t in range(TROPES):
            tt = (i + t) % TROPES
            if per[tt] < R and per[tt] < axes:
                cell = (tt, per[tt]); per[tt] += 1; vids.append((es, cell)); break
    return vids
def sim(vids, kit_rot):
    # kit slots identical except kit_rot rotated (assume rotated slots differ across all videos, pool large), fresh differ
    tot = 0; n = 0
    for a, b in combinations(range(len(vids)), 2):
        same = (KIT - kit_rot) + (vids[a][0] == vids[b][0]) + (vids[a][1][0] == vids[b][1][0])
        tot += same / (KIT + 2 + FRESH); n += 1
    return tot / n if n else 0
print("R size distinct-cells sim(kit fixed) sim(kit rot3)")
res = {}
for R in (1, 2, 3, 6):
    v = batch(R, AXES); cells = len({c for _, c in v})
    res[R] = (len(v), cells, sim(v, 0), sim(v, 3)); print(R, *[round(x, 4) if isinstance(x, float) else x for x in res[R]])
# mislabelled axis: treat borrowed-fame as duplicate of an existing axis -> only 4 distinct axes
res4 = {R: len(batch(R, 4)) for R in (1, 2, 3, 6)}
print("sizes with 4 usable axes", res4)
size_same = all(res4[R] == res[R][0] for R in (1, 2, 3))
# BREAK: shrink to 2 usable axes (a label error far bigger than one axis)
res2 = {R: len(batch(R, 2)) for R in (1, 2, 3, 6)}
print("sizes with 2 usable axes", res2)
d_sim = res[3][2] - res[1][2]; d_kit = res[3][2] - res[3][3]
ok = [res[R][0] for R in (1, 2, 3, 6)] == [6, 12, 16, 16] and size_same and res2[3] < 16 and abs(d_sim) < 0.02 and d_kit > 0.15
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"sizes {[res[R][0] for R in (1,2,3,6)]}; one lost axis keeps sizes {res4}; 2 axes gives {res2}; sim R3-R1={d_sim:.4f} vs kit rotation {d_kit:.3f}")
