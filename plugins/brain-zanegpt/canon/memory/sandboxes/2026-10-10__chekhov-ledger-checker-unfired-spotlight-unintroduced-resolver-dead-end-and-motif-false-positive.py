"""Sandbox: can the Chekhov's-gun promise be CHECKED, and where does a promise-only check go wrong?
Kernel: ideas:STORYTELLING/economy/chekhovs-gun-is-a-promise-not-just-foreshadowing (a spotlighted detail that goes
nowhere breaks the contract; resolving with something never introduced breaks it the other way).
Siblings: ideas:SONGWRITING/outline-tooling/causal-ledger-checker-for-story-songs (typed uses; echo does not count),
ideas:SONGWRITING/narrative/relay-token-payoff (a payoff must plant something that reaches the end).
A story is a list of beats; a beat = {plants: set of spotlighted details, uses: [(detail, type)], bg: unspotlighted}.
Types: action, reveal, consequence, echo.  Rules:
 R1 every planted (spotlighted) detail has an action/reveal/consequence use in a LATER beat (echo does not count);
 R2 every use of a detail refers to one planted in an EARLIER beat (no unintroduced resolver);
 R3 (relay) every detail's chain (use beat -> that beat's plants -> their uses ...) reaches the final beat.
PREDICTION (before first run), 3 hand-built stories (6 beats each), 5 mutation operators:
 drop_use (delete the only use of a planted detail) -> R1 catches 3/3; remove_plant (delete the introduction of a used
 detail) -> R2 catches 3/3; echo_only (turn its use into an echo) -> R1 catches 3/3 while a promise-only check (any use at
 all) misses 3/3; dead_end (use fires but plants nothing and is not in the last beat) -> R3 catches 3/3 and R1 misses them;
 BREAK: bg_to_spotlight-free case -- deleting an UNSPOTLIGHTED background mention flags nothing (0/3). Unmutated stories
 raise 0 flags. A legitimate recurring motif (planted, only echoed, by design) IS flagged -> the checker has a false
 positive rate of 1/1 on motifs, which needs an explicit 'motif' exemption. Stdlib only, deterministic, no RNG."""
import copy

def B(plants=(), uses=(), bg=()):
    return {"plants": set(plants), "uses": list(uses), "bg": set(bg)}

STORIES = {
 "heist": [B(plants=["key"], bg=["rain"]), B(plants=["guard"]), B(uses=[("guard", "action")], plants=["alarm"]),
           B(uses=[("key", "action")], plants=["vault"]), B(uses=[("alarm", "consequence")], plants=["map"]),
           B(uses=[("vault", "reveal"), ("map", "action")])],
 "sea": [B(plants=["net"], bg=["gulls"]), B(plants=["storm"]), B(uses=[("storm", "consequence")], plants=["wreck"]),
         B(uses=[("net", "action")], plants=["rope"]), B(uses=[("wreck", "reveal")], plants=["letter"]),
         B(uses=[("rope", "action"), ("letter", "reveal")])],
 "court": [B(plants=["ring"], bg=["clock"]), B(plants=["witness"]), B(uses=[("witness", "action")], plants=["alibi"]),
           B(uses=[("ring", "reveal")], plants=["ledger"]), B(uses=[("alibi", "consequence")], plants=["verdict"]),
           B(uses=[("ledger", "action"), ("verdict", "reveal")])],
}
GOOD = ("action", "reveal", "consequence")

def check(story):
    flags = []
    planted_at, uses_at = {}, {}
    for i, b in enumerate(story):
        for d in b["plants"]: planted_at.setdefault(d, i)
        for d, t in b["uses"]: uses_at.setdefault(d, []).append((i, t))
    for d, i in planted_at.items():                                  # R1
        if not any(j > i and t in GOOD for j, t in uses_at.get(d, [])): flags.append(("R1", d))
    for d, us in uses_at.items():                                    # R2
        if d not in planted_at or all(j <= planted_at[d] for j, _ in us): flags.append(("R2", d))
    last = len(story) - 1
    reach = {}
    def reaches(d, seen=()):
        if d in seen: return False
        for j, t in uses_at.get(d, []):
            if t not in GOOD: continue
            if j == last: return True
            if any(reaches(n, seen + (d,)) for n in story[j]["plants"]): return True
        return False
    for d in planted_at:                                             # R3 (only if R1 passed for d)
        if ("R1", d) not in flags and not reaches(d): flags.append(("R3", d))
    return flags

def promise_only(story):  # any later use of any type
    p = {}
    for i, b in enumerate(story):
        for d in b["plants"]: p.setdefault(d, i)
    return [("P", d) for d, i in p.items() if not any(j > i and any(u == d for u, _ in story[j]["uses"]) for j in range(len(story)))]

def mutate(story, op):
    s = copy.deepcopy(story)
    if op == "drop_use":
        for b in s[1:]:
            if b["uses"]: b["uses"] = b["uses"][1:]; return s
    if op == "remove_plant":
        s[0]["plants"].clear(); return s
    if op == "echo_only":
        for b in s[1:-1]:
            if b["uses"]: b["uses"] = [(b["uses"][0][0], "echo")] + b["uses"][1:]; return s
    if op == "dead_end":
        # a middle-beat use that fed nothing: detail used in beat 2 only, and beat 2 plants nothing forward
        s[2]["plants"].clear(); return s
    if op == "bg_delete":
        s[0]["bg"].clear(); return s

ok = True
base = {n: check(st) for n, st in STORIES.items()}
r0 = all(not v for v in base.values()); ok &= r0
print("unmutated flags:", {n: len(v) for n, v in base.items()}, r0)
want = {"drop_use": "R1", "remove_plant": "R2", "echo_only": "R1", "dead_end": "R3", "bg_delete": None}
caught = {}; promise_miss = {}
for op, rule in want.items():
    c = pm = 0
    for n, st in STORIES.items():
        m = mutate(st, op)
        fl = check(m)
        hit = (rule is None and not fl) or (rule is not None and any(r == rule for r, _ in fl))
        c += hit
        pm += (not promise_only(m)) if op in ("echo_only", "dead_end") else 0
    caught[op] = c; promise_miss[op] = pm
    print(f"op={op:<13} intended rule {rule}: caught {c}/3; promise-only check missed {pm}/3")
r1 = all(v == 3 for v in caught.values()); ok &= r1
r2 = promise_miss["echo_only"] == 3 and promise_miss["dead_end"] == 3; ok &= r2
# motif false positive: a legitimate recurring motif, planted and only echoed by design
motif = copy.deepcopy(STORIES["sea"]); motif[0]["plants"].add("gull-cry")
for i in (2, 4): motif[i]["uses"].append(("gull-cry", "echo"))
fl = check(motif); fp = any(d == "gull-cry" for _, d in fl)
exempt = [f for f in fl if f[1] != "gull-cry"]  # explicit motif exemption removes it
print("motif flagged by checker (false positive):", fp, "| after motif exemption flags:", len(exempt))
ok &= fp and not exempt
print(f"RESULT: {'PASS' if ok else 'FAIL'} unmutated flags 0; ops caught {caught}; promise-only missed echo_only {promise_miss['echo_only']}/3 dead_end {promise_miss['dead_end']}/3; "
      f"legit motif flagged={fp} (needs exemption)")
