"""Prediction (before run): on a 1/2 in poly lateral (ID 0.600 in, Hazen-Williams C=140) with emitters every 12 in rated 1.0 gph at 25 psi (q=q0*sqrt(P/25)),
(1) at 25 psi inlet the max run holding flow uniformity (min/max emitter flow) >= 90% is well over 100 emitters (>100 ft) with 1.0 gph emitters but shrinks when emitters are bigger;
(2) at an unregulated 60 psi inlet the per-emitter flow is ~1.55x at the head, the 5 gpm zone budget is hit at fewer emitters, yet uniformity along the SAME lateral is BETTER (relative drop smaller);
(3) so 'regulate to 20-25 psi' is a hardware/flow-budget rule, not a uniformity rule: uniformity gets worse at low inlet pressure; (4) pressure-compensating emitters (flat q) remove the length limit from uniformity.
Built to break: (2) goes against the intuition that high pressure hurts evenness. Deterministic, stdlib."""
import math
D=0.600; C=140.0; SP_FT=1.0
def hf_psi(q_gpm, L_ft):  # Hazen-Williams, psi
    return 4.52*(q_gpm**1.852)/((C**1.852)*(D**4.87))*L_ft
def lateral(inlet_psi, n, q0_gph=1.0, comp=False):
    """walk from the far end back: flows needed at each segment depend on pressure -> solve by fixed-point on inlet."""
    # iterate: guess pressures, compute flows, recompute pressures from inlet
    P=[inlet_psi]*n
    for _ in range(200):
        q=[q0_gph if comp else q0_gph*math.sqrt(max(p,0.01)/25.0) for p in P]   # gph
        cum=0.0; newP=[]; 
        down=[sum(q[i:])/60.0 for i in range(n)]    # gpm flowing in segment feeding emitter i
        p=inlet_psi
        for i in range(n):
            p-=hf_psi(down[i],SP_FT); newP.append(p)
        if max(abs(a-b) for a,b in zip(P,newP))<1e-9: break
        P=newP
    q=[q0_gph if comp else q0_gph*math.sqrt(max(p,0.01)/25.0) for p in P]
    return P,q
def uni(q): return min(q)/max(q)
def max_n(inlet, q0, comp=False, target=0.90, cap=2000):
    best=0
    for n in range(1,cap+1):
        P,q=lateral(inlet,n,q0,comp)
        if P[-1]<=1 : break
        if uni(q)>=target: best=n
        else: break
    return best
res={}
for inlet in (25,60):
    for q0 in (0.5,1.0,2.0):
        res[(inlet,q0)]=max_n(inlet,q0)
        print(f"inlet {inlet} psi q0 {q0} gph: max emitters at uniformity>=90% = {res[(inlet,q0)]}")
# flow budget: 5 gpm zone
head=lambda inlet,q0: q0*math.sqrt(inlet/25.0)
bud={inlet: int(5*60/head(inlet,1.0)) for inlet in (25,60)}
print("5 gpm budget emitters (head flow, 1 gph):", bud)
P25,q25=lateral(25,100); P60,q60=lateral(60,100)
print(f"n=100: uniformity 25psi {uni(q25):.3f} tail psi {P25[-1]:.1f}; 60psi {uni(q60):.3f} tail psi {P60[-1]:.1f}; head flow ratio {q60[0]/q25[0]:.2f}")
Pc,qc=lateral(25,500,1.0,True); print(f"compensating n=500 uniformity {uni(qc):.3f}")
# low-pressure failure: inlet 10 psi
low=max_n(10,1.0); print("inlet 10 psi max emitters at 90%:",low)
c1=res[(25,1.0)]>100 and res[(25,2.0)]<res[(25,1.0)]<res[(25,0.5)]
c2=bud[60]<bud[25] and uni(q60)>uni(q25) and res[(60,1.0)]>res[(25,1.0)]
c3=low<res[(25,1.0)]
c4=uni(qc)>0.999
print(("RESULT: PASS" if (c1 and c2 and c3 and c4) else "RESULT: FAIL")+f" max emitters 25psi q1.0={res[(25,1.0)]}, 60psi q1.0={res[(60,1.0)]}, 10psi={low}; budget 5gpm 25psi={bud[25]} 60psi={bud[60]}; uniformity n=100 25psi {uni(q25):.3f} 60psi {uni(q60):.3f}; flags {c1,c2,c3,c4}")
