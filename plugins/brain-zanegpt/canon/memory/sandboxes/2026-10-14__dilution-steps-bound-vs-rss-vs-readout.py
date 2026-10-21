# Dilution plan ranking under three judges: summed worst-case, root-sum-square, rounded-readout exact-hit rate
from itertools import product
from math import sqrt
D=1000.0; V=1000.0
def err(a,vol): return max(0.005,a/vol)
def steps(k,a):
    f=D**(1.0/k); v=V/f
    return [err(a,v)+err(a,V-v)*(V-v)/V for _ in range(k)]
def worst(k,a): return sum(steps(k,a))
def rss(k,a): return sqrt(sum(w*w for w in steps(k,a)))
def exact(k,a,q=0.02):
    ws=steps(k,a); hit=n=0
    for combo in product((-1,-0.5,0,0.5,1),repeat=k):
        e=sum(c*w for c,w in zip(combo,ws)); n+=1
        if round((1+e)/q)*q==round(1/q)*q: hit+=1  # reads exactly 1.00
    return hit/n
K=(1,2,3,4)
def best(fn,a): return min(K,key=lambda k:fn(k,a))
print("a      best_worst best_rss  hit-rate by k (q=0.02)")
rows={}
for a in (0.0,0.005,0.011,0.015,0.02,0.03):
    rows[a]=(best(worst,a),best(rss,a),[round(exact(k,a),2) for k in K])
    print(a,rows[a])
# BREAK: readout winner (max hit rate) vs worst-case winner
disagree=[a for a,(bw,br,h) in rows.items() if K[h.index(max(h))]!=bw]
print("a where readout-winner != worst-case winner:",disagree)
def cross(fn):
    a=0.0
    while fn(1,a)<=fn(2,a): a+=0.0001
    return round(a,4)
cw,cr=cross(worst),cross(rss)
at02=[round(worst(k,0.02)*100,2) for k in (1,2,3,6)]
print("worst-case % at a=0.02 for k=1,2,3,6:",at02)
print("crossover a (1 step -> 2 steps): worst-case",cw,"rss",cr)
# claim under test (E1/E225): crossover 0.024 for summed bounds, 0.011 for rss
claim_ok = abs(cw-0.024)<0.001 and abs(cr-0.011)<0.001
print("RESULT: %s model reproduces E1 values %s at a=0.02 but crossover is %s (worst) and %s (rss), not 0.024/0.011; readout winner differs from worst-case winner at %s"%("PASS" if claim_ok else "FAIL",at02,cw,cr,disagree))
