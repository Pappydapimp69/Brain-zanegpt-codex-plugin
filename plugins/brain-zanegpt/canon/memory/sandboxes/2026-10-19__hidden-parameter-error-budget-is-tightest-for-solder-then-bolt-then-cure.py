"""Prediction (before run): the relative error in the hidden parameter that a quoted spec silently assumes
can grow, before the spec fails, by: solder pad conduction <5%, bolt nut factor 5-10%, cure dose base >20%.
Order solder < bolt < cure. BREAK: with a 400 C tip the solder budget must widen (>= 2x the 350 C budget)."""
def solder_budget(tip, liquidus=183.0, tamb=25.0, frac=0.5):
    # steady state = tamb + (tip-tamb)*frac ; spec 'melts' holds while steady >= liquidus
    ss=tamb+(tip-tamb)*frac
    need=(liquidus-tamb)/(tip-tamb)       # smallest conduction fraction that still melts
    return (frac-need)/frac if ss>=liquidus else 0.0, ss
def bolt_budget(K0=0.20, yield_over_proof=640/600):
    # preload ~ T/(K d); spec gives 100% proof at K0; yield reached when K falls to K0/yield_over_proof
    return 1-1/yield_over_proof
def cure_budget(limit=156.25, legal_max=200.0):
    # dose base error inflates ppm by (1+e); allowed until legal_max
    return legal_max/limit-1
s350,ss350=solder_budget(350); s400,ss400=solder_budget(400); b=bolt_budget(); c=cure_budget()
# solder at 350 C: steady state 187.5 vs liquidus 183 => budget
print(f"solder 350C steady {ss350:.1f} budget {s350:.1%}; 400C steady {ss400:.1f} budget {s400:.1%}; bolt {b:.1%}; cure {c:.1%}")
ok = s350<0.05 and 0.05<=b<=0.10 and c>0.20 and s350<b<c and s400>=2*s350
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" error budgets solder {s350:.1%} < bolt {b:.1%} < cure {c:.1%}; 400C solder {s400:.1%}")
