# Variable hold durations vs more source frames for a 600 ms punch. Deterministic.
from fractions import Fraction
CYC=600
def truth(t):   # hand x in px: windup, strike, brief contact, rebound, rest
    if t<200: return -10*t/200
    if t<260: return -10+70*(t-200)/60
    if t<300: return 60-50*(t-260)/40
    return 10
def render(frames,t):   # frames: list of (start_ms,x); hold last started frame
    x=frames[0][1]
    for s,fx in frames:
        if s<=t: x=fx
    return x
def stats(frames):
    disp=[render(frames,t) for t in range(CYC)]
    dwell=sum(1 for x in disp if x>=55)                       # ms impact pose readable
    err=max(abs(d-truth(t)) for t,d in enumerate(disp))       # worst deviation from true path
    jump=max(abs(disp[i+1]-disp[i]) for i in range(CYC-1))    # largest single-step jump on screen
    return dwell,err,jump
# A: 4 key poses, variable holds (windup 150, pass 60, impact 350, recover 40)
A=[(0,0),(150,-10),(210,25),(260,60)]; A=[(0,-5),(150,-10),(200,10),(260,60)]  # windup, extreme, pass, impact
A=[(0,-5),(150,-10),(200,15),(260,60),(500,35),(560,10)]   # 5 poses incl. recover: holds 150,50,60,240,100
B=[(i*25,truth(i*25+12)) for i in range(24)]          # 24 uniform frames, 25 ms each (sampled mid-frame)
C=[(i*150,truth(i*150+75)) for i in range(4)]         # 4 uniform frames, 150 ms each
D=A[:3]+[(230,38)]+A[3:]                              # A plus one smear frame (230-260 ms)
for name,fr in (("A var-hold 6f",A),("B uniform 24f",B),("C uniform 4f",C),("D A+smear 7f",D)):
    d,e,j=stats(fr); print("%-14s frames=%2d impact_dwell=%3dms worst_err=%5.1fpx max_jump=%5.1fpx"%(name,len(fr),d,e,j))
sA,sB,sC,sD=stats(A),stats(B),stats(C),stats(D)
timing_ok = sA[0]>=5*sB[0] and sA[0]>sC[0]            # variable holds buy dwell at zero frame cost vs 4/24 uniform
fidelity_break = sB[1]<sA[1]                           # but trajectory error is worse than 24 frames: the lever does not replace frames
smear_ok = sD[2]<sA[2] and len(D)==len(A)+1            # one extra smear frame shrinks the worst on-screen jump
print("B has better fidelity than A:",fidelity_break,"; smear cuts jump",sA[2],"->",sD[2],"with +1 frame")
# playback: frame index from elapsed time, float accumulation vs exact integer/Fraction ticks at 60 Hz for 60 s
starts=[s for s,_ in A]
def idx(t_ms):
    i=0
    for k,s in enumerate(starts):
        if s<=t_ms: i=k
    return i
mism=0;n=3600;acc=0.0
for tick in range(n):
    exact=Fraction(tick*1000,60)%CYC
    acc+=1/60
    fl=(acc*1000)%CYC
    if idx(exact)!=idx(fl): mism+=1
print("float-accumulated clock vs exact: %d/%d renders show a different frame"%(mism,n))
ok = timing_ok and fidelity_break and smear_ok
print("RESULT: %s variable holds give impact dwell %dms vs %dms (24 uniform) and %dms (4 uniform) at %d frames, but worst path error %.1fpx vs %.1fpx for 24 frames; one smear frame cuts max jump %.0f->%.0f; float clock mismatched %d/%d renders"%("PASS" if ok else "FAIL",sA[0],sB[0],sC[0],len(A),sA[1],sB[1],sA[2],sD[2],mism,n))
