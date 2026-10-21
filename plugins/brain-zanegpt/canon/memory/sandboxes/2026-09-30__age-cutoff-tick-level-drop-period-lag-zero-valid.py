# Sandbox: contiguous window drop-period-lag, tick-level simulation vs closed form; restricted pool
# Prediction: for contiguous window w (residues 0..w-1) at P in {3,4,5,17,18}, pool 1..P with P dropped:
# cutoff = P-1 for w>=2, 0 for w=1. Restricted pool {1..P} minus lags whose residue isn't in W-W gives 0 mismatches.
def sim_valid(L,P,W,T):
    # lag valid iff some pair of ticks t, t-L both active in window (brute force over horizon)
    for t in range(L,T):
        if (t%P) in W and ((t-L)%P) in W: return True
    return False
def cutoff(pool,P,W):
    T=6*P+max(pool)+2*P
    v=[L for L in pool if sim_valid(L,P,W,T)]
    return max(v) if v else 0
mis=0;n=0;ones=0
for P in (3,4,5,17,18):
    for w in range(1,P+1):
        W=set(range(w))
        pool=[L for L in range(1,P)]
        got=cutoff(pool,P,W); exp=P-1 if w>=2 else 0
        n+=1; mis+= got!=exp
        if w==1: ones+= got==0
# scenario 2: pool = {1..P} minus P plus 2P (breaks next-lag): closed form largest valid
for P in (5,8):
    for w in range(1,P+1):
        W=set(range(w)); pool=list(range(1,P))+[2*P]
        got=cutoff(pool,P,W)
        D={(a-b)%P for a in W for b in W}
        exp=max([L for L in pool if L%P in D] or [0])
        n+=1; mis+= got!=exp
# scenario 3 breaker: zero-valid pool (lags never valid) -> 0 not max lag
for P in (9,):
    W={0}; pool=[2,3,5,7]; got=cutoff(pool,P,W); n+=1; mis+= got!=0
print("cases",n,"mismatches",mis,"w1_zero",ones)
print("RESULT:",("PASS" if mis==0 else "FAIL"),n,"cases",mis,"mismatches")
