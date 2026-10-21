# Does a rule card stating a harm ceiling let escalation land at the framing's distance? (benign-violation x matching-distance x rule-card)
# Prediction (before run): over 400 seeded 8-beat sketches at true distance D=6, the card (clamp severity to stated ceiling=D)
# lifts the share of beats that are both violating (sev>=2) and benign (sev<=D) from <=55% to >=90%, and the mean funny score
# (sum of sev over funny beats) by >=25%. Hidden assumption: the writer's stated ceiling equals the true distance.
# Break: ceiling stated D+3 too high -> gain should vanish; D=1 -> zero funny (nothing violates).
import random
def sketch(rng, D, ceiling, n=8):
    funny=0; score=0
    for t in range(n):
        s = 1 + t*1.2 + rng.uniform(-2,2)           # go-big schedule with noise
        s = max(1,min(10,round(s)))
        if ceiling is not None: s=min(s,ceiling)
        if 2<=s<=D: funny+=1; score+=s
    return funny/n, score
def run(D, ceiling, N=400, seed=7):
    rng=random.Random(seed); f=sc=0
    for _ in range(N):
        a,b=sketch(rng,D,ceiling); f+=a; sc+=b
    return f/N, sc/N
res={}
res["nocard_D6"]=run(6,None); res["card_D6"]=run(6,6)
res["card_over_D6"]=run(6,9); res["card_D1"]=run(1,1); res["nocard_D1"]=run(1,None); res["card_D9"]=run(9,9); res["nocard_D9"]=run(9,None)
for k,v in res.items(): print(k,"funny share %.3f score %.2f"%v)
sh0,sc0=res["nocard_D6"]; sh1,sc1=res["card_D6"]
lift=sc1/sc0-1
ok = sh0<=0.55 and sh1>=0.90 and lift>=0.25 and res["card_over_D6"][0]<sh1-0.1 and res["card_D1"][0]==0
print("RESULT:","PASS" if ok else "FAIL","D6 share %.3f->%.3f, score lift %.0f%%, over-stated ceiling share %.3f, D1 share %.3f, D9 share %.3f->%.3f"%(sh0,sh1,lift*100,res["card_over_D6"][0],res["card_D1"][0],res["nocard_D9"][0],res["card_D9"][0]))
