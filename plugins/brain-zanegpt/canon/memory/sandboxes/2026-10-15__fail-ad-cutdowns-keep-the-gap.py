"""New-half pick: tension-as-information-gap + film + GAME-ADS fixable-fail ending.
A fail ad works by ending on a suspense gap (outcome withheld) the viewer believes they
could fix (AppsFlyer Q1 2025: on social, fixable bad endings +65%). Film lesson: time a
reveal from the beat that opens its gap, not from the clock. Ads ship in cut-downs, so
the question is whether the fixable-fail beat survives being cut to 6/10/15/20 s.
Master 30 s beat sheet: hook 0-3, setup 3-8, attempt 8-20, near-win 20-22, FAIL 22-26
(the gap: last pour missing), end card 26-30. Two cut-down methods:
  TRUNCATE: keep the first L-4 s of the master, then the 4 s end card (clock-based)
  ANCHOR:   keep the hook, the FAIL beat and the end card, then fill the remaining time
            from setup/attempt in order (beat-based)
Pass for a cut = the FAIL beat is on screen for >= 2 s and ends <= 0.5 s before the end
card (so the ad ends on the open gap). Deterministic.
PREDICTION (written before running): TRUNCATE keeps the fail ending only at 30 s (0 of
the 4 cut-downs); ANCHOR keeps it in every cut-down >= 10 s and fails only at 6 s."""
MASTER = [("hook", 0, 3), ("setup", 3, 8), ("attempt", 8, 20), ("nearwin", 20, 22), ("FAIL", 22, 26), ("card", 26, 30)]
def truncate(L):
    body, out, t = L - 4, [], 0
    for name, a, b in MASTER[:-1]:
        if a >= body: break
        out.append((name, a, min(b, body)))
    out.append(("card", body, L)); return out
def anchor(L):
    hook, fail, card = 3, 4, 4
    room = L - card
    out = []; t = 0
    h = min(hook, room); out.append(("hook", 0, h)); t = h
    f = min(fail, room - t)
    fill = room - t - f
    for name, a, b in MASTER[1:4]:
        if fill <= 0: break
        d = min(b - a, fill); out.append((name, t, t + d)); t += d; fill -= d
    if f > 0: out.append(("FAIL", t, t + f)); t += f
    out.append(("card", t, L)); return out
def ok(cut):
    fails = [(a, b) for n, a, b in cut if n == "FAIL"]
    card = [a for n, a, b in cut if n == "card"][0]
    return bool(fails) and fails[-1][1] - fails[-1][0] >= 2 and card - fails[-1][1] <= 0.5
res = {}
for L in (6, 10, 15, 20, 30):
    res[L] = (ok(truncate(L)), ok(anchor(L)))
    print(f"{L:2d}s  truncate: {'fail ending kept' if res[L][0] else 'LOST'}  {[n for n, a, b in truncate(L)]}  |  "
          f"anchor: {'fail ending kept' if res[L][1] else 'LOST'}  {[n for n, a, b in anchor(L)]}")
cut = (6, 10, 15, 20)
t_keep = sum(res[L][0] for L in cut); a_keep = [L for L in cut if res[L][1]]
ok_ = t_keep == 0 and res[30][0] and a_keep == [10, 15, 20] and not res[6][1]
print(f"RESULT: {'PASS' if ok_ else 'FAIL'} clock truncation keeps the fixable-fail ending in {t_keep}/4 cut-downs; "
      f"beat-anchored keeps it in {len(a_keep)}/4 ({a_keep}); 6 s: {res[6][1]}")
