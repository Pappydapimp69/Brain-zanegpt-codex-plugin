"""Rebuild of sandbox-seeded-rng-state-words/E1 with my own fixture:
xoshiro128** (not sfc32), splitmix32 seeding by integer mix (not sha256),
10 seeds, 30000 rolls, insertion at 3 points. Deterministic, stdlib only."""
M = 0xFFFFFFFF
rotl = lambda x, k: ((x << k) | (x >> (32 - k))) & M
def splitmix32(x):
    x = (x + 0x9E3779B9) & M; z = x
    z = ((z ^ (z >> 16)) * 0x85EBCA6B) & M; z = ((z ^ (z >> 13)) * 0xC2B2AE35) & M
    return x, z ^ (z >> 16)
class X:
    def __init__(s, seed):
        st = []; x = seed & M
        for _ in range(4): x, z = splitmix32(x); st.append(z)
        s.s = st; s.count = 0
    def raw(s):  # one draw, no bookkeeping
        a, b, c, d = s.s; r = (rotl((b * 5) & M, 7) * 9) & M; t = (b << 9) & M
        c ^= a; d ^= b; b ^= c; a ^= d; c ^= t; d = rotl(d, 11); s.s = [a, b, c, d]; return r
    def next(s): s.count += 1; return s.raw()
def stream(seed, name): return X((seed * 2654435761 + sum(ord(ch) * 31 ** i for i, ch in enumerate(name))) & M)

SEEDS = [3, 17, 101, 2024, 65537, 99991, 123456, 7777777, 31337, 424242]
N = 30000; res = {}
# S1 state words exact; S2 count replay with one uncounted draw; S3 control all counted
w = r = c = 0; replay_cost = 0
for sd in SEEDS:
    g = X(sd)
    for i in range(N):
        g.next()
        if i == N // 2: g.raw()                      # one draw bypasses the counter
    saved_words, saved_count = list(g.s), g.count
    ref = [g.next() for _ in range(50)]
    a = X(0); a.s = list(saved_words); w += [a.next() for _ in range(50)] == ref
    b = X(sd)
    for _ in range(saved_count): b.next(); replay_cost += 1
    r += [b.next() for _ in range(50)] != ref
    h = X(sd)
    for i in range(N): h.next()
    cnt = h.count; refc = [h.next() for _ in range(50)]
    k = X(sd)
    for _ in range(cnt): k.next()
    c += [k.next() for _ in range(50)] == refc
res["words_exact"], res["replay_diverged"], res["control_exact"] = w, r, c
print(f"S1 state-word reload exact {w}/10 (4 words); S2 count replay diverged {r}/10 (cost {replay_cost // 10} rolls each); S3 all-counted control exact {c}/10")

# S4-S6: insertion points 0, 7, 40 rolls before a 6-roll combat sequence
def timeline(sd, split, extra_where, at):
    if split: spawn, combat = stream(sd, "spawn"), stream(sd, "combat")
    else: spawn = combat = X(sd)
    out = []
    for t in range(60):
        if t == at and extra_where == "spawn": spawn.next()
        if t == at and extra_where == "combat": combat.next()
        if t % 10 == 9: spawn.next()             # routine spawn rolls
        if t >= 45: out.append((combat.next() % 100, combat.count))  # (roll, stream position)
    return out
for label, split, where in [("shared+spawn", False, "spawn"), ("split+spawn", True, "spawn"), ("split+combat (BREAK)", True, "combat")]:
    changed = shifted = 0; trials = 0
    for sd in SEEDS:
        base = timeline(sd, split, None, -1)
        for at in (0, 7, 40):
            pert = timeline(sd, split, where, at); trials += 1
            changed += pert[0][0] != base[0][0]
            # shift: every combat roll now sits exactly one stream position later than in the base run
            shifted += all(pp[1] == bp[1] + 1 for pp, bp in zip(pert, base))
    res[label] = (changed, shifted, trials)
    print(f"{label}: first combat roll changed {changed}/{trials}, exact one-draw shift {shifted}/{trials}")
ok = res["words_exact"] == 10 and res["replay_diverged"] == 10 and res["control_exact"] == 10
ok &= res["shared+spawn"][1] == 30 and res["split+spawn"][1] == 0 and res["split+combat (BREAK)"][1] == 30
ok &= res["shared+spawn"][0] >= 27 and res["split+spawn"][0] == 0 and res["split+combat (BREAK)"][0] >= 27
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" xoshiro128**: words exact 10/10, count replay diverged 10/10 (control 10/10); combat roll changed shared {res['shared+spawn'][0]}/30,"
      f" split-spawn {res['split+spawn'][0]}/30, split-combat {res['split+combat (BREAK)'][0]}/30; one-draw shift shared {res['shared+spawn'][1]}/30")
