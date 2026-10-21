# Sandbox: even-tick fallback + restricted (odd-only) lag pools, tick-level simulation vs rule
# Prediction: lag L valid iff (L%P in W-W) or L even; odd-only pools with no residue-valid lag give cutoff 0;
# residue-only rule mispredicts any pool whose largest even lag exceeds its largest residue-valid lag.
import itertools
def valid_sim(L,P,W,T):
    for t in range(L,T):
        if (t%P in W and (t-L)%P in W) or (t%2==0 and (t-L)%2==0): return True
    return False
def cut_sim(pool,P,W):
    T=4*P+max(pool)+2*P+4
    v=[L for L in pool if valid_sim(L,P,W,T)]; return max(v) if v else 0
def rule(pool,P,W):
    D={(a-b)%P for a in W for b in W}
    v=[L for L in pool if L%P in D or L%2==0]; return max(v) if v else 0
def resid(pool,P,W):
    D={(a-b)%P for a in W for b in W}
    v=[L for L in pool if L%P in D]; return max(v) if v else 0
n=mis=rmis=0
for P in (5,6,9):
    for mask in range(1,2**P):
        W={i for i in range(P) if mask>>i&1}
        for pool in ([2,6,15],[4,8,10],[P+2,P+4],[1,3,5,7]):   # 4th odd-only breaker
            g=cut_sim(pool,P,W); n+=1; mis+= g!=rule(pool,P,W); rmis+= g!=resid(pool,P,W)
odd=[(P,W) for P in (7,) for W in [{0}]]
g=cut_sim([3,5,9],7,{0}); n+=1; mis+= g!=0
print("cases",n,"rule_mismatch",mis,"residue_only_mismatch",rmis)
print("RESULT:",("PASS" if mis==0 and rmis>0 else "FAIL"),n,"cases",mis,"rule mismatches",rmis,"residue-only misses")
