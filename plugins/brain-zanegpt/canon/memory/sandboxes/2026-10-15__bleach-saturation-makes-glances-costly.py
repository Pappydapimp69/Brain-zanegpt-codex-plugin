"""Night watch by a fire: looking at the fire warms you but bleaches night vision. The re-adaptation owed for a
look of e seconds saturates: 2 night-minutes for a glance, ~17 for a stare (dark-adaptation kernel), and a new
look doesn't stack on old debt (it takes the max). Cold drains warmth; warming refills it.
Question: what look length keeps you warm while losing the least sight and staying blind the shortest?
Deterministic, stdlib only. 1 s = 1 night-minute, as in the Embers game."""
import math
GLANCE, STARE, T = 2, 17, 5
cost = lambda e: STARE - (STARE - GLANCE) * math.exp(-max(0, e - .4) / T)
def watch(look, cold=3.4, warm=8, night=100, dt=.05, start_below=50, gap=1.2):
    t, warmth, debt, blind, longest_blind, cur_blind, froze, looking, e, cool = 0, 100, 0, 0, 0, 0, False, False, 0, 0
    while t < night:
        if looking:
            e += dt; debt = max(debt, cost(e)); warmth = min(100, warmth + warm * dt)
            if e >= look: looking, cool = False, gap
        else:
            debt = max(0, debt - dt); cool -= dt
            if warmth < start_below and cool <= 0: looking, e = True, 0
        warmth -= cold * dt
        if warmth <= 0: froze = True; break
        sight = 1 - math.sqrt(min(1, debt / STARE))
        b = looking or sight < .5     # "blind": looking at the fire, or night sight under half
        cur_blind = cur_blind + dt if b else 0; longest_blind = max(longest_blind, cur_blind); blind += dt if b else 0
        t += dt
    return dict(froze=froze, t=round(t), blind_frac=round(blind / max(t, 1e-9), 2), longest_blind=round(longest_blind, 1))
print("cost per warmth unit (night-minutes of sight per point of warmth gained by one look):")
for e in (.5, 1, 2.5, 5, 10, 20): print(f"  look {e:>4}s: debt {cost(e):5.1f} min for {8*e:5.1f} warmth -> {cost(e)/(8*e):.2f} min/pt")
res = {}
for look in (.5, 1.0, 2.5, 5.0, 12.0):
    res[look] = watch(look); print(f"look {look:>4}s: {res[look]}")
glance_cost, stare_cost = cost(.5) / 4, cost(12) / 96
# a creature reaches the fire about 12 s after it leaves the treeline: a blind stretch longer than that is a hit
ok = res[.5]['froze'] and not res[2.5]['froze'] and res[2.5]['longest_blind'] < 12 and res[12.0]['longest_blind'] >= 12 and glance_cost > 3 * stare_cost
print(f"RESULT: {'PASS' if ok else 'FAIL'} 0.5 s glances cost {glance_cost:.2f} min of sight per warmth point vs {stare_cost:.2f} for a 12 s stare and still froze; 2.5 s looks stayed warm with longest blind stretch {res[2.5]['longest_blind']} s; 12 s stares left a {res[12.0]['longest_blind']} s blind stretch")
