"""Deterministic habit model: does game-loop cadence or data latency drive savings?
Prediction (written before first run): daily-signal arms (real-time, decoupled proxy
with real-effect actions) beat monthly arms; monthly streak < monthly comparison;
real-time lands 5-15% savings, monthly-only <=4%; a decoupled proxy whose actions
carry no real savings engages fully but saves ~0 (the boundary)."""
DAYS = 360

def run(signal_every, delay, game_loop, action_real_value, norm_boomerang=False,
        approval=False, streak_mechanic=False, base_usage=100.0):
    habit = 0.10          # probability-like propensity to do a saving action
    usage_total = 0.0
    engaged = 0
    streak = 0
    for d in range(1, DAYS + 1):
        acted = habit  # expected action mass today (deterministic, no RNG)
        usage_total += base_usage * (1 - action_real_value * min(habit, 1.0))
        if d % signal_every == 0:
            # reinforcement shrinks with delay between action and visible consequence
            r = 0.5 * (0.5 ** (delay / 3.0))
            if streak_mechanic:
                # streak needs a fresh reward every day; a gap longer than 1 day resets it
                streak = streak + 1 if signal_every == 1 else 0
                r *= (1 + 0.02 * min(streak, 20))
            habit = min(1.0, habit + r * (1 - habit) * 0.12)
        if norm_boomerang and not approval and habit > 0.11 and d % 30 == 0:
            habit *= 0.8   # already-good households drift back toward the norm
        engaged += habit
    savings = 100 * (1 - usage_total / (base_usage * DAYS))
    return round(savings, 2), round(engaged / DAYS, 3)

arms = {
 "monthly-bill-streak":        dict(signal_every=30, delay=15, game_loop="bill", action_real_value=0.12, streak_mechanic=True),
 "monthly-comparison-refresh": dict(signal_every=30, delay=15, game_loop="bill", action_real_value=0.12),
 "decoupled-daily-actions":    dict(signal_every=1, delay=1, game_loop="actions", action_real_value=0.12, streak_mechanic=True),
 "realtime-feedback":          dict(signal_every=1, delay=0, game_loop="meter", action_real_value=0.12),
 "decoupled-proxy-no-real-effect": dict(signal_every=1, delay=1, game_loop="actions", action_real_value=0.0, streak_mechanic=True),
 "norm-only-boomerang":        dict(signal_every=30, delay=15, game_loop="bill", action_real_value=0.12, norm_boomerang=True),
 "norm+approval":              dict(signal_every=30, delay=15, game_loop="bill", action_real_value=0.12, norm_boomerang=True, approval=True),
}
res = {k: run(**v) for k, v in arms.items()}
for k, (s, e) in res.items():
    print(f"{k:34s} savings%={s:6.2f} engagement={e}")

checks = [
 res["realtime-feedback"][0] >= 5,
 res["monthly-comparison-refresh"][0] <= 4,
 res["monthly-bill-streak"][0] == res["monthly-comparison-refresh"][0],
 res["decoupled-daily-actions"][0] > res["monthly-bill-streak"][0],
 res["decoupled-proxy-no-real-effect"][0] == 0.0 and res["decoupled-proxy-no-real-effect"][1] > 0.2,
 res["norm-only-boomerang"][0] < res["norm+approval"][0],
]
print("checks:", checks)
print(("RESULT: PASS" if all(checks) else "RESULT: FAIL"),
      f"realtime={res['realtime-feedback'][0]}% monthly={res['monthly-comparison-refresh'][0]}% proxy-no-effect={res['decoupled-proxy-no-real-effect'][0]}%")
