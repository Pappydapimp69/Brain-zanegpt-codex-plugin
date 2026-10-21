"""Prediction (before run): a tick scheduler that runs 16.7% slow (period 20 ms instead of 17.14... modelled as 6 ticks per 7 expected)
still reaches target tick 600, so a poll-until-state check passes 3/3 scenarios (false all-clear), while a poll plus an
elapsed-time budget check (target_ticks * 1000/60 ms * 1.05) fails the slow scheduler and passes the exact one.
Built to break: a scheduler only 3% slow must pass the 5% budget (the elapsed check must not be a hair-trigger).
Integer milliseconds, deterministic, stdlib only."""
def reach(target, num, den):
    # scheduler advances `num` ticks every `den` expected ticks; returns wall ms (x1000 units) when target reached
    tick = 0; wall_us = 0
    while tick < target:
        wall_us += 16_667 * den // num        # slower scheduler takes longer per tick
        tick += 1
    return tick, wall_us // 1000

TARGET = 600
budget = TARGET * 1000 // 60 * 105 // 100
cases = {"exact": (1, 1), "slow16.7": (6, 7), "slow3": (100, 103)}
res = {}
for name, (n, d) in cases.items():
    t, ms = reach(TARGET, n, d)
    res[name] = (t == TARGET, ms <= budget, ms)
print(res, "budget", budget)
poll_pass = sum(v[0] for v in res.values())
ok = poll_pass == 3 and res["exact"][1] and not res["slow16.7"][1] and res["slow3"][1]
print("RESULT:", "PASS" if ok else "FAIL", f"poll_only_pass={poll_pass}/3 budget_ms={budget} " + " ".join(f"{k}:ms={v[2]},within={v[1]}" for k,v in res.items()))
