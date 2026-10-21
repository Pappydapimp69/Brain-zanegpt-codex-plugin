"""Train edge: od76 E16 (bank only newly crossed personal-best levels, apply on
the next run) + od76 E7 (record-only rewards either stall or snowball; pair
with a capped per-run term and simulate 40+ runs) - brainwork E189 asked to
audit what a saturated lever does to outcomes vs length.
Composed claim: E16's personal-best banking IS a record-only reward, so it
inherits E7's stall-or-snowball, and where it lands is set by gain per record
vs the next stage's cost; a capped per-run term removes the stall.
Own fixture, deterministic (seeded random.Random luck): stage s costs
min(25, 4 + s); a run reaches the deepest stage whose cumulative cost fits
budget x luck (luck uniform 0.85..1.15); budget starts 60. Banking: +k budget
per newly crossed personal-best stage. Variant: plus a per-run +1 capped at +20
total. 80 runs, 20 seeds.
PREDICTION (written before running): with small k (2) PB-only stalls - the
longest drought without a new PB exceeds 20 runs in most seeds (records thin
out like ln n); with large k (20) it snowballs - a new PB nearly every run
until the stage cost cap; adding the capped per-run term cuts the k = 2
drought below 10 runs in most seeds and does not change the k = 20 snowball.
"""
import random, sys
print("python", sys.version.split()[0])
def depth(budget):
    s = 0; spent = 0.0
    while spent + min(25, 4 + s + 1) <= budget: s += 1; spent += min(25, 4 + s)
    return s
def campaign(k, perrun, seed, runs=80):
    r = random.Random(seed); budget = 60.0; pb = 0; last_pb = 0; drought = 0; pbs = 0; bonus = 0
    for i in range(1, runs + 1):
        d = depth(budget * r.uniform(0.85, 1.15))
        if d > pb:
            budget += k * (d - pb); pb = d; pbs += 1
            drought = max(drought, i - last_pb - 1); last_pb = i
        if perrun and bonus < 20: budget += 1; bonus += 1
    drought = max(drought, runs - last_pb)
    return drought, pbs, pb
R = {}
for k in (2, 20):
    for pr in (False, True):
        out = [campaign(k, pr, s) for s in range(20)]
        R[(k, pr)] = out
        dr = sorted(o[0] for o in out)
        print(f"k {k:2d} per-run {pr!s:5s}: longest drought median {dr[10]}, max {dr[-1]}; PBs median {sorted(o[1] for o in out)[10]}; final depth median {sorted(o[2] for o in out)[10]}")
stall2 = sum(o[0] > 20 for o in R[(2, False)]); fix2 = sum(o[0] < 10 for o in R[(2, True)])
snow = sorted(o[1] for o in R[(20, False)])[10]
c = [stall2 >= 11, snow >= 30, fix2 >= 11]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/3; k2 PB-only drought>20 in {stall2}/20 seeds; k2 + capped per-run drought<10 in {fix2}/20; k20 median PBs {snow} of 80 runs")
