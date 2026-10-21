# Prediction (before run): a 1-frame cancel window [F, F+1) with frame-perfect input at F.
# (A) gate set BEFORE read: cancel accepted (1/1). (B) gate set AFTER read: dropped (0/1),
# accepted only when input is held one frame late. (C) a NaN in the phase timer makes the
# window comparison always false: 0 accepted, no exception; NaN persists for all 20 attempts.
# (D) isFinite guard on the timer resets to a finite value: attempts after recovery succeed (>=1).
def sim(order, input_frame, nan_at=None, guard=False, frames=12, window=(4, 5)):
    timer = 0.0
    gate = False
    accepted = 0
    for f in range(frames):
        if nan_at is not None and f == nan_at:
            timer = float("nan")
        if guard and timer != timer:
            timer = float(f)            # isFinite guard: resync
        def update_gate():
            nonlocal gate
            gate = window[0] <= timer < window[1]
        def read_input():
            nonlocal accepted
            if gate and f == input_frame:
                accepted += 1
        if order == "before":
            update_gate(); read_input()
        else:
            read_input(); update_gate()
        if timer == timer:
            timer += 1.0
    return accepted

A = sim("before", 4)
B = sim("after", 4)
B2 = sim("after", 5)
C = sum(sim("before", i, nan_at=0) for i in range(12))
D = sum(sim("before", i, nan_at=0, guard=True) for i in range(12))
print(dict(A=A, B=B, B_late=B2, C_nan=C, D_guard=D))
ok = (A, B, B2, C) == (1, 0, 1, 0) and D >= 1
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"before={A} after={B} after_late={B2} nan={C} guarded={D}")
