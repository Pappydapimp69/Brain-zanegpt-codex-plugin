# Learning-styles matching (kernel L) vs interleaving (kernel I) vs probing a learner's best method (E191 power logic). Exact arithmetic.
from fractions import Fraction as F
from math import comb
BLOCKED,INTER=F(38,100),F(72,100)     # delayed-test scores from the interleaving kernel (Rohrer & Taylor style numbers)
def policy_scores(m, q):
    """q = chance the style label is right; matching adds m when modality matches the learner's true style."""
    uniform_inter = INTER                              # same modality for all, interleaved
    match_blocked = BLOCKED + m*(2*q-1)                      # style-matched modality, blocked
    both = INTER + m*(2*q-1)
    return uniform_inter, match_blocked, both

print("A) breakeven m (match-blocked beats uniform interleaving) with a perfect label q=1:")
for q in (F(1),F(3,4),F(1,2)):
    be = (INTER-BLOCKED)/(2*q-1) if q>F(1,2) else None
    print(f"   q={float(q)}: need m > {float(be) if be else 'never'}")
assert (INTER-BLOCKED)==F(34,100)
def sym(m,q): return m*(2*q-1)
print("B) symmetric mismatch loss: net gain m*(2q-1); coin-flip label (q=1/2) gain =",float(sym(F(1,5),F(1,2))))
assert sym(F(1,5),F(1,2))==0
# C) sweep m from 0 to 0.5: where does each policy win?
wins={}
for mi in range(0,51):
    m=F(mi,100)
    u,mb,both=policy_scores(m,F(1))
    w = "interleave" if u>mb else "match" if mb>u else "tie"
    wins.setdefault(w,[]).append(mi)
print("C) m where interleaving beats matching:",wins["interleave"][0],"-",wins["interleave"][-1],"/ matching wins from",wins.get("match",[None])[0])
# D) can you even find a learner's better method? n probes per method, per-probe success p+/-m/2, majority/more-hits rule, ties broken coin (1/2)
def p_correct(m,n):
    pa=F(1,2)+m/2; pb=F(1,2)-m/2
    tot=F(0)
    for a in range(n+1):
        for b in range(n+1):
            pr=F(comb(n,a))*pa**a*(1-pa)**(n-a)*F(comb(n,b))*pb**b*(1-pb)**(n-b)
            tot+= pr if a>b else pr/2 if a==b else 0
    return tot
need={}
for m in (F(1,10),F(1,5),F(1,3)):
    for n in range(1,160):
        if p_correct(m,n)>=F(9,10): need[m]=n; break
    print(f"D) m={float(m):.2f}: probes per method for 90% correct pick = {need.get(m)}")
assert need[F(1,3)]<need[F(1,5)]<need[F(1,10)]
# E) joint: per-learner probing budget B (probes/method) vs one-size interleave when m=0.2: net score
for B in (1,3,6,12,24):
    pc=p_correct(F(1,5),B); net=BLOCKED+F(1,5)*(pc-(1-pc))/1   # chosen best method gives +m/2 vs worst -m/2 ... centered
    print(f"E) B={B}: P(correct pick)={float(pc):.3f}")
print("RESULT: PASS matching a blocked lesson to a true style only beats interleaving for everyone when the matching effect m exceeds 0.34 (perfect label) and a coin-flip label gives net 0; finding a learner's better method to 90%% takes %d, %d and %d probes per method at m=0.1, 0.2 and 0.33" % (need[F(1,10)],need[F(1,5)],need[F(1,3)]))
