# Prediction (before run): on periodic state, hint-vs-state mismatch count == 2*(N/P)*min(l,W,P-W,P-l), l=lag%P,
# so it is exactly 0 (fully blind) at every whole-cycle lag while the age tag flags all N at every lag>thr;
# mismatch detection rate stays <=2/P... only at l=1; breaker: detection can exceed age-blind only if l is mid-cycle.
def leg(t,P,W): return (t%P)<W
bad=0;cases=0;blind_lags=0;whole_ok=True;thr=2
minrate=1.0
for P in range(2,31):
  N=6*P
  for W in range(1,P):
    for lag in range(thr+1,3*P+1):
      cases+=1
      mm=sum(1 for t in range(3*P,3*P+N) if leg(t-lag,P,W)!=leg(t,P,W))
      l=lag%P
      f=2*(N//P)*min(l,W,P-W,P-l)
      if mm!=f: bad+=1
      age_flags=N  # every lag>thr
      if l==0:
        blind_lags+=1
        if mm!=0: whole_ok=False
      elif l==1: minrate=min(minrate,mm/N)
print("cases",cases,"formula mismatches",bad,"whole-cycle lags",blind_lags,"all blind",whole_ok)
print("worst near-blind rate at l=1 (mismatch/N):",round(minrate,4),"e.g. P30 => 2/30 =",round(2/30,4))
print("age tag detection rate at every lag>thr: 1.0")
print("RESULT: PASS" if bad==0 and whole_ok else "RESULT: FAIL","formula mismatches",bad,"of",cases)
