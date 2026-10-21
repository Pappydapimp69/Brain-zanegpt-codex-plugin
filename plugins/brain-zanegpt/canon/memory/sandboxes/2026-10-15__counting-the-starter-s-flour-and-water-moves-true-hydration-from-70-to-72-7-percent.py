# Baker's-percentage sandbox: true hydration when a 100%-hydration starter is part of the dough. Exact arithmetic, no RNG.
from fractions import Fraction as F
def naive(flour,water): return F(water,flour)
def true(flour,water,starter,starter_hyd):
    sf=F(starter)/(1+F(starter_hyd)); sw=F(starter)-sf       # flour/water inside the starter
    return (water+sw)/(flour+sf), sf, sw
cases=[("500 flour, 350 water, 100 starter @100%",500,350,100,F(1)),
       ("same with stiff starter @50%",500,350,100,F(1,2)),
       ("500 flour, 350 water, 200 starter @100% (high inoculation)",500,350,200,F(1)),
       ("500 flour, 350 water, 0 starter (control)",500,350,0,F(1))]
out={}
for n,f,w,s,h in cases:
    t,sf,sw=true(f,w,s,h); out[n]=t; print(f"{n}: naive {float(naive(f,w))*100:.1f}% true {float(t)*100:.1f}%  starter holds flour {float(sf):.1f} water {float(sw):.1f}")
a,b,c,d=[out[n[0]] for n in cases]
# to hit a 70% TRUE target with 100g @100% starter and 500g flour, water to add:
target=F(7,10); sf=F(50); sw=F(50); water_needed=target*(500+sf)-sw
print("water to add for 70% true hydration:",float(water_needed))
ok = abs(float(a)-0.7273)<0.0005 and abs(float(d)-0.7)<1e-9 and float(c)>float(a)>0.7>float(b) and float(water_needed)==335.0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"naive 70.0% vs true {float(a)*100:.1f}% (100g @100%), {float(b)*100:.1f}% (@50%), {float(c)*100:.1f}% (200g); add {float(water_needed):.0f}g water for a true 70%")
