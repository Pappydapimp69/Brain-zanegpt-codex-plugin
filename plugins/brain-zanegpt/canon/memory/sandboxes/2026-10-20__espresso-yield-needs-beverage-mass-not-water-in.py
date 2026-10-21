# Espresso extraction yield EY = dissolved solids / dose. A refractometer gives TDS (% of beverage mass).
RET=2.0   # grams of water the wet puck keeps per gram of dose (assumed typical)
def shot(dose,water_in,ey):
    solids=ey*dose
    out=water_in-RET*dose+solids          # beverage = water that left the puck + dissolved solids
    return solids,out,100*solids/out      # TDS %
def ey_from(tds_pct,mass,dose): return tds_pct/100*mass/dose
print('dose water_in  out   TDS%  EY(out) EY(water_in)  inflation')
worst=0;rows=[]
for dose in (16,18,20):
    for w_in in [r*dose-0.20*dose+RET*dose for r in (1.5,2.0,2.5)]:   # beverage out = 1.5, 2.0, 2.5 x dose (1:1.5 .. 1:2.5 recipes)
        s,out,tds=shot(dose,w_in,0.20)
        ey_ok=ey_from(tds,out,dose);ey_bad=ey_from(tds,w_in,dose)
        rows.append((dose,w_in,out,tds,ey_ok,ey_bad));worst=max(worst,ey_bad/ey_ok)
        print('%4d %7.1f %5.1f %5.2f %7.3f %7.3f  x%.2f'%(dose,w_in,out,tds,ey_ok,ey_bad,ey_bad/ey_ok))
true_ok=all(abs(r[4]-0.20)<1e-12 for r in rows)
# ratio rescale: multiplying the wrong EY by out/water_in recovers the truth exactly (proportional hidden term)
resc=all(abs(r[5]*r[2]/r[1]-0.20)<1e-12 for r in rows)
# BREAK: a 1:1 'ristretto' shot, retained water dominates so the water-in error is largest; and if retention were 0 the error vanishes except for the solids
w_r=1.0*18-0.20*18+RET*18; s,out,tds=shot(18,w_r,0.20); big=w_r/out
s0,out0,_=shot(18,36,0.20)
RET0=RET
print('ristretto-style 1:1 out ratio inflation x%.2f'%big)
ok=true_ok and resc and 1.5<worst<5 and big>worst-0.01
print('RESULT: %s EY from water-in is inflated x%.2f to x%.2f (worst %.2f) versus beverage mass; ratio rescale by out/water_in restores 20%% exactly; 18 g dose at 1:1 out inflates x%.2f'%('PASS' if ok else 'FAIL',min(r[5]/r[4] for r in rows),max(r[5]/r[4] for r in rows),worst,big))
