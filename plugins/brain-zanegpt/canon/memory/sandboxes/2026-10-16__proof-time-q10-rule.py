# Sandbox: dough proofing time versus temperature. Rate = Q10 rule up to an optimum, then a heat-kill falloff.
# Rule under test: time(T) = time(Tref) * 2**((Tref-T)/10) inside the working window.
Q10=2.0; TREF=24.0; BASE_H=4.0; TOPT=35.0; TDEAD=45.0
def rate(T):
    r=Q10**((T-TREF)/10)/BASE_H           # doublings of volume per hour, normalised so TREF takes BASE_H
    if T>TOPT: r*=max(0.0,(TDEAD-T)/(TDEAD-TOPT))
    return r
def time_to_rise(T,dt=0.001,cap=100.0):
    x=0.0;t=0.0
    while x<1.0 and t<cap: x+=rate(T)*dt;t+=dt
    return t if x>=1.0 else float("inf")
def rule(T): return BASE_H*2**((TREF-T)/10)
rows=[]
for T in(4,14,24,30,35,40,42):
    m=time_to_rise(T);r=rule(T);rows.append((T,m,r))
    print("T=%2d model=%7.2fh rule=%6.2fh ratio=%s"%(T,m,r,"inf" if m==float("inf") else "%.2f"%(m/r)))
inside=[(m/r) for T,m,r in rows if 4<=T<=35]
fridge=dict((T,m) for T,m,r in rows)[4]
hot=dict((T,(m,r)) for T,m,r in rows)[42]
ok = all(abs(x-1)<0.02 for x in inside) and abs(fridge-16)<0.1 and hot[0]/hot[1]>3
print("RESULT: %s window 4-35C within 2%% of rule (max dev %.3f), fridge 4C=%.2fh (rule 16h), 42C model %.2fh vs rule %.2fh (%.1fx slower)"%("PASS" if ok else "FAIL",max(abs(x-1) for x in inside),fridge,hot[0],hot[1],hot[0]/hot[1]))
