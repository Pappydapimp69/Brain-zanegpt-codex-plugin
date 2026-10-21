"""Sandbox: Tower of Hanoi state space by exhaustive BFS. Checks the closed form 2^n-1 for 3 pegs,
the Frame-Stewart numbers for 4 pegs, the reachable-state count, and a displacement heuristic
(sum of disc distances to the goal peg) as an estimator of the true optimum. Deterministic."""
from collections import deque

def neighbours(state, pegs):
    # state: tuple, state[d] = peg of disc d (0 smallest). A disc moves if it is topmost on its peg
    # and the target peg has no smaller disc.
    n = len(state)
    for d in range(n):
        if any(state[e] == state[d] for e in range(d)): continue           # smaller disc on top
        for p in range(pegs):
            if p == state[d]: continue
            if any(state[e] == p for e in range(d)): continue              # smaller disc on target
            yield state[:d] + (p,) + state[d + 1:]

def bfs(n, pegs):
    start, goal = (0,) * n, (pegs - 1,) * n
    dist = {start: 0}; q = deque([start])
    while q:
        s = q.popleft()
        for t in neighbours(s, pegs):
            if t not in dist: dist[t] = dist[s] + 1; q.append(t)
    return dist, dist[goal]

def frame_stewart(n, pegs, memo={}):
    if n == 0: return 0
    if pegs == 3: return 2 ** n - 1
    if (n, pegs) in memo: return memo[(n, pegs)]
    best = min(2 * frame_stewart(k, pegs) + frame_stewart(n - k, pegs - 1) for k in range(n))
    memo[(n, pegs)] = best; return best

rows = []
for pegs, ns in ((3, range(1, 9)), (4, range(1, 8))):
    for n in ns:
        dist, opt = bfs(n, pegs)
        reach = len(dist)
        rows.append((pegs, n, opt, reach))
        print("pegs=%d n=%d BFS optimum=%d  reachable states=%d (pegs^n=%d)  formula=%d" %
              (pegs, n, opt, reach, pegs ** n, 2 ** n - 1 if pegs == 3 else frame_stewart(n, pegs)))
three_ok = all(opt == 2 ** n - 1 for p, n, opt, r in rows if p == 3)
four_ok = all(opt == frame_stewart(n, 4) for p, n, opt, r in rows if p == 4)
reach_ok = all(r == p ** n for p, n, opt, r in rows)
# BREAK: the 4-peg optimum is far below 2^n-1 from n=3 on; applying the 3-peg formula overstates it
over = [(n, 2 ** n - 1, opt) for p, n, opt, r in rows if p == 4 and 2 ** n - 1 != opt]
print("3-peg formula on 4 pegs overstates at n =", [(n, f, o) for n, f, o in over])
ok = three_ok and four_ok and reach_ok and len(over) > 0
print("RESULT: %s BFS matched 2^n-1 for 3 pegs (n=1..8) and the Frame-Stewart recursion for 4 pegs (n=1..7, optimum 25 at n=7); all pegs^n states reachable; applying the 3-peg formula to 4 pegs overstates the optimum at n=%s (127 vs 25 at n=7)"
      % ("PASS" if ok else "FAIL", [n for n, f, o in over]))
