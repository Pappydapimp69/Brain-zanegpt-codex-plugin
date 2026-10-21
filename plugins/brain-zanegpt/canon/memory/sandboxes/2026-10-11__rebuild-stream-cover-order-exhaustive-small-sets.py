"""Own fixture: exhaustive subset tests over all pairs of subsets of {0..5} (64x64 pairs), no age-cutoff model.
Question: is `b subset of a` answered correctly by (1) set membership, (2) shared-iterator two-pointer, (3) heapify+heappop walk,
when a and b are presented ascending, with a reversed, with b reversed, with both reversed?
Prediction (before run): ascending: all three correct on all 4096 pairs. Reversed a: two-pointer wrong on some pairs, heappop correct (heapify is order-free),
set correct. Reversed b: both stream covers wrong on some pairs, set correct. Both reversed: two-pointer wrong, heappop wrong. Wrong answers are silent (no exception).
Control: sorted() first repairs both stream covers in every orientation. Rule claims silent failure only, not a count."""
import heapq, itertools
def c_set(b,a): sa=set(a); return all(x in sa for x in b)
def c_two(b,a):
    it=iter(a); cur=next(it,None)
    for x in b:
        while cur is not None and cur<x: cur=next(it,None)
        if cur!=x: return False
    return True
def c_heap(b,a):
    h=list(a); heapq.heapify(h)
    for x in b:
        while h and h[0]<x: heapq.heappop(h)
        if not h or h[0]!=x: return False
    return True
U=range(6)
subs=[list(c) for r in range(0,7) for c in itertools.combinations(U,r)]
def wrong(fn,ra,rb,presort=False):
    n=0
    for a in subs:
        for b in subs:
            aa=a[::-1] if ra else a; bb=b[::-1] if rb else b
            if presort: aa=sorted(aa); bb=sorted(bb)
            truth=set(b)<=set(a)
            if fn(bb,aa)!=truth: n+=1
    return n
res={}
for name,fn in (("set",c_set),("two",c_two),("heap",c_heap)):
    res[name]={(ra,rb):wrong(fn,ra,rb) for ra in (0,1) for rb in (0,1)}
    print(name,"wrong of 4096 [asc, rev-b, rev-a, rev-both]:",[res[name][k] for k in ((0,0),(0,1),(1,0),(1,1))])
fix_two=[wrong(c_two,ra,rb,True) for ra in (0,1) for rb in (0,1)]; fix_heap=[wrong(c_heap,ra,rb,True) for ra in (0,1) for rb in (0,1)]
print("presorted repair wrong counts: two",fix_two,"heap",fix_heap)
ok=(all(res[n][(0,0)]==0 for n in res) and all(v==0 for v in res["set"].values())
    and res["two"][(1,0)]>0 and res["heap"][(1,0)]==0 and res["two"][(0,1)]>0 and res["heap"][(0,1)]>0
    and res["two"][(1,1)]>0 and res["heap"][(1,1)]>0 and sum(fix_two)==0 and sum(fix_heap)==0)
print("RESULT: %s two[revA,revB,both]=%d,%d,%d heap[revA,revB,both]=%d,%d,%d set_all=0 presort_repairs=%s"%("PASS" if ok else "FAIL",
 res["two"][(1,0)],res["two"][(0,1)],res["two"][(1,1)],res["heap"][(1,0)],res["heap"][(0,1)],res["heap"][(1,1)],sum(fix_two)+sum(fix_heap)==0))
