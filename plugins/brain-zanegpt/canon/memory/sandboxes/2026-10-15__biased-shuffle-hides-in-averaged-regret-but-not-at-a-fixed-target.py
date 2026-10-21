# Exact (no RNG): enumerate every comparator outcome of insertion sort driven by a coin-flip comparator.
from fractions import Fraction
from itertools import product
def sort_with_bits(n, bits):
    a=list(range(n)); it=iter(bits)
    for i in range(1,n):
        j=i
        while j>0:
            try: b=next(it)
            except StopIteration: return None
            if b: a[j-1],a[j]=a[j],a[j-1]; j-=1   # comparator says "out of order"
            else: break
    return a
def count_comparisons(n):  # upper bound for bit strings
    return n*(n-1)//2
def naive_dist(n):
    # weight each leaf by 2^-(bits consumed): enumerate with a DFS over actual consumed bits
    dist={}
    def rec(prefix):
        r=sort_with_bits(n,prefix)
        if r is not None:
            dist[tuple(r)]=dist.get(tuple(r),0)+Fraction(1,2**len(prefix)); return
        rec(prefix+[0]); rec(prefix+[1])
    rec([]); return dist
def fisher_dist(n):
    from math import factorial
    from itertools import permutations
    return {p:Fraction(1,factorial(n)) for p in permutations(range(n))}
n=5
nd=naive_dist(n); fd=fisher_dist(n)
assert sum(nd.values())==1
# P(element 0 lands in position 0) etc.
def pos_prob(d,e,p): return sum(w for perm,w in d.items() if perm[p]==e)
print("n=5 P(item0 first): naive %s (%.4f) fisher %s" % (pos_prob(nd,0,0), float(pos_prob(nd,0,0)), pos_prob(fd,0,0)))
tv = max(abs(float(nd.get(p,0)-fd[p])) for p in fd)
print("max permutation prob gap: %.4f; permutations hit: %d of 120" % (tv, len(nd)))
# sweeping learner: cost to find treasure = rank of treasure in sweep order (rank 1..n)
def exp_cost(d,target):  # treasure is item `target`; position in permutation = rank
    return sum(w*(perm.index(target)+1) for perm,w in d.items())
avg_n = sum(exp_cost(nd,t) for t in range(n))/n
avg_f = sum(exp_cost(fd,t) for t in range(n))/n
print("averaged over uniform treasure: naive %s fisher %s" % (avg_n, avg_f))
worst = max(range(n), key=lambda t: exp_cost(nd,t)); best=min(range(n), key=lambda t: exp_cost(nd,t))
print("fixed treasure item: costs naive", [float(exp_cost(nd,t)) for t in range(n)], "fisher", [float(exp_cost(fd,t)) for t in range(n)])
spread_n = float(exp_cost(nd,worst)-exp_cost(nd,best)); spread_f = float(exp_cost(fd,worst)-exp_cost(fd,best))
# horizon cut: treasure must be found within H=2 steps
def hit(d,target,H): return sum(w for perm,w in d.items() if perm.index(target)<H)
print("P(find within 2) item0 naive %.3f fisher %.3f; item4 naive %.3f" % (hit(nd,0,2),hit(fd,0,2),hit(nd,4,2)))
ok = (avg_n==avg_f==Fraction(3) and spread_f==0 and spread_n>0.5 and len(nd)==120 and tv>0.01)
print("RESULT: %s averaged over a uniform treasure the naive shuffle costs %s = fisher %s steps, but at a fixed item cost ranges %.2f spread vs 0 (fisher); P(item0 first)=%.3f vs 0.200" % ("PASS" if ok else "FAIL", avg_n, avg_f, spread_n, float(pos_prob(nd,0,0))))
