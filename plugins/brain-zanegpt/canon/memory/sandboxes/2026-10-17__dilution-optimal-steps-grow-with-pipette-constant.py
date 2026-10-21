# Does the best serial-dilution step count stay at 2 as pipette small-volume constant a grows?
# Prediction (before run): best equal-factor step count is 1 at a=0, 2 at a=0.02..0.2, 3 at a=0.5, 4 at a=1.0;
# i.e. "extra steps beyond two only add error" holds up to ~0.2 and BREAKS by a=0.5.
def err(a, n, total=1000.0, vol=1000.0):
    f = total ** (1.0/n)
    t = vol/f; d = vol - t
    rel = lambda v: max(0.005, a/v)
    return n * (rel(t) + rel(d)*(d/vol))*100
def best(a):
    return min(range(1,9), key=lambda n: err(a,n))
picks = {}
for a in [0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]:
    picks[a] = best(a)
    print("a=%.2f best_n=%d  errs=%s" % (a, picks[a], [round(err(a,n),2) for n in (1,2,3,4,6)]))
ok = picks[0]==1 and all(picks[a]==2 for a in (0.05,0.1,0.2)) and picks[0.5]==3 and picks[1.0]==4
print("RESULT: %s best step count by a: %s" % ("PASS" if ok else "FAIL", picks))
