# Prediction (before run): for P in 2..24, W in 1..P-1, thr in {2,5}, lag 0..3P, N=8P:
#  validity-only invalid presses == 0 iff lag%P==0; age-gate rejects all N iff lag>thr;
#  combined (age AND validity) executed-invalid == 0 always and rejected == N when lag>thr, else validity-only rejects;
#  so whole-cycle lag > thr is the ONLY region where validity-only strictly beats the age gate on total wasted presses.
def leg(t,P,W): return (t%P)<W
viol=0;cases=0;cross=set();other_win=0
for P in range(2,25):
  N=8*P
  for W in range(1,P):
    for thr in (2,5):
      for lag in range(0,3*P+1):
        cases+=1
        # validity-only: press attempted every tick t where view legal; invalid if now illegal (executed invalid)
        val_invalid=sum(1 for t in range(3*P,3*P+N) if leg(t-lag,P,W) and not leg(t,P,W))
        val_blocked=sum(1 for t in range(3*P,3*P+N) if not leg(t-lag,P,W))  # rejected by view check
        # age gate alone: accepts iff lag<=thr, executed-invalid same as validity when accepted
        age_rej = N if lag>thr else 0
        age_inv = 0 if lag>thr else val_invalid
        # combined: rejected if age fails; else view check protects
        comb_inv=0
        if (val_invalid==0)!=(lag%P==0): viol+=1
        # wasted = invalid executed + rejected-by-age
        waste_val=val_invalid; waste_age=age_rej+age_inv
        if waste_val<waste_age and lag>thr: cross.add(lag%P==0)
        if waste_val>waste_age and lag<=thr: other_win+=1
print("cases",cases,"validity-zero-iff-whole-cycle violations",viol)
print("lags>thr where validity strictly beats age gate: whole-cycle flags seen",sorted(cross))
# breaker: lag>thr non-whole-cycle -> validity still wastes invalid presses, age pays N: which is larger?
P,W,lag,thr=15,5,8,2;N=120
vi=sum(1 for t in range(45,45+N) if leg(t-lag,P,W) and not leg(t,P,W))
print("breaker P15W5 lag8: validity invalid",vi,"vs age gate rejects",N)
print("RESULT: PASS" if viol==0 else "RESULT: FAIL","violations",viol,"of",cases)
