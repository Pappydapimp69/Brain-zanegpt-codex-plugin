# Toy two-channel caregiver model (ASSUMED constants, deterministic). Channels: distress (drains, scales with resonance
# with the patient's group) and compassion (replenishes, capped, same engagement for every group).
# PREDICTION (before run): across loads E=2..40 and distress shares a=0.5..0.9, switching mode (a -> 0.2) prevents burnout in
# strictly more cases than halving engagement (scale 0.5); mode shift keeps mean engagement higher; the in-group/out-group
# engagement gap is smaller after the mode shift than at baseline; and the mode shift fails at the highest loads (replenish cap).
from fractions import Fraction as F
RES={"in":F(1),"out":F(3,10)}; D=F(1); R=F(3,5); CAP=F(4); REC=F(3); R0=F(100); T=400
def burns(E,a,scale):
    res=R0
    for _ in range(T):
        drain=sum(E/2*a*D*RES[g]*scale for g in RES)
        rep=min(CAP,E*(1-a)*R*scale)+REC
        res=min(R0,res-drain+rep)
        if res<=0: return True
    return False
def engagement(a,scale): return {g:scale*(a*RES[g]+(1-a)) for g in RES}
cases=[(E,F(k,10)) for E in range(2,81,2) for k in range(5,10)]
base_burn=[(E,a) for E,a in cases if burns(E,a,1)]
less=[c for c in base_burn if not burns(c[0],c[1],F(1,2))]
shift=[c for c in base_burn if not burns(c[0],F(1,5),1)]
print("cases",len(cases),"burn at baseline",len(base_burn),"fixed by halving care",len(less),"fixed by mode shift",len(shift))
hi=[c for c in base_burn if c[0]>=40]; print("burning at E>=40:",len(hi),"still burning after shift:",sum(burns(E,F(1,5),1) for E,a in hi))
for name,a,s in (("baseline a=.8",F(4,5),F(1)),("care-less x0.5",F(4,5),F(1,2)),("mode shift a=.2",F(1,5),F(1))):
    e=engagement(a,s); mean=(e["in"]+e["out"])/2; print(name,"engagement in %.3f out %.3f gap %.3f mean %.3f"%(float(e["in"]),float(e["out"]),float(e["in"]-e["out"]),float(mean)))
eb=engagement(F(4,5),F(1)); es=engagement(F(1,5),F(1)); el=engagement(F(4,5),F(1,2))
ok=len(shift)>len(less) and (es["in"]+es["out"])>(el["in"]+el["out"]) and (es["in"]-es["out"])<(eb["in"]-eb["out"]) and sum(burns(E,F(1,5),1) for E,a in hi)>0
first_fail=min(E for E,a in cases if burns(E,F(1,5),1))
print("RESULT: %s of %d baseline burnout cases mode shift fixes %d, halving care fixes %d; gap %.3f->%.3f, mean engagement %.3f vs %.3f; shift first burns at E=%d (my guess of E>=36 missed), %d of %d burners at E>=40 (assumed constants)"%("PASS" if ok else "FAIL",len(base_burn),len(shift),len(less),float(eb["in"]-eb["out"]),float(es["in"]-es["out"]),float((es["in"]+es["out"])/2),float((el["in"]+el["out"])/2),first_fail,sum(burns(E,F(1,5),1) for E,a in hi),len(hi)))
first_fail=min(E for E,a in cases if burns(E,F(1,5),1))
