"""GC in a game loop (Unity's documented behaviour: a full collection runs in one frame; incremental
collection spreads marking over frames using idle time, adds write-barrier cost, and falls back to a
full collection when reference changes outrun marking). Deterministic, stdlib. 60 fps budget 16.7 ms.
Each frame: work W ms + allocation A KB; a collection triggers when garbage reaches T KB; its cost is
k ms per KB of live heap L. Incremental marks in slices using (budget - work) idle time per frame and
pays a write-barrier tax b ms per frame; if references changed per frame exceed what a slice marks,
marking restarts and after R restarts it falls back to a full collection."""
BUDGET=16.7
def run(frames=600, W=10.0, A=50, T=5000, L=40000, k=0.0004, mode="full", churn=0, b=0.3, R=3):
    garbage=0; over=0; worst=0; marking=0.0; restarts=0
    for f in range(frames):
        t=W; garbage+=A
        if mode=="incremental": t+=b
        if garbage>=T and A>0:
            if mode=="full":
                t+=k*L; garbage=0
            else:
                need=k*L                         # total marking work, ms
                idle=max(0.0,BUDGET-t)
                if churn>idle/k*0.5:              # reference changes outrun a slice: restart marking
                    marking=0.0; restarts+=1
                    if restarts>R: t+=need; garbage=0; restarts=0
                else:
                    marking+=idle; t+=idle
                    if marking>=need: garbage=0; marking=0.0
        over+=t>BUDGET+1e-9; worst=max(worst,t)
    return over, round(worst,2)
S={"1 full GC, 50 KB/frame":run(),
   "2 incremental, idle time available":run(mode="incremental"),
   "3 BREAK incremental, heavy reference churn":run(mode="incremental",churn=20000),
   "4 incremental, no idle time (work 16.6 ms)":run(mode="incremental",W=16.6),
   "5 pooled (0 KB/frame), full GC":run(A=0)}
for k,v in S.items(): print(f"{k:44s} frames over budget={v[0]:3d} worst={v[1]} ms")
f1,f2,f3,f4,f5=S.values()
ok=f1[0]>0 and f1[1]>BUDGET and f2[0]==0 and f3[0]>0 and f5[0]==0 and f4[0]>0
print(("RESULT: PASS " if ok else "RESULT: FAIL ")+f"full GC spikes {f1[0]} frames to {f1[1]} ms; incremental with idle time 0 over budget (worst {f2[1]}); "
      f"heavy churn falls back to full: {f3[0]} spikes; no idle time: {f4[0]} frames over; pooling: {f5[0]}")
