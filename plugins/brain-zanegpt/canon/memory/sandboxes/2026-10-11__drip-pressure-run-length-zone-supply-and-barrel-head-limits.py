"""Drip line model. Emitter flow q = q_nom*sqrt(P/P_nom) (uncompensated orifice law),
P_nom 20 psi for q_nom 1 gph. Tubing: 1/2 in poly, ID 0.600 in, Hazen-Williams C=150.
Head loss uses flow remaining along the line (emitters downstream), solved by marching.
S1 regulation: flow ratio 60 psi vs 25 psi (E112 recorded 1.55).
S2 run length: end-of-line flow ratio at 25 psi inlet for 1 gph emitters every 1.25 ft
   for runs 50..800 ft; find run where end emitter < 90% of first (uniformity limit).
S3 zone supply: GPM per zone must not exceed source; source 4 gpm, zones sized by emitter count.
S4 barrel-fed: 55 gal barrel at head h ft gives P = h/2.311 psi; flow ratio and hours to drain.
S5 break: same 800 ft with 0.5 gph emitters (half the load) -> longer run allowed?"""
import math
ID = 0.600
def hw_loss_psi(gpm, ft, C=150.0, d=ID):
    if gpm <= 0: return 0.0
    return 4.52 * (gpm ** 1.852) / (C ** 1.852 * d ** 4.8655) * ft
def march(inlet_psi, run_ft, q_nom, spacing=1.25, p_nom=20.0):
    n = int(run_ft / spacing)
    # iterate: pressures depend on downstream flow which depends on pressures
    p = [inlet_psi] * n
    for _ in range(60):
        q = [q_nom * math.sqrt(max(pi, 0.01) / p_nom) for pi in p]
        newp = []; cur = inlet_psi
        rem = sum(q) / 60.0
        for i in range(n):
            cur -= hw_loss_psi(rem, spacing)
            newp.append(cur)
            rem -= q[i] / 60.0
        p = newp
    return q
res = {}
res["S1_ratio_60_vs_25"] = round(math.sqrt(60 / 25), 3)
rows = {}
for run in (50, 100, 200, 400, 800):
    q = march(25.0, run, 1.0)
    rows[run] = q[-1] / q[0]
res["S2_end_ratio_1gph"] = {k: round(v, 3) for k, v in rows.items()}
limit = next((r for r in sorted(rows) if rows[r] < 0.9), None)
res["S2_first_run_below_90pct"] = limit
q05 = march(25.0, 800, 0.5); res["S5_end_ratio_800ft_0p5gph"] = round(q05[-1] / q05[0], 3)
q1 = march(25.0, 100, 1.0)
zone_gpm = sum(q1) / 60.0
res["S3_gpm_one_100ft_run"] = round(zone_gpm, 3)
res["S3_runs_per_4gpm_zone"] = int(4.0 // zone_gpm)
for h in (2.0, 4.0, 8.0):
    P = h / 2.311
    ratio = math.sqrt(P / 20.0)
    hours = 55.0 / (50 * 1.0 * ratio)  # 50 emitters at 1 gph nominal
    res[f"S4_barrel_{h}ft"] = (round(P, 2), round(ratio, 3), round(hours, 1))
for k, v in res.items(): print(k, v)
ok = (res["S1_ratio_60_vs_25"] == 1.549
      and rows[50] > 0.97 and rows[800] < 0.9 and limit is not None
      and res["S5_end_ratio_800ft_0p5gph"] > rows[800]
      and res["S4_barrel_2.0ft"][1] < 0.25)
print("RESULT:", "PASS" if ok else "FAIL",
      f"60 vs 25 psi x{res['S1_ratio_60_vs_25']}; end emitter {rows[100]:.2f} at 100 ft, {rows[400]:.2f} at 400, {rows[800]:.2f} at 800 ft (first <90% at {limit} ft); "
      f"half-flow emitters {res['S5_end_ratio_800ft_0p5gph']}; 2 ft barrel head gives {res['S4_barrel_2.0ft'][1]}x flow")
