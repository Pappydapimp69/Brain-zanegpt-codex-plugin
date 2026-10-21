"""Sandbox: ideas:ACCESSIBILITY/general/curb-cut-effect + ideas:ACCESSIBILITY/captions/captions-must-lie-the-same-way-the-audio-does
+ seven/E64 (a caption that disagrees with the audio is a tell). Does the majority really use an accessibility feature, and who sees the tell?
Population (1000 users, deterministic quantiles, no RNG): 5% permanent need (benefit 1.0); 35% situational need with benefit spread
0.15..0.55 evenly (noisy room, sound off, second language); 60% no need with benefit 0.02..0.10 evenly.
A user turns the feature on when benefit > friction, where friction = setup cost (0 = on by default, 0.2 = one toggle in-game,
0.6 = buried in a settings menu behind an account page). A tell (caption missing or disagreeing with audio) is noticed by a user with
caption on and attention a = 0.5 for situational users, 0.9 for permanent users, 0.3 for no-need users.
PREDICTION (before running):
 K1 friction 0: caption users >= 8x the permanent-need minority (the curb-cut multiplier).
 K2 friction 0.2: users >= 3x the minority.
 K3 (BREAK) friction 0.6: users == the minority exactly (curb-cut reach vanishes, the feature is back to a niche).
 K4 tell exposure (expected noticers) at friction 0 >= 6x that at friction 0.6.
 K5 monotone: users never increase with friction.
"""
people = []
people += [("perm", 1.0)] * 50
people += [("sit", 0.15 + 0.40 * i / 349) for i in range(350)]
people += [("none", 0.02 + 0.08 * i / 599) for i in range(600)]
ATT = {"perm": 0.9, "sit": 0.5, "none": 0.3}
def users(fr): return [(k, b) for k, b in people if b > fr]
def noticers(fr): return sum(ATT[k] for k, _ in users(fr))
rows = {}
for fr in (0.0, 0.1, 0.2, 0.4, 0.6):
    u = users(fr); rows[fr] = (len(u), noticers(fr))
    print("friction %.1f users %4d (%.1fx minority)  expected tell-noticers %.1f" % (fr, len(u), len(u) / 50, rows[fr][1]))
k1 = rows[0.0][0] >= 8 * 50; k2 = rows[0.2][0] >= 3 * 50; k3 = rows[0.6][0] == 50
k4 = rows[0.0][1] >= 6 * rows[0.6][1]; fr_sorted = sorted(rows); k5 = all(rows[a][0] >= rows[b][0] for a, b in zip(fr_sorted, fr_sorted[1:]))
print("checks K1..K5:", k1, k2, k3, k4, k5)
print(("RESULT: PASS" if all((k1, k2, k3, k4, k5)) else "RESULT: FAIL") + " users %d/%d/%d at friction 0/0.2/0.6 (minority 50); tell-noticers %.0f vs %.0f (%.1fx)" % (rows[0.0][0], rows[0.2][0], rows[0.6][0], rows[0.0][1], rows[0.6][1], rows[0.0][1] / rows[0.6][1]))
