"""Kernel pass: rain-barrel sizing (gallons = sq ft x inches x 0.623, ~10% haircut for gutter loss and
first flush) composed with passive water harvesting (overflow is slowed/sunk, rain garden ~ area/6-8)
and brainwork E105 (3 in of mulch cut drip water 47%, 424 -> 226 mm).
Deterministic 120-day season, 1000 sq ft roof, 6.0 in total rain in two climates:
  drizzle  0.15 in every 3 days      monsoon  0.75 in every 15 days
First-flush diverter per storm: clean 0.5 mm, dirty 2 mm over the roof (kernel's range); gutter loss 5%.
Garden: 150 sq ft bed needing 1 in/week bare (0.623*150 gal/week), mulched x 226/424 (E105).
Barrels 55/110/220/440 gal; daily draw = demand/7 when water is there.
Predictions written before running:
 P1 1000 sq ft x 1 in x 0.623 = 623 gal (the formula).
 P2 dirty-roof diverter + gutter loss takes > 30% of gross in the drizzle climate (kernel says ~10%).
 P3 clean diverter + gutter loss stays within 10-15% in the monsoon climate.
 P4 mulch lets a barrel HALF the size meet at least the bare garden's demand share (both climates, 110 vs 220).
 P5 in the monsoon climate a 220 gal barrel overflows > 50% of net catch (so the passive sink is not optional).
"""
ROOF, DAYS, BED = 1000, 120, 150
MM = 1 / 25.4

def season(climate, flush_mm, barrel, mulch):
    every, depth = (3, 0.15) if climate == "drizzle" else (15, 0.75)
    week = 0.623 * BED * 1.0 * ((226 / 424) if mulch else 1.0)
    draw = week / 7
    store = gross = lost = over = met = need = 0.0
    for d in range(DAYS):
        if d % every == 0:
            g = ROOF * depth * 0.623; gross += g
            flush = min(g, ROOF * flush_mm * MM * 0.623)
            net = (g - flush) * 0.95; lost += g - net
            space = barrel - store; take = min(space, net); store += take; over += net - take
        need += draw; use = min(draw, store); store -= use; met += use
    return dict(gross=gross, loss_share=lost / gross, met=met / need, over_share=over / max(1e-9, gross - lost))

p1v = ROOF * 1 * 0.623
print(f"formula: 1000 sq ft x 1 in = {p1v:.0f} gal")
R = {}
for c in ("drizzle", "monsoon"):
    for f, fl in (("clean", 0.5), ("dirty", 2.0)):
        for b in (55, 110, 220, 440):
            for m in (False, True):
                R[(c, f, b, m)] = season(c, fl, b, m)
    for f in ("clean", "dirty"):
        print(f"{c:7s} {f}: loss share {R[(c, f, 220, False)]['loss_share']:.3f}; demand met bare/mulched by barrel 55/110/220/440: " +
              " ".join(f"{R[(c,f,b,False)]['met']:.2f}/{R[(c,f,b,True)]['met']:.2f}" for b in (55, 110, 220, 440)) +
              f"; overflow share @220 {R[(c, f, 220, False)]['over_share']:.2f}")
p1 = abs(p1v - 623) < 0.5
p2 = R[("drizzle", "dirty", 220, False)]["loss_share"] > 0.30
p3 = 0.10 <= R[("monsoon", "clean", 220, False)]["loss_share"] <= 0.15
p4 = all(R[(c, "clean", 110, True)]["met"] >= R[(c, "clean", 220, False)]["met"] for c in ("drizzle", "monsoon"))
p5 = R[("monsoon", "clean", 220, False)]["over_share"] > 0.5
checks = [("P1 formula 623", p1), ("P2 drizzle dirty loss > 30%", p2), ("P3 monsoon clean loss 10-15%", p3),
          ("P4 mulched half barrel >= bare full barrel", p4), ("P5 monsoon 220 overflows > 50%", p5)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 5 else 'FAIL'} {held}/5; loss share drizzle dirty {R[('drizzle','dirty',220,False)]['loss_share']:.2f} "
      f"clean {R[('drizzle','clean',220,False)]['loss_share']:.2f}, monsoon dirty {R[('monsoon','dirty',220,False)]['loss_share']:.2f} "
      f"clean {R[('monsoon','clean',220,False)]['loss_share']:.2f}; monsoon met bare220 {R[('monsoon','clean',220,False)]['met']:.2f} "
      f"mulched110 {R[('monsoon','clean',110,True)]['met']:.2f}; overflow@220 {R[('monsoon','clean',220,False)]['over_share']:.2f}")
