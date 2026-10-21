"""Leitner box scheduling: what should a missed card do to its box?

PREDICTION (written BEFORE the first run; could come out wrong):
  P1. Savings learner (a lapse keeps half the strength, keep=0.5): demote-one-box
      needs >= 15% fewer reviews than reset-to-box-1 over 120 days
      (ratio minus1/reset <= 0.85) and ends with no fewer than reset's
      recallable cards minus 1.
  P2. Wipe learner (a lapse erases strength back to its starting value, keep=0):
      the review saving shrinks - ratio minus1/reset >= 0.95 is NOT required,
      but minus1 must lapse MORE than reset (lapses_minus1 > lapses_reset).
  P3. Massed daily review costs > 5x the reviews of either box policy
      (spacing is what makes the box system cheap).

RUN 1 RESULT (recorded honestly): FAIL. With GAIN=1.5 every success multiplies strength
by up to 2.5x, faster than the box interval doubles, so NO card ever lapsed (0 lapses,
140 reviews in every box policy); P1 and P2 refuted as stated. Lesson: the demotion rule
is moot unless a lapse can happen at all.

PREDICTION 2 (written after run 1, BEFORE run 2): sweep GAIN in {0.3, 0.6, 0.9}
  (growth 1.3x/1.6x/1.9x per success, vs interval growth 2x).
  P4. With keep=0.5, minus1 reviews <= 0.85 x reset reviews at GAIN 0.3 and 0.6.
  P5. With keep=0 (wipe), minus1 lapses > reset lapses at GAIN 0.3 and 0.6.
  P6. At GAIN 0.9 (growth nearly matches interval doubling) the two rules differ by < 10%
      in reviews, i.e. the choice of demotion rule fades as the learner keeps pace.

RUN 2 RESULT (recorded honestly): FAIL on P3 (too strong: daily/box is only 2.03x at
GAIN 0.3), P4 (ratio 0.995 at GAIN 0.6, not <= 0.85) and P6 (at GAIN 0.9 minus1 costs
1.33x MORE reviews than reset, direction reversed). P5 held. Mixed picture: the better
demotion rule flips with how fast strength grows. Narrowed claim for run 3.

PREDICTION 3 (written after run 2, BEFORE run 3), fine sweep GAIN 0.2..1.4 step 0.1,
  keep in {0.5, 0.0}, 120 days, 20 cards:
  P7. Zero-lapse boundary: smallest GAIN with 0 lapses (reset policy) lies in [1.0, 1.5].
  P8. Sign flip: under keep=0.5 minus1/reset review ratio is < 1 at GAIN 0.2 and > 1 at
      some GAIN in [0.7, 1.1] (crossover exists, between 0.6 and 1.1).
  P10 (added in run 3, same prediction round): with GAIN=0.0 (no difficulty bonus at all,
      the no-bonus control from sandbox-desirable-difficulty/E1) strength never grows,
      so reset-policy reviews >= the GAIN 0.2 figure (1184 from run 2) and the lapse
      share of reviews stays >= 40%.
  P9. Narrowed P3: daily massed reviews >= 2x the reviews of either box policy at every
      GAIN, and exactly equal reviews for both box rules at every zero-lapse GAIN.

Model (all deterministic, no RNG, no clock): a card has hidden strength S in days.
Review at gap e is a success iff e <= S. On success S grows by factor
1 + GAIN * min(e/S, 1)   (harder retrieval = bigger gain, the desirable-difficulty
mechanism from sandbox-desirable-difficulty/E1). On a lapse S = max(S0, KEEP * S).
Boxes 0..5 have intervals 1,2,4,8,16,32 days. Success: box+1 (cap 5).
"""
INTERVALS = [1, 2, 4, 8, 16, 32]
S0S = [1.0, 1.5, 2.0, 3.0, 5.0]
N = 20
DAYS = 120
GAIN = 1.5
SMAX = 400.0


def run(policy, keep, gain=GAIN, interval_scale=1):
    S0 = [S0S[i % len(S0S)] for i in range(N)]
    S = S0[:]
    box = [0] * N
    last = [0] * N        # day of last review (all cards "studied" on day 0)
    due = [0] * N
    reviews = lapses = 0
    for day in range(DAYS + 1):
        for i in range(N):
            if policy == "daily":
                is_due = True
            else:
                is_due = day >= due[i]
            if not is_due:
                continue
            e = day - last[i]
            if e == 0:
                # first exposure on day 0 counts as study, not a recall test
                last[i] = day
                due[i] = day + INTERVALS[box[i]] * interval_scale
                continue
            reviews += 1
            if e <= S[i]:
                S[i] = min(SMAX, S[i] * (1 + gain * min(e / S[i], 1.0)))
                box[i] = min(5, box[i] + 1)
            else:
                lapses += 1
                S[i] = max(S0[i], keep * S[i])
                if policy == "reset":
                    box[i] = 0
                elif policy == "minus1":
                    box[i] = max(0, box[i] - 1)
                elif policy == "hold":
                    pass
            last[i] = day
            due[i] = day + INTERVALS[box[i]] * interval_scale
    known = sum(1 for i in range(N) if (DAYS - last[i]) <= S[i])
    return dict(reviews=reviews, lapses=lapses, known=known)


def main():
    gains = [round(0.2 + 0.1 * k, 1) for k in range(13)]
    res = {}
    print("gain keep  reset(rev/lap/known)  minus1(rev/lap/known)  daily rev  ratio")
    for keep in (0.5, 0.0):
        for g in gains:
            a = run("reset", keep, gain=g)
            b = run("minus1", keep, gain=g)
            d = run("daily", keep, gain=g)
            res[(keep, g)] = (a, b, d)
            print(f"{g:3.1f} {keep:4.1f}  {a['reviews']:4d}/{a['lapses']:3d}/{a['known']:2d}"
                  f"          {b['reviews']:4d}/{b['lapses']:3d}/{b['known']:2d}"
                  f"          {d['reviews']:5d}   {b['reviews']/a['reviews']:.3f}")
    c = run("reset", 0.5, gain=0.0)
    p10 = c["reviews"] >= res[(0.5, 0.2)][0]["reviews"] and c["lapses"] / c["reviews"] >= 0.40
    print("control gain=0.0 reset:", c, "lapse share %.3f" % (c["lapses"] / c["reviews"]))
    zero = [g for g in gains if res[(0.5, g)][0]["lapses"] == 0]
    boundary = min(zero) if zero else None
    p7 = boundary is not None and 1.0 <= boundary <= 1.5
    ratios = {g: res[(0.5, g)][1]["reviews"] / res[(0.5, g)][0]["reviews"] for g in gains}
    flip = [g for g in gains if ratios[g] > 1.0 and g < (boundary or 9)]
    p8 = ratios[0.2] < 1.0 and any(0.7 <= g <= 1.1 for g in flip)
    p9 = True
    for (keep, g), (a, b, d) in res.items():
        if d["reviews"] < 2 * max(a["reviews"], b["reviews"]):
            p9 = False
        if a["lapses"] == 0 and b["lapses"] == 0 and a["reviews"] != b["reviews"]:
            p9 = False
    # the quality cost: cards not recallable on the last day
    lost = {g: (res[(0.5, g)][0]["known"], res[(0.5, g)][1]["known"]) for g in gains}
    print("zero-lapse boundary gain:", boundary, "| ratios>1 at:", flip)
    print("known(reset,minus1) at day 120 by gain:", lost)
    print(f"P7={p7} P8={p8} P9={p9} P10={p10}")
    ok = p7 and p8 and p9 and p10
    print(f"RESULT: {'PASS' if ok else 'FAIL'} P7={p7} P8={p8} P9={p9} P10={p10}; zero-lapse boundary gain={boundary}; "
          f"minus1/reset reviews (keep0.5) g0.2={ratios[0.2]:.3f} g0.6={ratios[0.6]:.3f} g0.9={ratios[0.9]:.3f} g1.2={ratios[1.2]:.3f}")


main()
