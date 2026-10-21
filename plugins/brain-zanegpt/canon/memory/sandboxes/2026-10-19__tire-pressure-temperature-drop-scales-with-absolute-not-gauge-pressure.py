# Domain: tire pressure vs temperature. Real scenario: set 35 psi gauge in a 70 F garage, drive out at 20 F.
# Prediction (before run): ideal gas at fixed volume, P_abs/T_abs constant (patm 14.7 psi).
#  - 35 psi, 70F -> 20F: gauge falls 4.7 psi (0.94 psi per 10F); a gauge-ratio shortcut gives 3.3 (30% too small).
#  - the drop is proportional to (gauge+14.7): 20 psi cold falls 3.2, 80 psi falls 8.6 over the same 50F.
#  - BREAK: 'one psi per ten degrees F' rule: right within 10% at 35 psi but off by more than 10% at 80 psi (cold side).
PATM = 14.7
def t_abs(f): return f + 459.67
def gauge_after(g0, f0, f1): return (g0 + PATM) * t_abs(f1) / t_abs(f0) - PATM
def shortcut(g0, f0, f1): return g0 * t_abs(f1) / t_abs(f0)
rows = {}
for g0 in (20, 35, 80):
    d = g0 - gauge_after(g0, 70, 20); s = g0 - shortcut(g0, 70, 20); r = 5.0
    rows[g0] = (d, s, r)
    print(f"{g0} psi: true drop {d:.2f}  gauge-ratio shortcut {s:.2f} ({(1-s/d)*100:.0f}% low)  1psi/10F rule {r:.1f} ({(r/d-1)*100:+.0f}%)")
for g0 in (35,):
    # hot side: +40F while driving
    rise = gauge_after(g0, 70, 110) - g0
    print(f"35 psi, 70F->110F: rise {rise:.2f} psi")
d20, d35, d80 = rows[20][0], rows[35][0], rows[80][0]
ok = (abs(d35 - 4.7) < 0.1 and abs(rows[35][1] - 3.3) < 0.1 and abs(d20 - 3.2) < 0.1 and abs(d80 - 8.6) < 0.1
      and abs(5.0 / d35 - 1) < 0.10 and abs(5.0 / d80 - 1) > 0.10)
print("RESULT:", "PASS" if ok else "FAIL", f"drop 70F to 20F: 20psi {d20:.2f}, 35psi {d35:.2f}, 80psi {d80:.2f}; gauge-ratio shortcut {rows[35][1]:.2f} at 35 psi; 1psi/10F rule {(5.0/d35-1)*100:+.0f}% at 35 and {(5.0/d80-1)*100:+.0f}% at 80")
