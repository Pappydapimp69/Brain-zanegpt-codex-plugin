# Exact (no RNG) permutation distribution of sort with a fair-coin comparator, by enumerating every comparison outcome tree.
from fractions import Fraction
from itertools import permutations
class Oracle:
    def __init__(s, bits): s.bits=bits; s.i=0
    def cmp(s, a, b):            # coin: True means a goes after b (comparator >0)
        if s.i >= len(s.bits): raise IndexError
        v=s.bits[s.i]; s.i+=1; return v
def insertion(a, gt):
    a=list(a)
    for i in range(1,len(a)):
        x=a[i]; j=i-1
        while j>=0 and gt(a[j],x): a[j+1]=a[j]; j-=1
        a[j+1]=x
    return a
def binary_insertion(a, gt):      # modern V8/TimSort style for short runs
    a=list(a)
    for i in range(1,len(a)):
        x=a[i]; lo,hi=0,i
        while lo<hi:
            mid=(lo+hi)//2
            if gt(a[mid],x): hi=mid
            else: lo=mid+1
        a[lo+1:i+1]=a[lo:i]; a[lo]=x
    return a
def merge_sort(a, gt):
    if len(a)<=1: return list(a)
    m=len(a)//2; l=merge_sort(a[:m],gt); r=merge_sort(a[m:],gt); out=[]
    while l and r: out.append(r.pop(0) if gt(l[0],r[0]) else l.pop(0))
    return out+l+r
def dist(algo, n):
    items=tuple(range(n)); probs={}
    def go(bits):
        o=Oracle(bits)
        try: res=tuple(algo(items, o.cmp))
        except IndexError:
            go(bits+[False]); go(bits+[True]); return
        probs[res]=probs.get(res,0)+Fraction(1,2**len(bits))
    go([]); return probs
def worst_ratio(p, n):
    fair=Fraction(1,len(list(permutations(range(n)))))
    allp=[p.get(q,Fraction(0)) for q in permutations(range(n))]
    return float(max(allp)/fair), float(min(allp)/fair)
def first_pos_freq(p, n): return [float(sum(v for k,v in p.items() if k[0]==e)) for e in range(n)]
ok=True
for name,algo in (("insertion",insertion),("binary_insertion",binary_insertion),("merge",merge_sort)):
    for n in (3,4,5):
        p=dist(algo,n); hi,lo=worst_ratio(p,n)
        print(f"{name:17} n={n} max/fair={hi:.2f} min/fair={lo:.2f} P(first==item): {[round(x,3) for x in first_pos_freq(p,n)]}")
        if n==3 and name!="merge": ok &= hi>1.2
        if name=="merge" and n==4: merge4=(hi,lo)
        if name=="insertion" and n==5: ins5=(hi,lo)
# control: n=2 is fair for every algorithm; n=4 merge has power-of-two leaves so check separately
p2=dist(merge_sort,2); ctrl=max(p2.values())==min(p2.values())
print("control n=2 uniform:", ctrl)
biased_all = all(worst_ratio(dist(a,4),4)[0]>1.0001 for a in (insertion,binary_insertion,merge_sort))
print("RESULT:", "PASS" if (ok and ctrl and biased_all) else "FAIL", f"coin-comparator sort non-uniform in all 3 algorithms n=3..5; insertion n=5 max/min vs fair {ins5[0]:.2f}/{ins5[1]:.2f}; merge n=4 {merge4[0]:.2f}/{merge4[1]:.2f}; n=2 uniform={ctrl}")
