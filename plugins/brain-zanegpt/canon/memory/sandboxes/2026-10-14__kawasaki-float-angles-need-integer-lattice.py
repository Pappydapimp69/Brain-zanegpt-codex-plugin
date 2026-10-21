# Prediction (first): degree-4 vertices built to be flat-foldable (a, b, 180-a, 180-b) with a,b on a 0.3-degree grid
# (359,001 patterns, all foldable by construction). Float '==' on the alternating sum or on the accumulated
# reflection map wrongly rejects a large share (>10%); a 1e-9 tolerance rejects 0; integer tenths-of-degree exact
# arithmetic rejects 0. Built to BREAK: a tolerance of 0.3 degrees (the grid step) wrongly ACCEPTS non-foldable
# neighbours (a+0.3 perturbed vertex), the origami/E1 failure mode in the float domain.
STEP=3                       # tenths of a degree -> 0.3 degrees
N=600
def sectors_float(a,b): return [a*0.1,b*0.1,(1800-a)*0.1,(1800-b)*0.1]
def alt_float(s): return s[0]+s[2]
def reflect_float(s):
    creases=[0.0]
    for x in s[:-1]: creases.append(creases[-1]+x)
    mm,sg=0.0,1
    for t in creases: sg,mm=-sg,(2*t-mm)
    return sg==1 and mm%360.0==0.0
def reflect_int(s):
    creases=[0]
    for x in s[:-1]: creases.append(creases[-1]+x)
    mm,sg=0,1
    for t in creases: sg,mm=-sg,(2*t-mm)
    return sg==1 and mm%3600==0
tot=0;eq_rej=0;refl_rej=0;tol_rej=0;int_rej=0;tol3_acc=0;perturbed=0
for i in range(1,N):
    for j in range(1,N):
        a,b=i*STEP,j*STEP
        if a>=1800 or b>=1800: continue
        tot+=1
        s=sectors_float(a,b)
        eq_rej+= alt_float(s)!=180.0
        refl_rej+= not reflect_float(s)
        tol_rej+= abs(alt_float(s)-180.0)>1e-9
        si=[a,b,1800-a,1800-b]
        int_rej+= not(reflect_int(si) and si[0]+si[2]==1800)
        # perturb: move 0.3 degrees from sector 3 to sector 4 -> alternating sum off by 0.3 -> not foldable
        p=[a,b,1800-a-3,1800-b+3]
        perturbed+=1
        tol3_acc+= abs((p[0]+p[2])/10.0-180.0)<=0.3+1e-9 and False or (abs((p[0]+p[2])/10.0-180.0)<=0.3+1e-9)
print(f"patterns {tot}: float '==' alt-sum rejects {eq_rej} ({eq_rej/tot:.3f}), float reflection-identity rejects {refl_rej} ({refl_rej/tot:.3f}), tol 1e-9 rejects {tol_rej}, integer exact rejects {int_rej}")
print(f"perturbed non-foldable patterns {perturbed}: tolerance 0.3 degrees accepts {tol3_acc}")
ok=eq_rej/tot>0.10 and tol_rej==0 and int_rej==0 and refl_rej/tot>0.10 and tol3_acc==perturbed
print("RESULT:","PASS" if ok else "FAIL",f"float == rejects {eq_rej}/{tot} foldable vertices, float reflection {refl_rej}/{tot}, 1e-9 tol and integer tenths 0; grid-step tolerance accepts {tol3_acc}/{perturbed} non-foldable")
