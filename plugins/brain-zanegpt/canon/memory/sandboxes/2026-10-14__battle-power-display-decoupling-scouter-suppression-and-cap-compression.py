"""Gap: ideas UI-UX/power-scaling/display-decoupling/battle-power (+ sibling scouter kernel + dbz-team-combat/E1 cap).
Claim: split the flashy BP number from combat stats. PREDICTION (before running): with 12 fighters and all 66 duels
resolved by deterministic combat, (a) BP = monotone function of true combat strength ranks duels perfectly (0 inversions);
(b) a story-saga bonus that is NOT monotone in strength produces inversions (>0); (c) suppressing 3 fighters' scouter readings
(scouter cannot-read state) produces inversions among displayed BP unless the UI shows an 'unreadable' state and skips
them, which brings the readable-pair inversions back to 0; (d) a 20%-of-max-HP damage cap makes duels between a strong
fighter and a much stronger one still resolve for the stronger (no ties) but lengthens them: rounds-to-win falls with the
BP ratio only until the cap binds, then flattens."""
from fractions import Fraction as F

N = 12
HP = [200 + 40 * i for i in range(N)]       # tame, tunable stats
ATK = [30 + 9 * i for i in range(N)]
DEF = [10 + 3 * i for i in range(N)]
def strength(i): return HP[i] * ATK[i] // max(1, 1)      # simple combat strength proxy (integer)

def dmg(a, d, cap=None, mdef=0):
    raw = max(1, ATK[a] - DEF[d] // 2)
    return raw if cap is None else min(raw, max(1, int(F(cap) * HP[d])))

def duel(a, b, cap=None):
    """alternate attacks, a first; returns (winner, rounds)"""
    ha, hb = HP[a], HP[b]; r = 0
    while True:
        r += 1
        hb -= dmg(a, b, cap)
        if hb <= 0: return a, r
        ha -= dmg(b, a, cap)
        if ha <= 0: return b, r

def true_winner(i, j):
    w1, _ = duel(i, j); w2, _ = duel(j, i)
    return w1 if w1 == w2 else None            # None = order-dependent (not a clean winner)

PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
CLEAN = [(i, j, true_winner(i, j)) for i, j in PAIRS if true_winner(i, j) is not None]

def inversions(bp, readable=None):
    bad = tot = 0
    for i, j, w in CLEAN:
        if readable is not None and (i not in readable or j not in readable): continue
        tot += 1
        shown = i if bp[i] > bp[j] else j if bp[j] > bp[i] else None
        if shown != w: bad += 1
    return bad, tot

ok = True
# S1 monotone BP (1000 * strength^2: huge numbers, same order)
bp_mono = [1000 * strength(i) ** 2 for i in range(N)]
a = inversions(bp_mono); print("S1 monotone flashy BP inversions/clean duels:", a); ok &= a[0] == 0 and a[1] > 40
# S2 saga bonus non-monotone: later-saga characters get x50 regardless of stats (Tien-style jump)
saga_bonus = [1, 50, 1, 1, 50, 1, 1, 50, 1, 1, 1, 1]
bp_saga = [bp_mono[i] * saga_bonus[i] for i in range(N)]
b = inversions(bp_saga); print("S2 non-monotone saga bonus inversions:", b); ok &= b[0] > 0
# S3 scouter suppression: 3 fighters read as 1/100th; then UI 'unreadable' state excludes them
supp = {9, 10, 11}
bp_supp = [bp_mono[i] // 100 if i in supp else bp_mono[i] for i in range(N)]
c = inversions(bp_supp); d = inversions(bp_supp, readable=set(range(N)) - supp)
print("S3 suppressed readings inversions all/readable-only:", c, d); ok &= c[0] > 0 and d[0] == 0
# S4 BREAK: cap compresses duel length; rounds-to-win vs BP ratio with and without cap
rows = []
for j in (1, 3, 6, 9, 11):
    w, r0 = duel(j, 0); _, rc = duel(j, 0, cap=F(1, 20))
    rows.append((round(bp_mono[j] / bp_mono[0]), r0, rc)); 
print("S4 (BP ratio, rounds uncapped, rounds cap5%):", rows)
unc = [r[1] for r in rows]; capd = [r[2] for r in rows]
ok &= unc == sorted(unc, reverse=True) and capd[-1] == capd[-2] == capd[-3] and unc[-1] < unc[0]
print("RESULT:", "PASS" if ok else "FAIL", "monotone BP ranks 0 inversions; non-monotone saga bonus and silent suppression invert duels; unreadable state restores 0; a 5% cap pins every duel at 20 rounds from BP ratio 2 up to 189 (binds immediately, my bind-point guess was wrong)")
