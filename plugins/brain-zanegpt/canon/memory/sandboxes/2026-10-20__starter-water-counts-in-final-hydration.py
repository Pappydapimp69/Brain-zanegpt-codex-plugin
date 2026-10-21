# Final dough hydration with a sourdough starter. Starter hydration h (water/flour by weight), inoculation i (starter flour
# as fraction of total flour is s = starter_flour/total_flour). Exact bookkeeping vs the naive "recipe water / recipe flour".
def final(flour, water, starter_g, h):
    sf = starter_g/(1+h); sw = starter_g-sf
    return (water+sw)/(flour+sf), sf, sw
cases=[]
print('naive vs true hydration, recipe 500 g flour + 350 g water (naive 70.0%)')
for h in (1.0,0.5,0.6):
    for i in (0.0,0.1,0.2,0.4):
        g=500*i; t,_,_=final(500,350,g,h); cases.append((h,i,t))
        print('starter h=%.1f inoc=%.0f%% true=%.1f%% error=%.1f pts'%(h,100*i,100*t,100*(t-0.70)))
# BREAK: the error sign flips with starter hydration relative to the recipe (first draft wrongly expected both negative)
err = lambda h,i: [t for hh,ii,t in cases if hh==h and ii==i][0]-0.70
signs_ok = err(1.0,0.2)>0 and err(0.5,0.2)<0 and abs(err(1.0,0.4))>abs(err(1.0,0.1))  # sign follows (starter h minus recipe h)
# at recipe hydration equal to starter hydration the starter changes nothing
t,_,_=final(500,500,100,1.0)
fixed = abs(t-1.0)<1e-12
# salt base (analog of curing weight base): 2% of flour vs 2% of whole dough
dough=500+350+100; salt_flour=0.02*(500+50); salt_total=0.02*dough
print('salt 2%% of total flour %.1f g vs of dough %.1f g (%.0f%% over)'%(salt_flour,salt_total,100*(salt_total/salt_flour-1)))
ok=signs_ok and fixed and salt_total>salt_flour
t1=err(1.0,0.2);t2=err(0.5,0.2)
print('RESULT: %s starter at 20%% inoculation shifts true hydration %.1f pts (h=1.0) and %.1f pts (h=0.5) from the naive 70%%; zero shift only when recipe hydration equals starter hydration; salt on dough weight runs %.0f%% over flour base'%('PASS' if ok else 'FAIL',100*t1,100*t2,100*(salt_total/salt_flour-1)))
