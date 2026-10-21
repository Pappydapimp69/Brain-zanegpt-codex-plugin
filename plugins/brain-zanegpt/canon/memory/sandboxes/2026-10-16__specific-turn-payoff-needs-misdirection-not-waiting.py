# Premise check (stock vs specific turn) x information-gap tension x H/E/X check. Exact Bayes, no RNG, stdlib only.
# Audience hypotheses about where the sketch is going: 0 = stock form, 1 = the writer's specific turn, 2,3 = other turns.
# Each beat is a clue = likelihood vector over the 4 hypotheses. Reveal beat = clue only the specific turn explains.
import math

def posterior(prior, clues):
    p = list(prior)
    for c in clues:
        p = [a * b for a, b in zip(p, c)]
        s = sum(p); p = [x / s for x in p]
    return p
def entropy(p): return -sum(x * math.log2(x) for x in p if x > 0)

def run(p_stock, n, kind, fair):
    rest = (1 - p_stock) / 3
    prior = [p_stock, rest, rest, rest]
    # fair = minimum likelihood of each earlier clue under the specific turn (retro-consistency, 'H or E not X')
    neutral = [1, 1, 1, 1]                       # clue fits stock and specific alike, tells audience nothing
    mislead = [1, fair, fair, fair]              # favors stock; still explainable by the specific turn at likelihood `fair`
    stock = [1, 0.05, 0.05, 0.05]                # clues that truly point at stock (hack sketch: payoff IS stock)
    clues = {'neutral': neutral, 'mislead': mislead, 'stock-payoff': stock}[kind]
    post = posterior(prior, [clues] * n)
    surprisal = -math.log2(post[1]) if kind != 'stock-payoff' else -math.log2(post[0])   # bits at the reveal
    gap = entropy(post)                          # tension just before the reveal
    return surprisal, gap, post

print('p_stock n kind -> surprisal bits, gap bits')
tab = {}
for p in (0.5, 0.9):
    for n in (0, 2, 4):
        for kind in ('stock-payoff', 'neutral', 'mislead'):
            s, g, _ = run(p, n, kind, 0.3)
            tab[(p, n, kind)] = (s, g)
            print('%.1f %d %-12s -> %.2f %.2f' % (p, n, kind, s, g))
# fair-play sweep: how far can misdirection go before earlier clues stop being explainable (fair < 0.1 = reads as a new game)
for fair in (0.5, 0.3, 0.1, 0.01):
    s, g, _ = run(0.9, 4, 'mislead', fair)
    print('fair=%.2f surprisal=%.2f gap=%.2f %s' % (fair, s, g, 'explainable' if fair >= 0.1 else 'reads as X (new game)'))
neutral_flat = all(abs(tab[(0.9, 0, 'neutral')][0] - tab[(0.9, n, 'neutral')][0]) < 1e-9 for n in (2, 4))
mis_up = tab[(0.9, 4, 'mislead')][0] > tab[(0.9, 0, 'mislead')][0] + 3
stock_low = tab[(0.9, 4, 'stock-payoff')][0] < 0.5
fair_cap = run(0.9, 4, 'mislead', 0.1)[0] < run(0.9, 4, 'mislead', 0.01)[0]
ok = neutral_flat and mis_up and stock_low and fair_cap
print('RESULT: %s waiting with neutral clues leaves the specific-turn surprisal flat at %.2f bits for n=0,2,4; misdirection raises it %.2f -> %.2f bits at n=4 (fair=0.3) and stock-payoff stays %.2f bits; below fair=0.1 the extra bits come from clues the turn no longer explains'
      % ('PASS' if ok else 'FAIL', tab[(0.9, 0, 'neutral')][0], tab[(0.9, 0, 'mislead')][0], tab[(0.9, 4, 'mislead')][0], tab[(0.9, 4, 'stock-payoff')][0]))
