"""Sandbox: projectile range with quadratic drag vs vacuum (stdlib RK4, deterministic)."""
import math
G=9.81
def rng(v0, ang, k, dt=0.002):
    """k = drag per metre (c*rho*A/2m); a = -k*|v|*v. Returns landing range on flat ground (linear interpolation)."""
    a=math.radians(ang); x=0.0; y=0.0; vx=v0*math.cos(a); vy=v0*math.sin(a)
    def acc(vx,vy):
        s=math.hypot(vx,vy); return -k*s*vx, -G-k*s*vy
    while True:
        a1x,a1y=acc(vx,vy)
        k2x,k2y=acc(vx+0.5*dt*a1x,vy+0.5*dt*a1y)
        k3x,k3y=acc(vx+0.5*dt*k2x,vy+0.5*dt*k2y)
        k4x,k4y=acc(vx+dt*k3x,vy+dt*k3y)
        nx=x+dt*(vx+0.5*dt*a1x); ny=y+dt*(vy+0.5*dt*a1y)
        nvx=vx+dt*(a1x+2*k2x+2*k3x+k4x)/6; nvy=vy+dt*(a1y+2*k2y+2*k3y+k4y)/6
        if ny<0 and y>=0 and nvy<0 or (ny<0 and vy<0):
            f=y/(y-ny) if y!=ny else 0; return x+f*(nx-x)
        x,y,vx,vy=nx,ny,nvx,nvy
def best(v0,k):
    angs=[a/2 for a in range(40,181)]   # 20..90 step 0.5 -> use 20..60
    angs=[a/2 for a in range(40,121)]
    rs=[(rng(v0,a,k),a) for a in angs]; return max(rs)
res={}
for v0,k in ((30,0.0),(30,0.002),(30,0.01),(60,0.002),(60,0.01)):
    r,a=best(v0,k); res[(v0,k)]=(r,a); 
    print(f"v0={v0} k={k}: best angle {a:.1f} deg, range {r:.1f} m, vacuum range at 45 deg {v0*v0/G:.1f} m")
vac=res[(30,0.0)]
mono=[res[(30,0.0)][1],res[(30,0.002)][1],res[(30,0.01)][1]]
ok = abs(vac[1]-45)<=0.5 and abs(vac[0]-30*30/G)<1 and mono[0]>mono[1]>mono[2] and res[(30,0.01)][0] < 0.7*30*30/G and res[(60,0.01)][1] < res[(30,0.01)][1]
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" vacuum best {vac[1]:.1f} deg matches v^2/g {vac[0]:.1f} m; drag k=0.002 {mono[1]:.1f} deg, k=0.01 {mono[2]:.1f} deg with range {res[(30,0.01)][0]:.1f} of {30*30/G:.1f} m; at 60 m/s k=0.01 best {res[(60,0.01)][1]:.1f} deg")
