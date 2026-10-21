# Prediction (before run): for every P in 2..30, 1<=W<P, lag 0..2P over N=P*k ticks,
# stale-illegal presses == (N/P)*min(lag%P... ) with lag reduced mod P; 0 mismatches expected.
def legal(t,P,W): return (t%P)<W
bad=0;total=0;zero_ok=True
for P in range(2,31):
    N=P*6
    for W in range(1,P):
        for lag in range(0,2*P+1):
            miss=sum(1 for t in range(N) if legal(t-lag,P,W) and not legal(t,P,W))
            l=lag%P
            f=(N//P)*min(l,W,P-W,P-l)
            total+=1
            if miss!=f: bad+=1
            if l==0 and miss!=0: zero_ok=False
print("cases",total,"mismatches",bad,"whole-cycle-zero",zero_ok)
# breaker: two-window shape (non-contiguous) is NOT covered by the formula
def legal2(t,P): return (t%P) in (0,1,6,7)
P=12;N=72;lag=3
miss=sum(1 for t in range(N) if legal2(t-lag,P) and not legal2(t,P))
print("two-window lag3 misses",miss,"contiguous-formula would give",(N//P)*min(3,4,8,9))
print("RESULT: PASS" if bad==0 and zero_ok else "RESULT: FAIL", "sweep mismatches",bad,"of",total)
