# Sandbox: benign-violation gate (E1 model) + held pause before ONE peak beat. Stdlib only.
import math
C=10.0; BEATS=6
def gate(I,d,mode):
    dd = I/C if mode=="matched" else d
    return math.exp(-((dd-I/C)/0.25)**2)
def score(sched, pause, d, mode, recover=0.8, w_peak=0.7):
    X=0.0; resp=[]
    for k,I in enumerate(sched):
        if pause and k==len(sched)-1: X*=(1-recover)   # held pause before the final (peak) beat
        r=(I/C)*math.exp(-0.2*X)*gate(I,d,mode)
        resp.append(r); X+=1/(1+I/5)
    return w_peak*max(resp)+(1-w_peak)*sum(resp)/len(resp)   # one-peak weighting
S={"mild":[3]*6,"flat_big":[10]*6,"setup_then_peak":[3,3,3,3,3,10],"ramp":[2,4,5,6,8,10]}
rows={}
for mode,d in (("fixed",0.3),("matched",None)):
    for n,s in S.items():
        for p in (0,1):
            rows[(mode,n,p)]=score(s,p,d,mode)
            print(mode,n,"pause" if p else "nopause",round(rows[(mode,n,p)],3))
gain=lambda m,n:rows[(m,n,1)]-rows[(m,n,0)]
print("pause gain fixed: peak",round(gain("fixed","setup_then_peak"),3),"mild",round(gain("fixed","mild"),3),"ramp",round(gain("fixed","ramp"),3))
print("pause gain matched: peak",round(gain("matched","setup_then_peak"),3),"mild",round(gain("matched","mild"),3))
best_fixed=max(S,key=lambda n:rows[("fixed",n,1)]); best_matched=max(S,key=lambda n:rows[("matched",n,1)])
print("best with pause: fixed",best_fixed,"matched",best_matched)
checks=[
 best_fixed in ("mild","ramp"),                       # pause does not make the 10-peak win when grounded
 rows[("fixed","setup_then_peak",1)]<rows[("fixed","mild",1)],
 gain("matched","setup_then_peak")>gain("fixed","setup_then_peak"),   # pause pays off more when distance matches
 best_matched=="setup_then_peak"]
print("checks",checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),
 f"fixed: peak+pause {rows[('fixed','setup_then_peak',1)]:.3f} vs mild+pause {rows[('fixed','mild',1)]:.3f}; matched: peak+pause {rows[('matched','setup_then_peak',1)]:.3f} best={best_matched}")
