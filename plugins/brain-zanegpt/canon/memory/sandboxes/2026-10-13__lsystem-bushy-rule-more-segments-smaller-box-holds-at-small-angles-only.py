# PREDICTION (written before first run): bushy rule (8 F per rewrite) has more segments than plant (3 F)
# at every iteration 1-5 at 25deg; its bbox area is smaller than plant's by iter 4-5 at 25deg;
# the inversion is NOT universal: at 60deg+ it should vanish or flip. Plant width grows monotonic in angle 20..45.
import math
def expand(axiom, rules, n):
    s = axiom
    for _ in range(n):
        s = ''.join(rules.get(c, c) for c in s)
    return s
def draw(s, ang):
    x=y=0.0; h=90.0; st=[]; segs=[]
    for c in s:
        if c=='F':
            nx=x+math.cos(math.radians(h)); ny=y+math.sin(math.radians(h))
            segs.append(((x,y),(nx,ny))); x,y=nx,ny
        elif c=='+': h+=ang
        elif c=='-': h-=ang
        elif c=='[': st.append((x,y,h))
        elif c==']': x,y,h=st.pop()
    return segs
def bbox(segs):
    xs=[p[0] for s in segs for p in s]; ys=[p[1] for s in segs for p in s]
    w=max(xs)-min(xs); hh=max(ys)-min(ys); return w,hh,w*hh
def lit(segs, cell=0.5):
    cells=set()
    for (a,b) in segs:
        for t in (0,0.5,1):
            cells.add((math.floor((a[0]+(b[0]-a[0])*t)/cell), math.floor((a[1]+(b[1]-a[1])*t)/cell)))
    return len(cells)
PLANT={'F':'F[+F]F[-F]F'}
BUSHY={'F':'FF[+F][-F]F[+F][-F]F'}
def run(rules, ang, n):
    segs=draw(expand('F',rules,n),ang); w,h,a=bbox(segs); return len(segs),w,a,lit(segs)
print("scenario1: 25deg, iter 1-5")
inv25=None
for n in range(1,6):
    p=run(PLANT,25,n); b=run(BUSHY,25,n)
    print(n,"plant seg/area/lit",p[0],round(p[2],1),p[3],"bushy",b[0],round(b[2],1),b[3])
    if n==5: inv25=(b[0]>p[0], b[2]<p[2])
print("scenario2 (BREAK): angle sweep at iter 4, segments bushy>plant and area bushy<plant?")
flips={}
for ang in (15,25,45,60,90):
    p=run(PLANT,ang,4); b=run(BUSHY,ang,4)
    flips[ang]=(b[0]>p[0], b[2]<p[2]); print(ang,"plant area",round(p[2],1),"bushy area",round(b[2],1),"inverted" if flips[ang][1] else "not inverted")
print("scenario3: plant width vs angle 20..45 step5, iter4")
ws=[run(PLANT,a,4)[1] for a in range(20,46,5)]; print([round(w,1) for w in ws])
mono=all(ws[i]<ws[i+1] for i in range(len(ws)-1))
print("scenario4: plant lit cells iter4->5 (E65-style fixed viewport)", run(PLANT,25,4)[3], run(PLANT,25,5)[3], "segments",run(PLANT,25,4)[0],run(PLANT,25,5)[0])
print("scenario5 (iteration 2 of design, after run 1 refuted straight-trunk bushy): curling 8-F rules, iter 4/5, angles 25/45/90")
VARS={"curl_a":{'F':'F+F[-F]F-F[+F]F'},"curl_b":{'F':'F[+F]F[-F]F[+F-F]F[-F+F]F'},"curl_c":{'F':'F+F-F[+F]F-F[-F]F+F'}}
inv_found={}
for nm,r in VARS.items():
    for ang in (25,45,90):
        p=run(PLANT,ang,5); b=run(r,ang,5)
        inv_found[(nm,ang)]=(b[0]>p[0], b[2]<p[2]); print(nm,ang,"F count",r['F'].count('F'),"segs",b[0],"vs",p[0],"area",round(b[2],1),"vs",round(p[2],1))
n_inv=sum(1 for v in inv_found.values() if v[0] and v[1])
ok_segs=inv25[0]; ok_inv=inv25[1]
nflips=sum(1 for a,v in flips.items() if v[1])
print(f"RESULT: {'PASS' if (n_inv>0 and n_inv<len(inv_found)) else 'FAIL'} straight_bushy_inverted={nflips}/5_angles curling_bushy_inverted={n_inv}/{len(inv_found)} monotonic_width={mono}")
