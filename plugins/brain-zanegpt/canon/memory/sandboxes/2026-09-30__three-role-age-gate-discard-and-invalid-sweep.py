# Prediction (before run): 3-role cyclic state r(t)=(t//S)%3, P=3S, hint=r(t-lag).
#  per-period disagreement = min(3*l, P, 3*(P-l)) with l=lag%P  (so 0 at whole-cycle lag);
#  validity+fallback executes 0 invalid at every lag (N/N valid);
#  age gate (thr) executes stale hints for lag<=thr -> invalid presses == disagreement*(N/P);
#  age gate above thr discards agreeing hints: discarded_valid == N - disagreement*(N/P), == N at whole-cycle lag.
def r(t,S): return (t//S)%3
bad=0;cases=0;full_at_cycle=True;inv_bad=0
for S in range(1,11):
  P=3*S;N=8*P
  for thr in (0,2,4):
    for lag in range(0,4*P+1):
      cases+=1
      dis=sum(1 for t in range(4*P,4*P+N) if r(t-lag,S)!=r(t,S))
      l=lag%P
      if dis!=(N//P)*min(3*l,P,3*(P-l)): bad+=1
      # validity+fallback: execute hint if agrees else current role => always valid
      valid_v=sum(1 for t in range(4*P,4*P+N) if (r(t-lag,S) if r(t-lag,S)==r(t,S) else r(t,S))==r(t,S))
      if valid_v!=N: inv_bad+=1
      if lag>thr:
        disc=N-dis   # agreeing hints thrown away by the age gate
        if l==0 and disc!=N: full_at_cycle=False
print("cases",cases,"disagreement formula errors",bad,"validity<N errors",inv_bad,"whole-cycle discards all N",full_at_cycle)
# breaker: with thr>=lag age gate executes stale hint; S=5,P=15,lag=3
S_=5;P=15;N=120;lag=3
inv=sum(1 for t in range(60,60+N) if r(t-lag,S_)!=r(t,S_))
print("breaker S5 lag3 inside thr: age gate invalid",inv,"of",N,"expected",(N//P)*min(9,P,36))
print("RESULT: PASS" if bad==0 and inv_bad==0 and full_at_cycle else "RESULT: FAIL","errors",bad+inv_bad)
