# Naismith's rule (1892): 1 h per 5 km walked + 1 h per 600 m climbed. Langmuir descent correction:
# gentle descent (5-12 deg) subtract 10 min per 300 m; steep (>12 deg) add 10 min per 300 m.
# Prediction (before run): 1 m of climb costs exactly 8.33 flat metres, so a 12 km route climbing 900 m ties a 22.5 km flat route (WRONG: my
# arithmetic; the rule gives 19.5 km, corrected in run 2); descending 600 m is -20 min at 8 deg but +20 min at 20 deg, so equal-ascent routes flip on descent steepness alone.
# routes flips on descent steepness alone. Hidden assumption: the rule's constants hold at a fit-walker pace (they are a model).
# Break: two routes with equal distance and ascent but different descent slope must NOT tie.
def naismith_h(km, up_m): return km/5 + up_m/600
def langmuir_min(down_m, slope_deg):
    if 5 <= slope_deg <= 12: return -10*down_m/300
    if slope_deg > 12: return +10*down_m/300
    return 0
def total_min(km, up, down, slope): return 60*naismith_h(km,up) + langmuir_min(down,slope)
flat_eq_km_per_100m = 100/600*5
r1 = total_min(12, 900, 900, 8)
flat = 60*naismith_h(19.5, 0)
rA = total_min(10, 600, 600, 8)    # gentle descent
rB = total_min(10, 600, 600, 20)   # steep descent, same distance and ascent
print("flat-eq km per 100 m climb: %.3f"%flat_eq_km_per_100m)
print("12 km +900/-900 @8deg: %.1f min ; 19.5 km flat: %.1f min (base without descent %.1f)"%(r1,flat,60*naismith_h(12,900)))
print("A gentle descent %.1f min ; B steep descent %.1f min ; gap %.1f"%(rA,rB,rB-rA))
ok = abs(flat_eq_km_per_100m-0.8333)<1e-3 and abs(60*naismith_h(12,900)-flat)<1e-6 and rA<rB and abs((rB-rA)-40)<1e-6
print("RESULT:","PASS" if ok else "FAIL","100 m climb = %.2f flat km; 12 km +900 m base %.0f min = 19.5 km flat %.0f min; same route %.0f min on 8deg descent vs %.0f min at 20deg (gap %.0f)"%(flat_eq_km_per_100m,60*naismith_h(12,900),flat,rA,rB,rB-rA))
