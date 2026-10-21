# Sandbox: replay fingerprint of end state, with and without the PRNG state words (sfc32), against a leaked draw.
# Prediction (written before running): over 50 seeds, a stray extra draw made as the LAST action is missed by a
# fingerprint of game state alone in 50/50 seeds but caught by one that includes the 4 state words in 50/50;
# the next 5 rolls after the leak differ in >=45/50; a leak EARLY in the run is caught by both in 50/50;
# canonical (sorted-key) hashing makes key-order shuffles hash equal 50/50 where naive insertion order differs >=40/50.
import hashlib, json, random
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, seed):
        s.a, s.b, s.c, s.d = 0x9E3779B9, 0x243F6A88 ^ seed & M, 0xB7E15162 ^ (seed * 2654435761) & M, 1
        for _ in range(15): s.next()
    def next(s):
        t = (s.a + s.b + s.d) & M; s.d = (s.d + 1) & M
        s.a = s.b ^ (s.b >> 9); s.b = (s.c + (s.c << 3)) & M
        s.c = (((s.c << 21) | (s.c >> 11)) & M) + t & M
        return t
    def state(s): return [s.a, s.b, s.c, s.d]
def play(seed, leak=None):
    r = Sfc32(seed); hp = 100; gold = 0
    for turn in range(40):
        if leak == "early" and turn == 3: r.next()          # cosmetic roll leaking into the shared stream
        if r.next() % 4 == 0: hp -= 3
        else: gold += r.next() % 7
    if leak == "late": r.next()                              # last action: stray draw, state unchanged
    return {"hp": hp, "gold": gold}, r
def fp(state, rng=None, canonical=True, shuffle=None):
    d = dict(state)
    if rng: d["rng"] = rng.state()
    if shuffle: d = dict(sorted(d.items(), key=lambda kv: shuffle.random()))
    return hashlib.sha256(json.dumps(d, sort_keys=canonical).encode()).hexdigest()
N = 50; res = dict(late_state_miss=0, late_rng_catch=0, next5=0, early_state=0, early_rng=0, canon=0, naive=0)
for seed in range(1, N + 1):
    s0, r0 = play(seed); s1, r1 = play(seed, "late"); s2, r2 = play(seed, "early")
    res["late_state_miss"] += fp(s0) == fp(s1)
    res["late_rng_catch"] += fp(s0, r0) != fp(s1, r1)
    res["next5"] += [r0.next() for _ in range(5)] != [r1.next() for _ in range(5)]
    res["early_state"] += fp(s0) != fp(s2); res["early_rng"] += fp(s0, r0) != fp(s2, r2)
    a, b = random.Random(seed), random.Random(seed + 1000)
    res["canon"] += fp(s0, play(seed)[1], True, a) == fp(s0, play(seed)[1], True, b)
    res["naive"] += fp(s0, play(seed)[1], False, a) != fp(s0, play(seed)[1], False, b)
print(res)
ok = (res["late_state_miss"] == N and res["late_rng_catch"] == N and res["next5"] >= 45 and
      res["early_state"] == N and res["early_rng"] == N and res["canon"] == N and res["naive"] >= 40)
print(("RESULT: PASS" if ok else "RESULT: FAIL"), res)
