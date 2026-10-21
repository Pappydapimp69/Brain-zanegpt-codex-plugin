"""Sandbox: sweep the percent-of-defender-max-HP damage cap fraction c and ask, in the same
3-vs-1 fight, (a) does the boss have a real chance and (b) does the burst skill keep a niche
band. Deterministic: skills cycle on fixed schedules, no RNG."""
PLAYER_HP, BOSS_HP = 100, 1000
BOSS_HIT = 400          # raw boss damage per action against one player (uncapped: one hit kills)
STEADY = 100             # raw steady skill damage per action
BURST_EVERY, BURST_DMG = 4, 400   # burst: 400 once every 4 turns, else 0 (same mean as steady)

def fight(c, skills, boss_actions=1, max_rounds=60):
    hp = [PLAYER_HP] * 3; boss = BOSS_HP
    for rnd in range(1, max_rounds + 1):
        for i in range(3):
            if hp[i] <= 0: continue
            sk = skills[i]
            raw = STEADY if sk == "steady" else (BURST_DMG if rnd % BURST_EVERY == i % BURST_EVERY else 0)
            boss -= min(raw, c * BOSS_HP)
            if boss <= 0: return "players", rnd, round(sum(max(h, 0) for h in hp) / (3 * PLAYER_HP), 2)
        for _ in range(boss_actions):
            alive = [i for i in range(3) if hp[i] > 0]
            if not alive: break
            t = min(alive, key=lambda j: hp[j])
            hp[t] -= min(BOSS_HIT, c * PLAYER_HP)
        if all(h <= 0 for h in hp): return "boss", rnd, 0.0
    return ("boss" if boss > 0 else "players"), max_rounds, round(sum(max(h, 0) for h in hp) / (3 * PLAYER_HP), 2)

def niche_band(c):
    """Single-hit thresholds (fraction of defender max HP) the burst skill can clear: min(raw, cap)/HP."""
    return min(BURST_DMG, c * BOSS_HP) / BOSS_HP

rows = []
for c in (0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.9, 1.0):
    out = {}
    for name, skills in (("all-steady", ["steady"] * 3), ("all-burst", ["burst"] * 3), ("mixed", ["steady", "steady", "burst"])):
        out[name] = fight(c, skills)
    oneshot = min(BOSS_HIT, c * PLAYER_HP) * 2 >= PLAYER_HP   # a player dies in 2 hits or fewer
    rows.append((c, out, niche_band(c), oneshot))
    print("c=%.2f" % c, {k: v for k, v in out.items()}, "burst_clears=%.2f" % niche_band(c), "boss_one_shots_player=%s" % oneshot)

TARGET_BAND = 0.40       # the burst skill's niche: clearing a 0.40-of-max-HP single hit
def classify(c):
    out = [fight(c, sk) for sk in (["steady"] * 3, ["burst"] * 3, ["steady", "steady", "burst"])]
    contested = all(v[0] == "boss" or v[2] <= 0.7 for v in out)
    niche = niche_band(c) >= TARGET_BAND - 1e-9
    safe = min(BOSS_HIT, c * PLAYER_HP) * 2 < PLAYER_HP
    return contested, niche, safe
fine = [round(x / 100, 2) for x in range(5, 101)]
tab = {c: classify(c) for c in fine}
fair = [c for c in fine if tab[c][0]]; niche = [c for c in fine if tab[c][1]]; safe = [c for c in fine if tab[c][2]]
window = [c for c in fine if all(tab[c])]
print("contested c in", (fair[0], fair[-1]), "count", len(fair), "| niche c >=", niche[0], "| no 2-hit kill c <", round(safe[-1] + 0.01, 2))
print("coexistence window (0.01 grid):", window)
# BREAK: change what 'contested' means / the boss hit and see the window move or vanish
BOSS_HIT = 60
alt = [c for c in fine if all(classify(c))]
print("BREAK boss raw hit 60 (cap rarely binds on players): window", alt)
ok = len(window) > 0 and len(window) <= 10 and window[0] >= 0.40 and window[-1] < 0.5
print("RESULT: %s fair team fight, burst niche and no two-hit kill coexist only for cap fractions %s (%d of %d grid points) with boss hit 400; with boss hit 60 the window is %s"
      % ("PASS" if ok else "FAIL", (window[0], window[-1]) if window else None, len(window), len(fine), alt if len(alt) < 6 else (alt[0], alt[-1], len(alt))))
