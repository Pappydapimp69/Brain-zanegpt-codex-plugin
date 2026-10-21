# Robustness sweep: does "a few posts misjudge a hit-or-miss format" hold across spreads?
# Safe format sigma sA, weird format sigma sB>sA, same median. Count how often after N posts
# the weird format (higher true mean) shows NO more >=30x-median hits than the safe one.
import random, math
random.seed(11)
T=3000
print("sA  sB   N=10  N=30  N=60")
worst={10:1,30:1,60:1}; best={10:0,30:0,60:0}
for sA in (1.0,1.4,1.8):
    for gap in (0.4,0.8):
        sB=sA+gap; row=[]
        for N in (10,30,60):
            w=0
            for _ in range(T):
                ha=sum(random.gauss(0,sA)>math.log(30) for _ in range(N))
                hb=sum(random.gauss(0,sB)>math.log(30) for _ in range(N))
                w+= hb<=ha
            p=w/T; row.append(p); worst[N]=min(worst[N],p); best[N]=max(best[N],p)
        print(f"{sA:.1f} {sB:.1f}  "+"  ".join(f"{p*100:4.0f}%" for p in row))
print(f"range N=10 {worst[10]*100:.0f}-{best[10]*100:.0f}%, N=30 {worst[30]*100:.0f}-{best[30]*100:.0f}%, N=60 {worst[60]*100:.0f}-{best[60]*100:.0f}%")
ok = worst[10]>=0.30
print("RESULT:", "PASS" if ok else "FAIL", f"at 10 posts the better hit-or-miss format fails to show more hits {worst[10]*100:.0f}-{best[10]*100:.0f}% of the time across 6 spread settings")
