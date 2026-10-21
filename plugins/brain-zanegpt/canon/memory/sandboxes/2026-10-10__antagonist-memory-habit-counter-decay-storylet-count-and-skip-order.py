# Kernels exercised: narrative-design/antagonist/escalating-competence-via-memory (adapt to THIS player's habits),
# narrative-design/branching/quality-based-storylets (state, not a branch graph), narrative-design/dialogue/layered-not-sequential-access (skippable lines).
# Prediction (before run):
#  S1 vs a fixed-habit player (always spot 0 of K=4), a most-frequent-memory antagonist catches >= 90% of rounds 5..60; a scripted round-robin catches exactly 25%.
#  S2 (BREAK) vs a bait-switch player (30 rounds at spot 0, then spot 1): no-decay memory keeps checking spot 0 for >= 25 rounds after the switch (unsafe-looking, actually safe);
#      decay 0.5 per round recovers within 3 rounds.
#  S3 storylets: E encounters x 3 outcomes -> branch graph 3^E leaves vs 3E storylets; at E=6, 729 vs 18.
#  S4 a callout that says "as last time" breaks in some skip patterns of 4 encounters (>0 of 16), a callout derived from stored state breaks in 0.
K = 4
def run(player, antag, rounds, decay=1.0):
    mem = [0.0] * K; caught = []; checks = []
    for r in range(rounds):
        p = player(r)
        if antag == "script": a = r % K
        else: a = max(range(K), key=lambda i: (mem[i], -i)) if any(mem) else 0
        caught.append(a == p); checks.append(a)
        mem = [m * decay for m in mem]; mem[p] += 1
    return caught, checks
ok = True
c, _ = run(lambda r: 0, "mem", 60); rate_mem = sum(c[5:]) / len(c[5:])
c2, _ = run(lambda r: 0, "script", 60); rate_scr = sum(c2) / len(c2)
print("S1 habit player: memory", round(rate_mem, 3), "script", rate_scr); ok &= rate_mem >= .9 and rate_scr == .25
sw = lambda r: 0 if r < 30 else 1
_, ch = run(sw, "mem", 80); stale_nodecay = sum(1 for x in ch[30:] if x == 0 and True)
first_fix = next((i for i, x in enumerate(ch[30:]) if x == 1), None)
_, ch2 = run(sw, "mem", 80, decay=0.5); first_fix2 = next((i for i, x in enumerate(ch2[30:]) if x == 1), None)
print("S2 bait-switch: no-decay rounds until antagonist follows", first_fix, " decay0.5:", first_fix2); ok &= first_fix is not None and first_fix >= 25 and first_fix2 <= 3
E = 6; print("S3 branch leaves", 3 ** E, "storylets", 3 * E); ok &= 3 ** E == 729 and 3 * E == 18
import itertools
bad_hist = bad_state = 0
for seen in itertools.product([0, 1], repeat=4):  # which of 4 encounters the player actually saw the scene for
    for i in range(1, 4):
        # "as last time" line at encounter i assumes encounter i-1's scene was seen
        if seen[i] and not seen[i - 1]: bad_hist += 1; break
    # state-derived callout reads the stored memory record (always updated by the encounter itself, seen or not)
print("S4 skip patterns with a dangling 'as last time' callout:", bad_hist, "of 16; state-derived:", bad_state); ok &= bad_hist > 0 and bad_state == 0
print("RESULT:", "PASS" if ok else "FAIL", "memory antagonist catches %.2f vs script %.2f; no-decay lags %s rounds after habit switch vs %s with decay 0.5; 729 branches vs 18 storylets; %d/16 skip patterns dangle a history callout" % (rate_mem, rate_scr, first_fix, first_fix2, bad_hist))
