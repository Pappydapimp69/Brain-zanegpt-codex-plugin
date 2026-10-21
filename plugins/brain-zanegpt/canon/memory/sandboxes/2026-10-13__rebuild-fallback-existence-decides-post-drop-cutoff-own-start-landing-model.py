# Own fixture: starts s are ticks where (s*m) % M < w (multiplier-scrambled availability).
# A press at lag d from start s lands at s+d; it is legal if base(s+d) or fallback(s+d).
# Nominal-period lag P is dropped; cutoff = largest remaining lag in 1..D with some legal press.
# Fallback kinds: none / always-on / even-ticks-only.
M=23; D=18; P=12; HORIZON=3*M
def base(t,m,w,o): return ((t+o)*m)%M < w
def cutoff(m,w,o,fb):
    best=0
    for d in range(1,D+1):
        if d==P: continue
        for s in range(HORIZON):
            if not base(s,m,w,o): continue
            t=s+d
            legal=base(t,m,w,o) or (fb=='always') or (fb=='even' and t%2==0)
            if legal: best=max(best,d);break
    return best
sets=0;ev_eq=0;none_below=0;z_below=0;y_below=0;mism=0
for m in range(1,M):
    for w in range(2,12):
        for o in range(0,M,5):
            sets+=1
            X=cutoff(m,w,o,'none');Y=cutoff(m,w,o,'always');Z=cutoff(m,w,o,'even')
            mx=max(d for d in range(1,D+1) if d!=P)
            ev_eq+= (Y==Z); mism+=(Y!=Z)
            none_below+= X<mx; y_below+= Y<mx; z_below+= Z<mx
print('sets',sets,'even==always',ev_eq,'mismatch',mism,'no-fallback below max',none_below,'always below max',y_below,'even below max',z_below)
ok = mism==0 and y_below==0 and z_below==0 and none_below>0
print('RESULT: %s even==always in %d/%d sets, no-fallback below max in %d, always/even below max %d/%d'%('PASS' if ok else 'FAIL',ev_eq,sets,none_below,y_below,z_below))
