import random
# Toy: concept -> 8 variants, each a film-style cut (shots in 15 s, ramp to shorter holds).
# Ranking A: raw IPM*D1.  Ranking B: same but a hold shorter than read time (1.0 s phone) is unreadable.
def holds(n, ramp):
    w=[1.0-ramp*i/(n-1) for i in range(n)]; s=15/sum(w); return [x*s for x in w]
def readable(h, rt): return sum(x for x in h if x>=rt)/sum(h)
def run(seed, rt, trials=2000, n_var=8):
    r=random.Random(seed); flips=0; lossA=0; lossB=0
    for _ in range(trials):
        vs=[]
        for _ in range(n_var):
            n=r.randint(6,22); ramp=r.uniform(0.0,0.7); h=holds(n,ramp)
            hype=r.uniform(0.8,1.2)*(1+0.03*n)          # busy cuts look exciting: raw IPM rises with shot count
            d1=r.uniform(0.8,1.2)
            rd=readable(h,rt)
            raw=hype*d1
            true=hype*d1*(0.3+0.7*rd)*(1 if rd>0 else 0.3) # viewers who cannot read the beats don't retain/convert
            vs.append((raw,true))
        a=max(range(n_var),key=lambda i:vs[i][0]); b=max(range(n_var),key=lambda i:vs[i][1])
        best=max(v[1] for v in vs)
        flips+= a!=b; lossA+=best-vs[a][1]
    return flips/trials, lossA/trials
for rt in (0.0,0.3,1.0):
    f,l=run(1,rt); print(f"read_time={rt}: pick flips {f:.3f} mean true-score loss of raw pick {l:.4f}")
f0,l0=run(1,0.0); f1,l1=run(1,1.0); f3,l3=run(2,1.0)
print(f"BREAK read_time=0: flips {f0:.3f}; seed2 rt=1.0 flips {f3:.3f}")
ok = f0<0.001 and f1>0.2 and f3>0.2 and l1>l0
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" flips rt0={f0:.3f} rt1={f1:.3f} seed2={f3:.3f} loss rt1={l1:.4f}")
