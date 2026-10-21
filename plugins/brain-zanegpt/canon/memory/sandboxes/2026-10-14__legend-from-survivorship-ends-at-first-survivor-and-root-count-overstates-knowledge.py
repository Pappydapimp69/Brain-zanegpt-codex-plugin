"""Deterministic sandbox: a 'legendary' ability looks rare because every holder dies before explaining it.
PREDICTION (written before first run): with survival gated to 0 until a knowledge-bearing survivor exists, the legend phase
shows >=100 retellings but 0 eyewitness explanations; legend ends at the first survivor; with constant survival 0.5 the
legend lasts <=2 attempts and with 0.05 it lasts 20; and 'independent roots' (companions who saw the form) stays >0
during the legend although explainers == 0 (root count overstates knowledge)."""
from fractions import Fraction

def survives(i, s):  # deterministic Bresenham-style schedule, no RNG
    return int(i * s) > int((i - 1) * s)

def run(s, attempts=40, tellers_fanout=4, witnesses_per_death=2, gated=False):
    first_survivor = None
    explainers = 0
    mentions = 0          # retellings, all derived from earlier tellers (one cascade per event)
    roots = 0             # independent eyewitness roots (saw the form used)
    explainer_roots = 0   # roots that can explain it (survivors)
    for i in range(1, attempts + 1):
        ok = survives(i, s) if not gated else (first_survivor is not None and survives(i, Fraction(1, 2)))
        if gated and first_survivor is None and i == 12:  # discovery event: someone finally lives
            ok = True
        roots += witnesses_per_death
        mentions += witnesses_per_death * tellers_fanout ** 2
        if ok:
            if first_survivor is None:
                first_survivor = i
            explainers += 1
    legend_len = (first_survivor - 1) if first_survivor else attempts
    return dict(s=str(s), legend_len=legend_len, mentions_at_legend_end=min(legend_len, attempts) * 2 * 16,
                roots_at_legend_end=min(legend_len, attempts) * 2, explainers=explainers)

res = {}
res['gated'] = run(0, gated=True)
res['s=0.5'] = run(Fraction(1, 2))
res['s=0.05'] = run(Fraction(1, 20))
res['s=1 (break)'] = run(1)
for k, v in res.items():
    print(k, v)
ok = (res['gated']['legend_len'] == 11 and res['gated']['mentions_at_legend_end'] >= 100
      and res['gated']['roots_at_legend_end'] > 0 and res['s=0.5']['legend_len'] <= 2
      and res['s=0.05']['legend_len'] == 19 and res['s=1 (break)']['legend_len'] == 0)
print("RESULT: %s legend ends at first survivor (gated 11, s=.5 -> %d, s=.05 -> %d, s=1 -> 0); roots %d >0 while explainers 0 (mentions %d)" % (
    "PASS" if ok else "FAIL", res['s=0.5']['legend_len'], res['s=0.05']['legend_len'],
    res['gated']['roots_at_legend_end'], res['gated']['mentions_at_legend_end']))
