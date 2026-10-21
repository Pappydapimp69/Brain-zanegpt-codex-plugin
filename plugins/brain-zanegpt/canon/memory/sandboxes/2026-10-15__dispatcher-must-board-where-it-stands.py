"""A lift dispatcher picks the next floor from requests, and (sensibly) never 'goes' to the floor it is
already at. If boarding only happens on ARRIVAL, people waiting at the lift's own floor are never picked up:
with everyone at the lobby (morning rush), the lift stays put forever. Deterministic, stdlib only."""
def run(board_here, minutes=2):
    lift, waiting, delivered, t, nxt, k = 0, [], 0, 0.0, 0.0, 0
    riders = []
    while t < minutes * 60:
        while nxt <= t: waiting.append((0, 1 + k % 6)); k += 1; nxt += 3   # everyone arrives at the lobby, one every 3 s
        here = lift
        if board_here and any(p[0] == here for p in waiting):
            riders += [p for p in waiting if p[0] == here][:8 - len(riders)]; waiting = [p for p in waiting if p not in riders]
        reqs = set(p[1] for p in riders) | set(p[0] for p in waiting)
        reqs.discard(here)                                    # never target the floor you are on
        if reqs:
            f = min(reqs, key=lambda x: abs(x - lift)); t += abs(f - lift) / 2.4 + .9; lift = f
            delivered += sum(1 for p in riders if p[1] == f); riders = [p for p in riders if p[1] != f]
            got = [p for p in waiting if p[0] == f][:8 - len(riders)]; riders += got; waiting = [p for p in waiting if p not in got]
        else: t += 1
    return delivered, len(waiting)
for flag in (False, True): print(f"board where it stands = {flag}: delivered {run(flag)[0]}, still waiting {run(flag)[1]}")
d0, w0 = run(False); d1, w1 = run(True)
print(f"RESULT: {'PASS' if d0 == 0 and w0 > 30 and d1 > 30 else 'FAIL'} without boarding at its own floor the lift delivered {d0} with {w0} stuck in the lobby; boarding there first delivered {d1}")
