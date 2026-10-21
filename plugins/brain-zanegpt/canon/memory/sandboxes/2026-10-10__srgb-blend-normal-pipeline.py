import math
def to_lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def to_srgb(l): return l*12.92 if l<=0.0031308 else 1.055*l**(1/2.4)-0.055
def lerp(a,b,t): return a+(b-a)*t
# S1: 50% white/black blend
naive=to_lin(lerp(1.0,0.0,0.5)); proper=to_lin(to_srgb(lerp(1.0,0.0,0.5)*0+0.5*1+0.5*0))
lin_blend=lerp(to_lin(1.0),to_lin(0.0),0.5)
print("S1 naive-lum",round(naive,4),"linear-lum",round(lin_blend,4))
# S2 BREAK: error vs colour distance (similar colours -> tiny error)
errs=[]
for d in (0.0,0.02,0.1,0.5,1.0):
    a,b=0.5,0.5+d/2 if d<=1 else 1; a=0.5-d/2; b=0.5+d/2
    n=to_lin(lerp(a,b,.5)); l=lerp(to_lin(a),to_lin(b),.5); errs.append((d,abs(n-l)))
print("S2 err by distance",[(d,round(e,5)) for d,e in errs])
# S3: normals under non-uniform scale (1,1,4 on z), light along +x/+z diagonal
def norm(v): m=math.sqrt(sum(x*x for x in v)); return [x/m for x in v]
sx,sy,sz=1,1,4
n_obj=norm([1,0,1]); L=norm([1,0,1])  # plane x+z=c
# true normal of scaled plane: (nx/sx,ny/sy,nz/sz)
true_n=norm([n_obj[0]/sx,n_obj[1]/sy,n_obj[2]/sz])
wrong_n=norm([n_obj[0]*sx,n_obj[1]*sy,n_obj[2]*sz])
# a surface tangent (1,0,-1) scaled -> (1,0,-4); true normal must be perpendicular
t=[1*sx,0,-1*sz]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
print("S3 true.t",round(dot(true_n,t),6),"wrong.t",round(dot(wrong_n,t),6))
# uniform scale: both agree
s=2; tn=norm([n_obj[0]/s,0,n_obj[2]/s]); wn=norm([n_obj[0]*s,0,n_obj[2]*s])
print("S4 uniform diff",round(max(abs(a-b) for a,b in zip(tn,wn)),9))
# S5 pipeline: diffuse shade then 50/50 blend with black, correct vs wrong
lam_true=max(0,dot(true_n,L)); lam_wrong=max(0,dot(wrong_n,L))
print("S5 lambert true",round(lam_true,4),"wrong",round(lam_wrong,4))
ok = abs(naive-0.214)<0.001 and abs(lin_blend-0.5)<1e-9 and errs[0][1]==0 and errs[1][1]<0.002 and errs[-1][1]>0.28 \
     and abs(dot(true_n,t))<1e-9 and abs(dot(wrong_n,t))>0.1
print("RESULT:", "PASS" if ok else "FAIL", "srgb lerp lum 0.214 vs 0.5; error grows with colour distance (~0 when close); inverse-transpose normal stays perpendicular, model-matrix normal does not; uniform scale agrees")
