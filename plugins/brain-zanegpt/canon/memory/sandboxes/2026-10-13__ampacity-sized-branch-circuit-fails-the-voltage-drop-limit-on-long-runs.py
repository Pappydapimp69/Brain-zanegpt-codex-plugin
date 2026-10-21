"""Branch-circuit wire sizing: ampacity-only vs voltage-drop-checked. Deterministic.
Data: NEC Table 310.16 60C copper ampacity (14:15, 12:20, 10:30, 8:40, 6:55 A) and NEC Chapter 9 Table 8
uncoated copper DC resistance ohm/1000ft (14:3.07, 12:1.93, 10:1.21, 8:0.778, 6:0.491). Single-phase 120 V, drop = 2*I*R*L.
Design target 3 percent drop (NEC 210.19 informational note). Continuous-load derate 125 percent applied to the sizing current."""
AWG = [(14, 15, 3.07), (12, 20, 1.93), (10, 30, 1.21), (8, 40, 0.778), (6, 55, 0.491)]
V = 120.0
def drop_pct(I, awg, feet):
    r = next(x for x in AWG if x[0] == awg)[2]
    return 100 * (2 * I * r * feet / 1000) / V
def ampacity_only(I, cont=False):
    need = I * (1.25 if cont else 1.0)
    return next(a for a, amp, r in AWG if amp >= need)
def checked(I, feet, cont=False, limit=3.0):
    for a, amp, r in AWG:
        if amp >= I * (1.25 if cont else 1.0) and drop_pct(I, a, feet) <= limit:
            return a
    return None
def first_fail_len(I, cont=False):
    a = ampacity_only(I, cont)
    for ft in range(10, 2001, 5):
        if drop_pct(I, a, ft) > 3.0: return a, ft
    return a, None
print("load A | ampacity-only AWG | first run length (ft, one way) where drop > 3 percent")
res = {}
for I in (10, 15, 20):
    for cont in (False, True):
        a, ft = first_fail_len(I, cont)
        res[(I, cont)] = (a, ft)
        print(f"{I:>5} {'cont' if cont else '    '} | {a:>2} | {ft}")
# scenarios: 15A at 100 ft, 20A at 150 ft, BREAK: light 3A load where drop never exceeds limit within 2000 ft?
for I, ft in ((15, 100), (20, 150), (3, 300)):
    a = ampacity_only(I); c = checked(I, ft)
    print(f"{I} A @ {ft} ft: ampacity-only {a} AWG drop {drop_pct(I, a, ft):.2f}%  | checked {c} AWG drop {drop_pct(I, c, ft):.2f}%")
a3, f3 = first_fail_len(3)
print("3 A load first fail:", f3)
ok = res[(15, False)][1] and res[(15, False)][1] < 100 and drop_pct(15, 14, 100) > 3 and checked(15, 100) == 8 \
     and drop_pct(3, 14, 300) > 3 and res[(20, False)][1] < res[(10, False)][1]
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" first fail ft 15A {res[(15,False)][1]}, 20A {res[(20,False)][1]}, 20A cont {res[(20,True)][1]}, 3A {f3}")
