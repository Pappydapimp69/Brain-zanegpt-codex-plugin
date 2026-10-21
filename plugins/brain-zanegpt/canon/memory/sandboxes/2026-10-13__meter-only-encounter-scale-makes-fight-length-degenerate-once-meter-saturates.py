"""Fight length vs day under two encounter scales. Deterministic, no RNG.
Player power = 8 + 2*day, HP = 10*power_base. Meter = min(100, 8*day) (saturates day 13).
meter_only: enemy power = 0.9 * meter ; anchored: enemy power = player * clamp(0.6 + meter/250, 0.6, 1.0).
Fight: each tick both deal their power to the other's HP (enemy HP = 6*its power, player HP = 6*player power).
Termination predicate keyed on a level: fight ends when either HP <= 0. Report ticks to end by day."""
def player(d): return 8 + 2 * d
def meter(d): return min(100, 8 * d)
def enemy(d, mode):
    if mode == "meter_only": return 0.9 * meter(d)
    return player(d) * min(1.0, max(0.6, 0.6 + meter(d) / 250))
def fight(d, mode, hp_mult=6):
    pp, ep = player(d), enemy(d, mode)
    php, ehp = hp_mult * pp, hp_mult * ep
    t = 0
    while php > 0 and ehp > 0 and t < 1000:
        ehp -= pp; php -= ep; t += 1
    return t, php > 0
def run(mode, hp=6, days=range(1, 31)):
    return {d: fight(d, mode, hp) for d in days}
for mode in ("meter_only", "anchored"):
    r = run(mode)
    print(mode, "ticks by day:", " ".join(f"{d}:{t}{'W' if w else 'L'}" for d, (t, w) in r.items() if d in (1, 3, 6, 10, 13, 20, 30)))
# scenarios: A hp x6, B hp x3 (stat inflation), C break: anchored with meter saturating earlier (meter=min(100,40*day))
mo, an = run("meter_only"), run("anchored")
mo_wins = sum(w for t, w in mo.values()); an_wins = sum(w for t, w in an.values())
mo_t = [t for t, w in mo.values()]; an_t = [t for t, w in an.values()]
print("meter_only: player wins", mo_wins, "of 30, ticks min/max", min(mo_t), max(mo_t))
print("anchored: player wins", an_wins, "of 30, ticks min/max", min(an_t), max(an_t))
# the saturation claim: after the meter saturates (day>=13) the meter-only fight length is a function of player growth only; check it keeps changing while anchored is constant
sat_mo = [mo[d][0] for d in range(13, 31)]; sat_an = [an[d][0] for d in range(13, 31)]
print("post-saturation ticks meter_only", sorted(set(sat_mo)), "anchored", sorted(set(sat_an)))
# break scenario: hp multiplier 1 (glass cannons) -> does anchored still keep fights multi-tick?
b = run("anchored", hp=1)
print("BREAK hp x1 anchored ticks", sorted(set(t for t, w in b.values())))
ok = mo_wins > an_wins and len(set(sat_an)) == 1 and max(an_t) - min(an_t) <= 2 and max(sat_mo) - min(sat_mo) >= 3
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" meter_only wins {mo_wins} ticks {min(mo_t)}-{max(mo_t)}; anchored wins {an_wins} ticks {min(an_t)}-{max(an_t)}")
