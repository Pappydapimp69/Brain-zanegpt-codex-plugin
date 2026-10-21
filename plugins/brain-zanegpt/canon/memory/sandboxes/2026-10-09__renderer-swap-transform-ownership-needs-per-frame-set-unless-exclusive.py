"""Sandbox: kernel FILM/structure/change-the-camera-language... a-renderer-swap-is-a-cut.

Mock 2D canvas (matrix + save/restore stack, no rendering) and two renderers
(A = side-on, B = first-person descent). Deterministic: no RNG, no timing.
Frames are integers; a 'device position' is computed from the live matrix.

PREDICTION (written before first run):
 P1 explicit transform at every frame  -> 0 misplaced draws in A->B->A.
 P2 B inherits A's transform           -> 100% of B's world draws misplaced.
 P3 'only the first drawer sets it' (init-once) -> nonzero errors on the
    swap-BACK (A inherits B), i.e. the kernel's guard rail is insufficient
    for a round trip; set-on-takeover fixes it ONLY while renderers are
    exclusive and no helper leaks a transform (leaky fade) -> breaks.
 P4 hide outgoing chrome + incoming own chrome -> 0 mixed-idiom frames;
    leaving outgoing chrome visible -> mixed frames == B span (40);
    incoming borrowing host HUD -> mixed frames == B span.
 P5 dual-renderer crossfade (both draw in one frame) with set-on-takeover
    -> errors > 0; per-frame set -> 0 (exclusivity is what makes the cheap
    rule safe).
"""
W, H = 800, 450
IDENT = (1, 0, 0, 1, 0, 0)


class Ctx:
    def __init__(self):
        self.m = IDENT
        self.stack = []
        self.log = []          # (frame, renderer, idiom, kind, dx, dy, ex, ey)
        self.frame = 0

    def setTransform(self, *m): self.m = tuple(m)
    def save(self): self.stack.append(self.m)
    def restore(self): self.m = self.stack.pop() if self.stack else IDENT
    def scale(self, sx, sy):
        a, b, c, d, e, f = self.m
        self.m = (a * sx, b * sx, c * sy, d * sy, e, f)
    def translate(self, tx, ty):
        a, b, c, d, e, f = self.m
        self.m = (a, b, c, d, a * tx + c * ty + e, b * tx + d * ty + f)
    def point(self, x, y):
        a, b, c, d, e, f = self.m
        return (a * x + c * y + e, b * x + d * y + f)
    def draw(self, who, idiom, kind, x, y, expected):
        dx, dy = self.point(x, y)
        self.log.append((self.frame, who, idiom, kind, dx, dy, expected))


# Each renderer's intended base transform: world->device
CAM = {"A": (2, 0, 0, 2, 100, 20),      # side-on cross-section camera
       "B": (1, 0, 0, 1, W / 2, H / 2)}  # first-person: origin at centre
WORLD = [(10, 10), (40, 25), (-30, 5), (0, 60)]


def expected(who, x, y):
    a, b, c, d, e, f = CAM[who]
    return (a * x + c * y + e, b * x + d * y + f)


def world_draw(ctx, who):
    idiom = "side" if who == "A" else "fp"
    for (x, y) in WORLD:
        ctx.draw(who, idiom, "world", x, y, expected(who, x, y))


def chrome_draw(ctx, who):
    idiom = "side" if who == "A" else "fp"
    ctx.draw(who, idiom, "chrome", 0, 0, (0, 0))


class Renderer:
    """policy: 'frame' set every frame; 'save' set inside save/restore;
    'takeover' set once when it gains the canvas; 'init' set once ever;
    'inherit' never sets."""
    def __init__(self, who, policy, leaks_fade=False, own_chrome=True):
        self.who, self.policy = who, policy
        self.leaks_fade, self.own_chrome = leaks_fade, own_chrome
        self.inited = False
        self.took = False

    def take(self):
        self.took = False

    def frame(self, ctx, fade=False):
        p = self.policy
        if p == "frame":
            ctx.setTransform(*CAM[self.who])
        elif p == "save":
            ctx.save(); ctx.setTransform(*CAM[self.who])
        elif p == "takeover" and not self.took:
            ctx.setTransform(*CAM[self.who]); self.took = True
        elif p == "init" and not self.inited:
            ctx.setTransform(*CAM[self.who]); self.inited = True
        if fade:  # incoming renderer draws its own fade overlay in screen space
            if self.leaks_fade:
                ctx.setTransform(*IDENT)          # helper resets, never restores
            else:
                ctx.save(); ctx.setTransform(*IDENT); ctx.restore()
        if p == "late":   # set immediately before the world draws, after any helper
            ctx.setTransform(*CAM[self.who])
        world_draw(ctx, self.who)
        if self.own_chrome:
            chrome_draw(ctx, self.who)
        if p == "save":
            ctx.restore()


def errors(ctx, who=None):
    n = bad = 0
    for (f, w, idm, kind, dx, dy, ex) in ctx.log:
        if kind != "world" or (who and w != who):
            continue
        n += 1
        if abs(dx - ex[0]) > 1e-9 or abs(dy - ex[1]) > 1e-9:
            bad += 1
    return bad, n


SCHEDULE = [("A", 30, False), ("B", 40, True), ("A", 30, True)]  # A -> B -> A; fade first 10 of a swap


def run_exclusive(pa, pb, leaks_fade=False):
    ctx = Ctx()
    ra, rb = Renderer("A", pa, leaks_fade), Renderer("B", pb, leaks_fade)
    rs = {"A": ra, "B": rb}
    prev = None
    for who, nframes, swapped in SCHEDULE:
        if who != prev:
            rs[who].take()
        for i in range(nframes):
            ctx.frame += 1
            rs[who].frame(ctx, fade=(swapped and i < 10 and prev is not None and who != prev))
        prev = who
    return ctx


def run_dual(policy):
    """Crossfade: for 10 frames BOTH renderers draw in the same frame."""
    ctx = Ctx()
    ra, rb = Renderer("A", policy), Renderer("B", policy)
    for i in range(30):
        ctx.frame += 1; ra.frame(ctx)
    ra.take(); rb.take()
    for i in range(10):
        ctx.frame += 1; ra.frame(ctx); rb.frame(ctx)
    for i in range(30):
        ctx.frame += 1; rb.frame(ctx)
    return ctx


def mixed_frames(ctx):
    byf = {}
    for (f, w, idm, kind, *_r) in ctx.log:
        byf.setdefault(f, set()).add(idm)
    return sum(1 for s in byf.values() if len(s) > 1)


def run_chrome(hide_outgoing=True, host_hud=False):
    """Host draws a side-on HUD (A idiom) every frame unless hidden for B span."""
    ctx = Ctx()
    ra = Renderer("A", "frame"); rb = Renderer("B", "frame", own_chrome=not host_hud)
    for who, n, _ in SCHEDULE:
        for i in range(n):
            ctx.frame += 1
            (ra if who == "A" else rb).frame(ctx)
            if who == "B":
                if not hide_outgoing:
                    ctx.draw("host", "side", "chrome", 0, 0, (0, 0))   # outgoing chrome left on
                if host_hud:
                    ctx.draw("host", "side", "chrome", 0, 0, (0, 0))   # incoming borrows host HUD
    return ctx


results = {}
checks = []

def rec(name, val, cond):
    results[name] = val
    checks.append((name, val, cond))
    print(f"{name:52s} {val}  {'ok' if cond else 'UNEXPECTED'}")

# S1 explicit per-frame (and save/restore) both ways
for pol in ("frame", "save"):
    c = run_exclusive(pol, pol)
    rec(f"S1 {pol}-set errors (A->B->A)", errors(c), errors(c)[0] == 0)
# S2 B inherits, A explicit
c = run_exclusive("frame", "inherit")
bad, n = errors(c, "B")
rec("S2 B inherits: B errors", (bad, n), bad == n and n > 0)
# S3 init-once (kernel guard rail read literally) on both
c = run_exclusive("init", "init")
ea, eb = errors(c, "A"), errors(c, "B")
rec("S3 init-once: A errors / B errors", (ea, eb), ea[0] > 0)
# S3b takeover-set, clean helpers
c = run_exclusive("takeover", "takeover")
rec("S3b takeover-set, clean fade", errors(c), errors(c)[0] == 0)
# S3c takeover-set with leaky fade helper (BREAK)
c = run_exclusive("takeover", "takeover", leaks_fade=True)
rec("S3c takeover-set, leaky fade [BREAK]", errors(c), errors(c)[0] > 0)
# S3d per-frame with leaky fade
c = run_exclusive("frame", "frame", leaks_fade=True)
rec("S3d per-frame, leaky fade", errors(c), errors(c)[0] == 0)
# S3e POST-HOC (iteration 2, not in the written prediction): set AFTER the leaky helper
c = run_exclusive("late", "late", leaks_fade=True)
print("S3e [post-hoc] set-late with leaky fade:", errors(c), "(0 errors => ORDER matters, not just frequency)")
assert errors(c)[0] == 0
# S5 dual-renderer crossfade
c = run_dual("takeover"); rec("S5 dual crossfade takeover-set [BREAK]", errors(c), errors(c)[0] > 0)
c = run_dual("frame");    rec("S5b dual crossfade per-frame", errors(c), errors(c)[0] == 0)
# S4 chrome
c = run_chrome(True, False);  rec("S4 hidden outgoing + own chrome: mixed frames", mixed_frames(c), mixed_frames(c) == 0)
c = run_chrome(False, False); rec("S4b outgoing chrome left on [NEG CONTROL]: mixed", mixed_frames(c), mixed_frames(c) == 40)
c = run_chrome(True, True);   rec("S4c incoming borrows host HUD [NEG CONTROL]: mixed", mixed_frames(c), mixed_frames(c) == 40)
# exclusivity of baseline
c = run_exclusive("frame", "frame")
fr = {}
for (f, w, *_r) in c.log: fr.setdefault(f, set()).add(w)
rec("S1 frames with >1 renderer drawing", sum(1 for s in fr.values() if len(s) > 1), all(len(s) == 1 for s in fr.values()))

# S3d is the one prediction that came out wrong: per-frame set was assumed sufficient;
# it is not when a helper resets the transform AFTER the set (order, not frequency).
ok = all(cond for _, _, cond in checks)
print(f"RESULT: {'PASS' if ok else 'FAIL'} predictions {sum(1 for *_x, c in checks if c)}/{len(checks)} matched")
