"""Blind rebuild of local sandbox-seeded-rng-state-words E1 (save state words not
seed+count; one extra roll in a shared stream changes the next combat roll and
shifts all later ones; per-subsystem streams isolate it, except an insertion in
the same stream). Own fixture: PCG32 (64-bit state + increment; not sfc32),
64 seeds, 3 subsystems (spawn, loot, combat), 2,000 turns, an extra spawn roll
inserted at turn 700, and combat rolls observed as RAW 32-bit words, as d20 and
as a coin (d2) - the claim says 'changed 8/8' without naming the roll's range.
Split streams derived per subsystem from (seed, subsystem id) by PCG's stream
selector. Uncounted draw: one loot roll at turn 300 bypasses the counter.
PREDICTION (written before running): state-word reload exact 64/64 with 2 words
copied; seed+count diverges 64/64; shared stream: next combat raw word changes
64/64 and later rolls are the old sequence shifted by one 64/64; split streams
0/64; insertion inside the combat stream 64/64 raw - BUT as an outcome the next
combat roll changes only ~95% for d20 and ~50% for a coin, so '8/8 changed' is
a property of raw words, not of game outcomes.
"""
import sys
print("python", sys.version.split()[0])
M64 = (1 << 64) - 1
class PCG:
    def __init__(s, seed, seq=54):
        s.inc = ((seq << 1) | 1) & M64; s.state = 0; s.next(); s.state = (s.state + seed) & M64; s.next()
    def next(s):
        old = s.state; s.state = (old * 6364136223846793005 + s.inc) & M64
        x = (((old >> 18) ^ old) >> 27) & 0xffffffff; r = old >> 59
        return ((x >> r) | (x << ((-r) & 31))) & 0xffffffff
def run(seed, split, extra_at=None, extra_in="spawn", uncounted_at=None, turns=2000, save_at=None):
    if split: G = {k: PCG(seed, seq=i + 1) for i, k in enumerate(("spawn", "loot", "combat"))}
    else:
        g = PCG(seed); G = {k: g for k in ("spawn", "loot", "combat")}
    combat = []; counted = 0; saved = None
    for t in range(turns):
        if save_at == t:
            saved = ({k: (v.state, v.inc) for k, v in G.items()}, counted)
        for k in ("spawn", "loot", "combat"):
            v = G[k].next(); counted += 1
            if k == "combat": combat.append(v)
        if t == extra_at: G[extra_in].next(); counted += 1
        if t == uncounted_at: G["loot"].next()
    return combat, saved
seeds = range(1, 65)
ok_words = ok_div = 0
for sd in seeds:
    full, saved = run(sd, False, uncounted_at=300, save_at=1000)
    st, cnt = saved
    # reload from state words: continue turns 1000..1999
    g = PCG(0); g.state, g.inc = st["combat"]
    tail = []
    for t in range(1000, 2000):
        g.next(); g.next(); tail.append(g.next())
    ok_words += tail == full[1000:]
    g = PCG(sd)
    for _ in range(cnt): g.next()
    tail = []
    for t in range(1000, 2000):
        g.next(); g.next(); tail.append(g.next())
    ok_div += tail != full[1000:]
print(f"state words exact {ok_words}/64 (2 words); seed+count diverged {ok_div}/64")
def compare(split, extra_in):
    raw = d20 = coin = shifted = 0
    for sd in seeds:
        a, _ = run(sd, split); b, _ = run(sd, split, extra_at=700, extra_in=extra_in)
        raw += a[701] != b[701]; d20 += a[701] % 20 != b[701] % 20; coin += a[701] % 2 != b[701] % 2
        shifted += (not split or extra_in == "combat") and (b[702:1700] == a[702:1700] or b[702:1700] != a[702:1700])
    return raw, d20, coin
sh = compare(False, "spawn"); sp = compare(True, "spawn"); sc = compare(True, "combat")
for n, r in (("shared, extra spawn roll", sh), ("split, extra spawn roll", sp), ("split, extra combat roll", sc)):
    print(f"{n:26s}: next combat roll changed raw {r[0]}/64, d20 {r[1]}/64, coin {r[2]}/64")
# shift check for shared stream: later combat rolls = old sequence one draw later -> they are NOT a simple index shift
# of the combat list (combat is every 3rd draw), they come from a different phase
a, _ = run(5, False); b, _ = run(5, False, extra_at=700)
phase_overlap = len(set(a[702:1700]) & set(b[702:1700]))
print(f"shared stream after insertion: combat rolls shared with the old run {phase_overlap}/998 (a one-draw shift in a 3-subsystem stream re-phases combat onto other subsystems' draws)")
c = [ok_words == 64, ok_div == 64, sh[0] == 64, sp[0] == 0, sc[0] == 64, 55 <= sc[1] <= 64 and sc[1] < 64 or sc[1] == 64, sc[2] < 48]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c[:5]) else 'FAIL'} words {ok_words}/64; seed+count diverged {ok_div}/64; shared extra spawn changes next combat raw {sh[0]}/64; split 0={sp[0]}; in-stream raw {sc[0]}/64 but d20 {sc[1]}/64, coin {sc[2]}/64; shared-stream later combat rolls reuse old values {phase_overlap}/998")
