# Does "the boss acts twice once you have companions" make boss threat grow with party size N? (re-verifies
# brain-builder E5 from a new angle: Stonewake numbers, deterministic expected-value round sim, no RNG)
D, H, BOSS_HP, HIT = 20.0, 90.0, 300.0, 18.0   # per-member damage/round, member HP, boss HP, boss hit
def fight(N, rule, rounds=200):
    hp = [H] * N; boss = BOSS_HP
    for r in range(1, rounds + 1):
        alive = [i for i in range(N) if hp[i] > 0]
        boss -= D * len(alive)
        if boss <= 0: return 'win', r, sum(max(0, h) for h in hp) / (H * N)
        acts = 2 if (rule in ('extra', 'game') and N >= 2) else 1
        for a in range(acts):
            alive = [i for i in range(N) if hp[i] > 0]
            if not alive: break
            aoe = rule == 'aoe' or (rule == 'game' and a == 0 and r % 3 == 0)
            if aoe:
                for i in alive: hp[i] -= HIT
            else:
                hp[min(alive, key=lambda i: hp[i])] -= HIT   # focus the weakest, the worst case for the party
        if all(h <= 0 for h in hp): return 'lose', r, 0.0
    return 'timeout', rounds, 0
res = []; table = {}
for rule in ('single', 'extra', 'aoe', 'game'):
    row = [fight(N, rule) for N in (1, 2, 3, 4)]; table[rule] = row
    print(f"{rule:6s} " + "  ".join(f"N={N}:{o[0]} r{o[1]} hpleft {o[2]:.2f}" for N, o in zip((1, 2, 3, 4), row)))
hp = {k: [o[2] for o in v] for k, v in table.items()}
# 1) a fixed single-target boss gets steadily weaker as N grows (party keeps more HP at N=4 than N=2)
res.append(hp['single'][3] > hp['single'][1])
# 2) BREAK case for my claim: acting twice is a constant factor - from N=2 to N=4 the party's leftover HP still climbs
res.append(hp['extra'][3] > hp['extra'][1] + .15)
# 3) AoE output scales with N: leftover HP still rises (kill time ~1/N) but at well under the single-target slope
#    (first-run prediction said 'flat' - refuted: 0.00 -> 0.40)
gain = lambda k: hp[k][3] - hp[k][1]
res.append(gain('aoe') < .6 * gain('single') and gain('extra') > .8 * gain('single'))
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" slope N=2->4 single +{gain('single'):.2f}, acts-twice +{gain('extra'):.2f}, AoE +{gain('aoe'):.2f}; leftover HP N=2->4: single {hp['single'][1]:.2f}->{hp['single'][3]:.2f}, acts-twice {hp['extra'][1]:.2f}->{hp['extra'][3]:.2f}, AoE {hp['aoe'][1]:.2f}->{hp['aoe'][3]:.2f}, game mix {hp['game'][1]:.2f}->{hp['game'][3]:.2f}")
