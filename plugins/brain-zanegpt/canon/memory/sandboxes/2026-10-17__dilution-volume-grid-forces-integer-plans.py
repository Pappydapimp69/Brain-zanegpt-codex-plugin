# Two-step 1000x dilution into 1000 uL final volumes; the pipette only sets whole microlitres.
# Prediction (before run): at a=0.1 the continuous optimum is two ~31.6x steps (1.97 pct worst-case from the
# earlier lesson); on a 1 uL grid the transfer 1000/31.6=31.6 uL rounds to 32 uL, giving a systematic factor
# error of 1.2 pct per step (2.5 pct combined) which exceeds the random-error advantage, so the grid-feasible best
# plan is 10x100 (or 20x50) instead, with total error (random bound + systematic) below the rounded 31.6x31.6.
def rel(a, v): return max(0.005, a/v)
def step_random(a, f, vol=1000.0):
    t = vol/f; d = vol-t
    return rel(a,t) + rel(a,d)*(d/vol)
def plan_err(a, f1, f2, grid):
    tot_rand = 0.0; actual = 1.0
    for f in (f1, f2):
        t = round((1000.0/f)/grid)*grid if grid else 1000.0/f
        fa = 1000.0/t                       # factor actually delivered
        tot_rand += step_random(a, fa)
        actual *= fa
    sys_err = abs(actual/1000.0 - 1.0)
    return (tot_rand + sys_err)*100, sys_err*100, actual
cands = [(10,100),(20,50),(25,40),(31.623,31.623),(40,25),(50,20),(100,10)]
out = {}
for grid in (0, 1.0, 5.0):
    best = min(cands, key=lambda c: plan_err(0.1, c[0], c[1], grid)[0])
    out[grid] = best
    print("grid", grid, "best", best, [ (c, round(plan_err(0.1,*c,grid)[0],2)) for c in cands])
cont = plan_err(0.1,31.623,31.623,0)[0]; g1 = plan_err(0.1,31.623,31.623,1.0)
print("31.6x31.6 continuous %.2f, on 1uL grid total %.2f (systematic %.2f)" % (cont, g1[0], g1[1]))
ok = out[0]==(31.623,31.623) and out[1.0]!=(31.623,31.623) and g1[0]>cont
print("RESULT: %s best plan continuous %s, 1 uL grid %s, 5 uL grid %s; 31.6x31.6 error %.2f -> %.2f" % ("PASS" if ok else "FAIL", out[0], out[1.0], out[5.0], cont, g1[0]))
