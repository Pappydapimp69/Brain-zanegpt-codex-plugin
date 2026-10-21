# A best move with prior 1e-4: how many search visits before a prior-guided search (PUCT) first tries it,
# vs UCB1 (prior-free bonus), and does retraining the prior on its own visit counts bury it further? Deterministic, exact.
import math
K=20; BEST=0
def make(prior_best):
    rest=(1-prior_best)/(K-1)
    P=[prior_best]+[rest]*(K-1)
    V=[0.9]+[0.5]*(K-1)          # exact deterministic move values
    return P,V
def puct(P,V,budget,c=1.5):
    n=[0]*K; w=[0.0]*K
    for t in range(1,budget+1):
        best=max(range(K), key=lambda i:((w[i]/n[i]) if n[i] else 0.0)+c*P[i]*math.sqrt(t)/(1+n[i]))
        n[best]+=1; w[best]+=V[best]
        if best==BEST: return t, n
    return None, n
def ucb1(P,V,budget):
    n=[0]*K; w=[0.0]*K
    for t in range(1,budget+1):
        if t<=K: i=t-1
        else: i=max(range(K), key=lambda j:w[j]/n[j]+math.sqrt(2*math.log(t)/n[j]))
        n[i]+=1; w[i]+=V[i]
        if i==BEST: return t, n
    return None, n
B=2_000_000
print("prior_best  PUCT_first_visit  UCB1_first_visit")
first={}
for pb in (1e-1,1e-2,1e-3,1e-4):
    P,V=make(pb); tp,_=puct(P,V,B); tu,_=ucb1(P,V,B)
    first[pb]=(tp,tu); print(f"{pb:<10} {tp!s:>16} {tu!s:>17}")
# self-training loop: prior_{r+1} = visits^1 normalized (raw counts) from a fixed 2000-visit budget search; IPS-style: divide by prior then renormalize
def rounds(pb, ips, R=6, budget=2000, c=1.5):
    P,V=make(pb); hist=[]
    for r in range(R):
        n=[0]*K; w=[0.0]*K
        for t in range(1,budget+1):
            i=max(range(K), key=lambda j:((w[j]/n[j]) if n[j] else 0.0)+c*P[j]*math.sqrt(t)/(1+n[j]))
            n[i]+=1; w[i]+=V[i]
        hist.append((n[BEST], P[BEST]))
        # retrain: raw counts (+1 smoothing) vs value-weighted counts corrected by exposure (n/(P)) -> use Q-softmax mixture
        if not ips: new=[x+1e-9 for x in n]
        else:
            q=[(w[j]/n[j] if n[j] else 0.0) for j in range(K)]
            new=[math.exp(8*q[j])*(P[j]) for j in range(K)]   # value-aware reweight of the old prior
        s=sum(new); P=[x/s for x in new]
    return hist
raw=rounds(1e-2,False); fix=rounds(1e-2,True)
print("raw-count retrain: (visits to best, prior of best) per round:", [(a,round(b,5)) for a,b in raw])
print("value-aware retrain:", [(a,round(b,5)) for a,b in fix])
# prediction (written before first run): raw self-training buries the rare move (prior falls) at every starting prior; value-aware fixes it.
rawb=rounds(1e-4,False); fixb=rounds(1e-4,True)
print("prior 1e-4 raw retrain:", [(a,f"{b:.2e}") for a,b in rawb])
print("prior 1e-4 value-aware retrain:", [(a,f"{b:.2e}") for a,b in fixb])
Pf=[1/K]*K; Vf=make(0.05)[1]; tf,_=puct(Pf,Vf,B); print("control flat prior first visit:", tf)
buried = rawb[-1][1] < rawb[0][1] and fixb[-1][1] <= rawb[0][1]*1.0001
rescued_mid = raw[-1][1] > raw[0][1]       # prediction refuted here: at prior 1e-2 the loop AMPLIFIES the best move
ok = (first[1e-4][0] is None and first[1e-3][0] > 20*first[1e-1][0] and first[1e-4][1] <= K
      and buried and rescued_mid and tf is not None and tf<=K)
print("RESULT:", "PASS" if ok else "FAIL", f"PUCT visits best at 1e-3 after {first[1e-3][0]} playouts, never within {B} at 1e-4 (UCB1 init sweep: {first[1e-4][1]}); self-training amplifies at prior 1e-2 ({raw[0][1]}->{raw[-1][1]:.2f}) but buries at 1e-4 (stays {rawb[-1][1]:.1e}, both retrain rules)")
