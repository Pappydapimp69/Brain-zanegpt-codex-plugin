"""Sandbox: serial-order effect in idea generation, and which submission rule a
brainstorm should use.

Model (a logic model, not human data): a pool of M ideas with population accessibility
a_i proportional to 1/rank^s (s=1 Zipf: a shared association ladder; s=0 flat). Each person
perturbs accessibility by a lognormal factor exp(sigma*z) (sigma = how idiosyncratic people
are) and generates ideas in order by sampling without replacement proportional to that
personal accessibility (Plackett-Luce). Rarity of an idea = -log2(share of a 3000-person
reference crowd whose 10-idea list contains it), with add-one smoothing.

Groups of 8 each generate 10 ideas and submit 3 per person:
  first3   the first three ideas each person thought of
  last3    ideas 8-10
  strike   cross-strike: drop any idea another group member also listed, submit the
           first three survivors (pad with last ideas if fewer than three survive)
Deterministic: seeded random.Random, stdlib only.
"""
import math, random, bisect

M, K, GROUP, SUBMIT, CROWD, GROUPS = 300, 10, 8, 3, 3000, 200


def person_list(rng, base, sigma):
    w = [b * math.exp(sigma * rng.gauss(0, 1)) for b in base]
    # Plackett-Luce without replacement via exponential race: key = Exp(1)/w
    keys = sorted(range(M), key=lambda i: rng.expovariate(1.0) / w[i])
    return keys[:K]


def scenario(s, sigma, seed):
    rng = random.Random(seed)
    base = [1.0 / (r + 1) ** s for r in range(M)]
    counts = [0] * M
    for _ in range(CROWD):
        for i in person_list(rng, base, sigma):
            counts[i] += 1
    rar = [-math.log2((c + 1) / (CROWD + 1)) for c in counts]
    pos = [0.0] * K
    sums = {'first3': [0.0, 0, 0], 'last3': [0.0, 0, 0], 'strike': [0.0, 0, 0]}
    for _ in range(GROUPS):
        lists = [person_list(rng, base, sigma) for _ in range(GROUP)]
        for L in lists:
            for p, i in enumerate(L):
                pos[p] += rar[i]
        subs = {'first3': [L[:SUBMIT] for L in lists], 'last3': [L[-SUBMIT:] for L in lists]}
        st = []
        for j, L in enumerate(lists):
            others = set(x for k, O in enumerate(lists) if k != j for x in O)
            keep = [x for x in L if x not in others][:SUBMIT]
            for x in reversed(L):
                if len(keep) >= SUBMIT:
                    break
                if x not in keep:
                    keep.append(x)
            st.append(keep)
        subs['strike'] = st
        for name, S in subs.items():
            flat = [x for P in S for x in P]
            sums[name][0] += sum(rar[x] for x in flat)
            sums[name][1] += len(flat)
            sums[name][2] += sum(1 for x in flat if flat.count(x) == 1)
    n_people = GROUPS * GROUP
    curve = [p / n_people for p in pos]
    out = {k: (v[0] / v[1], v[2] / v[1]) for k, v in sums.items()}
    return curve, out


if __name__ == '__main__':
    cases = [('S1 shared ladder s=1 sigma=0.5', 1.0, 0.5),
             ('S2 shared ladder s=1 sigma=1.5', 1.0, 1.5),
             ('S3 BREAK idiosyncratic s=1 sigma=4', 1.0, 4.0),
             ('S4 BREAK flat pool s=0 sigma=0.5', 0.0, 0.5)]
    res = {}
    for k, (name, s, sg) in enumerate(cases):
        curve, out = scenario(s, sg, 1000 + k)
        res[name] = (curve, out)
        gap = out['last3'][0] - out['first3'][0]
        print(name)
        print('   rarity by serial position:', ' '.join(f'{c:.2f}' for c in curve))
        for m, (r, u) in out.items():
            print(f'   {m:7s} mean rarity {r:.2f} bits, unique-in-group {100*u:.1f}%')
        print(f'   last3 - first3 gap {gap:.2f} bits; strike - last3 {out["strike"][0]-out["last3"][0]:.2f} bits')
    g = {n: res[n][1]['last3'][0] - res[n][1]['first3'][0] for n in res}
    gs = [g[c[0]] for c in cases]
    ok = gs[0] >= 1.0 and abs(gs[3]) < 0.1 and gs[2] < 0.5 * gs[0]
    print(f"RESULT: {'PASS' if ok else 'FAIL'} last3-first3 rarity gap: shared ladder {gs[0]:.2f} bits (sigma 1.5: {gs[1]:.2f}), "
          f"idiosyncratic sigma 4: {gs[2]:.2f}, flat pool: {gs[3]:.2f}; strike minus last3 on shared ladder "
          f"{res[cases[0][0]][1]['strike'][0]-res[cases[0][0]][1]['last3'][0]:.2f} bits")
