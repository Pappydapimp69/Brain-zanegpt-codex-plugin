# Positive-test posterior with natural frequencies, repeated tests, and shared-cause false positives. Exact fractions.
# PREDICTION (before run): prevalence 1%, sens 90%, FPR 9%: PPV after 1 positive 9.2%, after 2 independent ~50%;
# with half of repeat false positives shared (c=0.5) PPV after 2 stays under 20%; PPV after 2 drops below 20% at c about 0.4.
from fractions import Fraction as F
p,s,f=F(1,100),F(9,10),F(9,100)
def ppv(k,c):
    # k positives in a row; healthy repeat-FP chance given previous FP is c+(1-c)f
    hf=f; 
    for _ in range(k-1): hf*= c+(1-c)*f
    return p*s**k/(p*s**k+(1-p)*hf)
# natural-frequency check on 10000 people
N=10000; sick=int(N*p); tp=int(sick*s); fp=int((N-sick)*f)
print("10000 people: sick",sick,"true pos",tp,"false pos",fp,"PPV %.3f"%(tp/(tp+fp)))
print("single positive PPV %.4f"%float(ppv(1,0)))
for c in (0,F(1,4),F(2,5),F(1,2),F(3,4),1):
    print("c=%s: PPV after 2 = %.3f, after 3 = %.3f"%(c,float(ppv(2,c)),float(ppv(3,c))))
# negative result: odds multiplied by (1-s)/(1-f)
neg=p*(1-s)/(p*(1-s)+(1-p)*(1-f))
print("P(sick | one negative) %.5f (prior %.2f, factor %.3f)"%(float(neg),float(p),float((1-s)/(1-f))))
c_lo=next(F(i,100) for i in range(101) if ppv(2,F(i,100))<F(1,5))
print("PPV after 2 < 20%% from c=%s"%c_lo)
ok = abs(tp/(tp+fp)-0.0917)<0.002 and abs(float(ppv(2,0))-0.5)<0.01 and ppv(2,F(1,2))<F(1,5) and ppv(3,1)<ppv(1,0)
print("RESULT: %s single PPV %.1f%%, two independent %.1f%%, two with c=0.5 %.1f%%, c=1 repeats make it worse (my guess of flat and of a 0.4 threshold missed) (%.1f%% after 3), PPV<20%% from c=%s, one negative cuts 1%% to %.2f%%"%("PASS" if ok else "FAIL",100*float(ppv(1,0)),100*float(ppv(2,0)),100*float(ppv(2,F(1,2))),100*float(ppv(3,1)),c_lo,100*float(neg)))
