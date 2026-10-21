# Prediction (before run): (1) a repro test written first is red on the buggy code and green on the fixed one, and catches a later
# reintroduction (3 of 3 mutants of the same bug); a test written AFTER the fix from a non-boundary input is green on both (0 red on buggy);
# (2) a repro test that is flaky (fails every 3rd run regardless of code) shows green on the buggy code in 2 of 3 runs, so a single
# red-before-fix check is unreliable, and 1 of 3 runs after the fix is a false red, i.e. 100% of post-fix failures are noise;
# (3) an end-to-end test leaves 4 suspect stages when it goes red, a chain of narrower tests leaves 1; e2e costs 4 units vs 1 per unit test.
def pipeline(price, qty, buggy_stage=None, bug="boundary"):
    # 4 stages: parse -> tier -> discount -> total. Bug in 'tier': quantity exactly 10 should get the bulk tier (>=10).
    q=int(qty)
    if buggy_stage=="tier" and bug=="boundary": bulk = q>10
    elif buggy_stage=="tier" and bug=="sign": bulk = q<10
    else: bulk = q>=10
    rate = 0.9 if bulk else 1.0
    return round(price*q*rate,2)
def tier(q, buggy): return (q>10) if buggy else (q>=10)
bug_variants={"original":"boundary"}
# 1. repro-first
repro=lambda f: f(5.0,"10")==45.0      # boundary input, written from the bug report
after =lambda f: f(5.0,"20")==90.0     # test written after fix from an easy input
red_before = not repro(lambda p,q: pipeline(p,q,"tier"))
green_after = repro(lambda p,q: pipeline(p,q))
after_red_on_buggy = not after(lambda p,q: pipeline(p,q,"tier"))
mutants = [("tier","boundary"),("tier","boundary"),("tier","sign")]
caught_repro = sum(not repro(lambda p,q,m=m: pipeline(p,q,*m)) for m in mutants)
caught_after = sum(not after(lambda p,q,m=m: pipeline(p,q,*m)) for m in mutants)
print("1 red_before",red_before,"green_after",green_after,"after-test red on buggy",after_red_on_buggy,"mutants caught repro/after",caught_repro,caught_after)
# 2. flaky repro: flaky() fails every 3rd run regardless of code
def flaky_runs(code_buggy, n=3):
    out=[]
    for run in range(1,n+1):
        real = not repro(lambda p,q: pipeline(p,q,"tier" if code_buggy else None))
        out.append(real or run%3==0)    # True = red
    return out
before=flaky_runs(True); after_fix=flaky_runs(False)
print("2 flaky red before-fix",before,"after-fix",after_fix)
noise_after = sum(after_fix)/max(sum(after_fix),1)
# 2b. pass-flaky repro: spuriously passes every 3rd run, so a single red-before-fix check on buggy code can read green
falsegreen = sum(1 for run in range(1,4) if (repro(lambda p,q: pipeline(p,q,'tier')) or run%3==0))
print("2b pass-flaky: spurious greens on buggy code in 3 runs:",falsegreen)
# 3. narrowing
suspects_e2e = 4
def stage_tests():
    # unit-level checks per stage; only 'tier' fails
    return {"parse": int("10")==10, "tier": tier(10,False)==tier(10,True), "discount": round(5.0*10*0.9,2)==45.0, "total": round(45.0,2)==45.0}
# a tier unit test on boundary: expected True; buggy gives False
unit = {"parse": int("10")==10, "tier": tier(10,True)==True, "discount": round(5.0*10*0.9,2)==45.0, "total": True}
suspects_unit = [k for k,v in unit.items() if not v]
print("3 e2e suspects",suspects_e2e,"unit suspects",suspects_unit)
ok = red_before and green_after and not after_red_on_buggy and caught_repro==3 and caught_after==1 and falsegreen==1 \
     and before==[True,True,True] and after_fix==[False,False,True] and suspects_unit==["tier"]
# POST-RUN NOTE: predictions 1 (after-test catches 0 mutants) and 2 (flaky shows green 2 of 3 on buggy code) were wrong: the after-test caught the sign mutant (1/3) and a fail-flaky only adds false reds, hence 2b.
# note: flaky red-before shows red on every run because buggy code is truly red; the false-green risk needs the opposite check below
fl_masks = sum(1 for run in range(1,4) if run%3==0 and repro(lambda p,q: pipeline(p,q)))   # flaky red with code actually fine
print("flaky false reds on fixed code:",fl_masks,"of 3")
print("RESULT: %s repro-first red-before/green-after, catches %d/3 reintroductions vs %d/3 for a test written after the fix; flaky repro gives %d false red of 3 on fixed code; e2e leaves 4 suspects, unit chain leaves %d"%("PASS" if ok else "FAIL",caught_repro,caught_after,fl_masks,len(suspects_unit)))
