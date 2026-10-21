# Independent implementation: landing sets by whole-word shift algebra, land_L = ((~B | (B >> L)) & ones(T)) << L, base 301.
# PREDICTION (before run): recorded P11 215/11 at N=P and 460/11 at N=2P and P12 25 and 53 reproduce; flats of the one-period
# average are exactly [P,2P] for P=11..15 (composite 12, 14, 15 included); a base-0 control differs from the recorded value.
from itertools import combinations
from fractions import Fraction
def shadows(P,T,N):
    sh=0; ones=(1<<T)-1
    for w in range(1,P):
        B=sum(1<<t for t in range(T+N+1) if t%P<w)
        land={L:(((~B)|(B>>L))&ones)<<L for L in range(1,N+1)}
        for x,y in combinations(range(1,N+1),2):
            cut = y if land[y] & ~land[x] else (x if land[x] else 0)
            lg = y if land[y] else (x if land[x] else 0)
            sh += lg!=cut
    return sh
def avg(P,N,base): return Fraction(sum(shadows(P,base+r,N) for r in range(P)),P)
ok=True
rec={(11,11):Fraction(215,11),(11,22):Fraction(460,11),(12,12):Fraction(25),(12,24):Fraction(53)}
for (P,N),v in rec.items():
    a=avg(P,N,301); print("P",P,"N",N,"avg",a,"recorded",v,a==v); ok&=a==v
for P in (13,14,15):
    top=2*P+1; av={N:avg(P,N,301) for N in range(P-2,top+1)}
    flats=[N for N in range(P-1,top+1) if av[N]==av[N-1]]
    print("P",P,"flats",flats); ok&=flats==[P,2*P]
ctl=avg(11,11,0); print("base-0 control P11 N=11:",ctl,"differs",ctl!=Fraction(215,11)); ok&=ctl!=Fraction(215,11)
print("RESULT: %s shift-algebra implementation at base 301 reproduces P11 215/11 460/11, P12 25 53, flats exactly [P,2P] for P13-P15, base-0 control %s"%("PASS" if ok else "FAIL",ctl))
