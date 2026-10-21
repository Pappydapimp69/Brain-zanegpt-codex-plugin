# Sandbox: 8 comic engines (vary-the-comic-engine kernel) assigned to slot-machine
# cells (6 tropes x 5 axes = 30) for an idea batch. Engines: escalation, literalism,
# role_reversal, character_vs_player, anticlimax, running_gag, misdirection, genre_switch.
# PREDICTION (before run): a 10-idea batch drawn topic-first (random engine) has some
# engine 3+ times in at least 50% of batches; engine-first balanced assignment keeps
# the max at 2; and "no repeated engine" is IMPOSSIBLE for any batch over 8 (pigeonhole),
# so the kernel's 'check for repeated engines' needs a cap, not zero.
# Hidden assumption: the 8 listed engines are the whole space.
import random, math
E = 8; CELLS = 30
def max_repeat_topic_first(k, trials=20000, seed=3):
    r = random.Random(seed); ge3 = 0; rep = 0
    for _ in range(trials):
        cnt = [0] * E
        for _ in range(k): cnt[r.randrange(E)] += 1
        ge3 += max(cnt) >= 3; rep += max(cnt) >= 2
    return ge3 / trials, rep / trials
def engine_first(k):
    cnt = [0] * E; cells = random.Random(9).sample(range(CELLS), k) if k <= CELLS else None
    for i in range(k): cnt[i % E] += 1               # engines first, round robin
    pairs = {(cells[i] // 5, cells[i] % 5, i % E) for i in range(k)}
    return max(cnt), len(pairs)
ge3, rep10 = max_repeat_topic_first(10)
mx10, uniq10 = engine_first(10)
print(f"topic-first, 10 ideas: P(some engine >=3) {ge3:.2f}, P(any engine repeats) {rep10:.2f}")
print(f"engine-first, 10 ideas: max engine count {mx10}, unique (trope,axis,engine) triples {uniq10}/10")
no_repeat_cap = {k: engine_first(k)[0] for k in (8, 9, 15, 16, 17)}
print("engine-first max count by batch size:", no_repeat_cap, "(ceil(k/8) =", {k: math.ceil(k / 8) for k in no_repeat_cap}, ")")
p_none_8 = math.prod((E - i) / E for i in range(8))        # random 8 ideas all different engines
print(f"random 8 ideas all-different engines probability {p_none_8:.4f}")
# source-check lesson: axis 3 ('borrowed fame') is not the study's label; cells with it = 6 of 30
bad = {c for c in range(CELLS) if c % 5 == 2}
r = random.Random(4); hit = 0; T2 = 20000
for _ in range(T2): hit += len(bad & set(r.sample(range(CELLS), 10))) > 0
p_bad = 1 - math.comb(24, 10) / math.comb(30, 10)
print(f"10 distinct cells drawn: P(at least one carries the mislabelled axis) exact {p_bad:.3f}, sim {hit/T2:.3f}")
ok = (abs(p_bad - hit / T2) < 0.02 and p_bad > 0.9 and ge3 >= 0.5 and mx10 == 2 and uniq10 == 10
      and all(v == math.ceil(k / 8) for k, v in no_repeat_cap.items()) and no_repeat_cap[8] == 1 and no_repeat_cap[9] == 2 and p_none_8 < 0.01)
print(f"RESULT: {'PASS' if ok else 'FAIL'} 10 topic-first ideas have an engine 3+ times {ge3:.2f} of batches; engine-first max {mx10}; any batch over 8 must repeat (9 ideas -> 2); all-different at 8 random only {p_none_8:.4f}; mislabelled-axis cell in a 10-cell batch {p_bad:.2f}")
