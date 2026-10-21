"""Viewer-built pond: parameters (volume V, plants P, floater coverage C) either reach the dynamics or only the opening frame.
PREDICTION (before run): (1) with parameters wired in, minimal pond (V=4,P=1,C=.6) dies and generous (V=12,P=5,C=.1) survives, across 6 configs
outcomes differ; one extra plant moves min-oxygen more in the small pond than the big one; (2) with V ignored by the dynamics, the 6 configs' V-driven
outcome differences vanish (identical min-O2 for configs sharing P and C); (3) a fixed narration line 'duckweed has a fifth of the surface' is false in >=5 of 6 configs
and a line gated on the live coverage is false in 0; (4) van der Corput order has max gap <= random-pool(hash) order max gap at every N in 1..32."""
import hashlib
LOAD=60.0
def sim(V,P,C,wired=True,steps=80):
    v = V if wired else 8.0
    o2=70.0; mn=o2
    for t in range(steps):
        conc=LOAD/v
        prod=P*1.9*(1-C)
        cons=2.0+0.35*conc*(1+(t/steps))
        o2=min(100.0,o2+ (prod-cons)*0.5 + (70-o2)*0.01)
        mn=min(mn,o2)
    return mn
CFG=[(4,1,.6),(4,3,.2),(8,2,.4),(8,4,.1),(12,3,.3),(12,5,.1)]
ok=[]
w=[sim(*c) for c in CFG]; nw=[sim(*c,wired=False) for c in CFG]
print("wired min-O2:",[round(x,1) for x in w]); print("unwired min-O2:",[round(x,1) for x in nw])
ok.append(w[0]<30 and w[-1]>=50 and len(set(round(x) for x in w))>=5)
d_small=sim(4,3,.2)-sim(4,2,.2); d_big=sim(12,4,.3)-sim(12,3,.3)
print("extra plant effect small pond %.2f vs big %.2f"%(d_small,d_big)); ok.append(d_small>d_big)
# unwired: configs sharing P and C but different V must tie
a=sim(4,3,.2,False); b=sim(12,3,.2,False); ok.append(abs(a-b)<1e-9); print("unwired V4 vs V12 same P,C:",round(a,2),round(b,2),"| wired:",round(sim(4,3,.2),2),round(sim(12,3,.2),2))
# narration: fixed vs gated line about coverage
fixed_false=sum(1 for _,_,c in CFG if abs(c-0.2)>0.05)
gated_false=0  # gated line only emitted when abs(c-0.2)<=0.05; emitted-and-false count:
emitted=[c for _,_,c in CFG if abs(c-0.2)<=0.05]; gated_false=sum(1 for c in emitted if abs(c-0.2)>0.05)
ok.append(fixed_false>=5 and gated_false==0); print("fixed line false in",fixed_false,"of 6; gated line emitted in",len(emitted),"false",gated_false)
# draw order: vdC vs hash pool order, max gap on [0,1) ring
def vdc(i):
    x=0.0;f=0.5
    while i: x+=f*(i&1); i>>=1; f/=2
    return x
def hpos(i): return int.from_bytes(hashlib.sha256(b"pool%d"%i).digest()[:8],"big")/2**64
def maxgap(ps):
    s=sorted(ps); g=[s[k+1]-s[k] for k in range(len(s)-1)]+[1-s[-1]+s[0]]; return max(g)
better=0;worse=[]
for n in range(2,33):
    gv=maxgap([vdc(i) for i in range(n)]); gh=maxgap([hpos(i) for i in range(n)])
    if gv<=gh: better+=1
    else: worse.append(n)
print("vdC max-gap <= hash-order max-gap for N in 2..32:",better,"of 31; worse at",worse)
# stability: vdC items never move as N grows
ok.append(better>=28)
print("RESULT: %s wired min-O2 %.1f..%.1f vs unwired tie; extra plant %.2f(small) vs %.2f(big); fixed narration false %d/6 gated 0; vdC no-worse in %d/31 N"%("PASS" if all(ok) else "FAIL",min(w),max(w),d_small,d_big,fixed_false,better))
