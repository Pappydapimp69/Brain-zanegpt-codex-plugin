# Deterministic roster of 8 (tiers 1-4, two per tier). axes: 0 speed, 1 power, 2 technique, 3 defense.
# axis = 2*tier (+ NICHE on one axis per character). NICHE=0 is the scalar-power world.
def roster(niche):
    out = []
    for i in range(8):
        t = i // 2 + 1
        a = [2 * t] * 4
        a[i % 4] += niche
        out.append((i, t, a))
    return out
def race(r):  return max(r, key=lambda c: (c[2][0], -c[0]))[0]
def team(r):
    order = sorted(r, key=lambda c: (-sum(c[2]), c[0]))          # snake draft into 4 teams of 2
    teams = [[] for _ in range(4)]
    for k, c in enumerate(order):
        j = k % 8; j = j if j < 4 else 7 - j
        teams[j].append(c)
    best = max(teams, key=lambda tm: (sum(c[2][2] for c in tm), -tm[0][0]))
    return max(best, key=lambda c: (c[2][2], -c[0]))[0]            # team MVP
def duel(r):
    wins = {c[0]: 0 for c in r}; ups = 0; bouts = 0
    for x in r:
        for y in r:
            if x[0] < y[0]:
                dx = x[2][1] - y[2][3]; dy = y[2][1] - x[2][3]
                w = x if (dx, -x[0]) > (dy, -y[0]) else y
                lo = x if x[1] < y[1] else y
                bouts += 1
                if x[1] != y[1] and w is lo: ups += 1
                wins[w[0]] += 1
    return max(wins, key=lambda k: (wins[k], -k)), ups, bouts
def arc(niche):
    r = roster(niche); w3, ups, b = duel(r)
    return [race(r), team(r), w3], ups, b, r
res = {}
for niche in (0, 1, 3, 5):
    w, ups, b, r = arc(niche)
    tiers = [r[k][1] for k in w]
    res[niche] = (min(tiers), len(set(tiers)), ups, b)
    print(f"niche={niche}: winners race/team/duel={w} winner tiers={tiers} lowest={min(tiers)} lower-tier duel wins={ups}/{b}")
rep = len({duel(roster(5))[0] for _ in range(3)})
print("three repeated 1v1 brackets, niche=5: distinct winners =", rep)
# v2 metric (v1 counted distinct ids, which tie-breaks inflated in the scalar world): lowest winning tier and duel upsets
ok = (res[0][2] == 0 and res[0][0] >= 3 and res[5][0] <= 2 and res[5][2] > 0 and res[1][2] == 0 and rep == 1)
print("RESULT: %s scalar world lowest winner tier %d and 0 upsets; niche 5 lowest winner tier %d and %d/%d upsets; niche 1 %d upsets; repeated 1v1 = %d winner"
      % ("PASS" if ok else "FAIL", res[0][0], res[5][0], res[5][2], res[5][3], res[1][2], rep))
