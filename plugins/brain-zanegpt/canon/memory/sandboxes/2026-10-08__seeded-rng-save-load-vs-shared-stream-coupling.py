# Deterministic LCG. Claim 1: saving {seed,count} gives exact resume. Claim 2: with ONE shared stream, adding an
# unrelated RNG consumer shifts a mechanic's outcomes; per-entity substreams (seed derived from entity id) do not.
class R:
    def __init__(s,seed,count=0):
        s.seed=seed; s.x=seed; s.count=0
        for _ in range(count): s.next()
    def next(s):
        s.x=(s.x*1103515245+12345)%2**31; s.count+=1; return s.x/2**31
def sim_shared(extra):
    r=R(42); out=[]
    for tick in range(20):
        if extra: r.next()          # unrelated enemy rolls first each tick
        out.append(r.next()<0.3)    # spread roll under test
    return out
def sim_split(extra):
    spread=R(42*7919+1); other=R(99)
    out=[]
    for tick in range(20):
        if extra: other.next()
        out.append(spread.next()<0.3)
    return out
a,b=sim_shared(False),sim_shared(True); c,d=sim_split(False),sim_split(True)
r=R(7)
for _ in range(50): r.next()
saved=(r.seed,r.count); tail=[r.next() for _ in range(10)]
r2=R(*saved); tail2=[r2.next() for _ in range(10)]
shared_diff=sum(x!=y for x,y in zip(a,b)); split_diff=sum(x!=y for x,y in zip(c,d))
print("shared diffs",shared_diff,"split diffs",split_diff,"resume exact",tail==tail2)
ok=tail==tail2 and shared_diff>0 and split_diff==0
print("RESULT: %s resume exact=%s shared-stream outcomes changed in %d/20 ticks, split streams in %d/20"%("PASS" if ok else "FAIL",tail==tail2,shared_diff,split_diff))
