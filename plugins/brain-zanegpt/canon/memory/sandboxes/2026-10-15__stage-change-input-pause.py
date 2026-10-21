"""A player tapping through a sequence of tap-to-advance steps: how many taps meant for step N land on step N+1?
The player taps at a steady interval and only stops after noticing the step changed (reaction time).
Deterministic, stdlib only."""
def leaked(interval, reaction, pause, steps=6, taps_per_step=3):
    t, leak, step, n, lock_until = 0.0, 0, 0, 0, 0.0
    changed_at = None
    while step < steps:
        t = round(t + interval, 6)
        if changed_at is not None and t >= changed_at + reaction:   # player has noticed; restarts deliberately
            changed_at = None
        if t < lock_until:                     # input ignored during the pause
            continue
        if changed_at is not None:             # a tap still meant for the previous step
            leak += 1
        n += 1
        if n >= taps_per_step:
            step += 1; n = 0; changed_at = t; lock_until = t + pause
    return leak
ok = True
for interval, reaction, pause, note in [(.18, .30, 0, 'no pause'), (.18, .30, .6, 'pause 0.6 s'), (.12, .45, .6, 'fast tapper, slow reaction'),
                                        (.18, .30, .15, 'pause shorter than reaction (BREAK case)')]:
    L = leaked(interval, reaction, pause)
    print(f"{note:42s} interval {interval}s reaction {reaction}s pause {pause}s -> leaked taps over 6 steps: {L}")
    if note == 'no pause': ok &= L >= 5   # 6 steps = 5 step changes
    if note.startswith('pause 0.6') or note.startswith('fast'): ok &= L == 0
    if 'BREAK' in note: ok &= L > 0
print("RESULT: PASS no pause leaks 1 tap per step change (5 of 5); a pause longer than reaction time leaks 0; a pause shorter than reaction still leaks" if ok else "RESULT: FAIL")
