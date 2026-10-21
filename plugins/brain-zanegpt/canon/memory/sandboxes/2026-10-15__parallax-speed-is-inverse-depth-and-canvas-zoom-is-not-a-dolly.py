# Pinhole parallax: screen shift = F*dx/Z; dolly-in scale = Z/(Z-d); a canvas zoom gives zero parallax.
F = 1000.0
def proj(X, Z, camX=0.0, camZ=0.0): return F * (X - camX) / (Z - camZ)
L = {'fg': 0.5, 'hero': 1.0, 'village': 4.0, 'titan': 60.0}
res = []
# 1) truck dx=0.1: shift ratio between layers equals inverse depth ratio
sh = {k: proj(0, z) - proj(0, z, camX=.1) for k, z in L.items()}
print("1) truck shifts px:", {k: round(v, 1) for k, v in sh.items()})
res.append(abs(sh['fg'] / sh['village'] - L['village'] / L['fg']) < 1e-9)
# 2) dolly-in d=0.3: per-layer scale vs one uniform canvas zoom matched on the hero
sc = {k: (proj(1, z, camZ=.3) - proj(0, z, camZ=.3)) / (proj(1, z) - proj(0, z)) for k, z in L.items()}
print("2) dolly scales:", {k: round(v, 3) for k, v in sc.items()}, "uniform zoom would give", round(sc['hero'], 3), "to all")
res.append(sc['fg'] / sc['hero'] > 1.4 and sc['titan'] < 1.01)
# 3) BREAK 'linear speed factors are fine': factors .2/.5/1/1.5 imply depths Zhero/f; a giant 60 units away should move 1/60 of hero
for f in (.2,): print(f"3) speed factor {f} implies depth {L['hero']/f:.0f} units; titan at 60 needs factor {L['hero']/L['titan']:.3f}")
res.append(L['hero'] / L['titan'] < .2 / 5)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" truck shift fg/village = {sh['fg']/sh['village']:.0f}x = depth ratio; dolly .3 scales fg {sc['fg']:.2f} hero {sc['hero']:.2f} titan {sc['titan']:.3f}; distant giant needs factor {L['hero']/L['titan']:.3f}, not ~.2")
