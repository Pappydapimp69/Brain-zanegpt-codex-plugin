# Sandbox: leave-one-out of each lag at P12/P15 under even-tick fallback, contiguous windows, tick-level.
# Prediction: union rule (difference set OR even) has 0 mismatches over every leave-one-out;
# residue-only mispredicts ONLY when the dropped lag was the sole lag masking an even off-residue lag, never on drops of the max odd period lag (15) when the remaining evens are all in D.
def valid_sim(L,P,W,T):
    for t in range(L,T):
        if (t%P in W and (t-L)%P in W) or (t%2==0 and (t-L)%2==0): return True
    return False
def cut(pool,P,W):
    T=6*P+max(pool)+4
    v=[L for L in pool if valid_sim(L,P,W,T)]; return max(v) if v else 0
def D(P,W): return {(a-b)%P for a in W for b in W}
def union(pool,P,W):
    d=D(P,W); v=[L for L in pool if L%P in d or L%2==0]; return max(v) if v else 0
def resid(pool,P,W):
    d=D(P,W); v=[L for L in pool if L%P in d]; return max(v) if v else 0
pools={12:[[2,6,12],[3,7,12],[5,8,12,24]],15:[[2,6,15],[4,9,15],[3,8,15,30],[5,7,11,15]]}
n=um=rm=0; odd15_resid_miss=0
for P,pl in pools.items():
    for pool in pl:
        for w in range(1,P+1):
            W=set(range(w))
            for drop in pool:
                p=[x for x in pool if x!=drop]
                g=cut(p,P,W); n+=1; um+= g!=union(p,P,W)
                if g!=resid(p,P,W):
                    rm+=1
                    if P==15 and drop==15 and all(x%2 for x in p): odd15_resid_miss+=1  # breaker: odd-only rest
print("cases",n,"union_miss",um,"resid_miss",rm,"odd_rest_resid_miss",odd15_resid_miss)
print("RESULT:",("PASS" if um==0 and odd15_resid_miss==0 else "FAIL"),n,"cases",um,"union mismatches",rm,"residue-only misses")
