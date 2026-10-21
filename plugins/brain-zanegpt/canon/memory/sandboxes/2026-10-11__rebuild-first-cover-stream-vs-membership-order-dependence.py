"""Own-fixture rebuild of the ORDER-DEPENDENCE claim only (not the 38/7, 100/9 period fractions: the entry's landing-time model is not in the claim text,
so I did not re-derive them). Two landing lists A, B of integer times; cover = number of times in both, plus union length.
Implementations: membership (set), union length, shared-iterator two-pointer (assumes both ascending), heap-pop (heap of A pops ascending, B scanned linearly assuming ascending).
PREDICTION (before run): membership and union length identical under asc/asc, desc/desc, asc/desc; shared-iterator two-pointer correct on asc/asc and WRONG on
desc/desc and on mixed; heap-pop correct when B is ascending (A order irrelevant) and wrong when B is descending. Checked on 40 generated list pairs."""
import heapq
def lists(seed):
    a=sorted({(seed*7+k*(3+seed%5))%97 for k in range(14)}); b=sorted({(seed*11+k*(4+seed%7))%97 for k in range(16)}); return a,b
def membership(a,b): return len(set(a)&set(b))
def union_len(a,b): return len(set(a)|set(b))
def two_ptr(a,b):
    ia=iter(a); ib=iter(b); n=0
    x=next(ia,None); y=next(ib,None)
    while x is not None and y is not None:
        if x==y: n+=1; x=next(ia,None); y=next(ib,None)
        elif x<y: x=next(ia,None)
        else: y=next(ib,None)
    return n
def heap_pop(a,b):
    h=list(a); heapq.heapify(h); j=0; n=0
    while h and j<len(b):
        x=heapq.heappop(h)
        while j<len(b) and b[j]<x: j+=1
        if j<len(b) and b[j]==x: n+=1; j+=1
    return n
orders={"asc/asc":(False,False),"desc/desc":(True,True),"asc/desc":(False,True),"desc/asc":(True,False)}
N=40; stats={o:{"mem":0,"uni":0,"tp":0,"hp":0} for o in orders}; nontrivial=0
for s in range(N):
    a,b=lists(s); truth=len(set(a)&set(b)); nontrivial+= truth>0
    for o,(ra,rb) in orders.items():
        aa=sorted(a,reverse=ra); bb=sorted(b,reverse=rb)
        st=stats[o]
        st["mem"]+= membership(aa,bb)==truth
        st["uni"]+= union_len(aa,bb)==len(set(a)|set(b))
        st["tp"]+= two_ptr(aa,bb)==truth
        st["hp"]+= heap_pop(aa,bb)==truth
for o in orders: print(o,{k:f"{v}/{N}" for k,v in stats[o].items()})
print("pairs with nonzero overlap:",nontrivial,"of",N)
ok=[all(stats[o]["mem"]==N and stats[o]["uni"]==N for o in orders),
    stats["asc/asc"]["tp"]==N, stats["desc/desc"]["tp"]<N, stats["asc/desc"]["tp"]<N,
    stats["asc/asc"]["hp"]==N, stats["desc/asc"]["hp"]==N, stats["desc/desc"]["hp"]<N, stats["asc/desc"]["hp"]<N, nontrivial>20]
print("RESULT: %s membership/union exact in 4 orders x %d pairs; two-pointer exact only asc/asc (%d/%d, desc/desc %d, mixed %d); heap-pop exact iff B ascending (desc/asc %d/%d, desc/desc %d)"%(
 "PASS" if all(ok) else "FAIL",N,stats["asc/asc"]["tp"],N,stats["desc/desc"]["tp"],stats["asc/desc"]["tp"],stats["desc/asc"]["hp"],N,stats["desc/desc"]["hp"]))
