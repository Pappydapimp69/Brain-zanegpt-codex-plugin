# START triage (Benson, Koenig, Schultz 1996 Prehosp Disaster Med: walk -> breathing -> RPM) as a decision list.
# Exhaustive enumeration over patient attribute combos weighted by a fixed prevalence table (no RNG).
import itertools
P_WALK=0.5; P_NOBREATH_AFTER_REPOS=0.05
P_R=0.10   # resp rate > 30
P_P=0.25   # cap refill > 2 s / no radial pulse
P_M=0.15   # cannot follow commands
def classify(walk, breathes, r, p, m, order):
    """returns (category, checks_done). A failing R/P/M check ends at IMMEDIATE."""
    n=1                                  # check 1: can walk
    if walk: return "MINOR", n
    n+=1                                 # check 2: breathing (after one airway reposition)
    if not breathes: return "EXPECTANT", n
    flags={"R":r,"P":p,"M":m}
    for k in order:
        n+=1
        if flags[k]: return "IMMEDIATE", n
    return "DELAYED", n
def classify_wrong(walk, breathes, r, p, m, order):      # BREAK: stops at first PASS instead of first FAIL
    n=1
    if walk: return "MINOR", n
    n+=1
    if not breathes: return "EXPECTANT", n
    flags={"R":r,"P":p,"M":m}
    for k in order:
        n+=1
        if not flags[k]: return "DELAYED", n
    return "IMMEDIATE", n
def run(fn, order):
    cats={}; mean=0.0
    for walk,br,r,p,m in itertools.product([1,0],[1,0],[1,0],[1,0],[1,0]):
        w=(P_WALK if walk else 1-P_WALK)*(1-P_NOBREATH_AFTER_REPOS if br else P_NOBREATH_AFTER_REPOS)
        w*=(P_R if r else 1-P_R)*(P_P if p else 1-P_P)*(P_M if m else 1-P_M)
        c,n=fn(walk,br,r,p,m,order); cats[(walk,br,r,p,m)]=c; mean+=w*n
    return cats, mean
orders=list(itertools.permutations("RPM"))
base,_=run(classify,orders[0])
diffs=0; means={}
for o in orders:
    c,m=run(classify,o); means["".join(o)]=m
    diffs+=sum(c[k]!=base[k] for k in c)
best=min(means,key=means.get); worst=max(means,key=means.get)
print("mean checks per patient by order:",{k:round(v,4) for k,v in means.items()})
bad_c,_=run(classify_wrong,orders[0]); bad_diff=sum(bad_c[k]!=base[k] for k in base)
# most-often-failing check first should be fastest
by_rate=sorted("RPM",key=lambda k:-{"R":P_R,"P":P_P,"M":P_M}[k])
print("best",best,"worst",worst,"order by fail rate",''.join(by_rate),"wrong-logic category diffs",bad_diff)
ok = diffs==0 and best==''.join(by_rate) and means[worst]-means[best]>0.01 and bad_diff>0
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" category diffs across 6 orders {diffs}; mean checks {means[best]:.4f} ({best}) vs {means[worst]:.4f} ({worst}); stop-at-first-pass changed {bad_diff} of 32 patient types")
