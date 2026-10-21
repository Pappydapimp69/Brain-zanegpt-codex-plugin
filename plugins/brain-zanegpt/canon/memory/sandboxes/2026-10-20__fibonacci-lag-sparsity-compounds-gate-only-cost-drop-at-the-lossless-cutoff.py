import random
def fibword(n):
    s="1"
    while len(s)<n+200:
        s="".join("10" if c=="1" else "1" for c in s)
    return [int(c) for c in s[:n+200]]
N=600; MAXL=120
def inv(sig,L): return sum(1 for t in range(N) if sig[t] and not sig[t+L])
fib=fibword(N)
rng=random.Random(7)
fibl=[1,2,3,5,8,13,21,34,55,89]
# sparse non-Fibonacci lag set of equal size, far from integer*phi
dense=list(range(1,MAXL+1))
def prox(L):
    x=L*0.6180339887; return abs(x-round(x))
far=sorted(sorted(range(1,MAXL+1),key=lambda L:-prox(L))[:len(fibl)])
def bound(lags,p=0.618): return len(lags)*N*p*(1-p)
def ratio(sig,lags): return sum(inv(sig,L) for L in lags)/bound(lags)
bern=[[1 if rng.random()<0.618 else 0 for _ in range(N+MAXL+5)] for _ in range(20)]
def bratio(lags): return sum(ratio(b,lags) for b in bern)/len(bern)
r={}
for name,lags in [("fib-lags",fibl),("far-lags",far),("dense",dense)]:
    r[name]=(ratio(fib,lags),bratio(lags))
    print(name,"fibword ratio %.3f bernoulli ratio %.3f"%r[name])
ok = r["fib-lags"][0]<=0.2 and r["far-lags"][0]>0.7 and r["dense"][0]>0.5 and abs(r["fib-lags"][1]-1)<0.1
print("RESULT: %s fibword/staircase fib-lags %.3f far-lags %.3f dense %.3f; bernoulli fib-lags %.3f"%("PASS" if ok else "FAIL",r["fib-lags"][0],r["far-lags"][0],r["dense"][0],r["fib-lags"][1]))
