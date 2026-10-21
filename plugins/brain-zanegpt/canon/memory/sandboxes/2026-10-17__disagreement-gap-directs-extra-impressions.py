# Tension-as-information-gap: where the IPM ranking and the IPM*D1 ranking disagree, spend extra impressions there.
# Prediction (before run): with conflicting metrics (D1 falls as conversion rises) targeting the union of the two
# top-3s lifts correct-winner rate over a uniform spend by >=5 points at equal budget; with aligned metrics
# (D1 flat) the targeting gives <=2 points. Assumption: the two rankings' top sets contain the true winner.
class Lcg:
    def __init__(s, seed): s.x = seed
    def u(s):
        s.x = (1103515245*s.x + 12345) % (2**31); return s.x/2**31
def binom(r, n, p):  # normal approx with LCG (sum of 12 uniforms)
    z = sum(r.u() for _ in range(12)) - 6
    return max(0, min(n, round(n*p + z*(n*p*(1-p))**0.5)))
def trial(seed, conflict, budget, targeted):
    r = Lcg(seed)
    ipm = [0.030+0.004*i for i in range(8)]                       # true install rate rises with i
    d1  = [0.40-0.03*i if conflict else 0.30 for i in range(8)]  # D1 falls with i (conflict) or flat
    score = [a*b for a,b in zip(ipm,d1)]; truth = max(range(8), key=lambda i: score[i])
    inst=[0]*8; imp=[0]*8; ret=[0]*8
    def spend(i, n):
        k = binom(r, n, ipm[i]); imp[i]+=n; inst[i]+=k; ret[i]+=binom(r, k, d1[i]) if k else 0
    for i in range(8): spend(i, budget//16)
    est_ipm = lambda i: inst[i]/imp[i]
    est_sc  = lambda i: ret[i]/imp[i]
    rest = budget//2
    if targeted:
        top = set(sorted(range(8), key=est_ipm)[-3:]) | set(sorted(range(8), key=est_sc)[-3:])
        for i in top: spend(i, rest//len(top))
    else:
        for i in range(8): spend(i, rest//8)
    pick = max(range(8), key=est_sc)
    return pick==truth
def rate(conflict, targeted, budget=40000, n=300):
    return sum(trial(s+1, conflict, budget, targeted) for s in range(n))/n
res = {}
for c in (True, False):
    for t in (False, True): res[(c,t)] = rate(c, t)
    print("conflict" if c else "aligned", "uniform %.3f targeted %.3f" % (res[(c,False)], res[(c,True)]))
gc = res[(True,True)]-res[(True,False)]; ga = res[(False,True)]-res[(False,False)]
ok = gc>=0.05 and ga<=0.02
print("RESULT: %s targeting gain conflict %+.3f aligned %+.3f (uniform %.3f/%.3f)" % ("PASS" if ok else "FAIL", gc, ga, res[(True,False)], res[(False,False)]))
