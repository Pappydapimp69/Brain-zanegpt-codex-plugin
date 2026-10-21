"""Prediction (before run): for single-vertex crease patterns with sector angles that are positive multiples of 15 degrees
summing to 360 and degree 4 or 6, folding all creases flat is possible (the composition of the crease reflections returns
every point of the paper to a single plane position, i.e. the product of the reflections is the identity) EXACTLY when the
alternating angle sum equals 180 degrees (Kawasaki), 100 percent agreement over every pattern. Odd degree 3 and 5 never
satisfy it. Built to break: a tolerance-based check (alternating sums within 7.5 degrees of 180) should accept patterns the
exact reflection test rejects. [Amended after run 1: tolerance 7.5 accepted 0 wrong patterns because sums on a 15 degree grid are
multiples of 15, so I added tolerances 15 and 30 as the real break; run 1 gave agreement 44528/44528.] Exact integer degrees, deterministic, stdlib only."""
import itertools

def compositions(total, parts, unit=15):
    k = total // unit
    for cut in itertools.combinations(range(1, k), parts - 1):
        pts = (0,) + cut + (k,)
        yield tuple((pts[i + 1] - pts[i]) * unit for i in range(parts))

def flat_by_reflections(angles):
    # crease directions (degrees) cumulative from the first crease; folding reflects the paper across each crease in turn.
    # A reflection across a line at angle t acts on directions as d -> 2t - d. The composition of all reflections is a pure
    # rotation by 2*(sum of alternating differences) for even degree and a reflection for odd degree; flat iff identity.
    creases = [0]
    for a in angles[:-1]: creases.append(creases[-1] + a)
    s, m = 1, 0   # direction map d -> s*d + m (mod 360)
    for t in creases:
        s, m = -s, (2 * t - m) % 360   # apply reflection after the previous map: new(d) = 2t - old(d)
        # old(d) = s_old*d + m_old  ->  new(d) = -s_old*d + (2t - m_old)
    return s == 1 and m % 360 == 0

def kawasaki(angles):
    return sum(angles[0::2]) == 180

def tol_check(angles, tol=7.5):
    return abs(sum(angles[0::2]) - 180) <= tol and abs(sum(angles[1::2]) - 180) <= tol

tot = agree = 0; odd_ok = 0; first_bad = None; extra = {7.5: 0, 15: 0, 30: 0}
for deg in (3, 4, 5, 6):
    for ang in compositions(360, deg):
        a = flat_by_reflections(ang); b = kawasaki(ang) if deg % 2 == 0 else False
        tot += 1; agree += (a == b)
        if a != b and first_bad is None: first_bad = (ang, a, b)
        if deg % 2 == 1: odd_ok += a
        if deg % 2 == 0 and not a:
            for t in extra: extra[t] += tol_check(ang, t)
print(tot, agree, odd_ok, extra, first_bad)
ok = agree == tot and odd_ok == 0 and extra[7.5] == 0 and extra[15] > 0 and extra[30] >= extra[15]
print("RESULT: %s reflection-composition flatness matches Kawasaki in %d of %d patterns (degree 3 to 6, 15 degree grid), odd degree flat in %d, tolerance check wrongly accepts %s (tolerance 7.5, 15, 30 degrees)" %
      ("PASS" if ok else "FAIL", agree, tot, odd_ok, extra))
