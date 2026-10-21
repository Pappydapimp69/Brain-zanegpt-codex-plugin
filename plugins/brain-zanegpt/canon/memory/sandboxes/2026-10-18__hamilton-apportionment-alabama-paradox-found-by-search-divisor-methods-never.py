# Prediction (written before the first run): exhaustive search over 3 states with populations 1..45 (sorted a<=b<=c)
# and house sizes 3..40 finds at least 50 Alabama-paradox cases for Hamilton (a state loses a seat when the house
# grows by one); Webster (Sainte-Lague) and Jefferson (D'Hondt) highest-averages allocation show 0 such cases;
# Hamilton always satisfies quota (floor/ceil of exact share) while Webster violates quota in at least 1 case.
# (Revised after run 1, which showed 0 Webster quota violations on 3 states: Webster quota violations need 4 states and count 'tie-free' separately.)
# BREAK: a hand-checked classic style case must exist where Hamilton at h gives the state s seats and at h+1 gives s-1.
from fractions import Fraction
def hamilton(pops, h):
    tot = sum(pops); q = [Fraction(p*h, tot) for p in pops]
    seats = [int(x) for x in q]
    order = sorted(range(len(pops)), key=lambda i: (-(q[i]-seats[i]), i))
    for i in order[:h-sum(seats)]: seats[i] += 1
    return seats
def highest_avg(pops, h, div):
    seats = [0]*len(pops)
    for _ in range(h):
        i = max(range(len(pops)), key=lambda i: (Fraction(pops[i], div(seats[i])), -i))
        seats[i] += 1
    return seats
webster = lambda s: 2*s+1
jefferson = lambda s: s+1
import itertools
cnt = {"hamilton": 0, "webster": 0, "jefferson": 0}
ham_quota_viol = web_quota_viol = 0
example = None
for a in range(1, 46):
    for b in range(a, 46):
        for c in range(b, 46):
            pops = [a, b, c]; tot = a+b+c
            prev = {"hamilton": hamilton(pops, 3), "webster": highest_avg(pops, 3, webster), "jefferson": highest_avg(pops, 3, jefferson)}
            for h in range(4, 41):
                cur = {"hamilton": hamilton(pops, h), "webster": highest_avg(pops, h, webster), "jefferson": highest_avg(pops, h, jefferson)}
                for k in cnt:
                    if any(x < y for x, y in zip(cur[k], prev[k])):
                        cnt[k] += 1
                        if k == "hamilton" and example is None: example = (pops, h-1, prev[k], h, cur[k])
                prev = cur
                for i in range(3):
                    ex = Fraction(pops[i]*h, tot)
                    if not (int(ex) <= cur["hamilton"][i] <= int(ex)+1): ham_quota_viol += 1
                    if not (int(ex) <= cur["webster"][i] <= int(ex)+1): web_quota_viol += 1
# Iteration 2 (after the 3-state scan found no Webster quota violation, refuting that part of the prediction):
# 4 states, pops 1..18, h 4..30; a violation is 'tie-free' when the last awarded priority strictly exceeds the best rejected one.
def priorities(pops, h, div):
    seats = highest_avg(pops, h, div)
    last = min(Fraction(pops[i], div(seats[i]-1)) for i in range(len(pops)) if seats[i] > 0)
    nxt = max(Fraction(pops[i], div(seats[i])) for i in range(len(pops)))
    return seats, last == nxt
w4 = w4_tiefree = 0
for a in range(1, 19):
    for b in range(a, 19):
        for c in range(b, 19):
            for d in range(c, 19):
                pops = [a, b, c, d]; tot = sum(pops)
                for h in range(4, 31):
                    seats, tie = priorities(pops, h, webster)
                    if any(not (int(Fraction(pops[i]*h, tot)) <= seats[i] <= int(Fraction(pops[i]*h, tot))+1) for i in range(4)):
                        w4 += 1
                        if not tie: w4_tiefree += 1
print("4-state webster quota violations", w4, "tie-free", w4_tiefree)
print("paradox counts:", cnt, "example:", example)
print("quota violations hamilton %d webster %d" % (ham_quota_viol, web_quota_viol))
ok = cnt["hamilton"] >= 50 and cnt["webster"] == 0 and cnt["jefferson"] == 0 and ham_quota_viol == 0 and web_quota_viol == 0 and w4 >= 1 and example is not None
print("RESULT: %s Hamilton Alabama-paradox cases %d (first %s), Webster %d, Jefferson %d; quota violations hamilton %d webster3 %d webster4 %d (tie-free %d)" % ("PASS" if ok else "FAIL", cnt["hamilton"], example, cnt["webster"], cnt["jefferson"], ham_quota_viol, web_quota_viol, w4, w4_tiefree))
