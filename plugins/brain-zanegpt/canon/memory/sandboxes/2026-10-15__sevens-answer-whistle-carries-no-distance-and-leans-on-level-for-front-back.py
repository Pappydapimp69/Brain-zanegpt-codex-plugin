"""Gap (brain query front-back: 0, hrtf: 0 lessons). What can a player tell
about WHERE a companion is from SEVEN's 'answer' whistle? Read from
src/audio.js and src/soundscape.js (seven-1.18.0, not modified):
  pan = sin(a), front = cos(a)  (a = bearing relative to facing)
  answer gain = 0.35 + 0.25 * front;  no distance term; no rear low-pass
  (the hallucinated 'voice' DOES get distance and a rear low-pass).
Exact arithmetic, no rng. A source at bearing a and its front/back mirror
pi - a have the same pan; they differ only in level by
20 log10((0.35 + 0.25 cos a)/(0.35 - 0.25 cos a)) dB. A listener judging one
whistle in isolation compares against a remembered level: ASSUMED criterion
4 dB (absolute level memory is poor; 1 dB is the side-by-side JND).
Head turn (Wallach 1940, head movements resolve front-back): turning 10 deg
right moves a front source's pan left and a rear source's pan right.
PREDICTION (written before running): distance information carried = 0 (gain
does not depend on distance); at a 1 dB criterion only bearings within ~5 deg
of the side are front/back ambiguous, at a 4 dB criterion ~20 deg either side
of each ear (roughly a quarter of all bearings); a 10 deg head turn resolves
front/back at every bearing except exactly 90 deg; the voice layer, which has
distance and a rear low-pass, carries both.
"""
import math, sys
print("python", sys.version.split()[0])
def gain(a): return 0.35 + 0.25 * math.cos(a)
def mirror_db(a): return abs(20 * math.log10(gain(a) / gain(math.pi - a)))
bearings = [math.radians(d) for d in range(0, 360)]
amb = {}
for crit in (1.0, 4.0):
    amb[crit] = [d for d in range(360) if mirror_db(math.radians(d)) < crit]
    print(f"criterion {crit} dB: {len(amb[crit])}/360 bearings front/back ambiguous; e.g. {amb[crit][:6]} ...")
# distance info: gain at distance 1 vs 30 cells at same bearing
dist_info = all(gain(a) == gain(a) for a in bearings)   # the code has no distance term at all
print("answer gain depends on distance: False (no distance term in audio.js) -> distance information 0 bits")
def turn_resolves(a, turn=math.radians(10)):
    front_pan_change = math.sin(a - turn) - math.sin(a)
    rear = math.pi - a
    rear_pan_change = math.sin(rear - turn) - math.sin(rear)
    return (front_pan_change > 0) != (rear_pan_change > 0) and abs(front_pan_change - rear_pan_change) > 1e-9
unres = [d for d in range(360) if not turn_resolves(math.radians(d))]
print(f"10 deg head turn leaves unresolved bearings: {unres}")
c = [True, len(amb[1.0]) <= 24, 60 <= len(amb[4.0]) <= 110, all(d in (85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275) for d in unres)]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; answer whistle carries 0 bits of distance; front/back ambiguous at {len(amb[1.0])}/360 bearings (1 dB) and {len(amb[4.0])}/360 (4 dB); 10 deg turn unresolved at {unres}")
