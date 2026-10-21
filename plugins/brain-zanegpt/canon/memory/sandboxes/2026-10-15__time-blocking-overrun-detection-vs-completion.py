"""Prediction (before run): day = 480 min, six tasks estimated 60,90,45,60,90,45 (390 min, 90 slack). True duration = estimate * bias.
Start delay: a loose to-do list costs 20 min of deciding before every task, a calendar block costs 0 (this is the ASSUMED implementation-intention
effect, a parameter, not evidence). I predict: at bias 1.0 list completes 5 and soft blocks (sequential, no hard stop) 6; at bias 1.5 soft blocks
complete exactly 4 and the loose list 3; a HARD timebox (cut each task at its estimated slot) completes 0 at bias 1.5 but flags the first overrun at
minute 60 versus minute 480 for soft blocks (it only learns at day end); a 25% buffered hard timebox completes 6 only while bias <= 1.25.
Built to BREAK 'time blocking helps': at bias 1.0 with start delay 0 the list must equal soft blocks. Deterministic, stdlib only."""
DAY = 480; EST = (60, 90, 45, 60, 90, 45)
def run(policy, bias, delay):
    t = 0; done = 0; first_flag = None
    for e in EST:
        true = e * bias
        d = delay if policy == "list" else 0
        t += d
        if t >= DAY: break
        if policy in ("list", "soft"):
            if t + true <= DAY + 1e-9: t += true; done += 1
            else:
                t = DAY; first_flag = first_flag or DAY; break
        else:
            slot = e * (1.25 if policy == "buffered" else 1.0)
            if true <= slot + 1e-9: t += true; done += 1   # (slot unused time is idle in a rigid calendar)
            else:
                first_flag = first_flag if first_flag is not None else t + slot
                t += slot
            if policy in ("hard", "buffered") and true <= slot: t = t - true + slot  # rigid calendar: next block starts at slot end
    return done, first_flag
R = {}
for b in (0.8, 1.0, 1.25, 1.5, 2.0):
    R[b] = {p: run(p, b, 20) for p in ("list", "soft", "hard", "buffered")}
    print(b, R[b])
z = run("list", 1.0, 0), run("soft", 1.0, 0)
ok = (R[1.0]["list"][0] == 5 and R[1.0]["soft"][0] == 6 and R[1.5]["soft"][0] == 4 and R[1.5]["list"][0] == 3
      and R[1.5]["hard"][0] == 0 and R[1.5]["hard"][1] == 60 and R[1.5]["soft"][1] == 480
      and R[1.25]["buffered"][0] == 6 and R[1.5]["buffered"][0] < 6 and z[0] == z[1])
print("RESULT:", "PASS" if ok else "FAIL", f"bias1.5: soft {R[1.5]['soft']} list {R[1.5]['list']} hard {R[1.5]['hard']} buffered {R[1.5]['buffered']}; bias1.25 buffered {R[1.25]['buffered']}; zero-delay list==soft {z[0]==z[1]}")
