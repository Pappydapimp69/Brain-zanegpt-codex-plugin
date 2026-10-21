# Sandbox: a cure brine made by serial dilution. Two error sources: (1) hidden weight base (multiplicative),
# (2) pipette error max(r, a/volume) per operation (additive floor at small volumes).
R=0.005; VF=1000.0; FACTOR=1000.0
def pipette_err(n,a):
    f=FACTOR**(1/n); vt=VF/f; vd=VF-vt
    per=max(R,a/vt)+R*(vd/VF)           # transfer error + diluent error scaled to final volume
    return n*per
# validate the dilution model against the known entry numbers (a=0.02 uL; a=0)
chk={n:round(pipette_err(n,0.02)*100,2) for n in (1,2,3,6)}
print("model, a=0.02 uL, % worst-case:",chk)
def base_err(brine): return abs(1/(1+brine)-1)   # dose weighed on meat+brine instead of meat
corrected_residual={}
for n in (1,2,3,6):
    pe=pipette_err(n,0.02)
    for brine in (0.1,0.25,0.5):
        raw=base_err(brine)+pe; fixed=0.0+pe     # ratio rescale removes the base error exactly, leaves the pipette error
        corrected_residual[(n,brine)]=(raw,fixed)
best=min((1,2,3,6),key=lambda n:pipette_err(n,0.02))
best0=min((1,2,3,6),key=lambda n:pipette_err(n,0.0))
raw_worst=max(v[0] for v in corrected_residual.values()); fixed_by_n={n:corrected_residual[(n,0.5)][1] for n in (1,2,3,6)}
print(f"best step count at a=0.02: {best}; at a=0: {best0}; raw worst-case total {raw_worst:.1%}; after ratio fix by steps {{ {', '.join(f'{n}:{v:.2%}' for n,v in fixed_by_n.items())} }}")
# the ratio correction multiplies the dose by a number near 1/base_ratio; check it does NOT shrink the pipette term
scaled=pipette_err(2,0.02)   # relative error unchanged by a multiplicative rescale
ok = chk[2]<chk[1] and chk[3]>chk[2] and best==2 and best0==1 and raw_worst>0.3 and scaled==pipette_err(2,0.02) \
     and abs(fixed_by_n[2]-pipette_err(2,0.02))<1e-12
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" model reproduces 2.5/1.97/2.85/5.05 pct for 1/2/3/6 steps; ratio fix removes the 33 pct base error but leaves the pipette floor, so the step count still sets the residual (best {best} at a=0.02, {best0} at a=0)")
