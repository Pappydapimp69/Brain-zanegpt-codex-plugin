"""Rebuild of seven E59 (a sanity meter that reduces competence makes a death spiral;
even a mild 0.03/level penalty ~x1.8 collapse).
Own fixture: meter 0..8 (start 8), 25 encounters, base fail 0.25, recovery on success
rho = 0.1/0.3/0.6/0.9, penalties 0.02 and 0.08 per lost level. Exact Markov chain, no RNG.
Also tests E59's Fix: a penalty paired with easier recovery at low sanity (rho rises 0.08/level lost).
Predictions written before running:
 P1 any penalty raises collapse at every recovery rate (expect hold).
 P2 the mild-penalty ratio stays >= x1.5 at every recovery rate (E59: x1.82) (expect MISS at high rho).
 P3 the strong-penalty ratio stays within x2..x6 (E59: x3.97) (expect MISS: unbounded at high rho).
 P4 the damped-recovery fix brings strong-penalty collapse back within x1.3 of perception-only at rho = 0.3.
"""
TOP, ENC, BASE = 8, 25, 0.25

def collapse(pen, rho, damp=0.0):
    dist = {TOP: 1.0}; dead = 0.0
    for _ in range(ENC):
        nd = {}
        for s, pr in dist.items():
            lost = TOP - s
            f = min(0.95, BASE + pen * lost)
            r = min(1.0, rho + damp * lost)
            down = s - 1
            if down == 0: dead += pr * f
            else: nd[down] = nd.get(down, 0) + pr * f
            up = min(TOP, s + 1)
            nd[up] = nd.get(up, 0) + pr * (1 - f) * r
            nd[s] = nd.get(s, 0) + pr * (1 - f) * (1 - r)
        dist = nd
    return dead

rows = {}
for rho in (0.1, 0.3, 0.6, 0.9):
    c0, cm, cs = collapse(0, rho), collapse(0.02, rho), collapse(0.08, rho)
    rows[rho] = (c0, cm, cs)
    print(f"rho={rho}: collapse perception {c0:.4f} mild {cm:.4f} (x{cm/c0:.2f}) strong {cs:.4f} (x{cs/c0:.2f})")
damped = collapse(0.08, 0.3, damp=0.08)
print(f"strong penalty + recovery rising 0.08/level at rho=0.3: {damped:.4f} vs perception {rows[0.3][0]:.4f} (x{damped/rows[0.3][0]:.2f})")
p1 = all(cm > c0 and cs > c0 for c0, cm, cs in rows.values())
p2 = all(cm / c0 >= 1.5 for c0, cm, cs in rows.values())
p3 = all(2 <= cs / c0 <= 6 for c0, cm, cs in rows.values())
p4 = damped / rows[0.3][0] <= 1.3
checks = [("P1 penalty always raises collapse", p1), ("P2 mild ratio >= 1.5 at all rho", p2),
          ("P3 strong ratio within 2..6", p3), ("P4 damped recovery within x1.3", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; mild ratio " +
      "/".join(f"x{cm/c0:.2f}" for c0, cm, cs in rows.values()) + "; strong ratio " +
      "/".join(f"x{cs/c0:.2f}" for c0, cm, cs in rows.values()) + f" (rho 0.1/0.3/0.6/0.9); damped x{damped/rows[0.3][0]:.2f}")
