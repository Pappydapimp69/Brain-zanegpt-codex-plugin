# Sandbox: the card's ceiling is the writer's estimate of framing distance. Error e = ceiling - true distance.
# Beat funny iff 1<=min(sev,ceiling)<=true distance. Score = sum of sev of funny beats. Go-big schedule.
GO_BIG = [1, 2, 3, 4, 5, 5]
def score(true_d, ceiling):
    s = f = 0
    for sev in GO_BIG:
        v = min(sev, ceiling)
        if 1 <= v <= true_d: s += v; f += 1
    return s, f
tot = {}
for e in (-2, -1, 0, 1, 2):
    sc = [score(d, d + e) for d in (2, 3, 4)]
    tot[e] = (sum(x[0] for x in sc), sum(x[1] for x in sc))
    print("error %+d: score %d funny beats %d (of 18) over d=2,3,4" % (e, *tot[e]))
ok = tot[0][0] > tot[-1][0] > tot[-2][0] and tot[0][0] > tot[1][0] >= tot[2][0] and tot[1][0] < tot[-1][0]
print("RESULT: %s exact ceiling scores %d; underestimating by 1 scores %d, overestimating by 1 scores %d" % ("PASS" if ok else "FAIL", tot[0][0], tot[-1][0], tot[1][0]))
