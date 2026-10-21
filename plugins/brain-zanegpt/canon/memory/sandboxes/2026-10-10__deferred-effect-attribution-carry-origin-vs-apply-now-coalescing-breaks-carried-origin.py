"""Sandbox: deferred execution launders attribution; carried origin vs apply-now; where carry-origin breaks.
Kernels: ideas:architecture/state/deferred-execution-launders-attribution (+ sibling attribution-by-write-path);
memory: sandbox-execute-resolve-conserves-mismatch/E1 (lag conservation, target resolved at arm vs fire time).
PREDICTION (before first run), world of 40 ticks, player arms effects at ticks 0,4,8,...,36 (10 effects),
world arms 5 of its own at ticks 4,12,20,28,36, every effect lands D ticks later via the world sweep:
 S1 D=0: all policies credit the player 10/10 (no laundering).
 S2 D=3: naive batch-source attribution credits the player 0/10 while final state is identical to S1's;
         carry-origin and apply-now both credit 10/10.
 S3 coalescing: if the player and the world arm the SAME effect on the same tick and the sweep dedupes,
         carry-origin credits one of them only (first armer); apply-now credits the player. Credits sum to 1 not 2.
 S4 bypass: one convenience write outside the applier is unattributed ('?') under every policy (sibling cost).
 S5 execute-resolve conservation: target moves with period 5; wrong effects of execute-as-armed == surprises of
         execute-at-fire, both equal #effects whose target moved within D (closed form), for D in 0..8.
Stdlib only, deterministic."""
from collections import Counter

def run(D, policy, coalesce_pairs=(), bypass=False, ticks=40):
    state = Counter(); credit = Counter(); pending = []   # (due, effect, origin)
    def apply(effect, origin):
        state[effect] += 1; credit[origin] += 1
    player_arms = list(range(0, 40, 4)); world_arms = [4, 12, 20, 28, 36]
    for t in range(ticks):
        # actions at this tick (player acts first)
        batch = [("P", f"p{t}")] if t in player_arms else []
        batch += [("W", f"w{t}")] if t in world_arms else []
        for (src, eff) in batch:
            if t in coalesce_pairs and src == "W": eff = f"p{t}"      # world arms the same effect as the player
            if policy == "apply_now" or D == 0: apply(eff, src)
            else: pending.append((t + D, eff, src))
        # world sweep: lands due deferred items
        due = [p for p in pending if p[0] == t]; pending = [p for p in pending if p[0] != t]
        seen = set()
        for _, eff, src in due:
            if eff in seen: continue                                    # sweep dedupes identical effects
            seen.add(eff)
            apply(eff, "W" if policy == "naive" else src)               # naive: the sweep is the writer
        if bypass and t == 20: state["conv"] += 1; credit["?"] += 1     # write outside the applier
    return state, credit

ok = True; notes = []
s1 = {p: run(0, p) for p in ("naive", "carry", "apply_now")}
c1 = {p: v[1]["P"] for p, v in s1.items()}
r1 = all(c == 10 for c in c1.values()); ok &= r1; print("S1 D=0 player credit", c1, r1)
s2 = {p: run(3, p) for p in ("naive", "carry", "apply_now")}
c2 = {p: v[1]["P"] for p, v in s2.items()}
same_state = s2["naive"][0] == s2["carry"][0] == s2["apply_now"][0]
r2 = c2["naive"] == 0 and c2["carry"] == 10 and c2["apply_now"] == 10 and same_state
ok &= r2; print("S2 D=3 player credit", c2, "identical final state:", same_state, r2)
s3 = {p: run(3, p, coalesce_pairs=(12,)) for p in ("carry", "apply_now")}
tot = {p: (v[1]["P"], v[1]["W"]) for p, v in s3.items()}
r3 = tot["carry"] == (10, 4) and tot["apply_now"] == (10, 5)
# at t=12 both arm p12: carry credits player once (first) and DROPS world's arm -> world total 5 not 6; apply_now credits both
ok &= r3; print("S3 coalescing (player,world) credits:", tot, "world's duplicate arm lost under carry:", tot["carry"][1] < tot["apply_now"][1], r3)
s4 = {p: run(3, p, bypass=True)[1]["?"] for p in ("naive", "carry", "apply_now")}
r4 = all(v == 1 for v in s4.values()); ok &= r4; print("S4 bypass unattributed", s4, r4)
# S5 execute-resolve conservation: two real policies over a moving target (period 5 ticks, 3 cells)
def pos(t): return (t // 5) % 3
def policy_as_armed(D):
    cells = Counter(); wrong = 0
    for t in range(0, 40, 4):
        cells[pos(t)] += 1                      # effect lands on the cell seen when armed
        wrong += pos(t) != pos(t + D)           # ... which is not where the target is at fire time
    return wrong
def policy_at_fire(D):
    cells = Counter(); surprise = 0
    for t in range(0, 40, 4):
        cells[pos(t + D)] += 1                  # effect lands on the target's cell at fire time
        surprise += pos(t) != pos(t + D)        # ... but the arm-time hint promised another cell
    return surprise
res = []
for D in range(0, 9):
    closed = sum(any(b % 5 == 0 for b in range(t + 1, t + D + 1)) and pos(t) != pos(t + D) for t in range(0, 40, 4))
    res.append((D, policy_as_armed(D), policy_at_fire(D), closed))
r5 = all(a == b == c for _, a, b, c in res); ok &= r5
print("S5 (D, wrong, surprise, closed):", res, r5)
print(f"RESULT: {'PASS' if ok else 'FAIL'} naive credits player {c2['naive']}/10 at D=3 vs carry {c2['carry']}/10; coalescing loses "
      f"{tot['apply_now'][1]-tot['carry'][1]} credit under carry; bypass unattributed={s4['carry']}; conservation holds D0-8={r5}")
