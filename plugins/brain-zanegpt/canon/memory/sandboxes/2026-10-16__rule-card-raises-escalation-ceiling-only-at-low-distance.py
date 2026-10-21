# Benign-violation beats + escalation schedule + rule card (who may hurt whom). Deterministic, stdlib only.
# A beat scores its violation v only if 0 < v <= capacity (benign reading arrives at the same moment); else 0.
# Outside-force variant of a gag: stronger (v+2) but capacity is just the framing distance d.
# Self-inflicted variant (what the rule card forces): capacity d+3 (humiliated, not harmed).
SCHEDULES = {'go-big': [2, 4, 6, 8, 10], 'mild': [1, 2, 3, 4, 5], 'ramp': [1, 3, 5, 7, 9]}

def score(sched, d, card):
    tot = 0
    for v in sched:
        if card: vv, cap = v, d + 3          # self-inflicted only
        else:    vv, cap = v + 2, d          # writer takes the stronger outside-force variant
        tot += vv if 0 < vv <= cap else 0
    return tot

rows = {}
for d in range(0, 13):
    for name, s in SCHEDULES.items():
        rows[(d, name)] = (score(s, d, False), score(s, d, True))
for d in (0, 2, 4, 6, 8, 10, 12):
    print('d=%2d' % d, ' '.join('%s no-card/card=%d/%d' % ((n,) + rows[(d, n)]) for n in SCHEDULES))
best_nc = {d: max(rows[(d, n)][0] for n in SCHEDULES) for d in range(13)}
best_c = {d: max(rows[(d, n)][1] for n in SCHEDULES) for d in range(13)}
low_win = [d for d in range(13) if best_c[d] > best_nc[d]]
high_lose = [d for d in range(13) if best_c[d] < best_nc[d]]
tie = [d for d in range(13) if best_c[d] == best_nc[d]]
# is the card's benefit coming from mild schedules too? go-big at fixed distance
gb_zero_nc = [d for d in range(13) if rows[(d, 'go-big')][0] == 0]
gb_zero_c = [d for d in range(13) if rows[(d, 'go-big')][1] == 0]
print('card wins at d=%s; no-card wins at d=%s; tie at d=%s' % (low_win, high_lose, tie))
print('go-big scores 0 without card at d=%s, with card at d=%s' % (gb_zero_nc, gb_zero_c))
# sensitivity: card wins only when the cap boost from self-inflicted framing beats the outside-force strength bonus
def best(d, boost, bonus, card):
    tot = []
    for s in SCHEDULES.values():
        x = 0
        for v in s:
            vv, cap = (v, d + boost) if card else (v + bonus, d)
            x += vv if 0 < vv <= cap else 0
        tot.append(x)
    return max(tot)
grid = {}
for boost in range(0, 5):
    for bonus in range(0, 5):
        w = sum(best(d, boost, bonus, True) > best(d, boost, bonus, False) for d in range(13))
        l = sum(best(d, boost, bonus, True) < best(d, boost, bonus, False) for d in range(13))
        grid[(boost, bonus)] = (w, l)
        print('boost=%d bonus=%d card_wins_d=%d card_loses_d=%d' % (boost, bonus, w, l))
lose_cells = [k for k, (w, l) in grid.items() if l > 0]
le_wins = [k for k, (w, l) in grid.items() if k[0] <= k[1] and w > 0]
print('cells where card loses at some d: %d/25; cells with boost<=bonus where card still wins somewhere: %d/%d'
      % (len(lose_cells), len(le_wins), sum(1 for k in grid if k[0] <= k[1])))
ok = bool(low_win) and bool(high_lose) and max(low_win) < min(high_lose)
print('RESULT: %s card wins at d<=%d and loses at d>=%d (default boost 3, bonus 2); my boost>bonus-only hypothesis is REFUTED: card still wins somewhere in %d of %d boost<=bonus cells'
      % ('PASS' if ok else 'FAIL', max(low_win), min(high_lose), len(le_wins), sum(1 for k in grid if k[0] <= k[1])))
