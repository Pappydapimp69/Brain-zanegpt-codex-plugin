"""Prediction (before first run): chaining the three garden kernels as roof -> barrel -> gravity drip, with barrel overflow to a
rain garden sized roof/6 (clay):
 1) head needed for the drip kernel's 20 psi is about 46 ft (0.433 psi/ft), so a barrel on a 2 ft stand gives about 0.87 psi;
 2) a non-compensating emitter (flow ~ sqrt(pressure), the exponent behind the recorded x1.55 at 60 psi) at 0.87 psi runs at about 21% of nominal,
    so 16 emitters of 0.5 gph drain a 55 gal barrel in ~6.9 h at nominal but ~33 h by gravity;
 3) a 0.5 in storm on a 1000 sq ft roof is 311.5 gal (0.623 constant), overflowing a 55 gal barrel by ~256 gal, which ponds ~2.5 in on the 167 sq ft rain garden;
 BREAK: a 1 in storm should push ponding past a 3 in design depth only with the barrel absent or small; a barrel does not rescue a large storm."""
GAL_PER_SQFT_IN = 0.623          # rain-barrel kernel
PSI_PER_FT = 0.433               # water column
ROOF, BARREL, STAND_FT = 1000.0, 55.0, 2.0
DRIP_PSI, GPH, N_EMIT = 20.0, 0.5, 16
RG_AREA = ROOF / 6.0             # rain-garden kernel, clay soil

head_needed = DRIP_PSI / PSI_PER_FT
psi = STAND_FT * PSI_PER_FT
frac = (psi / DRIP_PSI) ** 0.5   # sqrt exponent; at 60 psi vs 25 psi this gives the recorded x1.55
print(f"1) head for {DRIP_PSI:g} psi = {head_needed:.1f} ft; {STAND_FT:g} ft stand gives {psi:.2f} psi; sqrt(60/25)={ (60/25)**0.5:.3f}")
assert 45 < head_needed < 47 and psi < 1 and abs((60/25)**0.5 - 1.55) < 0.01

nominal_h = BARREL / (GPH * N_EMIT)
grav_h = nominal_h / frac
print(f"2) flow fraction {frac:.2f}; drain time nominal {nominal_h:.1f} h, gravity {grav_h:.1f} h")

def storm(inches, barrel):
    runoff = ROOF * inches * GAL_PER_SQFT_IN
    over = max(0.0, runoff - barrel)
    pond_in = over / (RG_AREA * GAL_PER_SQFT_IN)
    return runoff, over, pond_in
rows = {i: storm(i, BARREL) for i in (0.1, 0.5, 1.0, 2.0)}
for i, (r, o, p) in rows.items(): print(f"3) storm {i} in: runoff {r:.1f} gal, overflow {o:.1f} gal, rain-garden ponding {p:.2f} in")
nb = {i: storm(i, 0.0)[2] for i in (0.5, 1.0, 2.0)}
print("   no barrel ponding", {k: round(v, 2) for k, v in nb.items()})
fill_in = BARREL / (ROOF * GAL_PER_SQFT_IN)
print(f"   barrel fills at {fill_in:.3f} in of rain")
DESIGN = 3.0
barrel_fixes = [i for i in (0.5, 1.0, 2.0) if nb[i] > DESIGN >= rows[i][2]]
print("   storms where barrel alone brings ponding under", DESIGN, "in:", barrel_fixes)
ok = (abs(rows[0.5][2] - 2.46) < 0.05 and abs(rows[0.5][1] - 256.5) < 1 and 0.18 < frac < 0.25 and 30 < grav_h < 36
      and rows[2.0][2] > DESIGN and barrel_fixes == [])
print("RESULT:", "PASS" if ok else "FAIL",
      f"gravity head {psi:.2f} psi vs {DRIP_PSI:g} needed ({head_needed:.0f} ft); flow {frac:.0%}; drain {nominal_h:.1f}->{grav_h:.1f} h; 0.5 in overflow {rows[0.5][1]:.0f} gal ponds {rows[0.5][2]:.2f} in; 2 in ponds {rows[2.0][2]:.1f} in despite barrel")
