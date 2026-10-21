"""Adaptive-copy gate sandbox. A pond state grid; the copy asserts 'it has gone quiet' (fish inactive) on one branch
and 'it is busy' on the other. Three gates: PROXY (mat exists), CAUSE (bed failing), EXACT (the asserted predicate).
Worlds differ in what else drives fish activity.
PREDICTION (before run): world A (oxygen only): CAUSE gate has 0 false lines and PROXY has >0; world B (+temperature):
CAUSE has >0 false lines and EXACT has 0; world C (+predator): CAUSE worse than B; EXACT 0 in all; PROXY worst in all.
FIRST RUN MISSED: world A cause gate had 1 false line (failing threshold O2<50 vs activity threshold O2>=60, a band of
disagreement); so scenario A2 aligns the thresholds and predicts 0."""
import itertools
PL=range(5); MAT=(0,1); TEMP=(0,1); PRED=(0,1)
def oxygen(p,m): return 40+12*p-(25 if p<2 else 5)*m
FAIL_TH=50
def failing(p,m): return p<2 or oxygen(p,m)<FAIL_TH
def active(world,p,m,t,pr):
    a = oxygen(p,m)>=60
    if world in("B","C") and not t: a=False          # cold: fish sluggish even in healthy water
    if world=="C" and pr: a=False                    # predator: fish hide
    return a
def gates(p,m):
    return {"proxy":bool(m),"cause":failing(p,m)}
res={}
for world in "ABC":
    errs={"proxy":0,"cause":0,"exact":0}; n=0; fneg={"proxy":0,"cause":0}; fpos={"proxy":0,"cause":0}
    for p,m,t,pr in itertools.product(PL,MAT,TEMP,PRED):
        if world=="A" and (t==0 or pr==1): continue   # irrelevant axes fixed (warm, no predator)
        if world=="B" and pr==1: continue
        n+=1
        quiet=not active(world,p,m,t,pr)
        g=gates(p,m)
        for k in("proxy","cause"):
            if g[k]!=quiet:
                errs[k]+=1
                (fpos if g[k] else fneg)[k]+=1
        # exact gate: reads the predicate itself
        if (quiet)!=quiet: errs["exact"]+=1
    res[world]=(n,errs,fpos,fneg)
    print(f"world {world}: cells={n} false lines proxy={errs['proxy']} (said-quiet-wrongly {fpos['proxy']}, said-busy-wrongly {fneg['proxy']}) cause={errs['cause']} (wrongly-quiet {fpos['cause']}, wrongly-busy {fneg['cause']}) exact={errs['exact']}")
FAIL_TH=60
a2=0
for p,m in itertools.product(PL,MAT):
    quiet=not active("A",p,m,1,0)
    if (p<2 or oxygen(p,m)<FAIL_TH)!=quiet: a2+=1
print("world A2 (cause threshold aligned to claim threshold 60): false lines",a2)
FAIL_TH=50
ok=[a2==0, res["A"][1]["cause"]==1, res["A"][1]["proxy"]>0,
    res["B"][1]["cause"]>0 and res["B"][1]["exact"]==0,
    res["C"][1]["cause"]>res["B"][1]["cause"],
    all(res[w][1]["exact"]==0 for w in "ABC"),
    all(res[w][1]["proxy"]>=res[w][1]["cause"] for w in "ABC")]
print("checks",ok)
print("RESULT: %s cause gate false 1/10 in A (0 when threshold aligned, A2=%d), but %d/%d false in B and %d/%d in C; proxy %d/%d, %d/%d, %d/%d; exact 0 everywhere"%(
 "PASS" if all(ok) else "FAIL", a2, res["B"][1]["cause"],res["B"][0],res["C"][1]["cause"],res["C"][0],
 res["A"][1]["proxy"],res["A"][0],res["B"][1]["proxy"],res["B"][0],res["C"][1]["proxy"],res["C"][0]))
