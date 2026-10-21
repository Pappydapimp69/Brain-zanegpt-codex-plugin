# Three specs written for an assumed condition: cure dose (meat vs meat+brine base), bolt torque (nut factor K), dough water (starter).
def residual_curing(base_assumed,base_actual,pct=0.0025):
    dose_spec=pct*base_assumed*1e6/base_assumed       # ppm of the assumed base
    mass_nitrite=pct*base_assumed                       # grams of cure salt for the assumed base
    actual_ppm=mass_nitrite/base_actual*1e6
    fixed=mass_nitrite*(base_actual/base_assumed)/base_actual*1e6   # ratio rescale of the amount
    return abs(fixed-dose_spec)/dose_spec
def residual_torque(Ka,Kb,target=0.75):
    T=target*Ka                                          # F ~ T/K  (units absorbed)
    T2=T*Kb/Ka                                           # ratio rescale
    return abs(T2/Kb-target)/target
def residual_dough(F=500,W=350,g=100,h=0.5,target=0.70):
    sf=g/(1+h);sw=g-sf
    scaled=W*(target*(F+sf)/(F+sf))                      # placeholder to keep names
    # ratio rescale: multiply recipe water by target/true
    true=(W+sw)/(F+sf);W_ratio=W*target/true
    after_ratio=(W_ratio+sw)/(F+sf)
    W_sub=target*(F+sf)-sw                                # subtract the hidden water instead
    after_sub=(W_sub+sw)/(F+sf)
    return abs(after_ratio-target)/target, abs(after_sub-target)/target
rc=max(residual_curing(1000,1000*1.25),residual_curing(1000,1000*1.5))
rt=max(residual_torque(.20,.15),residual_torque(.20,.12))
rd_ratio,rd_sub=residual_dough()
rd_sweep=[residual_dough(g=g,h=h)[0] for g in (50,100,200) for h in (1.0,0.5)]
print('curing ratio residual %.2e  torque ratio residual %.2e  dough ratio residual %.4f (subtract fix %.2e)'%(rc,rt,rd_ratio,rd_sub))
print('dough ratio residual sweep over inoculation/hydration:',' '.join('%.4f'%x for x in rd_sweep))
ok=rc<1e-9 and rt<1e-9 and rd_ratio>0.001 and rd_sub<1e-9
print('RESULT: %s ratio rescale is exact (residual %.0e) for proportional hidden terms (cure base, nut factor) but leaves %.2f%% hydration error for the additive starter water (up to %.2f%% over the sweep); subtracting the hidden water is exact'%('PASS' if ok else 'FAIL',max(rc,rt),100*rd_ratio,100*max(rd_sweep)))
