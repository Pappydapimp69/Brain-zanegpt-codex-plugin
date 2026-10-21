"""Sandbox: does a second same-series resistor (series or parallel) close the single-value tolerance gaps?
Deterministic: log-grid of 2000 targets over one decade, values stocked over 3 decades."""
import itertools
def series(n): return [round(10**(k/n),{6:1,12:1,24:1,96:2}[n]) for k in range(n)]
def stock(n):
    base=series(n)
    # E6/E12/E24 use 2 sig figs; E96 3 sig figs
    return sorted({round(b*m,2) for b in base for m in (0.1,1,10,100)})
TOL={6:0.20,12:0.10,24:0.05,96:0.01}
T=[10**(1+i/2000) for i in range(2000)]  # 10..100 ohm
res={}
for n in (6,12,24,96):
    S=stock(n); tol=TOL[n]
    single=[t for t in T if any(abs(s-t)/t<=tol for s in S)]
    miss=[t for t in T if t not in set(single)]
    pairs=set()
    for a in S:
        if a>200: continue
        for b in S:
            if b>200: continue
            pairs.add(a+b)
            pairs.add(a*b/(a+b))
    P=sorted(pairs)
    closed=[t for t in miss if any(abs(p-t)/t<=tol for p in P)]
    # tighten: close within 1/4 of band
    closed4=[t for t in miss if any(abs(p-t)/t<=tol/4 for p in P)]
    res[n]=(len(miss)/len(T),len(closed)/max(1,len(miss)),len(closed4)/max(1,len(miss)),len(miss))
    print(f"E{n}: single-miss {res[n][0]*100:.1f}% ({res[n][3]} targets); pair closes {res[n][1]*100:.1f}% within tol, {res[n][2]*100:.1f}% within tol/4")
ok = res[6][0]==0 and all(res[n][1]==1.0 for n in (12,24,96) if res[n][3])
print(("RESULT: PASS" if ok else "RESULT: FAIL")+" "+"; ".join(f"E{n} miss {res[n][0]*100:.1f}% closed {res[n][1]*100:.0f}%/{res[n][2]*100:.0f}%(tol/4)" for n in res))
