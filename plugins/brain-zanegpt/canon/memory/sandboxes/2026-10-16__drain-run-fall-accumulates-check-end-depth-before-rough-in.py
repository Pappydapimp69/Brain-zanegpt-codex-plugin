"""Drain-waste pipe fall (real scenario: a 3-inch basement-floor drain run laid at the
common minimum slope of 1/4 inch per foot, 2 percent, per plumbing code for pipes up to 3 in).
Assumption: per-piece slope rounding is harmless. Question: how does total fall behave, and does the
run's far end still fit the available depth?
Prediction (before run): a 40 ft run at 1/4 in/ft drops exactly 10.00 in; when each 10 ft stick is
hung with its drop rounded DOWN to the nearest 1/2 inch the run loses 0.5 to 2 in of fall and gets
flatter than the 1/4 in/ft minimum (effective slope below 0.25); with 3 in of pipe + 1.5 in of cover
the 40 ft run needs 14.5 in of depth, so a 12 in deep joist/slab bay FAILS the run. Breaker: a run
where every stick drop is already a multiple of 1/2 in (10 ft x 1/4 = 2.5 in) loses nothing."""
import math
SLOPE = 0.25  # inches per foot
def fall(run_ft, stick_ft, round_to=None):
    left, total = run_ft, 0.0
    while left > 1e-9:
        L = min(stick_ft, left); d = L * SLOPE
        if round_to: d = math.floor(d / round_to + 1e-9) * round_to
        total += d; left -= L
    return total
exact = fall(40, 10)
odd = fall(40, 7)                        # 7 ft sticks: 1.75 in drop each
odd_r = fall(40, 7, round_to=0.5)        # hung to the half inch, rounded down
even_r = fall(40, 10, round_to=0.5)      # breaker: 2.5 in drops, already on the half inch
eff = lambda f, r: f / r
need = exact + 3 + 1.5
print(f"exact 40ft: {exact:.2f} in; 7ft sticks rounded: {odd_r:.2f} in (eff {eff(odd_r,40):.3f} in/ft); "
      f"10ft sticks rounded: {even_r:.2f} in; depth needed {need:.1f} in vs bay 12")
ok = (abs(exact - 10) < 1e-9 and 0.5 <= exact - odd_r <= 2.0 and eff(odd_r, 40) < SLOPE
      and need > 12 and even_r == exact)
print(f"RESULT: {'PASS' if ok else 'FAIL'} exact={exact:.2f} rounded_7ft={odd_r:.2f} lost={exact-odd_r:.2f} need={need:.1f} breaker_loss={exact-even_r:.2f}")
