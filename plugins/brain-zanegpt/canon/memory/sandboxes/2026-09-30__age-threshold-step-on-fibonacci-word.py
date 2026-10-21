# Prediction (before run): combined (age<=T AND view-legal) usable presses equal validity-only usable
# presses for every lag<=T and are exactly 0 for every lag>T, on periodic AND Fibonacci-word state, for all T
# swept 0..40; so cost-vs-lag is a step at T whose height is the validity-only count. Breaker: a fractional
# (soft) age weight is NOT a step.
N=600
def fibword(n):
    a,b="1","10"
    while len(b)<n+80: a,b=b,b+a
    return [int(c) for c in b[:n+80]]
FW=fibword(N)
def per(P,W): return [1 if (t%P)<W else 0 for t in range(N+80)]
shapes={"P15W5":per(15,5),"fib":FW}
def usable(s,lag,T,soft=False):
    c=0
    for t in range(80,80+N):
        v=s[t-lag]==1 and s[t]==1   # view-legal and still legal (valid press)
        if not v: continue
        if lag<=T: c+=1
    return c
bad=0;steps=0;peak={}
for name,s in shapes.items():
    for T in range(0,41):
        for lag in range(0,80):
            vo=usable(s,lag,10**9); co=usable(s,lag,T)
            exp=vo if lag<=T else 0
            steps+=1
            if co!=exp: bad+=1
    peak[name]=max(usable(s,l,10**9) for l in range(0,80))
    print(name,"validity-only max over lags 0..79:",peak[name],"of",N)
# breaker: soft weight (linear decay to 0 at 2T) gives non-step, intermediate costs
T=10;lag=15;vo=usable(shapes["P15W5"],lag,10**9)
print("breaker soft-weight lag15 T10: weighted",round(vo*max(0,1-(lag-T)/T),1),"vs hard-step",usable(shapes["P15W5"],lag,T),"validity-only",vo)
print("RESULT: PASS" if bad==0 else "RESULT: FAIL","step mismatches",bad,"of",steps)
