# Hip rafter length from 3D coordinates vs the shortcut "common rafter length x sqrt(2)". Pitch rise per 12 inches of run.
# PREDICTION (before run): the shortcut overstates by 5.4% at 6/12 (18.97 vs 18.00 in per foot of common run) and 15.5% at 12/12,
# is exact only at pitch 0, grows monotonically with pitch; the right formula is sqrt(2*run^2 + rise^2); and a flat-plan
# (horizontal) length times sqrt(2) is right in plan but the true length needs the 3D rise.
from math import sqrt, hypot
def lengths(pitch,run=12.0):
    rise=pitch*run/12.0
    # square hip roof: corner (0,0,0), ridge point directly above the centre-line at (run,run,rise) for a square plan 2*run wide
    hip=sqrt(run**2+run**2+rise**2)
    common=sqrt(run**2+rise**2)
    return hip,common,rise
print("pitch  hip   common*sqrt2  overstate%")
errs=[]
for p in (0,2,4,6,8,10,12,14,16):
    hip,common,rise=lengths(p)
    naive=common*sqrt(2); e=(naive-hip)/hip*100; errs.append(e)
    print("%4d %6.3f %6.3f %6.2f"%(p,hip,naive,e))
mono=all(b>a for a,b in zip(errs,errs[1:]))
hip6,c6,_=lengths(6); hip12,c12,_=lengths(12)
# plan-only (horizontal) hip length times 1 is wrong: horizontal run diagonal = sqrt(2)*run
plan=sqrt(2)*12
ok = abs(errs[0])<1e-9 and mono and abs((c6*sqrt(2)-hip6)/hip6*100-5.4)<0.1 and abs((c12*sqrt(2)-hip12)/hip12*100-15.5)<0.1 and abs(hip6-18.0)<1e-9
print("RESULT: %s hip 6/12 %.2f in per ft vs shortcut %.2f (+%.1f%%), 12/12 %.2f vs %.2f (+%.1f%%), exact only at flat, monotone=%s"%("PASS" if ok else "FAIL",hip6,c6*sqrt(2),(c6*sqrt(2)-hip6)/hip6*100,hip12,c12*sqrt(2),(c12*sqrt(2)-hip12)/hip12*100,mono))
