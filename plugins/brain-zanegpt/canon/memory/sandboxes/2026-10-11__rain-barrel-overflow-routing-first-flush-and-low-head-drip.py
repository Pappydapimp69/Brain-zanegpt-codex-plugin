"""Rain barrel sizing: 0.623 formula, first-flush haircut, barrel size vs storm,
overflow routed to a rain garden (area/6), and low-head drip feed.
Prediction (written before first run): a 55 gal barrel catches <10% of a year of
net roof water, a barrel sized to the 2 in storm (~1100 gal) is needed to catch
it, the /6 rain garden alone spills on the 2 in storm, and 2 ft head gives
about 0.21 of nominal drip flow so 20 gal needs ~4.8 h not 1 h. Assumed constants."""
ROOF = 1000.0                     # sq ft
GAL_PER_SQFT_IN = 0.623
HAIRCUT = 0.10
M2 = ROOF * 0.092903
FF = {"clean": 0.5 * M2 / 3.785, "dirty": 2.0 * M2 / 3.785}   # L/m2 or 2 mm depth -> gal
STORMS = {3: 0.1, 10: 0.6, 11: 0.3, 20: 1.0, 33: 2.0, 45: 0.05, 52: 0.8}  # day: inches
DAYS = 60
DEMAND = 20.0                     # gal/day wanted by 20 x 1 gph emitters for 1 h
GARDEN_GAL = (ROOF / 6.0) * 0.5 * 7.48   # /6 garden, 6 in ponding, no infiltration

def net(inches, ff):
    gross = ROOF * inches * GAL_PER_SQFT_IN
    return max(0.0, gross * (1 - HAIRCUT) - ff), gross

def run(vol, ff, head_ft=None):
    flow = 1.0 if head_ft is None else (max(head_ft, 0) / 2.311 / 20.0) ** 0.5
    daily_cap = DEMAND / flow if flow > 0 else 0   # gal/day deliverable stays DEMAND; hours needed
    hours = 1.0 / flow
    stored = 0.0; caught = 0.0; over = 0.0; used = 0.0; met = 0; garden_spill = 0.0
    for d in range(DAYS):
        if d in STORMS:
            n, _ = net(STORMS[d], ff)
            take = min(n, vol - stored); stored += take; caught += take
            o = n - take; over += o
            garden_spill += max(0.0, o - GARDEN_GAL)
        draw = min(DEMAND, stored)
        stored -= draw; used += draw
        met += draw >= DEMAND - 1e-9
    return dict(caught=caught, over=over, used=used, met=met, spill=garden_spill, hours=hours)

total_net = sum(net(i, FF["clean"])[0] for i in STORMS.values())
g1 = 623 * 1
print(f"1) formula 1000 sqft x 1 in x 0.623 = {g1:.0f} gross; net after 10% haircut = {g1*0.9:.0f}")
print(f"   first flush clean {FF['clean']:.1f} gal, dirty {FF['dirty']:.1f} gal (kernel 12.5-50)")
ok_ff = 12 <= FF["clean"] <= 13 and 48 <= FF["dirty"] <= 51
print(f"2) season net roof water (clean) = {total_net:.0f} gal over {DAYS} d")
res = {}
for vol in (55, 200, 1100, 2500):
    r = run(vol, FF["clean"]); res[vol] = r
    print(f"   barrel {vol:5d}: caught {r['caught']:7.0f} ({r['caught']/total_net:5.1%}) overflow {r['over']:7.0f} used {r['used']:6.0f} demand-days-met {r['met']:2d} garden-spill {r['spill']:7.0f}")
d = run(1100, FF["dirty"]); c = res[1100]
print(f"3) dirty roof diverter: caught {d['caught']:.0f} vs clean {c['caught']:.0f} (loses {c['caught']-d['caught']:.0f} gal)")
print(f"4) rain garden /6 holds {GARDEN_GAL:.0f} gal; 2 in storm net {net(2.0, FF['clean'])[0]:.0f}; 55 gal barrel + garden spill {res[55]['spill']:.0f}")
h = run(1100, FF["clean"], head_ft=2.0)
print(f"5) 2 ft head: flow x{1.0/h['hours']:.2f}, run time for 20 gal = {h['hours']:.1f} h vs 1.0 h")
small_ok = res[55]["caught"] / total_net < 0.10
big_ok = res[1100]["over"] < 1.0 and res[55]["spill"] > 0
head_ok = 4.0 < h["hours"] < 5.5
print("checks", dict(ok_ff=ok_ff, small_ok=small_ok, big_ok=big_ok, head_ok=head_ok))
allok = ok_ff and small_ok and big_ok and head_ok
print(f"RESULT: {'PASS' if allok else 'FAIL'} 55gal catches {res[55]['caught']/total_net:.1%}; 1100gal overflow {res[1100]['over']:.0f}; 55gal+garden spill {res[55]['spill']:.0f}; 2ft head {h['hours']:.1f}h")
