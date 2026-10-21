# Sandbox: the FIREWOOD kernel's unit trap. Net heat q = 19(1-m) - 2.443 m MJ/kg
# needs WET-basis moisture m. What happens if a calculator or game feeds it the
# DRY-basis figure u = water/dry mass instead (wood meters and forestry tables
# often report u)? Wet basis from dry basis: m = u / (1 + u). Deterministic.
HHV, LAT = 19.0, 2.443
def q(m): return HHV * (1 - m) - LAT * m
rows = []
for u in (0.10, 0.20, 0.25, 0.43, 0.67, 1.00, 1.50, 2.00):
    m = u / (1 + u)
    right, wrong = q(m), q(u)
    err = (wrong - right) / right
    rows.append((u, m, right, wrong, err))
    print(f"dry-basis u={u:4.2f}  wet m={m:4.3f}  right {right:6.2f}  wrong {wrong:6.2f} MJ/kg  error {err*100:7.1f}%")
# per-log view: 2 kg dry matter, same u
for u in (0.25, 1.00):
    m = u / (1 + u); mass = 2 * (1 + u)
    print(f"per log (2 kg dry) u={u}: right {q(m)*mass:5.1f} MJ  wrong {q(u)*mass:5.1f} MJ")
seasoned = [r for r in rows if r[0] <= 0.25]
green = [r for r in rows if r[0] >= 1.0]
ok = all(abs(r[4]) < 0.10 for r in seasoned) and all(r[3] <= 0 for r in green)
# where does the wrong value first hit zero? q(u)=0 at u = 19/21.443
print(f"wrong formula reaches zero at dry-basis u={HHV/(HHV+LAT):.3f} (wet m {HHV/(HHV+LAT)/(1+HHV/(HHV+LAT)):.3f}); the right one only at m=0.886 (u={0.886/(1-0.886):.1f})")
print("RESULT:", "PASS" if ok else "FAIL",
      f"seasoned (u<=0.25) error {min(r[4] for r in seasoned)*100:.1f}% to {max(r[4] for r in seasoned)*100:.1f}%; green (u>=1.0) wrong value {green[0][3]:.2f} MJ/kg, i.e. zero or negative heat")
