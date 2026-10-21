# Composes ipm-d1-rank-needs-derived-link-not-new-noun-check (rank recuts on IPM x D1 using a derived-from-game link
# check, not a new-noun check), rank-ipm-times-d1-needs-fidelity-retention-link (flashy low-fidelity recuts convert
# more but retain worse: D1 .40 derived vs .20 not) and ideas:COMEDY-CRAFT/vary-the-comic-engine-not-the-topic
# (vary the engine across the batch). Added: each of 8 engines has its own chance of producing a derived recut
# (engine k: 0.15 + 0.10*k, so cosmic/escalation-type engines are rarely derived). 12 recuts per batch, engines assigned
# round-robin then random. Rank by IPM x estimated D1 where the check marks faithful: link = derived, noun = random
# 50% of the time biased to flashy (not derived). 2000 seeded batches, true value = ipm x true D1.
# PREDICTION (before run): the link gate leaves fewer distinct engines among the recuts it passes (mean <= 5.0 of 8,
# versus >= 6.5 for noun), the link top-3 repeats an engine in >= 20 points more batches than noun, yet link still beats
# noun on mean true value of the top pick by > 10%; a cap of 1 per engine on the link top-3 costs < 10% true value.
# BREAK: if every engine is equally derivable (0.5), the link gate should not narrow engines (distinct >= 6.5).
import random
E, N, T = 8, 12, 2000
def batch(rnd, flat):
    out = []
    for i in range(N):
        e = i % E if i < E else rnd.randrange(E)
        p = 0.5 if flat else 0.15 + 0.10 * e
        derived = rnd.random() < p
        ipm = rnd.uniform(4, 8) + (2.5 if not derived else 0)
        d1 = 0.40 if derived else 0.20
        out.append((e, derived, rnd.random() < 0.5 or not derived, ipm, d1))
    return out
def run(flat, seed=11):
    rnd = random.Random(seed)
    acc = dict(dn=0, dl=0, rn=0, rl=0, vn=0, vl=0, loss=0, bn=0, n=0)
    for _ in range(T):
        b = batch(rnd, flat)
        link_ok = [v for v in b if v[1]]
        noun_ok = [v for v in b if v[2]]
        if not link_ok: continue
        est_l = sorted(link_ok, key=lambda v: -v[3] * 0.40)
        est_n = sorted(b, key=lambda v: -v[3] * (0.40 if v[2] else 0.20))
        tv = lambda v: v[3] * v[4]
        acc["dl"] += len({v[0] for v in link_ok}); acc["dn"] += len({v[0] for v in noun_ok})
        top_l, top_n = est_l[:3], est_n[:3]
        acc["rl"] += len({v[0] for v in top_l}) < 3; acc["rn"] += len({v[0] for v in top_n}) < 3
        acc["vl"] += tv(est_l[0]); acc["vn"] += tv(est_n[0])
        seen, cap = set(), []
        for v in est_l:
            if v[0] not in seen: seen.add(v[0]); cap.append(v)
            if len(cap) == 3: break
        acc["loss"] += (sum(map(tv, top_l)) - sum(map(tv, cap))) / sum(map(tv, top_l))
        acc["n"] += 1
    n = acc["n"]
    return {k: v / n for k, v in acc.items() if k != "n"}
a, b = run(False), run(True)
for name, r in (("engine-dependent derivability", a), ("flat derivability (BREAK)", b)):
    print(f"{name}: distinct engines left link {r['dl']:.2f} noun {r['dn']:.2f}; top3 repeats engine link {r['rl']*100:.1f}% noun {r['rn']*100:.1f}%; "
          f"top-pick true value link {r['vl']:.2f} noun {r['vn']:.2f}; cap-1 loss {r['loss']*100:.1f}%")
ok = (a["dl"] <= 5.0 and a["dn"] >= 6.5 and a["rl"] - a["rn"] >= 0.20 and a["vl"] > 1.10 * a["vn"] and a["loss"] < 0.10 and b["dl"] >= 6.5)
print(f"RESULT: {'PASS' if ok else 'FAIL'} distinct engines link {a['dl']:.2f} vs noun {a['dn']:.2f}; top3 repeat gap {100*(a['rl']-a['rn']):.1f} pts; value ratio {a['vl']/a['vn']:.2f}; cap-1 loss {a['loss']*100:.1f}%; flat-derivability distinct {b['dl']:.2f}")
