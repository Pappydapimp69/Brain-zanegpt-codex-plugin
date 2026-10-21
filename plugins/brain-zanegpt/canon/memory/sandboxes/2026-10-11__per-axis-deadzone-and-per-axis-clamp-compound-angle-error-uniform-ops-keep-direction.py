"""Compose two 2D-vector lessons: radial-vs-per-axis deadzone (brainwork/E48) and uniform-vs-per-axis clamp (offscreen marker E1).
A vector (r, theta) goes through a deadzone stage then a clamp-to-box stage (box half-extents BX,BY, non-square).
PREDICTION (before run): (1) both-uniform stages keep direction exactly (max error 0.00 deg); (2) per-axis deadzone only, and per-axis clamp only, each give
errors >5 deg somewhere; (3) both per-axis gives a max error LARGER than either alone on the same sweep (compounding), but at some angles the errors partly CANCEL
(composed error < clamp-only error) -- this cancellation is the part I expect might fail; FIRST RUN REFUTED (3): at r=.35 in a 0.3 box the composed error equalled the larger single error at all 360 angles (no
compounding, no cancelling): once the per-axis deadzone zeroes a component the vector sits on an axis and the later clamp cannot bend it, and where
nothing is zeroed only the clamp acts. REVISED PREDICTION (5): the order dz->clamp gives composed == max(single) at every angle; swapping the order
(clamp->dz) breaks that and gives angles where composed > both singles.
(4) with square box the per-axis clamp error is symmetric about 45 deg, with 16:9 it is not."""
import math
DZ=0.2
def dz_axis(x,y):  return (x if abs(x)>=DZ else 0.0, y if abs(y)>=DZ else 0.0)
def dz_rad(x,y):
    r=math.hypot(x,y)
    return (0.0,0.0) if r<DZ else (x,y)
def clamp_axis(x,y,bx,by): return (max(-bx,min(bx,x)), max(-by,min(by,y)))
def clamp_uni(x,y,bx,by):
    s=min(1.0, bx/abs(x) if x else 9e9, by/abs(y) if y else 9e9); return (x*s,y*s)
def ang(x,y): return math.degrees(math.atan2(y,x))
def err(a,b):
    d=abs(a-b)%360; return min(d,360-d)
def run(dz,cl,bx,by,r):
    out=[]
    for k in range(0,360):
        th=math.radians(k+0.5); x,y=r*math.cos(th),r*math.sin(th)
        x1,y1=dz(x,y)
        if x1==0 and y1==0: out.append(None); continue
        x2,y2=cl(x1,y1,bx,by); out.append(err(ang(x2,y2),ang(x,y)))
    return out
def mx(l): return max(e for e in l if e is not None)
R=2.0   # far outside box so clamp always engages
ok=[]
for name,(bx,by) in {"square":(1,1),"16:9":(1.78,1.0)}.items():
    uu=run(dz_rad,clamp_uni,bx,by,R); pa=run(dz_axis,clamp_uni,bx,by,R)
    ap=run(dz_rad,clamp_axis,bx,by,R); bb=run(dz_axis,clamp_axis,bx,by,R)
    print(f"{name}: uniform+uniform {mx(uu):.2f} | perAxisDZ+uni {mx(pa):.2f} | radDZ+perAxisClamp {mx(ap):.2f} | both perAxis {mx(bb):.2f}")
    if name=="square": sq=(mx(uu),mx(pa),mx(ap),mx(bb),ap,bb)
    else: wide=(mx(uu),mx(pa),mx(ap),mx(bb),ap,bb)
ok.append(sq[0]<1e-9 and wide[0]<1e-9)
ok.append(sq[2]>5 and wide[2]>5)
# at R=2 the deadzone does nothing (all components >= DZ except near axes), so deadzone-only error: use R near DZ, no clamp engagement
nb=1e9
da=run(dz_axis,clamp_uni,nb,nb,0.25); print("per-axis DZ only at r=0.25: max error %.2f deg, dead directions %d of 360"%(mx([e for e in da]) if any(e is not None for e in da) else 0, sum(e is None for e in da)))
ok.append(mx(da)>5)
# compounding: composed vs each alone on a radius where BOTH act: r where per-axis DZ cuts a component AND clamp engages
# small box so clamp engages at modest r
bx,by=0.3,0.3; r=0.35
a=run(dz_axis,clamp_uni,bx,by,r); b=run(dz_rad,clamp_axis,bx,by,r); c=run(dz_axis,clamp_axis,bx,by,r)
idx=[i for i in range(360) if a[i] is not None and c[i] is not None]
comp=sum(1 for i in idx if c[i]>max(a[i],b[i])+1e-9); cancel=sum(1 for i in idx if c[i]<max(a[i],b[i])-1e-9); eq=len(idx)-comp-cancel
print(f"small box r=.35: max single {max(mx(a),mx(b)):.2f}, composed {mx(c):.2f}; angles composed>both {comp}, composed<max single (cancel) {cancel}, equal {eq}, dead {360-len(idx)}")
ok.append(comp==0 and cancel==0 and eq==360)
# order swap: clamp first, then deadzone
def run_rev(dz,cl,bx,by,r):
    out=[]
    for k in range(360):
        th=math.radians(k+0.5); x,y=r*math.cos(th),r*math.sin(th)
        x1,y1=cl(x,y,bx,by); x2,y2=dz(x1,y1)
        out.append(None if (x2==0 and y2==0) else err(ang(x2,y2),ang(x,y)))
    return out
rv=run_rev(dz_axis,clamp_axis,0.3,0.3,0.35)
idx2=[i for i in range(360) if rv[i] is not None and a[i] is not None and b[i] is not None]
comp2=sum(1 for i in idx2 if rv[i]>max(a[i],b[i])+1e-9)
print("clamp->dz order: max %.2f, angles worse than both singles %d, dead %d"%(max(e for e in rv if e is not None),comp2,sum(e is None for e in rv)))
ok.append(comp2==0)   # second guess (order swap compounds) also REFUTED here
# iteration 3: sweep radius, box, both orders; count angles where composed > worst single, and where fixing one stage changes the max
tot=0; worse=0; stage_fix_noop=0; cases=0
for r_ in (0.22,0.3,0.4,0.6,1.0,1.5,2.5):
    for bx_,by_ in ((0.3,0.3),(0.5,0.5),(1,1),(1.78,1),(0.4,1.0)):
        sa=run(dz_axis,clamp_uni,bx_,by_,r_); sb=run(dz_rad,clamp_axis,bx_,by_,r_)
        fw=run(dz_axis,clamp_axis,bx_,by_,r_); rw=run_rev(dz_axis,clamp_axis,bx_,by_,r_)
        for i in range(360):
            if fw[i] is None or sa[i] is None: continue
            tot+=1
            m=max(sa[i],sb[i])
            if fw[i]>m+1e-9: worse+=1
            if rw[i] is not None and rw[i]>m+1e-9: worse+=1
        cases+=1
        mxs=(mx(sa) if any(e is not None for e in sa) else 0, mx(sb))
        if min(mxs)>0 and abs(mx(fw)-max(mxs))<1e-9: stage_fix_noop+=1
print("sweep: %d cases, %d angle samples, composed worse than worst single in %d samples (both orders); max-error set by worse stage in %d of %d cases with both stages active"%(cases,tot,worse,stage_fix_noop,cases))
ok.append(worse==0 and stage_fix_noop>0)
# symmetry about 45 deg for per-axis clamp
def sym(lst): return max(abs(lst[k]-lst[89-k]) for k in range(45))
ap_sq=run(dz_rad,clamp_axis,1,1,R); ap_w=run(dz_rad,clamp_axis,1.78,1,R)
print("symmetry gap about 45deg (first quadrant): square %.2f, 16:9 %.2f"%(sym(ap_sq),sym(ap_w)))
ok.append(sym(ap_sq)<1e-6 and sym(ap_w)>1)
print("RESULT: %s uniform stages 0.00 deg; per-axis clamp max %.1f; dz->clamp composed %.1f equals worst single %.1f at all 360 angles; no compounding in %d samples across both orders"%("PASS" if all(ok) else "FAIL",sq[2],mx(c),max(mx(a),mx(b)),tot))
