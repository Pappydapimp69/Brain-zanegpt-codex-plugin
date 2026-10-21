"""Prediction (before run), 9x9 open grid, seeker fixed at (4,4), hidden actor tries to reach goal (0,0), hidden moves first each turn then seeker moves one step; all 80 spawns run:
 omniscient seeker -> hidden win rate < signals seeker win rate; signals seeker (noise marker every 2nd move + goal bias) keeps hidden win rate strictly between 0.2 and 0.8;
 no-grace/unsafe-spawn variant has >0 turn-1 captures, grace+safe spawn has 0; noise every turn (period 1) matches omniscient (boundary: too many signals = omniscience).
Deterministic, stdlib only."""
N = 9; GOAL = (0, 0); SEEK0 = (4, 4)

def step(a, b):
    """one king-less (4-dir) greedy step from a toward b, x axis first."""
    x, y = a
    if x != b[0]: x += 1 if b[0] > x else -1
    elif y != b[1]: y += 1 if b[1] > y else -1
    return (x, y)

def play(spawn, mode, period=2, grace=False):
    h, s = spawn, SEEK0
    marker = None; turn = 0; moves = 0
    while turn < 60:
        turn += 1
        if h == s and not (grace and turn == 1):
            return ("caught", turn)
        h = step(h, GOAL); moves += 1
        if h == GOAL: return ("escaped", turn)
        if period and moves % period == 0: marker = h
        if not (grace and turn == 1):
            if h == s: return ("caught", turn)
            if mode == "omni": tgt = h
            else: tgt = marker if marker else GOAL
            s = step(s, tgt)
            if h == s: return ("caught", turn)
    return ("timeout", turn)

def stats(mode, period=2, grace=False, safe=False):
    spawns = [(x, y) for x in range(N) for y in range(N) if (x, y) != GOAL and (x, y) != SEEK0 and (not safe or abs(x - 4) + abs(y - 4) >= 3)]
    r = [play(sp, mode, period, grace) for sp in spawns]
    win = sum(o != "caught" for o, _ in r) / len(r)
    t1 = sum(o == "caught" and t == 1 for o, t in r)
    return win, t1, len(r)

omni = stats("omni"); sig2 = stats("sig", 2); sig1 = stats("sig", 1); sigN = stats("sig", 0)
ng = stats("sig", 2, grace=False, safe=False); gr = stats("sig", 2, grace=True, safe=True)
for k, v in (("omni", omni), ("signals p2", sig2), ("signals p1", sig1), ("no signals", sigN), ("no grace/unsafe", ng), ("grace+safe", gr)):
    print(f"{k:16} hidden_win={v[0]:.3f} turn1_captures={v[1]} spawns={v[2]}")
c1 = omni[0] < sig2[0]
c2 = 0.2 < sig2[0] < 0.8
c3 = ng[1] > 0 and gr[1] == 0
c4 = abs(sig1[0] - omni[0]) < 0.05
c5 = sigN[0] > sig2[0]
print("checks", c1, c2, c3, c4, c5)
print("RESULT:", "PASS" if all((c1, c2, c3, c4, c5)) else "FAIL", f"omni={omni[0]:.3f} signals={sig2[0]:.3f} noSignals={sigN[0]:.3f} p1={sig1[0]:.3f} t1_nograce={ng[1]} t1_grace={gr[1]}")
