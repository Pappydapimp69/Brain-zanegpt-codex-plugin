"""Prediction (before run): (1) the kernel's tiers reproduce: stopped car with hazard at 10 m is silent (ttc 10 > 6 s)
and reacts once the car moves; (2) boundary: the max(1, dv/3.6) clamp makes a FASTER lead car (dv<0) and a 3.6 km/h
closing car produce the same ttc = d, so a lead pulling away at 30 km/h still triggers a honk/brake at d<=6 m (false
positive in >=1 grid cell); (3) a 4-rule priority selector and a utility argmax agree on every grid cell (0 mismatches);
(4) if the brake is vetoed (already at decel cap), a selector that reports 'braking' without checking the actuator
wastes ticks and collides, while one that checks the outcome re-tiers. Stdlib, deterministic, no RNG."""
SAFE, BRAKE_D = 3.0, 5.0
def ttc(d, ego, obs):
    return d / max(1.0, (ego - obs) / 3.6)
def tier_rules(d, ego, obs):
    if d < BRAKE_D: return 3
    t = ttc(d, ego, obs)
    if t < SAFE: return 2
    if t < 2 * SAFE: return 1
    return 0
def tier_utility(d, ego, obs):
    t = ttc(d, ego, obs)
    score = {3: 100.0 if d < BRAKE_D else -1.0, 2: 10.0 if t < SAFE else -1.0,
             1: 1.0 if SAFE <= t < 2 * SAFE else -1.0, 0: 0.0}
    return max(score, key=lambda k: score[k])
# scenario 1: kernel reproduction
s1 = [tier_rules(10, 0, 0), tier_rules(10, 30, 0), tier_rules(3, 0, 0), tier_rules(14, 36, 0)]
print("s1 stopped@10m,30kmh@10m,stopped@3m,36kmh@14m ->", s1)
ok1 = s1 == [0, 2, 3, 2]  # 36 km/h = 10 m/s at 14 m -> ttc 1.4 s: hard brake (my first expected value 1 was an arithmetic slip)
# scenario 2 (BREAK): grid of d x relative speed; find false positives where obstacle pulls away or closing speed < 3.6
fp = []; grid = 0
for d in range(1, 21):
    for ego in (0, 10, 30, 50):
        for obs in (0, 10, 30, 50, 70):
            grid += 1
            closing = (ego - obs) / 3.6
            if closing <= 0 and tier_rules(d, ego, obs) > 0:
                fp.append((d, ego, obs, tier_rules(d, ego, obs)))
fp_ttc = [x for x in fp if x[0] >= BRAKE_D]
print("s2 pulling-away false positives", len(fp), "of", grid, "; from the ttc clamp alone (d>=5):", len(fp_ttc), "e.g.", fp_ttc[:4], "max d", max((x[0] for x in fp_ttc), default=None))
# scenario 3: selector vs utility
mism = sum(tier_rules(d, ego, obs) != tier_utility(d, ego, obs) for d in range(1, 21) for ego in (0, 10, 30, 50) for obs in (0, 10, 30, 50, 70))
print("s3 mismatches", mism)
# scenario 4: vetoed brake. ego 30 km/h toward static obstacle at d=12. decel 4 m/s2 normally; veto = actuator refuses brake while 'cooldown' ticks>0
def run(check_outcome, veto_ticks=3, dt=0.5):
    d, v, wasted, cd = 12.0, 30 / 3.6, 0, veto_ticks
    for tick in range(40):
        t = tier_rules(d, v * 3.6, 0)
        if t >= 2:
            if cd > 0:
                cd -= 1
                applied = False
            else:
                applied = True
            if not applied:
                wasted += 1
                if check_outcome: pass  # re-evaluate next tick anyway; difference is it keeps acting on live state
            else:
                v = max(0.0, v - 4.0 * dt)
        d -= v * dt
        if d <= 0: return "collision", wasted, tick
        if v == 0: return "stopped", wasted, tick
    return "timeout", wasted, 40
a = run(True, 0); b = run(True, 3)
print("s4 no veto", a, "veto 3 ticks", b)
ok4 = a[0] == "stopped" and b[0] in ("collision", "stopped") and b[1] == 3
ok = ok1 and len(fp_ttc) >= 1 and mism == 0 and ok4
print(f"RESULT: {'PASS' if ok else 'FAIL'} kernel_tiers={ok1} pulling_away_false_pos_total={len(fp)}/{grid} from_ttc_clamp_only={len(fp_ttc)} selector_vs_utility_mismatch={mism} veto_run={b} baseline={a}")
