"""Sandbox: terminal-demo state machine. Kernels exercised:
 K1 ideas:UX/stream-output-then-gate-the-explanation-behind-a-click (one command in flight, gate is the only way forward, reset the lock on route change)
 K2 ideas:UX/gate-advancement-on-participation-and-reveal-controls-one-at-a-time (Next disabled while a gate is pending, skip hatch clears it)
 K3 ideas:UX/carry-demo-state-and-scrollback-across-separate-steps (scrollback is shared across slides)
Model: 3 slides, state = (slide, lock, scrollback). lock=None or the slide index whose gate is pending.
Events: run (needs no lock), gate (clears lock, only on the lock's own slide), next (blocked while lock), jump (route change, to any other slide, never blocked), skip.
A DEAD SLIDE = current slide where run is disabled because a gate pends on another slide.
Prediction (before run): over all event sequences of length <=6, design NO_RESET (jump keeps the lock) ends on a dead slide in a nonzero share;
RESET (jump clears the lock) in exactly 0; RESET keeps scrollback length == number of runs (K3) in 100%, CLEARED_SCROLLBACK variant fails that in a nonzero share.
Break scenario: RESET with gating off on next (K2 removed) must still be 0 dead slides, i.e. the reset alone carries the guarantee.
FIRST RUN REFUTED THE BREAK PREDICTION: RESET_NOGATE (reset only on jump) gave 1587 dead endings because next carries the lock. Added RESETALL_NOGATE (reset on every slide change) and expect 0."""
import itertools
EVENTS = ["run", "gate", "next", "jump", "skip"]

def step(st, ev, design):
    slide, lock, sb, runs = st
    reset, clear_sb, gating = design[:3]
    reset_next = len(design) > 3 and design[3]
    if ev == "run":
        if lock is not None: return st
        return (slide, slide, sb + 1, runs + 1)          # run leaves a gate pending on this slide
    if ev == "gate":
        if lock == slide: return (slide, None, sb, runs)
        return st
    if ev == "skip": return (slide, None, sb, runs)
    if ev == "next":
        if gating and lock is not None: return st
        return ((slide + 1) % 3, None if reset_next else lock, 0 if clear_sb else sb, runs)
    if ev == "jump":
        ns = (slide + 2) % 3
        return (ns, None if reset else lock, 0 if clear_sb else sb, runs)

DESIGNS = {  # (reset lock on jump, clear scrollback on slide change, gate next)
 "NO_RESET":  (False, False, True),
 "RESET":     (True,  False, True),
 "RESET_NOGATE": (True, False, False),
 "RESET_CLEARSB": (True, True, True),
 "RESETALL_NOGATE": (True, False, False, True),
}
res = {}
for name, d in DESIGNS.items():
    dead = sbbad = total = 0
    for seq in itertools.chain.from_iterable(itertools.product(EVENTS, repeat=n) for n in range(1, 7)):
        st = (0, None, 0, 0)
        for ev in seq: st = step(st, ev, d)
        total += 1
        slide, lock, sb, runs = st
        dead += (lock is not None and lock != slide)
        sbbad += (sb != runs)
    res[name] = (dead, sbbad, total)
    print(name, "dead-slide endings", dead, "scrollback!=runs", sbbad, "of", total)
ok = (res["NO_RESET"][0] > 0 and res["RESET"][0] == 0 and res["RESET_NOGATE"][0] > 0 and res["RESETALL_NOGATE"][0] == 0
      and res["RESET"][1] == 0 and res["RESET_CLEARSB"][1] > 0)
print("RESULT: %s dead slides NO_RESET %d RESET %d RESET_NOGATE %d RESETALL_NOGATE %d; scrollback mismatch RESET %d vs CLEARSB %d (of %d)" % (
  "PASS" if ok else "FAIL", res["NO_RESET"][0], res["RESET"][0], res["RESET_NOGATE"][0], res["RESETALL_NOGATE"][0], res["RESET"][1], res["RESET_CLEARSB"][1], res["RESET"][2]))
