# Premack gate (kernel A) x matching law (kernel B) x goal gradient (kernel C). Deterministic, no RNG.
from fractions import Fraction as F
T=50; BL,BH=F(5),F(45)   # bliss point from the Premack kernel: 5 min low-pref, 45 min high-pref
def best(r):
    """minimise (L-5)^2+(H-45)^2 s.t. H<=r*L, L+H<=T, L,H>=0; r = minutes of H access earned per minute of L (grid search, exact)."""
    bestd=None; bl=None
    for i in range(0,501):
        L=F(i,10)
        H=min(r*L, T-L)
        if H<0: continue
        # H can be anywhere in [0, min(rL, T-L)]; closest to bliss is min(BH, that)
        H=min(BH,H)
        d=(L-BL)**2+(H-BH)**2
        if bestd is None or d<bestd: bestd=d; bl=(L,H)
    return bl
print("A) gate ratio r -> (L,H) time chosen; ungated bliss =",(float(BL),float(BH)))
rows={}
for r in (F(1),F(2),F(3),F(5),F(8),F(9),F(12)):
    L,H=best(r); rows[r]=(L,H); print(f"  r={float(r):>4}: L={float(L):5.1f} (x{float(L/BL):.2f}) H={float(H):5.1f}")
assert rows[F(9)][0]==BL and rows[F(12)][0]==BL      # response-deprivation boundary: no effect when r >= H/L bliss ratio (=9)
assert rows[F(3)][0]>BL and rows[F(1)][0]>rows[F(3)][0]
# B) matching law across two gated tasks with H-access per unit of effort ratio 1:1,2:1,4:1,9:1
shares=[float(F(a,a+1)) for a in (1,2,4,9)]; print("B) matching shares",[round(s,3) for s in shares])
assert [round(s,3) for s in shares]==[0.5,0.667,0.8,0.9]
# B2) break: matching share applies to responses, but the gate still needs both tasks' L volume; if task A pays r=1 and B pays r=9 with H capped by budget
LA,HA=best(F(1)); LB,HB=best(F(9)); print(f"B2) r=1 gate total L={float(LA)} vs r=9 gate L={float(LB)}: reward-rate ratio alone does not raise effort once r>=9")
# C) goal gradient: vigor at step k of an n-step gate = 1/(n-k); agent persists while vigor >= theta
def completes(n, theta): return all(F(1,n-k)>=theta for k in range(n))
theta=F(1,10)
maxn=max(n for n in range(1,60) if completes(n,theta)); print("C) theta=1/10 largest n-step gate ever started and finished:",maxn)
assert maxn==10 and not completes(20,theta)
# C2) split a 20-step gate into 2 stacked 10-step sub-gates each unlocking a slice of H
split_ok=completes(10,theta) and completes(10,theta); print("C2) 20 steps as 2x10:",split_ok,"as 1x20:",completes(20,theta))
# D) joint claim: with a big gate, Premack's raise of L vanishes (L stays at baseline 5 because the gate is never started) unless split
def L_effect(r,n,theta,splits=1):
    ok=all(completes(-(-n//splits),theta) for _ in range(splits))
    return best(r)[0] if ok else BL
print("D) r=2, n=20: unsplit L=",float(L_effect(F(2),20,theta)),"split into 2 L=",float(L_effect(F(2),20,theta,2)))
assert L_effect(F(2),20,theta)==BL and L_effect(F(2),20,theta,2)>BL
print("RESULT: PASS Premack gate raises low-pref time only when earn ratio r < 9 (bliss ratio): L=5.0 at r>=9, %.1f at r=3, %.1f at r=1; matching shares 0.5/0.667/0.8/0.9; goal-gradient quit threshold 1/10 caps an unsplit gate at 10 steps (a 20-step gate never starts, L stays 5.0) and splitting into 2x10 restores L=%.1f at r=2" % (float(rows[F(3)][0]),float(rows[F(1)][0]),float(best(F(2))[0])))
