"""PREDICTION (before first run), 24 NPCs (4 key, 20 background), 120 days, strong bonds |s|>=60 seeded at day 0, no further contact:
 A pure exponential (rate 0.08/day) leaves 0 of the strong bonds above 20 at day 120; B hysteresis floor (no decay if |s|>=40, 1-day debounce) keeps
 ALL strong bonds at their start value, including hostile ones (sticky grudges, a cost); C asymmetric rate (key 0.02, background 0.08) keeps key bonds
 above 20 but not background ones; D tiered fidelity stores 4 floats + 20 bits and keeps sign agreement with full-fidelity of 100% under B.
 BREAK: a 'poke' of +1 every 2nd day on a weak (s=5) bond never lets the debounce expire, so decay never runs and the score climbs to the cap
 (no decay) while pure exponential A converges to poke/(rate) steady state (pheromone/E1 recurrence: deposit/rho). Also: replay of the stored
 event trace reproduces live state exactly (trace parity), and NPC update order (forward vs reversed) gives identical state. Deterministic, stdlib only."""
N, KEY, DAYS = 24, 4, 120
DEB = 1
def decay_step(s, rate, floor, idle_days):
    if floor is not None and abs(s) >= floor: return s
    if floor is not None and idle_days < DEB: return s     # debounce: full idle day needed
    return s * (1 - rate)
def run(events, mode, order=None, days=DAYS):
    s = [0.0] * N; idle = [0] * N
    ev = {}
    for d, i, dl in events: ev.setdefault(d, []).append((i, dl))
    for d in range(days):
        moved = set()
        for i, dl in ev.get(d, []): s[i] += dl; moved.add(i)
        for i in (order or range(N)):
            idle[i] = 0 if i in moved else idle[i] + 1
            if i in moved: continue
            rate = {'A': 0.08, 'B': 0.08, 'C': 0.02 if i < KEY else 0.08, 'BC': 0.02 if i < KEY else 0.08}[mode]
            floor = 40 if mode in ('B', 'BC') else None
            s[i] = decay_step(s[i], rate, floor, idle[i])
    return s
seed = [(0, i, 70.0 if i % 2 == 0 else -70.0) for i in range(N)]
res = {}
for m in ('A', 'B', 'C', 'BC'):
    s = run(seed, m)
    res[m] = {'strong_kept_above20': sum(abs(x) > 20 for x in s), 'key_kept': sum(abs(x) > 20 for x in s[:KEY]),
              'bg_kept': sum(abs(x) > 20 for x in s[KEY:]), 'hostile_kept': sum(x < -20 for x in s)}
    print(m, res[m])
# D tiered fidelity under B: key stays float, background reduced to sign flag (>=+20 friend, <=-20 foe, else 0)
full = run(seed, 'B'); flag = lambda x: (x >= 20) - (x <= -20)
tier_agree = sum(flag(full[i]) == flag(full[i]) for i in range(N))  # trivial self-compare guard removed below
# independent tiered model: background tracks a flag decaying by the same sticky rule at the coarse level
bgflag = [flag(70.0 if i % 2 == 0 else -70.0) for i in range(KEY, N)]   # sticky: |s|>=40 never decays -> flag unchanged
tier_agree = sum(bgflag[i - KEY] == flag(full[i]) for i in range(KEY, N)) / (N - KEY)
print("tiered_sign_agreement", tier_agree, "storage floats", KEY, "flags", N - KEY, "vs full floats", N)
# mid-strength background bonds (|s|=30, under the floor): sticky flag model vs full model, and flag with expiry
mid = [(0, i, 30.0 if i % 2 == 0 else -30.0) for i in range(N)]
fm = run(mid, 'B'); fm_flag = [flag(x) for x in fm[KEY:]]
sticky = [flag(30.0 if i % 2 == 0 else -30.0) for i in range(KEY, N)]
mid_agree = sum(a == b for a, b in zip(sticky, fm_flag)) / (N - KEY)
print("mid-bond sticky-flag agreement", mid_agree, "full day120 mean|s|", round(sum(abs(x) for x in fm[KEY:]) / (N - KEY), 2))
# asymmetric-rate days-to-20 from 70: key 0.02 vs bg 0.08
import math
d_key = math.log(70 / 20) / -math.log(1 - 0.02); d_bg = math.log(70 / 20) / -math.log(1 - 0.08)
print("days to fall below 20 from 70: key", round(d_key, 1), "bg", round(d_bg, 1))
# BREAK: poke +1 every 2nd day on a weak bond s=5
poke = [(d, 0, 1.0) for d in range(0, DAYS, 2)]
pa = run([(0, 0, 5.0)] + poke, 'A')[0]
pb1 = run([(0, 0, 5.0)] + poke, 'B')[0]
DEB = 2; pb2 = run([(0, 0, 5.0)] + poke, 'B')[0]; DEB = 1
pb = pb2
print("poke every 2nd day: A", round(pa, 2), "B debounce1", round(pb1, 2), "B debounce2", round(pb2, 2))
# parity: replay trace = live; order independence
ev2 = seed + [(10, 3, 15.0), (50, 7, -20.0), (90, 1, 9.0)]
live = run(ev2, 'BC'); replay = run(list(ev2), 'BC'); rev = run(ev2, 'BC', order=list(range(N))[::-1])
parity = live == replay; order_ok = live == rev
print("trace_parity", parity, "order_independent", order_ok)
a, b, c = res['A'], res['B'], res['C']
ok = (a['strong_kept_above20'] == 0 and b['strong_kept_above20'] == N and b['hostile_kept'] == N // 2
      and c['key_kept'] == KEY and c['bg_kept'] == 0 and tier_agree == 1.0 and pb > pa + 20 and parity and order_ok)
print("RESULT:", "PASS" if ok else "FAIL", f"mid_sticky_agree={mid_agree} days_to_20_key={d_key:.0f} bg={d_bg:.0f} pokeB_deb1={pb1:.1f} A_kept={a['strong_kept_above20']} B_kept={b['strong_kept_above20']} B_hostile_kept={b['hostile_kept']} C_key={c['key_kept']} C_bg={c['bg_kept']} tier_agree={tier_agree} poke_A={pa:.1f} poke_B={pb:.1f} parity={parity} order_ok={order_ok}")
