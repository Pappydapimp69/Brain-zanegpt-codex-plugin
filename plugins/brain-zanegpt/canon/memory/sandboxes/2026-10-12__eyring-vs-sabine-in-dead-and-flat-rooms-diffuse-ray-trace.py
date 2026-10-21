# PREDICTION (before run): 10x8x4 at uniform a=0.5: Sabine ~ +20% (15..30), Eyring ~ -10% (-5..-17), Kuttruff within 5%.
# 20x16x3 with absorbing floor/ceiling (0.9) and walls 0.02: Eyring is >25% low and Sabine is closer than Eyring (open tension: Eyring not safe when absorption is lumped).
# Uniform very dead rooms (a=0.7, 0.9) in a 6x5x3 shoebox: Eyring is still closer than Sabine (shape-independent) -- this one could come out wrong.
import math
def frac(x): return x-math.floor(x)
def traced_t60(L,a_faces,nray=2500,maxb=400):
    Lx,Ly,Lz=L; c=343.0
    # faces: x0,x1,y0,y1,z0,z1
    src=(0.31*Lx,0.37*Ly,0.43*Lz)
    events=[]   # (time, energy after hit) per ray, stored as lists
    phi=(1+5**.5)/2
    curves=[]
    for i in range(nray):
        z=1-2*(i+.5)/nray; r=math.sqrt(max(0,1-z*z)); th=2*math.pi*i/phi
        d=[r*math.cos(th),r*math.sin(th),z]; p=list(src); t=0.0; e=1.0; ev=[(0.0,1.0)]
        for b in range(maxb):
            best=None
            for ax,(Lax) in enumerate((Lx,Ly,Lz)):
                if d[ax]>1e-12: s=(Lax-p[ax])/d[ax]; f=2*ax+1
                elif d[ax]<-1e-12: s=(0-p[ax])/d[ax]; f=2*ax
                else: continue
                if best is None or s<best[0]: best=(s,ax,f)
            s,ax,f=best
            p=[p[k]+d[k]*s for k in range(3)]; t+=s/c; e*=1-a_faces[f]
            ev.append((t,e))
            if e<1e-7: break
            # Lambertian reflection about the wall normal, low-discrepancy (deterministic) sample
            u1=frac(0.5+(i+1)*0.6180339887+b*0.7548776662); u2=frac(0.3+(i+1)*0.5698402910+b*0.5698402910*0.3)
            cost=math.sqrt(1-u1); sint=math.sqrt(u1); ph=2*math.pi*u2
            tang=[k for k in range(3) if k!=ax]
            nd=[0,0,0]; sign=-1 if f%2==1 else 1
            nd[ax]=sign*cost; nd[tang[0]]=sint*math.cos(ph); nd[tang[1]]=sint*math.sin(ph); d=nd
        curves.append(ev)
    # energy decay curve on a time grid
    tmax=max(ev[-1][0] for ev in curves); n=600; grid=[tmax*k/n for k in range(n+1)]
    E=[0.0]*(n+1)
    for ev in curves:
        j=0
        for k,tg in enumerate(grid):
            while j+1<len(ev) and ev[j+1][0]<=tg: j+=1
            E[k]+=ev[j][1]
    E=[x/nray for x in E]
    # fit slope between -5 and -35 dB
    pts=[(grid[k],10*math.log10(E[k])) for k in range(n+1) if E[k]>0]
    sel=[(t,db) for t,db in pts if -35<=db<=-5]
    mt=sum(t for t,_ in sel)/len(sel); md=sum(d for _,d in sel)/len(sel)
    slope=sum((t-mt)*(d-md) for t,d in sel)/sum((t-mt)**2 for t,_ in sel)
    return -60.0/slope
def formulas(L,a_faces):
    Lx,Ly,Lz=L; V=Lx*Ly*Lz
    A=[Ly*Lz,Ly*Lz,Lx*Lz,Lx*Lz,Lx*Ly,Lx*Ly]; S=sum(A)
    abar=sum(x*y for x,y in zip(A,a_faces))/S
    sab=0.161*V/(S*abar); eyr=-0.161*V/(S*math.log(1-abar)); lg=math.log(1-abar)
    kut=-0.161*V/(S*lg*(1+0.37/2*lg)) if False else -0.161*V/(S*lg*(1+(0.37/2)*lg))
    return abar,sab,eyr,kut
cases=[("A 10x8x4 a=0.5",(10,8,4),[.5]*6),
       ("B 20x16x3 floor+ceil 0.9, walls 0.02",(20,16,3),[.02]*4+[.9]*2),
       ("C 6x5x3 uniform 0.7",(6,5,3),[.7]*6),
       ("D 6x5x3 uniform 0.9",(6,5,3),[.9]*6)]
R={}
for name,L,af in cases:
    tt=traced_t60(L,af); ab,sab,eyr,kut=formulas(L,af)
    R[name[0]]=(tt,sab,eyr,kut)
    print("%s abar=%.2f traced=%.3f Sabine %+.1f%% Eyring %+.1f%% Kuttruff %+.1f%%"%(name,ab,tt,100*(sab/tt-1),100*(eyr/tt-1),100*(kut/tt-1)))
e=lambda k,i:100*(R[k][i]/R[k][0]-1)
okA=15<=e('A',1)<=30 and -17<=e('A',2)<=-5 and abs(e('A',3))<5
okB=e('B',2)<-25 and abs(e('B',1))<abs(e('B',2))
okC=abs(e('C',2))<abs(e('C',1)) and abs(e('D',2))<abs(e('D',1))
print("RESULT: %s A=%s B=%s C/D(Eyring closer in uniform dead rooms)=%s; A Sabine %+.0f%% Eyring %+.0f%%; B Sabine %+.0f%% Eyring %+.0f%%; D Sabine %+.0f%% Eyring %+.0f%%"%("PASS" if (okA and okB and okC) else "FAIL",okA,okB,okC,e('A',1),e('A',2),e('B',1),e('B',2),e('D',1),e('D',2)))
