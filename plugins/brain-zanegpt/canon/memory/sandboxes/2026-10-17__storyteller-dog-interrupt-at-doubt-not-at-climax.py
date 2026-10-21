"""Sandbox: a listener character who interrupts the teller (The StoryTeller's dog).

Toy model of one told story of 12 beats. Each beat has stakes s (how much it can
land) and confusion c (doubt it raises in the audience). Two state values:
  I = immersion (0..1), D = open doubt.
Per beat:
  D += c
  if the story answers its own doubts at this beat: D -> 0 (no break)
  if the listener interrupts here: the teller answers (D -> 0) but the telling is
     broken, so immersion drops by a fraction K of its current value
  I += G * s * (1 - I) - H * D        (open doubt drags immersion down)
  felt impact of the beat = I * s
Score = sum of felt impact. Deterministic, stdlib only.

FIRST RUN (v1, no story self-answer) PREDICTED climax-timed interruptions would
score >= 10% below none; it FAILED: an open doubt that the story never answers
drags every later beat, so even a mid-climax answer scored 1.17x of none, and a
doubt raised at the climax lost the climax whichever way it was answered.
Those results are kept below as scenarios A0 and C.

PREDICTION for v2 (written after v1, before the v2 run):
  A) the story answers its doubts itself at beat 8: doubt-timed interruptions
     (beats 2, 5) score >= 10% above none; the same two interruptions at the
     climax (beats 9, 10) score below none, because nothing is left to answer.
  A0) the story never answers: climax-timed still beats none (v1 finding).
  B) single-interrupt sweep with self-answer at 8: gain > 0 only at beats 2-7,
     gain < 0 at every beat from 8 on.
  C) doubt raised at the climax (beat 9): answer-now, answer-after and none all
     land within 3% of each other, while the same doubt raised and answered at
     beat 7 (before the climax) scores >= 5% higher than any of them.
  BREAK) a clear story (no confusion): the doubt-beat interruptions score below
     none, so all the help comes from real doubt.

PREDICTION for D (added after the v2 run, before the D run): sweep the break
share K in {0.4, 0.5, 0.6} and doubt drag H in {0.32, 0.4, 0.48} with a doubt
at beat 9. Small doubt (0.3): riding it beats the beat-7 aside in all 9 cells.
Large doubt (0.9): answering mid-climax beats riding it in all 9 cells, so the
"stay quiet near the climax" half holds only for small doubts.
"""

G, H, K = 0.5, 0.4, 0.5
STAKES = [0.3, 0.4, 0.4, 0.5, 0.5, 0.6, 0.6, 0.7, 0.8, 1.0, 1.0, 0.5]
CLIMAX = [9, 10]


def run(stakes, confusion, interrupts, self_answer=None, k=None, h=None):
    k = K if k is None else k
    h = H if h is None else h
    I, D, score = 0.2, 0.0, 0.0
    for i, (s, c) in enumerate(zip(stakes, confusion)):
        D += c
        if self_answer is not None and i == self_answer:
            D = 0.0
        if i in interrupts:
            D = 0.0
            I -= k * I
        I += G * s * (1 - I) - h * D
        I = max(0.0, min(1.0, I))
        score += I * s
    return score


def conf(at, amount=0.3):
    c = [0.0] * len(STAKES)
    for a in at:
        c[a] = amount
    return c


ok = True
confusing = conf([2, 5])

# A: story answers its own doubts at beat 8
none = run(STAKES, confusing, set(), 8)
at_doubt = run(STAKES, confusing, {2, 5}, 8)
at_climax = run(STAKES, confusing, set(CLIMAX), 8)
print(f"A self-answer@8: none={none:.3f} doubt-timed={at_doubt:.3f} "
      f"({at_doubt/none:.2f}x) climax-timed={at_climax:.3f} ({at_climax/none:.2f}x)")
ok &= at_doubt >= 1.10 * none and at_climax < none

# A0: story never answers (v1 setting)
n0 = run(STAKES, confusing, set())
d0 = run(STAKES, confusing, {2, 5})
c0 = run(STAKES, confusing, set(CLIMAX))
print(f"A0 never answered: none={n0:.3f} doubt-timed={d0:.3f} ({d0/n0:.2f}x) "
      f"climax-timed={c0:.3f} ({c0/n0:.2f}x)")
ok &= c0 > n0

# B: sweep with self-answer at 8
gains = [run(STAKES, confusing, {b}, 8) - none for b in range(len(STAKES))]
print("B single-interrupt gain by beat: " + " ".join(f"{b}:{g:+.3f}" for b, g in enumerate(gains)))
pos = [b for b, g in enumerate(gains) if g > 0]
print(f"  positive at beats {pos}")
ok &= all(2 <= b <= 7 for b in pos) and len(pos) > 0 and all(g < 0 for g in gains[8:])

# C: doubt raised at the climax vs pre-empted before it
late = conf([9])
c_none = run(STAKES, late, set())
c_now = run(STAKES, late, {9})
c_after = run(STAKES, late, {11})
pre = run(STAKES, conf([7]), {7})
trio = [c_none, c_now, c_after]
print(f"C doubt@9: none={c_none:.3f} answer-now={c_now:.3f} answer-after={c_after:.3f}; "
      f"raised+answered@7={pre:.3f}")
ok &= max(trio) <= 1.03 * min(trio) and pre >= 1.05 * max(trio)

# BREAK: clear story
clear = conf([], 0.0)
b_none = run(STAKES, clear, set())
b_doubt = run(STAKES, clear, {2, 5})
print(f"BREAK clear story: none={b_none:.3f} same-interrupts={b_doubt:.3f} ({b_doubt/b_none:.2f}x)")
ok &= b_doubt < b_none

# D: sensitivity of the climax half to K, H and doubt size
small_ok = large_ok = 0
for k in (0.4, 0.5, 0.6):
    for h in (0.32, 0.4, 0.48):
        ride_s = run(STAKES, conf([9], 0.3), set(), k=k, h=h)
        pre_s = run(STAKES, conf([7], 0.3), {7}, k=k, h=h)
        ride_l = run(STAKES, conf([9], 0.9), set(), k=k, h=h)
        now_l = run(STAKES, conf([9], 0.9), {9}, k=k, h=h)
        small_ok += ride_s > pre_s
        large_ok += now_l > ride_l
print(f"D sweep 9 cells: small doubt ride>aside in {small_ok}/9; large doubt answer-now>ride in {large_ok}/9")
ok_d = small_ok == 9 and large_ok == 9

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" C refuted: pre-empting a climax doubt with an aside at beat 7 scored {pre:.2f}, below"
      f" letting it ride ({c_none:.2f}) or answering mid-climax ({c_now:.2f}); held: with the story"
      f" answering at beat 8 doubt-timed {at_doubt/none:.2f}x and climax-timed {at_climax/none:.2f}x"
      f" of no-interrupt, never answered climax-timed {c0/n0:.2f}x, clear story {b_doubt/b_none:.2f}x;"
      f" D sweep: small climax doubt ride>aside {small_ok}/9, large doubt answer-now>ride {large_ok}/9"
      f" ({'as predicted' if ok_d else 'D prediction missed'})")
