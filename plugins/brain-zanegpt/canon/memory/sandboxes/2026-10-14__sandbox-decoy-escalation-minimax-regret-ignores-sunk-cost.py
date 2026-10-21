# Continue-or-withdraw decision under minimax regret (Savage). States: S1 turnaround, S2 stall.
def regret_choice(acts):
    cols = [max(a[s] for a in acts.values()) for s in range(2)]
    mr = {k: max(cols[s] - a[s] for s in range(2)) for k, a in acts.items()}
    best = min(mr.values())
    return sorted(k for k, v in mr.items() if v == best), mr
base = {"continue": (15, 0), "withdraw": (5, 9)}
w0, m0 = regret_choice(base)
print("base:", w0, m0)
# 1) pure sunk cost S lost under every act: subtract from all payoffs
inv = all(regret_choice({k: (a[0]-S, a[1]-S) for k, a in base.items()})[0] == w0 for S in (0, 10, 100, 1000))
print("sunk cost shifts all acts -> choice unchanged:", inv)
# 2) with the y=20 decoy on the menu (winner: withdraw), what fallacy bonus b for continuing restores continue?
need = [b for b in range(0, 60) if regret_choice({"continue": (15+b, 0+b), "withdraw": (5, 9), "pivot": (0, 20)})[0] == ["continue"]]
print("fallacy bonus restoring continue under the decoy: b >=", min(need) if need else None)
# 3) never-chosen-or-not decoy C=(0,y) added to the menu
seq = []
for y in range(0, 31):
    seq.append((y, regret_choice({**base, "pivot": (0, y)})[0]))
regimes = []
for y, w in seq:
    if not regimes or regimes[-1][2] != w: regimes.append([y, y, w])
    else: regimes[-1][1] = y
for lo, hi, w in regimes: print(f"decoy S2 payoff {lo}..{hi}: winner {w}")
flip_withdraw = [y for y, w in seq if w == ["withdraw"]]
pivot_wins = [y for y, w in seq if w == ["pivot"]]
ok = inv and w0 == ["continue"] and min(flip_withdraw) == 11 and max(flip_withdraw) == 23 and min(pivot_wins) == 25 and bool(need)
print("RESULT: %s base picks continue; sunk-cost shift invariant (%s); decoy S2 payoff 11..23 flips to withdraw without being chosen, 24 ties, >=25 the decoy wins; a continue-only bonus of b>=%s is needed to undo it"
      % ("PASS" if ok else "FAIL", inv, min(need) if need else None))
