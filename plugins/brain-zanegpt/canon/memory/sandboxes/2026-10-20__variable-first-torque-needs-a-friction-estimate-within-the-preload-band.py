# Sandbox: bolt torque, knob-first (apply the quoted torque) vs variable-first (rescale by estimated friction K).
# Preload target 75% of proof, acceptable band 60-90% of proof (clamp enough, below yield margin).
K_SPEC=0.20
KS=[0.10,0.12,0.15,0.17,0.20,0.22,0.25]
def preload_frac(K_true, K_used):            # torque set from K_used, delivered preload from K_true
    T=0.75*K_used                            # torque in units of (proof*d)
    return T/K_true
def ok(f): return 0.60-1e-9<=f<=0.90+1e-9   # band edge is a hit; guards float rounding
knob_first=[ok(preload_frac(K,K_SPEC)) for K in KS]
def var_first(err):
    # estimate of K off by +/-err (worst of both signs counts as a failure)
    return [ok(preload_frac(K,K*(1+s*err))) for K in KS for s in (-1,1)]
res={e:var_first(e) for e in (0.0,0.10,0.15,0.20,0.30)}
share=lambda L: 1-sum(L)/len(L)
print("knob-first fail share:",f"{share(knob_first):.0%}", "failing K:",[K for K,o in zip(KS,knob_first) if not o])
for e,L in res.items(): print(f"variable-first, K estimate error {e:.0%}: fail share {share(L):.0%}")
# analytic break point: preload = 0.75*(1+-e) must stay inside 0.60-0.90 -> 1-e>=0.8, 1+e<=1.2 -> e<=0.2
ok_all = share(knob_first)>0.3 and share(res[0.0])==0 and share(res[0.10])==0 and share(res[0.20])==0 and share(res[0.30])>0
print(("RESULT: PASS" if ok_all else "RESULT: FAIL")+f" knob-first fails {share(knob_first):.0%} of 7 friction cases; variable-first fails 0% with a K estimate within 20% and {share(res[0.30]):.0%} at 30% error")
