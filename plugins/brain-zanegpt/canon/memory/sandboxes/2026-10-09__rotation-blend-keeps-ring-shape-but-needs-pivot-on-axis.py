import math
# Deterministic, stdlib-only. Ring of N verts radius R, tube axis = +z.
R=1.0; N=16
def rot(axis,a):
    x,y,z=axis; n=math.sqrt(x*x+y*y+z*z); x,y,z=x/n,y/n,z/n
    c,s=math.cos(a),math.sin(a); C=1-c
    return [[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]]
def mv(M,v): return [sum(M[i][j]*v[j] for j in range(3)) for i in range(3)]
def add(a,b): return [p+q for p,q in zip(a,b)]
def sub(a,b): return [p-q for p,q in zip(a,b)]
def sc(a,k): return [p*k for p in a]
def ring(c=(0,0,0)): return [[c[0]+R*math.cos(2*math.pi*i/N),c[1]+R*math.sin(2*math.pi*i/N),c[2]] for i in range(N)]
def cen(vs): return [sum(v[i] for v in vs)/len(vs) for i in range(3)]
def meanrad(vs):
    c=cen(vs); return sum(math.dist(v,c) for v in vs)/len(vs)
def lbs(v,mats_w,pivots):  # blend transformed positions
    out=[0,0,0]
    for (M,w),p in zip(mats_w,pivots):
        out=add(out,sc(add(mv(M,sub(v,p)),p),w))
    return out
def quat(axis,a):
    n=math.sqrt(sum(t*t for t in axis)); s=math.sin(a/2)
    return [math.cos(a/2)]+[t/n*s for t in axis]
def qmat(q):
    n=math.sqrt(sum(t*t for t in q)); w,x,y,z=[t/n for t in q]
    return [[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
def rb(v,qs_w,pivot):  # blend rotations (nlerp quats), single pivot
    q=[0]*4
    for qq,w in qs_w: q=[a+w*b for a,b in zip(q,qq)]
    return add(mv(qmat(q),sub(v,pivot)),pivot)
I=quat((0,0,1),0)
deg=math.radians
print("S1 pure twist about tube axis, 50/50 seam")
s1ok=True
for t in (30,90,120,170,179):
    th=deg(t); r=ring()
    L=meanrad([lbs(v,[(rot((0,0,1),0),.5),(rot((0,0,1),th),.5)],[(0,0,0)]*2) for v in r])
    B=meanrad([rb(v,[(I,.5),(quat((0,0,1),th),.5)],(0,0,0)) for v in r])
    print(f" {t}deg LBS={L:.4f} cos(t/2)={math.cos(th/2):.4f} RB={B:.4f}")
    s1ok&=abs(L-math.cos(th/2))<1e-9 and abs(B-1)<1e-9
print("S2 twist split over N twist bones, theta=179")
th=deg(179); fr={}
for n in (1,2,3,4):
    seam=th/n; fr[n]=abs(math.cos(seam/2)); print(f" N={n} LBS radius factor={fr[n]:.4f}")
s2ok=abs(fr[1]-.0087)<5e-4 and abs(fr[2]-.7102)<5e-4 and abs(fr[3]-.8675)<5e-4 and abs(fr[4]-.9247)<5e-4
print("S3 BREAK: tube centerline offset d from the pivot (axis does not pass through pivot)")
th=deg(90); d=0.5; r=ring((d,0,0))  # tube centered at x=d, pivot at origin
Bc=cen([rb(v,[(I,.5),(quat((0,0,1),th),.5)],(0,0,0)) for v in r]); Br=meanrad([rb(v,[(I,.5),(quat((0,0,1),th),.5)],(0,0,0)) for v in r])
drift=math.dist(Bc,(d,0,0))
Lr=[lbs(v,[(rot((0,0,1),0),.5),(rot((0,0,1),th),.5)],[(0,0,0)]*2) for v in r]
print(f" RB radius={Br:.4f} centerline drift={drift:.4f} (expected 2*d*sin(t/4)={2*d*math.sin(th/4):.4f}); LBS radius={meanrad(Lr):.4f}")
s3ok=abs(Br-1)<1e-9 and drift>0.1
print("S4 bend 90deg about x through pivot, 50/50")
th=deg(90); r=ring()
Lb=meanrad([lbs(v,[(rot((1,0,0),0),.5),(rot((1,0,0),th),.5)],[(0,0,0)]*2) for v in r])
Rb=meanrad([rb(v,[(I,.5),(quat((1,0,0),th),.5)],(0,0,0)) for v in r])
print(f" LBS ring mean radius={Lb:.4f} RB={Rb:.4f}")
s4ok=Rb>0.999 and Lb<0.95
ok=s1ok and s2ok and s3ok and s4ok
print("RESULT: %s rotation-blend holds radius 1.0 for pure twist and bend (S1,S4), LBS=cos(t/2); twist-bone split matches sibling numbers (S2); breaks when pivot is off the tube axis: centerline drift %.3f (S3)"%("PASS" if ok else "FAIL",drift))
