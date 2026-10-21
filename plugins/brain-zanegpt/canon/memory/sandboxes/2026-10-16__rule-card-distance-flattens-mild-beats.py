# Severe harm needs distance, mild harm needs closeness; a self-inflicted-only rule card adds cartoon distance (+3).
# Beat score: severe (v>=6): v if v <= cap else 0, cap = effective distance (+ margin 0). Mild (v<=5): v * closeness(d_eff),
# closeness = 1 up to d_eff 4, falling linearly to 0 at d_eff 8. Exact arithmetic, no RNG, stdlib only.
from fractions import Fraction as F
def closeness(d): return F(1) if d <= 4 else max(F(0), F(8 - d, 4))
def beat(v, d, card):
    de = d + (3 if card else 0)
    if v >= 6:
        return F(v) if v <= de + (0 if card else 0) else F(0)   # outside variant gets +2 strength w/o card, capacity d
    return v * closeness(de)
def beat_nc(v, d):
    if v >= 6:
        vv = v + 2
        return F(vv) if vv <= d else F(0)
    return v * closeness(d)
SCHED = {'all-severe': [6, 7, 8, 9, 10], 'all-mild': [1, 2, 3, 4, 5], 'mixed': [2, 4, 6, 8, 10]}
rows = {}
for d in range(0, 11):
    for n, s in SCHED.items():
        nc = sum(beat_nc(v, d) for v in s); c = sum(beat(v, d, True) for v in s)
        rows[(d, n)] = (nc, c)
for d in range(0, 11, 2):
    print('d=%2d ' % d + ' | '.join('%s nc/card=%s/%s' % (n, rows[(d, n)][0], rows[(d, n)][1]) for n in SCHED))
def region(n, sign): return [d for d in range(11) if (rows[(d, n)][1] - rows[(d, n)][0]) * sign > 0]
sev_win, mild_win, mild_loss, mix_win, mix_loss = region('all-severe', 1), region('all-mild', 1), region('all-mild', -1), region('mixed', 1), region('mixed', -1)
print('all-severe card wins d=%s' % sev_win); print('all-mild card wins d=%s loses d=%s' % (mild_win, mild_loss))
print('mixed card wins d=%s loses d=%s' % (mix_win, mix_loss))
ok = (len(sev_win) >= 6 and mild_loss and min(mild_loss) <= 4 and not mild_win and 0 < len(mix_win) and mix_loss)
print('RESULT: %s card helps all-severe at d=%s but hurts all-mild at d=%s (card pushes mild past the closeness limit); the mixed schedule wins at d=%s and loses at d=%s'
      % ('PASS' if ok else 'FAIL', sev_win, mild_loss, mix_win, mix_loss))
