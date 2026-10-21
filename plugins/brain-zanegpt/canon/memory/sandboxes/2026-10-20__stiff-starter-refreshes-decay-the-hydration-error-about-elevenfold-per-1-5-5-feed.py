from fractions import Fraction as F
# starter 50g at hydration h; each refresh keeps 10 g, adds 50 g flour + 50 g water (1:5:5), like a serial dilution step
def refresh(h):
    keep=F(10); sf=keep/(1+h); sw=keep-sf
    return (sw+50)/(sf+50)
def dough_hyd(h_starter, starter=100, flour=500, water=350):
    sf=F(starter)/(1+h_starter); sw=starter-sf
    return (water+sw)/(flour+sf)
assumed=dough_hyd(F(1))
h=F(1,2); rows=[]
for n in range(0,6):
    err_h=1-h; err_d=assumed-dough_hyd(h)
    rows.append((n,float(h),float(err_h),float(err_d)))
    print(f"refreshes={n} starter hyd={float(h):.5f} starter err={float(err_h):.5f} dough hyd err vs 100%-assumption={float(err_d)*100:.3f} pts")
    h=refresh(h)
ratios=[rows[i+1][2]/rows[i][2] for i in range(4)]
print("successive starter-error ratios",[round(r,4) for r in ratios])
ok = abs(rows[0][3]*100-5.08)<0.01 and rows[2][3]*100<0.05 and all(abs(r-1/11)<0.03 for r in ratios[1:]) and abs(ratios[-1]-1/11)<0.001
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"dough hydration error {rows[0][3]*100:.2f} pts for a 50% starter, {rows[1][3]*100:.2f} after 1 refresh, {rows[2][3]*100:.3f} after 2; starter error shrinks about x{ratios[-1]:.3f} (1/11, not 1/6) per 1:5:5 feed")
