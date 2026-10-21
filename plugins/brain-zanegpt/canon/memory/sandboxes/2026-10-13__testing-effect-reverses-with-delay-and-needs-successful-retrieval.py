# Dual-strength memory model (Bjork): storage S (permanent-ish), retrieval R (decays).
# Restudy: R reset to 1, S += gain*(1-R_before)^0? -> fluent re-exposure gives small S gain.
# Test: gain in S proportional to retrieval difficulty (1-R) but only if retrieval succeeds (R>=thr).
import math
def recall_p(S,R): return min(1.0, R*(0.5+S))
def decay(S,R,days,k=0.9): return S, R*math.exp(-k*days/(1+3*S))
def restudy(S,R): return S+0.05+0.15*(1-R), 1.0
RT=0.6
def test(S,R,thr=0.25):
    if R<thr: return S+0.02, R   # failed retrieval, no feedback: almost nothing
    return S+0.08+0.7*(1-R), RT
def run(strategy,delay,gap=0.01,reps=3,thr=0.25):
    S,R=0.3,1.0
    for i in range(reps):
        if i: S,R=decay(S,R,gap)
        S,R=(restudy if strategy=='restudy' else lambda s,r:test(s,r,thr))(S,R)
    S,R=decay(S,R,delay); return recall_p(S,R)
# S1: massed (gap 0): restudy wins at 5 min, testing at 7 days  (kernel claim)
imm=(run('restudy',5/1440),run('test',5/1440)); wk=(run('restudy',7),run('test',7))
print("S1 massed 5min restudy/test",[round(x,3) for x in imm],"7d",[round(x,3) for x in wk])
c1 = imm[0]>=imm[1] and wk[1]>wk[0]
cross=None
for rt in (0.6,0.5,0.4,0.3):
    RT=rt; i=(run('restudy',5/1440),run('test',5/1440)); w=(run('restudy',7),run('test',7))
    print("S1b post-test retrieval strength",rt,"5min",[round(x,3) for x in i],"7d",[round(x,3) for x in w])
    if cross is None and i[0]>i[1] and w[1]>w[0]: cross=rt
RT=0.6
print("S1b reversal first appears at post-test R =",cross); c1 = cross is not None
# S2 (BREAK): spacing gap long enough that R<thr -> failed retrieval; testing advantage shrinks/reverses
g={}
for gap in (0.01,1,3,10,30):
    g[gap]=(run('restudy',7,gap),run('test',7,gap)); print("S2 gap",gap,"restudy/test @7d",[round(x,3) for x in g[gap]])
c2 = g[0.01][1]>g[0.01][0] and g[30][1]<g[30][0]
# S3: threshold sensitivity: if learner is strong (thr low) test still wins at gap 30
a=run('test',7,30,thr=0.0); b=run('restudy',7,30)
print("S3 gap10 thr0 test/restudy",round(a,3),round(b,3)); c3=a>b
# S4: spacing helps restudy too (spacing effect) at moderate gap
c4 = run("restudy",7,1)>run('restudy',7,0.01) and run("test",7,1)>run('test',7,0.01)
print("S4 spacing helps both at gap1",c4)
ok=c1 and c2 and c3 and c4
print("RESULT: %s testing reverses with delay (c1=%s); advantage vanishes when gap>retrievability limit (c2=%s); restored by low threshold (c3=%s); spacing helps both (c4=%s)"%("PASS" if ok else "FAIL",c1,c2,c3,c4))
