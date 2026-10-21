"""Toy open-water gas plan. Tank 12 L x 200 bar = 2400 L. Dive: bottom time at 30 m (4.0 ata), ascent 3 min at
avg 2.5 ata, safety stop 3 min at 1.5 ata. 10 divers with fixed surface air consumption (SAC, L/min).
Plans choose a bottom time from a SAC assumption; then each diver's REAL gas use decides who surfaces with
>=50 bar (600 L... 50 bar x 12 L) of reserve. BREAK: a buddy out-of-gas ascent shares one tank at 2x stress SAC.
Deterministic: fixed lists, no RNG."""
TANK_L = 12*200; RESERVE_L = 12*50
SACS = [14,15,16,17,18,20,22,24,26,28]
def need_ascent(sac, mult=1.0): return sac*mult*(3*2.5 + 3*1.5)
def bottom_gas_per_min(sac, mult=1.0): return sac*mult*4.0
def plan_bottom_time(plan_sac, mult=1.0):
    budget = TANK_L - RESERVE_L - need_ascent(plan_sac, mult)
    return int(budget // bottom_gas_per_min(plan_sac, mult))
def surface_reserve(sac, t, mult=1.0):
    return TANK_L - bottom_gas_per_min(sac, mult)*t - need_ascent(sac, mult)
def share_ok(sac_a, sac_b, t, mult=2.0):
    # out-of-gas ascent: both use ONE tank (B's) at stress multiplier; bottom already used by B for t minutes
    left = TANK_L - bottom_gas_per_min(sac_b, 1.0)*t
    return left - (need_ascent(sac_a, mult) + need_ascent(sac_b, mult)) >= 0
def stats(t):
    ok = sum(surface_reserve(s, t) >= RESERVE_L for s in SACS)
    sh = sum(share_ok(a, b, t) for a, b in zip(SACS[:5], SACS[::-1][:5]))   # pair lightest with heaviest
    return ok, sh
mean_sac = sum(SACS)/len(SACS)
plans = {"plan to mean SAC": plan_bottom_time(mean_sac), "plan to worst SAC": plan_bottom_time(max(SACS)),
         "plan to worst SAC with 2x stress (shared ascent)": plan_bottom_time(max(SACS), 2.0)}
# rule of thirds: use 1/3 of the tank on the bottom
plans["rule of thirds (1/3 tank at depth)"] = int((TANK_L/3) // bottom_gas_per_min(max(SACS)))
res = {}
for name, t in plans.items():
    ok, sh = stats(t); res[name] = (t, ok, sh)
    print(f"{name}: bottom time {t} min, divers keeping the 50 bar reserve {ok}/10, buddy pairs surviving a shared ascent {sh}/5")
M, W, S2, T = (res[k] for k in plans)
ok = M[1] < 10 and W[1] == 10 and W[2] < 5 and S2[2] == 5 and S2[0] < W[0] and T[1] == 10
print("RESULT: PASS" if ok else "RESULT: FAIL",
      f"mean-SAC plan {M[0]} min leaves {M[1]}/10 divers with reserve; worst-SAC plan {W[0]} min keeps 10/10 but only {W[2]}/5 pairs survive a shared ascent; stress-planned {S2[0]} min keeps {S2[2]}/5")
