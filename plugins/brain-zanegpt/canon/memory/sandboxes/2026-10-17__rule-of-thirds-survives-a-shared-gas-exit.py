# Penetration dive (cave/wreck): out leg and back leg of equal length. Gas planning rule of thirds (NSS-CDS style):
# use 1/3 going in, 1/3 coming out, keep 1/3 reserve. Rule of halves: use 1/2 in, 1/2 out, no reserve.
# Worst case: at the turn point a buddy loses all gas and both divers exit breathing from ONE tank at the donor's
# stressed rate (multiplier m on the donor's normal rate, applied to both divers' combined consumption).
# Normal consumption per leg for ONE diver = u (units of tank). Tank = 1.0 (usable). 
def exit_gas_needed(u, m=2.0, stress=1.0):
    # two divers breathing one tank for one leg: 2 * u * stress ; stress >= 1 models rushed breathing
    return 2*u*stress
def plan_ok(rule, m_stress):
    # rule gives how much of the tank the planner lets the OUT leg consume: planned u
    u = {"thirds":1/3, "halves":1/2, "quarters":1/4}[rule]      # gas used going in, = u per leg
    remaining_at_turn = 1.0 - u                                   # donor's tank at the turn
    need = exit_gas_needed(u, stress=m_stress)
    return remaining_at_turn - need                               # margin; >=0 survives
rows={}
for rule in ("halves","thirds","quarters"):
    rows[rule]=[round(plan_ok(rule,s),3) for s in (1.0,1.25,1.5)]
    print(rule,"margin at stress 1.0,1.25,1.5:",rows[rule])
# Note with thirds: remaining 2/3, need 2/3 at stress 1.0 => margin 0 exactly; any stress > 1 fails.
ok = rows["halves"][0]<0 and abs(rows["thirds"][0])<1e-9 and rows["thirds"][1]<0 and rows["quarters"][2]>=0
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" margins halves {rows['halves']} thirds {rows['thirds']} quarters {rows['quarters']}")
