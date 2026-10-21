# Sandbox: age-cutoff lossless threshold under a symmetric gate (state[t-L]==state[t]) versus a one-sided gate
# (reject only when the old state was OFF while now ON). Square wave, period P, half duty.
P=12;N=600;PRE=200
s=[1 if (i%P)<P//2 else 0 for i in range(N+PRE)]
def acc(L,gate):
    return sum(1 for t in range(PRE,PRE+N) if (s[t-L]==s[t] if gate=="sym" else not(s[t]==1 and s[t-L]==0)))
def m(L): r=L%P; return min(r,P-r)
def formula(L,gate): return N-(2 if gate=="sym" else 1)*(N//P)*m(L)
lags=[5,6,7,17,18,19,29,30,31,41,42]
bad=[(L,g) for L in lags for g in("sym","one") if acc(L,g)!=formula(L,g)]
print("formula mismatches",bad)
def thr(gate): return max(L for L in lags if acc(L,gate)>0)
def loss(gate,C): return sum(acc(L,gate) for L in lags if L>C)
ts,to=thr("sym"),thr("one")
print("sym thr",ts,"one thr",to,"loss at sym-thr by one-sided",loss("one",ts),"loss at one-thr",loss("one",to))
print("sym accepted at lag 30:",acc(30,"sym"),"lag 42:",acc(42,"sym"),"one at 30:",acc(30,"one"))
ok = not bad and ts==41 and to==42 and loss("one",ts)>0 and loss("sym",ts)==0
print("RESULT: %s formulas exact on %d cells, sym thr=%d one-sided thr=%d, cutting one-sided at the sym thr loses %d"%("PASS" if ok else "FAIL",len(lags)*2-len(bad),ts,to,loss("one",ts)))
