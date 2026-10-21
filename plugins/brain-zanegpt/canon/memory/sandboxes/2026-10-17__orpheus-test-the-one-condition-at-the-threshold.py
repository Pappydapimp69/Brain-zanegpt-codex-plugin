"""Orpheus and Eurydice: where does one trivial condition actually get tested?

A walk of N steps out of the underworld. The condition never changes
("do not look back"), but the urge to break it does:
  pull(i)    = N / (N - i)      eagerness to see her, grows as the exit nears
  silence(i) = steps since the last cue that she is still behind (0 on a cue step)
  strain(i)  = pull(i) * silence(i)
Orpheus looks back at the first step where strain > RESOLVE.
Deterministic, stdlib only.
"""
N = 20
RESOLVE = 20.0


def walk(cues, pull_fn=None):
    """cues: set of step indices where a cue (footsteps) reassures him."""
    pull_fn = pull_fn or (lambda i: N / (N - i))
    last_cue = -1
    peak = 0.0
    for i in range(N):
        if i in cues:
            last_cue = i
        silence = i - last_cue
        strain = pull_fn(i) * silence
        peak = max(peak, strain)
        if strain > RESOLVE:
            return i, peak
    return None, peak


def layout_with_silence(start, length):
    """Cue every other step, except a silent stretch [start, start+length)."""
    return {i for i in range(0, N, 2) if not (start <= i < start + length)}


def fmt(b):
    return "none" if b is None else f"step {b} of {N}"


ok = True

# S1: Ovid-like layout: steady cues on the open path, then silence and fog near the threshold.
ovid = {i for i in range(0, 13, 2)}
b1, p1 = walk(ovid)
print(f"S1 Ovid layout (cues to step 12, silent 13-19): looks back at {fmt(b1)}, peak strain {p1:.1f}")
ok &= b1 is not None and b1 >= 15

# S2: the same 6-step silence placed early in the walk.
early = layout_with_silence(1, 6)
b2, p2 = walk(early)
print(f"S2 same silence early (steps 1-6): looks back at {fmt(b2)}, peak strain {p2:.1f}")
ok &= b2 is None

# S3: sweep the start of a 6-step silence across the walk.
print("S3 sweep: start of 6-step silence -> break step")
breaking_starts = []
for s in range(0, N - 6 + 1):
    b, p = walk(layout_with_silence(s, 6))
    print(f"   start {s:2d} (silent {s}-{s+5}): {fmt(b):14s} peak {p:6.1f}")
    if b is not None:
        breaking_starts.append(s)
first_break = min(breaking_starts) if breaking_starts else None
print(f"   silence breaks the condition only when it starts at step >= {first_break}")
ok &= first_break is not None and all(s in breaking_starts for s in range(first_break, N - 5))

# S4: one reassurance just before the threshold.
b4, p4 = walk(ovid | {16})
print(f"S4 Ovid layout + one cue at step 16: looks back at {fmt(b4)}")
ok &= b4 is not None and b4 > b1

# S5: how dense must reassurance be in the final stretch to survive?
# Find the largest gap between cues allowed at each step (strain <= RESOLVE).
gaps = [int(RESOLVE // (N / (N - i))) for i in range(N)]
print("S5 longest safe silence at each step:", gaps)

# BREAK: no goal-gradient pull (eagerness flat). The threshold claim depends on pull rising.
flat = lambda i: 1.0
bb, pb = walk(ovid, flat)
print(f"BREAK flat pull, Ovid layout: looks back at {fmt(bb)}, peak strain {pb:.1f}")
# With flat pull, a break needs a long silence wherever it sits; compare an
# 8-step silence early vs late under a lower resolve so a break is possible at all.
def walk_r(cues, pull_fn, resolve):
    last_cue = -1
    for i in range(N):
        if i in cues:
            last_cue = i
        if pull_fn(i) * (i - last_cue) > resolve:
            return i
    return None
be = walk_r(layout_with_silence(1, 8), flat, 6.0)
bl = walk_r(layout_with_silence(11, 8), flat, 6.0)
print(f"BREAK flat pull, resolve 6: 8-step silence early breaks at {fmt(be)}, late breaks at {fmt(bl)} "
      f"(the exit adds nothing; position follows the silence)")
break_holds = bb is None and be is not None and be < 10
ok &= break_holds


# S6: sweep resolve and silence length; shortest silence that breaks when it sits at the
# start of the walk versus at the end (ending on the last step).
def min_breaking_len(resolve, where, pull_fn):
    for L in range(1, N + 1):
        start = 1 if where == "early" else N - L
        cues = {i for i in range(N) if not (start <= i < start + L)}  # cue every step outside the silence
        if walk_r(cues, pull_fn, resolve) is not None:
            return L
    return None

mult = lambda i: N / (N - i)
print("S6 shortest breaking silence, multiplicative strain (resolve: early / late)")
s6_ok = True
for res in (10, 15, 20, 30, 40):
    e, l = min_breaking_len(res, "early", mult), min_breaking_len(res, "late", mult)
    print(f"   resolve {res:2d}: early {e} / late {l}")
    s6_ok &= l is not None and (e is None or l < e)
print("S7 same, additive strain = pull + silence (resolve: early / late)")
s7_ok = True
for res in (10, 15, 20, 30, 40):
    def walk_add(cues, resolve=res):
        last = -1
        for i in range(N):
            if i in cues:
                last = i
            if mult(i) + (i - last) > resolve:
                return i
        return None
    def mbl(where):
        for L in range(1, N + 1):
            start = 1 if where == "early" else N - L
            if walk_add({i for i in range(N) if not (start <= i < start + L)}) is not None:
                return L
        return None
    base = walk_add(set(range(N)))  # a cue on every step: no silence at all
    if base is not None:
        print(f"   resolve {res:2d}: breaks at step {base} even with a cue on every step (pull alone passes resolve at the exit)")
        s7_ok &= base >= N - 3
        continue
    e, l = mbl("early"), mbl("late")
    print(f"   resolve {res:2d}: early {e} / late {l}")
    s7_ok &= (l is not None and (e is None or l < e)) or (e is None and l is None)
ok &= s6_ok and s7_ok

print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"one fixed condition breaks at {fmt(b1)} when silence overlaps the exit, never when the same silence is early; "
      f"only silences starting at step >= {first_break} break it; a late cue delays it to {fmt(b4)}; "
      f"across resolve 10-40 a late silence breaks it at 1-3 steps vs 7-14 early (early is cheaper, not free); "
      f"an additive form agrees or breaks at the exit with no silence at all; "
      f"BREAK: with flat pull the exit adds nothing (an early silence breaks at {fmt(be)})")
