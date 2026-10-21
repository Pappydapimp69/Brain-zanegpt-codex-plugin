"""Rebuild (own fixture): perfect faro shuffles on one tracked card. Claim: Elmsley's binary rule is the fewest faros
for every target position, even n=8..54, and any card returns to the top within 6 faros at 52.
PREDICTION (before run): (1) BFS over single-card positions (states = n positions, moves in/out) finds a route no shorter
than the binary rule for every start-at-top target at every even n 8..54 (0 mismatches); (2) at n=52 the worst
shortest route from any position to the top is <= 6; (3) BREAK: the 'rule' fails for odd n (outer shuffles
of odd decks differ), so I also run odd n 9..53 where the same binary recipe is expected to mismatch for some targets
(>= 1 mismatch); (4) a buried card going to the top, from every start, at n=52 maximum is 6 but at n=8 whatever BFS says
is at most log2(n)=3 (card positions 8). Assumption: bit-by-bit in/out digit rule uses 0-based position from the top.
Wrong if (1) shows any mismatch at even n."""
from collections import deque
def out(i, n): return 2 * i if i < n // 2 else 2 * i - (n - 1)
def inn(i, n): return 2 * i + 1 if i < n // 2 else 2 * i - n
def bfs(n, src):
    d = {src: 0}; q = deque([src])
    while q:
        x = q.popleft()
        for f in (out, inn):
            y = f(x, n)
            if 0 <= y < n and y not in d: d[y] = d[x] + 1; q.append(y)
    return d
def rule_route(n, p):
    """binary rule from the top (position 0) to position p: bits of p MSB first; 1=in, 0=out; apply and return reached pos."""
    bits = bin(p)[2:] if p else ""   # p=0: already on top, 0 faros (first run mis-counted 1 out-shuffle: 24 phantom mismatches)
    pos = 0; steps = 0
    for b in bits:
        pos = inn(pos, n) if b == "1" else out(pos, n); steps += 1
    return pos, steps
def rule_len(n, p):   # first bit needs care: top card under 'in' moves to 1, 'out' keeps 0
    # standard rule: write p+... verified by BFS below instead of assuming; here use p itself
    return rule_route(n, p)
evmis = 0; evtot = 0; reach_fail = 0; shorter = 0
for n in range(8, 55, 2):
    d = bfs(n, 0)
    for p in range(n):
        pos, steps = rule_route(n, p)
        evtot += 1
        if pos != p: reach_fail += 1       # rule does not even land on p
        elif p in d and steps > d[p]: shorter += 1   # BFS shorter than rule
        elif p not in d: reach_fail += 1
oddmis = 0
for n in range(9, 54, 2):
    d = bfs(n, 0)
    for p in range(n):
        pos, steps = rule_route(n, p)
        if pos != p or (p in d and steps > d[p]): oddmis += 1
# return-to-top: max over start of shortest distance TO position 0 (reverse search)
def to_top(n):
    best = 0
    for s in range(n):
        d = bfs(n, s)
        if 0 not in d: return None
        best = max(best, d[0])
    return best
t52 = to_top(52); t8 = to_top(8)
print("even n 8..54: targets", evtot, "rule-not-landing", reach_fail, "BFS-shorter", shorter, "| odd n mismatches", oddmis)
print("worst shortest route to top: n=52", t52, "n=8", t8)
ok = reach_fail == 0 and shorter == 0 and t52 is not None and t52 <= 6 and oddmis >= 1
print("RESULT: %s even n 8..54 rule-wrong %d and BFS-shorter %d of %d targets; worst to-top n=52 %s, n=8 %s; odd-n mismatches %d"
      % ("PASS" if ok else "FAIL", reach_fail, shorter, evtot, t52, t8, oddmis))
