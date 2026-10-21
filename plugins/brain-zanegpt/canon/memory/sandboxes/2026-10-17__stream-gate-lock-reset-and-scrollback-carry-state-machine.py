"""Sandbox: a deterministic state machine for the UX kernel stream-output-then-gate-the-explanation-behind-a-click.
Chunks are ('out', line) literal output, ('blank',), or ('exp', text) explanation that needs a click.
Rules under test: stream lines one at a time (40 ms per line, 15 ms per blank, 0 under reduced motion); gate only
'exp' chunks; one action at a time (a lock held while streaming or while a gate is pending); the lock is reset
on slide change; the scrollback list is shared across slides (kernel carry-demo-state-and-scrollback-across-
separate-steps) and the reduced-motion path is instant (kernel scroll-effects-break-keyboard-and-vestibular-safety).
Prediction (written before first run): with 2 slides of 9 chunks each (3 explanation chunks per slide) gating
only explanations needs 6 clicks versus 18 when everything is gated; reduced motion drops stream time to 0;
without a lock reset on slide change, navigating away at a pending gate strands the next slide in 100 percent of
the 6 gate positions, and with a reset 0; the shared scrollback keeps all prior lines. Assumption: navigation
cancels pending stream timers. BREAK: navigate mid-stream with timers NOT cancelled, expecting ghost lines."""
SLIDES = [
    [("out", "$ brain query save"), ("blank",), ("out", "3 results"), ("exp", "what just happened A1"), ("out", "local: 1"),
     ("blank",), ("exp", "what just happened A2"), ("out", "ok"), ("exp", "what just happened A3")],
    [("out", "$ brain sync"), ("blank",), ("out", "pushed"), ("exp", "what just happened B1"), ("out", "held: 0"),
     ("blank",), ("exp", "what just happened B2"), ("out", "done"), ("exp", "what just happened B3")],
]
LINE_MS, BLANK_MS = 40, 15
class Demo:
    def __init__(self, reduced=False, reset_lock=True, cancel_timers=True):
        self.scroll, self.reduced, self.reset_lock, self.cancel = [], reduced, reset_lock, cancel_timers
        self.slide, self.pos, self.busy, self.clicks, self.ms, self.ghost = 0, 0, False, 0, 0, 0
    def run(self):
        if self.busy: return False                       # one action at a time
        self.busy = True; self.stream(); return True
    def stream(self):
        chunks = SLIDES[self.slide]
        while self.pos < len(chunks):
            c = chunks[self.pos]
            if c[0] == "exp":
                return                                    # gate pending; lock stays held
            self.scroll.append((self.slide, c)); self.pos += 1
            self.ms += 0 if self.reduced else (BLANK_MS if c[0] == "blank" else LINE_MS)
        self.busy = False
    def click(self):
        c = SLIDES[self.slide][self.pos]; self.scroll.append((self.slide, c)); self.pos += 1; self.clicks += 1; self.stream()
    def goto(self, s):
        if self.reset_lock: self.busy = False
        self.slide, self.pos = s, 0
# 1 clicks: gate only explanations versus gate every chunk
d = Demo(); [ (d.run(), [d.click() for _ in range(3)]) for _ in [0] ]; d.goto(1); d.run(); [d.click() for _ in range(3)]
clicks_exp = d.clicks; total_chunks = sum(len(s) for s in SLIDES)
print("clicks gating explanations only:", clicks_exp, "; clicks gating all chunks (arithmetic, not simulated):", total_chunks)
# 2 stream time with and without reduced motion
t_norm = Demo(); t_norm.run(); [t_norm.click() for _ in range(3)]
t_red = Demo(reduced=True); t_red.run(); [t_red.click() for _ in range(3)]
print("stream ms slide 0: normal", t_norm.ms, "reduced-motion", t_red.ms)
# 3 strand test: leave the slide at each of the 3 gate positions per slide (6 positions) and try to run the next slide
strand = {True: 0, False: 0}
for reset in (True, False):
    for s in (0, 1):
        for k in range(3):
            d = Demo(reset_lock=reset); d.goto(s); d.run(); [d.click() for _ in range(k)]   # leave with gate k+1 pending
            d.goto(1 - s)
            strand[reset] += (not d.run())
print("strands over 6 gate positions: with reset", strand[True], "; without reset", strand[False])
# 4 scrollback carry
d = Demo(); d.run(); [d.click() for _ in range(3)]; n0 = len(d.scroll); d.goto(1); d.run(); [d.click() for _ in range(3)]
print("scrollback after both slides:", len(d.scroll), "lines, first slide kept:", sum(1 for s, _ in d.scroll if s == 0) == n0 == 9)
# 5 BREAK: navigate mid-stream; model pending timers as a list of (slide, line) still to append
def mid_stream_ghosts(cancel):
    pending = [(0, c) for c in SLIDES[0][5:]]            # remaining chunks of slide 0 when leaving after 5 lines
    shown = [(0, c) for c in SLIDES[0][:5]]
    shown += ([] if cancel else [p for p in pending if p[1][0] != "exp"])   # uncancelled timers keep appending
    return len(shown) - 5
g_cancel, g_leak = mid_stream_ghosts(True), mid_stream_ghosts(False)
print("ghost lines after leaving mid-stream: cancelled timers", g_cancel, "; uncancelled", g_leak)
ok = (clicks_exp == 6 and total_chunks == 18 and t_red.ms == 0 and t_norm.ms > 0 and strand[True] == 0 and strand[False] == 6
      and g_cancel == 0 and g_leak > 0)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" clicks {clicks_exp} vs {total_chunks}; stream ms {t_norm.ms} vs reduced {t_red.ms}; strands with reset {strand[True]}/6 without {strand[False]}/6; uncancelled timers leak {g_leak} ghost lines")
