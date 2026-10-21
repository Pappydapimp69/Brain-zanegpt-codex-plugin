"""Rebuild of seven E46 (on-screen recede cannot be both invisible and unbeatable).
Own fixture: gap 60 m, walk 1.4 m/s, thresholds j = 0.03/0.08/0.15, a different
off-screen model (the player KEEPS WALKING while looking away; the relief backs
off at 1.5x walk speed only while unwatched), and a night deadline with slack s.
Predictions written before running:
 P1 an invisible recede (f = j) delays a disciplined player by exactly 1/(1-j), never more.
 P2 the look-away share that stops a player is 0.4 whatever the walking model (E46's number) -- expect MISS: 0.667 here.
 P3 an invisible recede never makes the relief unreachable for a disciplined player -- expect MISS once a deadline sits within j/(1-j) slack.
"""
GAP, V = 60.0, 1.4

def arrive_time(f=0.0, look_away=0.0, back=1.5, stop_when_away=False):
    walk = V * (1 - look_away) if stop_when_away else V
    close = walk * (1 - f * (1 - look_away)) - back * V * look_away
    return GAP / close if close > 1e-12 else float("inf")

base = arrive_time()
rows = {}
for j in (0.03, 0.08, 0.15):
    rows[j] = arrive_time(f=j) / base
    print(f"j={j:.2f}: invisible recede delay x{rows[j]:.4f} (1/(1-j) = {1/(1-j):.4f})")
p1 = all(abs(rows[j] - 1 / (1 - j)) < 1e-9 for j in rows)

def stop_share(stop_when_away):
    for k in range(0, 1001):
        a = k / 1000
        if arrive_time(look_away=a, stop_when_away=stop_when_away) == float("inf"):
            return a
stop_walk, stop_freeze = stop_share(False), stop_share(True)
print(f"look-away share that stops arrival: keeps walking {stop_walk:.3f}; freezes while looking away {stop_freeze:.3f}")
p2 = abs(stop_walk - 0.4) < 0.01

# deadline: night falls at base*(1+s). Disciplined player, invisible recede f=j=0.08.
stopped = []
for s in (0.02, 0.05, 0.08, 0.10, 0.20):
    t = arrive_time(f=0.08)
    ok = t <= base * (1 + s)
    stopped.append((s, ok))
    print(f"slack {s:.2f}: disciplined player under invisible f=0.08 arrives before night: {ok}")
p3 = all(ok for _, ok in stopped)
checks = [("P1 invisible delay == 1/(1-j)", p1), ("P2 stop share 0.4 in any walking model", p2),
          ("P3 invisible recede never decisive", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks:
    print(("held   " if ok else "MISSED ") + n)
blocked = [s for s, ok in stopped if not ok]
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; delay x{rows[0.03]:.3f}/x{rows[0.08]:.3f}/x{rows[0.15]:.3f}; "
      f"stop share walk {stop_walk:.3f} freeze {stop_freeze:.3f}; invisible f=0.08 blocks slack <= {max(blocked) if blocked else 0}")
