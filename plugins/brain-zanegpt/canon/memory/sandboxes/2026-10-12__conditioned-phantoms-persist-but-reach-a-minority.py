"""Gap pass: seven E63 and E75 price conditioned phantoms with symmetric Rescorla-Wagner (extinction as fast
as acquisition), E79 shows the budget is a learner artefact. Human data (Psychological Medicine 2022 review
of conditioning-evoked hallucinations, Table 1, read first-hand): Ellson 1942 (n = 30, 60 trials) found
conditioned hallucinations PERSISTED through extinction trials, even when told the tone was gone; in the
placebo arm of the scopolamine study (n = 21, 80 trials) only 29% of participants reported at least one.
Deterministic model: RW acquisition rate a = 0.3, extinction rate a/r for r = 1 (E63/E75), 4, 10, 20;
60 teaching pairings, threshold 0.6 for a susceptible player.
Predictions written before running:
 P1 symmetric RW (r = 1) stops conditioned phantoms within 6 cue-alone trials at every a in 0.2-0.45 --
    which contradicts Ellson's persistence.
 P2 persisting through 20 cue-alone trials at threshold 0.6 needs extinction at least 8x slower than acquisition.
 P3 at that fitted r an all-phantom schedule lands >= 10 of 12 for a susceptible player, so E75's 2:1 refresh is not needed.
 P4 with 29% of players susceptible, no schedule lands a given phantom for more than 0.29 of all players.
"""
def alone_run(a, r, teach=60, thr=0.6, n=40):
    V = 0.0
    for _ in range(teach): V += a * (1 - V)
    landed = 0
    for _ in range(n):
        if V >= thr: landed += 1
        else: break
        V *= (1 - a / r)
    return landed

def schedule(a, r, ratio, thr=0.6, teach=60, cues=12):
    V = 0.0
    for _ in range(teach): V += a * (1 - V)
    seq = [False] if ratio == 0 else [True] * ratio + [False]
    landed = phantoms = 0
    for c in range(cues * (ratio + 1) if ratio else cues):
        if seq[c % len(seq)]: V += a * (1 - V)
        else:
            phantoms += 1; landed += V >= thr; V *= (1 - a / r)
        if phantoms == cues: break
    return landed

stop = {a: alone_run(a, 1) for a in (0.2, 0.3, 0.45)}
print("symmetric RW: consecutive phantoms landed before stopping, a 0.2/0.3/0.45:", "/".join(str(stop[a]) for a in stop))
need_r = next(r for r in range(1, 200) if alone_run(0.3, r) >= 20)
print(f"smallest extinction slow-down r for 20 persisting phantoms at a 0.3: {need_r}")
for r in (1, 4, 10, need_r):
    print(f"r={r:3d}: all-phantom lands {schedule(0.3, r, 0)}/12; 1:1 {schedule(0.3, r, 1)}/12; 2:1 {schedule(0.3, r, 2)}/12")
SUS = 0.29
pop = {name: SUS * schedule(0.3, need_r, k) / 12 for name, k in (("all-phantom", 0), ("1:1", 1), ("2:1", 2))}
print("share of ALL players a given phantom lands for: " + ", ".join(f"{k} {v:.3f}" for k, v in pop.items()))
p1 = all(v <= 6 for v in stop.values())
p2 = need_r >= 8
p3 = schedule(0.3, need_r, 0) >= 10
p4 = max(pop.values()) <= 0.29 + 1e-9
checks = [("P1 symmetric RW stops within 6", p1), ("P2 persistence needs >= 8x slower extinction", p2),
          ("P3 fitted learner: all-phantom >= 10/12", p3), ("P4 population cap 0.29", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; symmetric RW stops after {stop[0.2]}/{stop[0.3]}/{stop[0.45]}; "
      f"persistence needs r>={need_r}; fitted all-phantom {schedule(0.3, need_r, 0)}/12; population share max {max(pop.values()):.3f}")
