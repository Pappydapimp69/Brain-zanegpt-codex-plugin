"""Gap sandbox: (a) kernel NARRATION/voiceover-restraint: a caption earns its place only if it
adds information beyond what the on-screen state already shows -> novelty gate on tokens;
(b) kernel NARRATION/drone-riser-stinger: the stinger must fire exactly on the reveal cue;
(c) memory sandbox-combined-brain-viz-growth/E8: accumulated-dt playback misses an exact
t>=cue test. Prediction (before run): novelty gate flags the 3 count-restating captions and passes
the 3 causal ones; at 30 fps the exact-compare scheduler drops the final cue (t=1.0) for at least
one dt in {1/30,1/60,0.1} while half-tick tolerance fires all cues; BREAK: a caption restating
the visible count in different words slips past the token gate (gate is lexical, so refuted there)."""
import re
SCREEN = {"count", "ideas", "memories", "arrived", "now", "new", "total", "have"}
def tokens(s): return set(re.findall(r"[a-z]+|\d+", s.lower()))
def novelty(caption, screen_numbers):
    t = tokens(caption)
    visible = SCREEN | {str(n) for n in screen_numbers}
    new = {w for w in t - visible if len(w) > 3}
    return len(new) / max(1, len(t))
def gate(caption, nums, thresh=0.5): return novelty(caption, nums) >= thresh
captions = [
    ("and now 445 ideas have arrived", [445], False),
    ("total memories now 356", [356], False),
    ("new count: 12 ideas", [12], False),
    ("a steward starts promoting entries automatically", [120], True),
    ("a cross-project sweep revealed shared failure causes", [200], True),
    ("a new domain founded from scratch after music kept recurring", [30], True),
]
ok_gate = 0
for c, n, want in captions:
    got = gate(c, n); ok_gate += (got == want); print(f"gate {got!s:5} want {want!s:5} | {c}")
# BREAK: paraphrase of visible count passes the lexical gate
para = "four hundred forty five concepts exist at this point"
brk = gate(para, [445]); print("BREAK paraphrase of count passes gate:", brk)
cues = [0.25, 0.5, 0.75, 1.0]  # last cue = reveal frame (stinger)
def run(dt, tol):
    t, fired, steps = 0.0, set(), int(round(1 / dt))
    for _ in range(steps):
        t += dt
        for i, c in enumerate(cues):
            if (t >= c - tol) if tol else (t >= c): fired.add(i)
    return len(fired)
rows = {}
for dt in (1/30, 1/60, 0.1, 1/24):
    rows[dt] = (run(dt, 0.0), run(dt, dt / 2))
    print(f"dt={dt:.5f} exact fires {rows[dt][0]}/4  half-tick fires {rows[dt][1]}/4")
missing = [dt for dt, (e, h) in rows.items() if e < 4]
c1 = ok_gate == 6
c2 = len(missing) >= 1 and all(h == 4 for e, h in rows.values())
c3 = brk is True
print("c1 gate classifies 6/6:", c1, "| c2 exact drops stinger at some dt, tolerance never:", c2, "(", len(missing), "dts )", "| c3 paraphrase slips through:", c3)
print("RESULT: %s novelty gate %d/6 on constructed captions, paraphrase of visible count slips through=%s; exact cue compare drops the final stinger for %d of 4 dts, half-tick tolerance 4/4 each"
      % ("PASS" if c1 and c2 and c3 else "FAIL", ok_gate, brk, len(missing)))
