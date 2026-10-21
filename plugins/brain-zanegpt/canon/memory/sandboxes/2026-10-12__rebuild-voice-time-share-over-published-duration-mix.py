"""Blind rebuild of seven#E71 (voices dominate hallucination TIME). Own fixture:
instead of E71's 30-180 min voice sweep, use the full published distributions
(McCarthy-Jones 2014, PMC3885292: duration seconds 12% / minutes 31% / hours 59%;
frequency constant 48% / often 11-20 per week 26% / daily 16% / rarely 0-5 per
week 10%) and Waters 2014 (PMC4141306: visions last seconds to several minutes,
frequency rare to frequent; prevalence auditory 59%, visual 27%).
Per PERSON with both kinds, auditory share of hallucinating minutes per week,
across vision duration 0.1..5 min and vision frequency 1..50 per week."""
import itertools
DUR = [(0.12, 10 / 60), (0.31, 5.0), (0.59, 120.0)]            # minutes per voice episode
FREQ = [(0.48, None), (0.26, 15), (0.16, 7), (0.10, 3)]        # per week; None = constant
Z = sum(w for w, _ in DUR); DUR = [(w / Z, d) for w, d in DUR]
WAKE = 7 * 16 * 60                                               # waking minutes per week
def voice_min(d, f):
    return WAKE * 0.5 if f is None else min(WAKE, d * f)           # 'constant' = half of waking time
prev = 0.59 / (0.59 + 0.27)
print(f"prevalence share {prev:.3f}")
worst_corner = None; rows = []
for vd, vf in itertools.product((0.1, 1.0, 5.0), (1, 7, 50)):
    vis = vd * vf
    below = 0.0; pop_v = pop_t = 0.0; mn = 1.0
    for (wd, d), (wf, f) in itertools.product(DUR, FREQ):
        w = wd * wf; v = voice_min(d, f); share = v / (v + vis)
        mn = min(mn, share); pop_v += w * v; pop_t += w * (v + vis)
        if share < prev: below += w
    rows.append((vd, vf, pop_v / pop_t, below, mn))
    print(f"vision {vd:>4} min x {vf:>2}/wk: population time share {pop_v/pop_t:.3f}  persons below prevalence {below:.2f}  lowest person {mn:.3f}")
c_pop = all(r[2] > prev for r in rows)
c_floor = all(r[4] >= 0.75 for r in rows)
worst = min(rows, key=lambda r: r[4])
most_below = max(r[3] for r in rows)
print(f"population ordering holds in every corner: {c_pop}; every person >= 0.75 (E71's floor): {c_floor}")
print(f"RESULT: {'PASS' if (c_pop and c_floor) else 'FAIL'} pop share >= {min(r[2] for r in rows):.3f} everywhere; but lowest person {worst[4]:.3f} "
      f"(vision {worst[0]} min x {worst[1]}/wk) and up to {most_below:.2f} of voice-hearers below the prevalence share")
