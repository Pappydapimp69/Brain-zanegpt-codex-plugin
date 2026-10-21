"""CHESS-CLOCKS kernel: simple delay and Bronstein delay leave identical remaining time after
every move and 'differ only in what the display shows during the move'. But the flag falls
DURING a move: under simple delay the clock is frozen for the first d s, so with R s left a
move may take up to R + d; under Bronstein the clock runs from the start and the delay is
only given back when the move is completed, so the flag falls at t = R.
Test: T 60 s, d 5 s; deterministic move-time sequences (LCG, 2-12 s per move, with time-
trouble endings where moves cluster at 4-6 s), up to 80 moves. A player flags when a move's
thinking time exceeds what the scheme allows at that moment. Compare per sequence.
PREDICTION (written before running): after every completed move the two schemes show the
same remaining time (kernel holds); but in >= 20% of sequences that reach time trouble the
player flags under Bronstein and survives under simple delay; never the reverse."""
class LCG:
    def __init__(self, s): self.s = s
    def r(self, m): self.s = (6364136223846793005 * self.s + 1442695040888963407) % 2 ** 64; return (self.s >> 33) % m
T, D = 60.0, 5.0
def play(times, scheme):
    rem = T; hist = []
    for t in times:
        if scheme == "simple":
            if t > rem + D: return "flag", hist
            rem -= max(0.0, t - D)
        else:                                   # Bronstein: clock runs during the move, refund up to D after it
            if t > rem: return "flag", hist
            rem = rem - t + min(t, D)
        hist.append(round(rem, 6))
    return "ok", hist
g = LCG(9); only_b = only_s = trouble = same_hist = 0; N = 2000
for _ in range(N):
    times = [2 + g.r(11) for _ in range(30)] + [4 + g.r(3) for _ in range(50)]   # opening/middlegame then time trouble
    rs, hs = play(times, "simple"); rb, hb = play(times, "bronstein")
    k = min(len(hs), len(hb)); same_hist += hs[:k] == hb[:k]
    if rs == "flag" or rb == "flag" or min(hs[-1:] or [T]) < D: trouble += 1
    only_b += rb == "flag" and rs == "ok"; only_s += rs == "flag" and rb == "ok"
share = only_b / max(trouble, 1)
ok = same_hist == N and share >= 0.2 and only_s == 0
print(f"sequences {N}: remaining time identical move by move (until one flags) in {same_hist}; reached time trouble {trouble}; "
      f"flag under Bronstein only {only_b}, under simple delay only {only_s}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} remaining time identical after every completed move in {same_hist}/{N}; Bronstein flags "
      f"where simple delay survives in {only_b}/{trouble} time-trouble sequences ({share:.0%}); reverse {only_s}")
