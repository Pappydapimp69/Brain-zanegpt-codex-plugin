# Own rebuild: engine-first vs topic-first assignment with 8 engines. Stdlib only, deterministic.
# Prediction (before run): P(some engine >=3 in 10 uniform draws over 8) between 0.6 and 0.85;
# round-robin max = ceil(k/8) for k=1..24; no batch of 9+ can have all-distinct engines.
import random
from math import ceil, factorial
E=8
def exact_p_max_ge3(k):
    # P(max count <=2) by counting compositions: sum over j pairs, i singles
    from math import comb
    tot=0
    for pairs in range(0,k//2+1):
        singles=k-2*pairs
        if pairs+singles>E: continue
        ways=comb(E,pairs)*comb(E-pairs,singles)*factorial(k)//(2**pairs)
        tot+=ways
    return 1-tot/E**k
rng=random.Random(20261015)
def mc(k,n=20000):
    hit=0
    for _ in range(n):
        c=[0]*E
        for _ in range(k): c[rng.randrange(E)]+=1
        hit+= max(c)>=3
    return hit/n
ex=exact_p_max_ge3(10); m=mc(10)
print("k=10 exact",round(ex,4),"mc",round(m,4))
rr_ok=True
for k in range(1,25):
    c=[0]*E
    for i in range(k): c[i%E]+=1
    if max(c)!=ceil(k/E): rr_ok=False
print("round-robin max==ceil(k/8) for k=1..24:",rr_ok)
# all-distinct probability by k: zero above 8 for any assignment
alld=[k for k in range(1,13) if k<=E]
p9=exact_p_max_ge3(9)
print("k=9 P(max>=3)",round(p9,4))
# BREAK: if the space is 12 engines the 8-cap disappears: round-robin over 12 keeps k=10 all distinct
print("12 engines, k=10 round-robin max",max(__import__('collections').Counter(i%12 for i in range(10)).values()))
ok = 0.6<=ex<=0.85 and abs(ex-m)<0.02 and rr_ok and max(__import__('collections').Counter(i%12 for i in range(10)).values())==1
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"k=10 topic-first P(max>=3) exact {ex:.3f} mc {m:.3f}; round-robin max=ceil(k/8) k=1..24 {rr_ok}; 12 engines k=10 max 1")
