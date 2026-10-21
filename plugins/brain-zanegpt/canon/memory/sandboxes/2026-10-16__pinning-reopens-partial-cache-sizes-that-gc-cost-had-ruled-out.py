"""Sandbox: loop of 5 items, 1000 accesses. Cache = pinned first k items + LRU for the rest (total size s).
Cost = hits*1 + misses*100 + (accesses/GC_EVERY) * pause_per_slot * s. Sweep pause. Is any 1<=s<=4 ever best?
Prediction (before running): plain LRU never best at s in 1..4 (earlier gc-cost entry); with pin-k (s=k) a mid band of
pause cost exists where s in 1..4 is best, because pinned hits grow linearly (k/5 of accesses) while GC cost grows linearly
in s, so the best of the linear family flips at a pause crossover, giving 2 distinct winners besides 0 and 5 only if
marginal savings per slot differ; I expect exactly one winner per band, monotone in pause (5 -> ... -> 0)."""
from collections import OrderedDict
N, ACC, GC_EVERY = 5, 1000, 50
def run(size, pin):
    pinned=[]; lru=OrderedDict(); hits=0
    for t in range(ACC):
        x=t%N
        if x in pinned or x in lru:
            hits+=1
            if x in lru: lru.move_to_end(x)
            continue
        if size==0: continue
        if len(pinned)<pin: pinned.append(x); continue
        room=size-len(pinned)
        if room<=0: continue
        if len(lru)>=room: lru.popitem(last=False)
        lru[x]=1
    return hits
def cost(size,pin,pause):
    h=run(size,pin); return h+(ACC-h)*100+(ACC/GC_EVERY)*pause*size
for s in range(0,6): print("size",s,"lru hits",run(s,0),"pin-all hits",run(s,s))
def best(pause,pin_mode):
    c={s:cost(s,s if pin_mode else 0,pause) for s in range(0,6)}
    return min(c,key=lambda s:(c[s],s))
winners={}
for mode in (False,True):
    seq=[]
    for p in range(0,2000,5):
        b=best(p,mode)
        if not seq or seq[-1][1]!=b: seq.append((p,b))
    winners[mode]=seq
    print("pin" if mode else "lru","winner by pause start:",seq)
# Scenario built to BREAK linearity: skewed loop, items 0,1 appear 3x per cycle, 2,3,4 once; pin top-k by frequency.
PAT=[0,1,0,1,0,1,2,3,4]
def skew_hits(k):
    top=[0,1,2,3,4][:k]; return sum(1 for t in range(ACC) if PAT[t%len(PAT)] in top)
def skew_cost(k,pause):
    h=skew_hits(k); return h+(ACC-h)*100+(ACC/GC_EVERY)*pause*k
sk=[]
for p in range(0,2000,5):
    b=min(range(6),key=lambda k:(skew_cost(k,p),k))
    if not sk or sk[-1][1]!=b: sk.append((p,b))
print("skewed pin winners by pause start:",sk)
lru_mid=[b for p,b in winners[False] if 1<=b<=4]
pin_mid=[b for p,b in winners[True] if 1<=b<=4]
sk_mid=[b for p,b in sk if 1<=b<=4]
checks=[lru_mid==[], pin_mid==[], [b for _,b in winners[True]]==[5,0], sk_mid!=[]]
print("checks",checks)
print("RESULT:", "PASS" if all(checks) else "FAIL", f"uniform loop: lru winners {[b for _,b in winners[False]]}, pin winners {[b for _,b in winners[True]]} (no mid size); skewed loop pin winners {[b for _,b in sk]} (mid sizes {sk_mid})")
