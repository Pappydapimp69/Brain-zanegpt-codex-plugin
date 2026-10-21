"""Sandbox: 1D yard x=0..20 (integer cells, 1 mosquito per cell x 10), person at x=10 emitting CO2 strength 1.
A decoy at x=D emits strength S. A mosquito moves to the source with the highest S/(1+dist)^2 (ties -> person);
if it lands on the decoy it is killed with probability = KILL (fractional: that fraction of mosquitoes removed), the
rest stay at the decoy and re-choose next round from there. Bites = mosquito-rounds that choose the person.
Prediction (before running): decoy at x=1 (far), S=3, KILL=0 cuts round-1 bites vs no decoy but over 5 rounds the
bites return to within 10% of the no-decoy count, because unkilled mosquitoes re-choose from the decoy and find the
person nearer than any exit; a near decoy (x=8, 2 cells from person) with KILL=0 makes bites WORSE than no decoy over 5
rounds; KILL=0.5 at x=1 keeps the 5-round bites at least 40% under no decoy. Wrong if the far decoy still cuts 5-round bites >25%."""
PERSON=10
def choose(x, decoy, r=0):
    p=1/(1+abs(x-PERSON))**2
    if decoy is None: return "p"
    D,S,_,fuel=decoy
    if r>=fuel: return "p"          # decoy out of CO2: everything left chooses the person
    d=S/(1+abs(x-D))**2
    return "d" if d>p else "p"
def sim(decoy, rounds=5):
    pos=[(x,10.0) for x in range(21)]   # (cell, count)
    bites=0.0; first=0.0
    for r in range(rounds):
        nxt={}
        for x,n in pos:
            c=choose(x,decoy,r)
            if c=="p":
                bites+=n
                if r==0: first+=n
                nxt[PERSON]=nxt.get(PERSON,0)+n      # lingers at person
            else:
                kill=decoy[2]
                nxt[decoy[0]]=nxt.get(decoy[0],0)+n*(1-kill)
        pos=list(nxt.items())
    return bites,first
base=sim(None)
# FIRST RUN (recorded): prediction refuted. A decoy stronger than the person is an absorbing sink in this model
# (mosquitoes at the decoy re-choose the decoy), so far no-kill cut five-round bites to 0.67x, not back to 1.0x.
# Added scenarios: decoy fuel runs out (built to BREAK the sink), and a weak decoy S=0.5.
S1={"none":None,"far,S3,no kill":(1,3,0.0,99),"near,S3,no kill":(8,3,0.0,99),"far,S3,kill .5":(1,3,0.5,99),
    "far,S3,fuel 2 rounds":(1,3,0.0,2),"far,S0.5,no kill":(1,0.5,0.0,99),"far,S3,fuel 2,kill .5":(1,3,0.5,2)}
R={k:sim(v) for k,v in S1.items()}
for k,v in R.items(): print(f"{k:22s} round1 bites {v[1]:6.1f} five-round bites {v[0]:7.1f} ({v[0]/base[0]:.2f}x)")
f=R["far,S3,no kill"]; o=R["far,S3,fuel 2 rounds"]; w=R["far,S0.5,no kill"]; k=R["far,S3,fuel 2,kill .5"]
checks=[f[0]<0.8*base[0],                      # sink holds while fueled (refutes original expectation)
        R["near,S3,no kill"][0]<f[0],          # nearer decoy has the bigger basin
        R["far,S3,kill .5"][0]<=f[0],          # killing never makes it worse
        f[0]<w[0]<base[0],                     # weak decoy captures only its own corner (second slip: I first expected nothing)
        o[0]>f[0] and o[1]==f[1],
        k[0]<o[0]]                             # killing while fueled shrinks the reservoir released later              # fuel out: same round 1, more total bites (reservoir released)
print("checks",checks)
print("RESULT:","PASS" if all(checks) else "FAIL",f"five-round bites vs none: fueled far {f[0]/base[0]:.2f}x, near {R['near,S3,no kill'][0]/base[0]:.2f}x, weak decoy {w[0]/base[0]:.2f}x, fuel out after 2 rounds {o[0]/base[0]:.2f}x (round-1 {o[1]:.0f} same as fueled), fuel out with kill .5 {k[0]/base[0]:.2f}x")
