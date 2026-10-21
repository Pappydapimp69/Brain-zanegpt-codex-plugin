# Beat severity 1..5, framing distance d 1..5. Severe beats (s>=3) are funny only if s<=d, value s.
# Mild beats (s<=2) are funny up close and go flat when distant: value s*(1 if d<=2 else 0 if d>=4 else 0.5).
# Harm (s>d) scores -2. A mild beat above d cannot occur (s<=2<=d only fails at d=1,s=2 -> harm).
def beat(s,d):
    if s>d: return -2
    if s<=2: return s*(1.0 if d<=2 else 0.5 if d==3 else 0.0)
    return s
def sk(sched,d): return sum(beat(s,d) for s in sched)
RAMP=[1,2,3,4,5,5]
def ceiling(d): return [min(s,d) for s in RAMP]
def banded(d):                       # ceiling plus floor: when d>=4 mild beats are replaced by the severity ceiling
    c=ceiling(d)
    return [max(x,3) if d>=4 else x for x in c]
tot_c=tot_b=0; diffs=[]
for d in range(1,6):
    c,b=sk(ceiling(d),d),sk(banded(d),d); tot_c+=c; tot_b+=b; diffs.append(b-c)
    print(f"d={d} ceiling-only={c} ceiling+floor={b}")
tie_low = diffs[0]==0 and diffs[1]==0
wins_high = diffs[3]>0 and diffs[4]>0
# BREAK: a floor that is applied at every distance hurts close framings
bad=[sk([max(x,3) for x in ceiling(d)],d) for d in range(1,6)]
hurts_low = bad[0]<sk(ceiling(1),1)
print("always-floor:",bad)
ok=tie_low and wins_high and hurts_low and tot_b>tot_c
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" floor gain by distance {diffs}, total {tot_c}->{tot_b}; always-on floor lost {sk(ceiling(1),1)-bad[0]} points at d=1")
