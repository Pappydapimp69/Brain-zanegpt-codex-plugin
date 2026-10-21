# Deterministic sandbox: %-max-HP damage cap vs a burst skill's per-band niche,
# plus cap division in N-vs-1 fights, plus the contested cap window.
H = 100.0
def hit_seq(skill, base, turns=60):
    # damage per turn for a skill before cap
    out = []
    for t in range(turns):
        if skill == "steady": out.append(base)
        else: out.append(base * 3 if t % 3 == 0 else base * 0.5)  # burst: big every 3rd turn, weak between
    return out
def ttk(skill, base, cap, nattackers=1, divide=False):
    seq = hit_seq(skill, base)
    c = cap * H / (nattackers if divide else 1)
    hp = H
    for t, d in enumerate(seq):
        hp -= min(d * nattackers if not divide else d, c * (nattackers if divide else 1)) if False else nattackers * min(d, c)
        if hp <= 0: return t + 1
    return 99
def band_wins(cap):
    # ratio r = attacker base / defender-hp-fraction; bases span weak..strong
    bands = {"weak(base 5-10)": [5, 8, 10], "mid(base 15-30)": [15, 20, 30], "strong(base 60-200)": [60, 100, 200]}
    res = {}
    for name, bases in bands.items():
        b = s = 0
        for base in bases:
            tb, ts = ttk("burst", base, cap), ttk("steady", base, cap)
            if tb < ts: b += 1
            elif tb > ts: s += 1
        res[name] = (b, s)
    return res
def agg(cap):
    r = band_wins(cap)
    return sum(v[0] for v in r.values()), sum(v[1] for v in r.values())

print("S1 aggregate vs per-band, burst wins/steady wins")
for cap in (1.0, 0.45, 0.30, 0.10):
    print(" cap", cap, "agg", agg(cap), band_wins(cap))
nocap, capped = band_wins(1.0), band_wins(0.10)
niche_lost = nocap["strong(base 60-200)"][0] > 0 and capped["strong(base 60-200)"][0] == 0
agg_nocap, agg_capped = agg(1.0), agg(0.10)
# S2 team: 3 attackers vs a boss, cap per hit divided among attackers vs not
print("S2 3v1 time-to-kill, base 20 steady")
t_nodiv = ttk("steady", 20, 0.10, 3, False); t_div = ttk("steady", 20, 0.10, 3, True)
t_one = ttk("steady", 20, 0.10, 1, False)
print(" 1v1", t_one, "3v1 undivided", t_nodiv, "3v1 divided cap", t_div)
# S3 window: caps where burst niche in the mid band survives AND two-hit-kill not possible
print("S3 cap window, burst wins in mid band & strong band")
window = []
for i in range(5, 101, 5):
    cap = i / 100
    w = band_wins(cap)
    window.append((cap, w["mid(base 15-30)"][0], w["strong(base 60-200)"][0]))
for row in window: print(" ", row)
mid_survive = [c for c, m, s in window if m > 0]
# BREAK scenario: claim "aggregate flat means niche intact" -- find a cap where agg equal to nocap yet strong band niche gone
flat_but_lost = [c for c, m, s in window if agg(c) == agg_nocap and s == 0 and nocap["strong(base 60-200)"][0] > 0]
print("BREAK: caps with aggregate burst/steady identical to uncapped yet strong-band burst wins 0:", flat_but_lost)
ok = niche_lost and t_div > t_nodiv and len(window) > 0
print("agg nocap", agg_nocap, "agg cap0.10", agg_capped, "niche_lost", niche_lost)
print(("RESULT: PASS" if ok else "RESULT: FAIL"), "niche_lost=%s 3v1 ttk undivided=%d divided=%d flat_but_lost_caps=%d" % (niche_lost, t_nodiv, t_div, len(flat_but_lost)))
