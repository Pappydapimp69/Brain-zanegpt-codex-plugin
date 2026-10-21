"""Deterministic step-transition model. No RNG, no real timing: time is a simulated clock.
Claims tested: (kernel) step transition = short, directional, instant under reduced motion;
(sibling kernel) each step swap needs one live-region announce; (back-free-forward-blocked)
forward past unvisited steps is blocked; (sandbox-anim/E3) motion must be a function of dt."""
import math

def ease(t): return 1 - (1 - t) ** 3

class Stepper:
    def __init__(self, dur_ms=250, reduced=False, retarget=True, fps=60, nsteps=6):
        self.dur = 0 if reduced else dur_ms
        self.retarget, self.dt = retarget, 1000 / fps
        self.step = 0; self.max_seen = 0; self.n = nsteps
        self.pos = 0.0           # visual position in step units
        self.frm = 0.0; self.to = 0.0; self.t0 = None
        self.announces = []; self.trace = []; self.now = 0.0; self.go_jumps = []
    def go(self, target):
        target = max(0, min(target, self.max_seen + 1, self.n - 1))  # forward-blocked rule
        if target == self.step: return
        before = self.pos
        self.step = target; self.max_seen = max(self.max_seen, target)
        self.announces.append(target)
        self.frm = self.pos if self.retarget else float(self.to)   # naive: restart from old rest slot
        if not self.retarget: self.pos = self.frm
        self.to = float(target); self.t0 = self.now
        if self.dur == 0: self.pos = self.to
        self.go_jumps.append(abs(self.pos - before) if self.dur else 0.0)
    def tick(self):
        if self.t0 is not None and self.dur:
            k = min(1.0, (self.now - self.t0) / self.dur)   # elapsed/duration, dt-independent
            self.pos = self.frm + (self.to - self.frm) * ease(k)
            if k >= 1: self.t0 = None
        self.trace.append((self.now, self.pos))
        self.now += self.dt

def run(events, **kw):
    s = Stepper(**kw); i = 0; end = max(t for t, _ in events) + 1500
    while s.now <= end:
        while i < len(events) and events[i][0] <= s.now:
            s.go(events[i][1](s)); i += 1
        s.tick()
    return s

def max_jump(tr): return max(abs(b[1] - a[1]) for a, b in zip(tr, tr[1:]))
def settle_ms(s, target):
    for t, p in s.trace:
        if abs(p - target) < 1e-9: return t
    return None
def bad_dir_frames(tr, sign):  # frames moving against the nav direction
    return sum(1 for a, b in zip(tr, tr[1:]) if (b[1] - a[1]) * sign < -1e-9)

ok = True
def check(name, cond, info):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name + " | " + info)

# S1: single forward at 60 and 30 fps: directional, settles in ~dur regardless of fps (anim/E3 contrast below)
for fps in (60, 30):
    s = run([(0, lambda s: s.step + 1)], fps=fps)
    check(f"S1 forward fps={fps}", bad_dir_frames(s.trace, +1) == 0 and abs(settle_ms(s, 1) - 250) <= 1000/fps + 1,
          f"settle={settle_ms(s,1):.0f}ms bad_dir=0 announces={len(s.announces)}")
# per-frame fixed factor (the anti-pattern from sandbox-anim/E3): settle time depends on fps
def factor_settle(fps):
    v, t = 0.0, 0.0
    while abs(1 - v) >= 0.01: v += (1 - v) * 0.1; t += 1000 / fps
    return t
f60, f30 = factor_settle(60), factor_settle(30)
check("S1b per-frame factor is fps-dependent (anim/E3)", f30 > 1.8 * f60, f"60fps={f60:.0f}ms 30fps={f30:.0f}ms")

# S2 BREAK: fwd, fwd, back within 100ms each. naive restart vs retarget
ev = [(0, lambda s: s.step + 1), (100, lambda s: s.step + 1), (200, lambda s: s.step - 1)]
r = run(ev, retarget=True); n = run(ev, retarget=False)
check("S2 retarget: zero teleport at each input", max(r.go_jumps) == 0.0, f"go_jumps={[round(j,3) for j in r.go_jumps]}")
check("S2 naive restart teleports on reversal (cue lost)", max(n.go_jumps) > 0.05, f"go_jumps={[round(j,3) for j in n.go_jumps]}")
check("S2 one announce per swap", r.announces == [1, 2, 1], f"announces={r.announces}")

# S3: reduced motion -> zero intermediate frames, still announces
s = run([(0, lambda s: s.step + 1)], reduced=True)
mid = [p for _, p in s.trace if 0 < p < 1]
check("S3 reduced motion instant", not mid and s.announces == [1], f"intermediate_frames={len(mid)} announces={s.announces}")

# S4: forward-blocked / back-free
ev = [(0, lambda s: s.step + 1), (50, lambda s: s.step + 5), (900, lambda s: 0)]
s = run(ev)
check("S4 forward cannot skip unvisited; back is free", s.announces == [1, 2, 0], f"announces={s.announces} max_seen={s.max_seen}")

# S5 BREAK: key-repeat every 80ms for 10 presses, 250 vs 600ms duration: perceived lag (kernel's 200-300ms bound)
for dur in (250, 600):
    ev = [(80 * k, lambda s: s.step + 1) for k in range(5)]
    s = run(ev, dur_ms=dur)
    lag = settle_ms(s, 5.0) - 80 * 4 if settle_ms(s, 5.0) else None
    print(f"  S5 dur={dur}: visual lag after last press = {lag:.0f}ms")
    if dur == 250: lag250 = lag
    else: lag600 = lag
check("S5 lag after final press stays within one duration; long durations add delay", lag250 <= 250 + 34 and lag600 > 2 * lag250 - 17,
      f"lag250={lag250:.0f} lag600={lag600:.0f}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} 5 scenarios; teleport at input: retarget {max(r.go_jumps):.3f} vs naive {max(n.go_jumps):.3f}")
