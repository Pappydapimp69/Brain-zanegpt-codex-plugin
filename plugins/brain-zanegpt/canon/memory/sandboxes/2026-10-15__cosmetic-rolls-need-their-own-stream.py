"""A fight's outcome is decided by a seeded RNG (hit rolls). Adding flavour (which line a character says) that
draws from the SAME stream shifts every later gameplay roll; giving flavour its OWN seeded stream leaves the fight
byte-identical. Deterministic, stdlib only. Mirrors the Boss's Bad Day daughter-lines change."""
import random
def fight(seed, flavour, separate, swings=40, p_hit=.45):
    game = random.Random(seed); talk = random.Random(seed * 7 + 99) if separate else game
    log = []
    for k in range(swings):
        hit = game.random() < p_hit; log.append(hit)
        if flavour and (hit or k % 3 == 0): talk.random()   # pick a line on hits and now and then
    return log
seeds = range(30)
same_changed = sum(fight(s, False, False) != fight(s, True, False) for s in seeds)
sep_changed = sum(fight(s, False, False) != fight(s, True, True) for s in seeds)
hits_drift = sum(abs(sum(fight(s, False, False)) - sum(fight(s, True, False))) for s in seeds) / len(seeds)
print(f"shared stream: {same_changed}/30 fights changed after adding lines (mean hit-count drift {hits_drift:.1f})")
print(f"own stream:    {sep_changed}/30 fights changed")
ok = same_changed >= 25 and sep_changed == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} cosmetic rolls on the gameplay stream changed {same_changed}/30 seeded fights; on their own seeded stream 0/30")
