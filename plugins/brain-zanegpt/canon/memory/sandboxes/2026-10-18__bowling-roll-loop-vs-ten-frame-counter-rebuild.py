"""Rebuild: roll-loop scorer (fill balls become frames 11, 12) vs ten-frame scorer. Own fixture: games built
from frame lists, known totals computed by hand-derived constants, not by either scorer."""
def frame_scorer(r, max_frames=10):
    s, i = 0, 0
    for f in range(max_frames):
        if i >= len(r): break
        if r[i] == 10: s += 10 + r[i+1] + r[i+2]; i += 1
        elif r[i] + r[i+1] == 10: s += 10 + r[i+2]; i += 2
        else: s += r[i] + r[i+1]; i += 2
    return s

def roll_loop(r):                 # treats every roll group as a frame: no ten-frame stop
    return frame_scorer(r, max_frames=99) if False else _loop(r)
def _loop(r):
    s, i = 0, 0
    while i < len(r):
        a = r[i]
        b1 = r[i+1] if i + 1 < len(r) else 0
        b2 = r[i+2] if i + 2 < len(r) else 0
        if a == 10: s += 10 + b1 + b2; i += 1
        elif a + b1 == 10: s += 10 + b2; i += 2
        else: s += a + b1; i += 2
    return s

# (rolls, hand-known total, has tenth-frame mark)
games = [
    ([10]*12, 300, True),
    ([5]*21, 150, True),
    ([0]*20, 0, False),
    ([9, 0]*10, 90, False),
    ([3, 4]*9 + [2, 5], 7*10, False),                         # 70, open tenth
    ([0, 0]*9 + [10, 7, 2], 19, True),                       # tenth strike + fill 7,2
    ([0, 0]*9 + [4, 6, 8], 18, True),                        # tenth spare + fill 8
    ([10, 10, 10] + [0, 0]*7 + [0, 0], 60 + 30 + 20 + 10 + 0 + 0 + 0 + 0 + 0 + 0 - 0, False),
]
games[-1] = ([10, 10, 10] + [0, 0]*7, 60, False)
wrong_naive = wrong_frame = mark_wrong = mark_total = 0
for r, known, mark in games:
    f, n = frame_scorer(r), _loop(r)
    print(len(r), known, "frame", f, "roll-loop", n, "mark" if mark else "")
    wrong_frame += f != known; wrong_naive += n != known
    if mark: mark_total += 1; mark_wrong += n != known
# hand check of the open-frame game 10,10,10 then zeros: 30+20+10+0.. = 60 -> frames 1-3 bonuses
ok = wrong_frame == 0 and mark_wrong == mark_total and wrong_naive == mark_wrong and _loop([10]*12) == 330
print(f"RESULT: {'PASS' if ok else 'FAIL'} ten-frame scorer wrong {wrong_frame}/{len(games)}; roll-loop wrong {wrong_naive}/{len(games)} (all {mark_wrong}/{mark_total} tenth-frame-mark games, 0 others); perfect game roll-loop {_loop([10]*12)}")
