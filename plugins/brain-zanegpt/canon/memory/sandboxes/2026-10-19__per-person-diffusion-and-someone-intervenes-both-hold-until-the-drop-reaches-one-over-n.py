import math
LAB={1:0.85,3:0.62,6:0.31}      # per-person report rate by group size (Darley & Latane figures quoted in the kernel)
def any_act(q,n): return 1-(1-q)**n
for n,q in LAB.items(): print("lab n",n,"per-person",q,"P(someone acts) %.3f"%any_act(q,n))
# fit q_n = 0.85 * n^-k
ks={n:-math.log(q/0.85)/math.log(n) for n,q in LAB.items() if n>1}
print("implied exponent k",{n:round(k,2) for n,k in ks.items()})
def curve(k,ns=range(1,11)): return [any_act(min(1,0.85*n**-k),n) for n in ns]
rows={}
for k in (0.0,0.3,0.56,1.0,1.5):
    c=curve(k); rows[k]=c
    print("k",k,"P(someone) n=1..10",[round(v,2) for v in c],"rising" if c[-1]>c[0] else "falling")
rising=[k for k,c in rows.items() if c[9]>c[0]]
# smallest k where P(someone) at n=10 falls below n=1
ks_scan=[i/100 for i in range(0,201)]
kcross=next(k for k in ks_scan if curve(k)[9]<curve(k)[0])
print("crossover exponent",kcross)
lab_mid=any_act(LAB[3],3)
ok=(0.55<=ks[6]<=0.57 and abs(lab_mid-0.945)<0.01 and rows[0.56][9]>0.85 and rows[1.0][9]<rows[1.0][0] and 0.4<kcross<1.0)
print("RESULT:","PASS" if ok else "FAIL",f"lab per-person rates 0.85/0.62/0.31 still give P(someone acts) {any_act(.85,1):.2f}/{lab_mid:.2f}/{any_act(.31,6):.2f}; at n=10 it stays above 0.85 for exponent k up to about {kcross} and falls only past it, while full 1/n dilution (k=1.0) falls to {rows[1.0][9]:.2f}")
