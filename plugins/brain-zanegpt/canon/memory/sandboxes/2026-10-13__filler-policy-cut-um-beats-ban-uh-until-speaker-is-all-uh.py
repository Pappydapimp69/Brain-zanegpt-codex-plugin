# Filler-policy sandbox for a 1,000-word talk. Prediction (written before running):
# cut-um saves more net seconds than ban-uh whenever the speaker's um share is >= 0.4 at any
# filler duration >= 0.1 s; ban-uh only wins for (near) all-uh speakers; the uh comprehension
# aid (47 ms/uh, um = 0) never outweighs an uh's own duration unless duration < 47 ms.
WORDS=1000; RATE=2.56/100       # fillers per word (Bortfeld et al. 2001 base rate)
AID=0.047                        # s faster word recognition after an uh (um: none)
P_UH=0.05; UM_PAUSE_X=5.7        # assumed uh pause (s); um expected pause 5.7x uh's (kernel)
def net_saved(policy,d,uh_share):
    n=WORDS*RATE; nuh=n*uh_share; num=n-nuh
    d_uh=d; d_um=d+(UM_PAUSE_X-1)*P_UH
    saved=0.0
    if policy in("ban-uh","cut-both"): saved+=nuh*d_uh-nuh*AID   # time freed minus aid lost
    if policy in("cut-um","cut-both"): saved+=num*d_um
    return saved
def best(d,share): return max(("ban-uh","cut-um"),key=lambda p:net_saved(p,d,share))
# S1 default card values
n=WORDS*RATE; print("S1 fillers",round(n,1),"aid total all-uh",round(n*AID,2),"s")
s1=n*AID<1.5
# S2 sweep: cut-um vs ban-uh
loses=[(d,s) for d in(0.1,0.2,0.3,0.5) for s in(0.1,0.2,0.3,0.4) if best(d,s)!="cut-um"]
print("S2 cut-um fails to win at (d,uh_share) with share<=0.4:",loses); s2=not loses
# S3 BREAK: all-uh speaker flips to ban-uh; find crossover share at d=0.3
cross=None
for k in range(0,101):
    s=k/100
    if best(0.3,s)=="ban-uh": cross=s;break
print("S3 ban-uh first wins at uh_share",cross); s3=cross is not None and cross>0.5
# S4 uh pays its own way only when duration < aid
paying=[d for d in(0.02,0.04,0.047,0.05,0.1) if net_saved("ban-uh",d,1.0)<=0]
print("S4 durations where banning uh does not save time:",paying); s4=paying==[0.02,0.04,0.047]
ok=s1 and s2 and s3 and s4
print("RESULT: %s cut-um beats ban-uh for uh_share<=0.4 at d>=0.1s (s2=%s); ban-uh wins only from uh_share=%s at d=0.3 (s3=%s); uh aid is %.2fs/talk (s1=%s); uh pays its way only if d<=47ms (s4=%s)"%("PASS" if ok else "FAIL",s2,cross,s3,n*AID,s1,s4))
