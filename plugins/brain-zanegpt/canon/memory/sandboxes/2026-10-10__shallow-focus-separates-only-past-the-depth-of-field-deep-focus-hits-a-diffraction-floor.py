"""Thin-lens depth-of-field model for the kernel on deep vs shallow focus as a narrative choice.

PREDICTIONS (written before the first run; each is checked below as P1..P9):
 P1 formula: closed-form blur equals the image-plane (thin-lens) blur to 1e-9 mm, and a
    full-frame 50 mm f/8 hyperfocal distance is 10.47 m (+-0.02) with near limit 5.23 m (+-0.02).
 P2 elasticities of blur at 50 mm f/2.8, subject 3 m, partner 0.3 m behind, full frame:
    aperture -1.00 (+-0.01); focal length at fixed distance +2.0 (1.95..2.10);
    distance at fixed focal length -1.9 (-2.1..-1.8); sensor at fixed field of view and distance,
    blur as a share of frame width +1.0 (0.9..1.1).
 P3 at FIXED framing, 24 mm -> 200 mm changes the blur of a partner 0.3 m behind the subject by a
    factor 1.0..1.3, but changes the blur of a background 50 m behind by >= 6x.
 P4 span ranking for a near partner (0.3 m), fixed framing: aperture f/1.4..f/16 span >= 10x,
    sensor 1-inch..medium format span between 3x and 6x, focal 24..200 span <= 1.3x.
 P5 deep focus 0.6 m to 12 m on full frame 50 mm: no aperture makes the worst plane sharp under
    the 1/1500-diagonal circle; best total blur is 2.0..3.0 times the circle, best f-number 30..48.
 P6 that best f-number costs 8.4..8.8 stops of light against f/2.
 P7 deep focus from 3 m to infinity is reachable on a 22x16 mm frame with 24 mm lens (positive control).
 P8 two-shot, partner 0.5 m behind subject at 3 m framing: 35 mm f/2.8 gives separation 0.70 (+-0.06)
    circles (both sharp, shallow does not choose); 85 mm f/1.4 at the same framing gives 1.54 (+-0.12);
    85 mm at f/2.8 over 35 mm at f/2.8 is 1.05..1.20 (focal length barely matters at fixed framing).
 P9 full frame 50 mm f/2 at 3 m: partner reaches 1 circle at 0.23 m behind (+-0.02) and 3 circles at
    0.81 m behind (+-0.05); in FRONT of the subject the 1-circle distance is shorter (0.20 +-0.02).
"""
import math

LAM = 0.00055  # mm, green light


def sensor(w, h):
    return {"w": w, "h": h, "diag": math.hypot(w, h)}


SENS = {
    "1in": sensor(13.2, 8.8), "mft": sensor(17.3, 13.0), "apsc": sensor(23.6, 15.6),
    "ff": sensor(36.0, 24.0), "mf": sensor(56.0, 41.5), "academy": sensor(22.0, 16.0),
}


def coc(sn):
    return sn["diag"] / 1500.0


def blur_image_plane(f, N, s, d):
    """geometric blur disc (mm) for object at d when focused at s; thin lens, image-plane method"""
    v = f * s / (s - f)
    vd = f if math.isinf(d) else f * d / (d - f)
    return (f / N) * abs(v - vd) / vd


def blur_closed(f, N, s, d):
    if math.isinf(d):
        return f * f / (N * (s - f))
    return f * f * abs(d - s) / (N * d * (s - f))


def airy(f, N, s):
    return 2.44 * LAM * N * (1 + f / (s - f))


def total_blur(f, N, s, d):
    return math.hypot(blur_closed(f, N, s, d), airy(f, N, s))


def hyperfocal(f, N, c):
    return f * f / (N * c) + f


def dof_limits(f, N, c, s):
    H = hyperfocal(f, N, c)
    near = s * (H - f) / (H + s - 2 * f)
    far = math.inf if s >= H else s * (H - f) / (H - s)
    return near, far


def focus_distance_fixed_framing(f, sn, cover_h_m):
    m = sn["h"] / (cover_h_m * 1000.0)
    return f * (1 + 1 / m) / 1000.0  # metres


def sep(f, N, s_m, d_m, sn):
    """separation measure: blur of the partner in circles of confusion"""
    return blur_closed(f, N, s_m * 1000, d_m * 1000) / coc(sn)


def best_worst_plane(f, sn, near_m, far_m, taus=None):
    """scan N, focus at the metre-equalising distance; return (N*, worst blur / c)"""
    best = None
    for k in range(0, 160):
        N = 1.0 * 2 ** (k / 12.0 / 1.0 * 0.5 * 1.0)  # sixth-stop steps over ~13 doublings of N
        if N > 128:
            break
        n, fa = near_m * 1000, far_m * 1000
        s = 2 * n * fa / (n + fa) if not math.isinf(fa) else 2 * n
        w = max(total_blur(f, N, s, n), total_blur(f, N, s, fa))
        if best is None or w < best[1]:
            best = (N, w)
    return best[0], best[1] / coc(sn)


results = []


def check(tag, ok, text):
    results.append(ok)
    print(("ok   " if ok else "MISS ") + tag + " " + text)


def elast(fn, x0, rel=1e-4):
    return (math.log(fn(x0 * (1 + rel))) - math.log(fn(x0 * (1 - rel)))) / (math.log(1 + rel) - math.log(1 - rel))


def main():
    ff = SENS["ff"]
    # P1
    worst = 0
    for f, N, s, d in [(50, 2, 3000, 3500), (85, 1.4, 2000, 2100), (24, 8, 1500, 9000), (50, 2.8, 3000, math.inf), (35, 4, 4000, 3000)]:
        worst = max(worst, abs(blur_closed(f, N, s, d) - blur_image_plane(f, N, s, d)))
    H = hyperfocal(50, 8, 0.03) / 1000
    near, far = dof_limits(50, 8, 0.03, hyperfocal(50, 8, 0.03))
    # the limits must really sit at one circle
    b_near = blur_closed(50, 8, hyperfocal(50, 8, 0.03), near)
    check("P1", worst < 1e-9 and abs(H - 10.47) < 0.02 and abs(near / 1000 - 5.23) < 0.02 and abs(b_near - 0.03) < 1e-3,
          "closed-vs-image-plane max diff %.2e mm, H=%.3f m, near=%.3f m, blur at near limit %.4f mm" % (worst, H, near / 1000, b_near))
    # P2
    f0, N0, s0, D0 = 50.0, 2.8, 3000.0, 300.0
    eN = elast(lambda N: blur_closed(f0, N, s0, s0 + D0), N0)
    ef = elast(lambda f: blur_closed(f, N0, s0, s0 + D0), f0)
    es = elast(lambda s: blur_closed(f0, N0, s, s + D0), s0)

    def sensor_scale(k):
        m = 24.0 * k / 2000.0
        f = 3000.0 * m / (1 + m)
        return blur_closed(f, N0, 3000.0, 3300.0) / (36.0 * k)
    ek = elast(sensor_scale, 1.0)
    check("P2", abs(eN + 1) < 0.01 and 1.95 <= ef <= 2.10 and -2.1 <= es <= -1.8 and 0.9 <= ek <= 1.1,
          "elasticities N %.3f, f(fixed s) %.3f, s(fixed f) %.3f, sensor(fixed FOV, share of width) %.3f" % (eN, ef, es, ek))
    # P3 fixed framing, frame covers 2 m tall at the subject
    def fixed_framing_blur(f, N, dpart, sn=ff):
        s = focus_distance_fixed_framing(f, sn, 2.0)
        return blur_closed(f, N, s * 1000, (s + dpart) * 1000), s
    b24n, s24 = fixed_framing_blur(24, 2.8, 0.3)
    b200n, s200 = fixed_framing_blur(200, 2.8, 0.3)
    b24f, _ = fixed_framing_blur(24, 2.8, 50)
    b200f, _ = fixed_framing_blur(200, 2.8, 50)
    rn, rf = b200n / b24n, b200f / b24f
    check("P3", 1.0 <= rn <= 1.3 and rf >= 6, "24->200 mm at fixed framing (s %.2f -> %.2f m): partner 0.3 m behind x%.3f, background 50 m behind x%.2f" % (s24, s200, rn, rf))
    # P4 spans for partner 0.3 m behind, fixed framing, blur as share of frame width
    def share(f, N, sn, dpart=0.3):
        s = focus_distance_fixed_framing(f, sn, 2.0)
        return blur_closed(f, N, s * 1000, (s + dpart) * 1000) / sn["w"]
    span_N = share(50, 1.4, ff) / share(50, 16, ff)
    def share_fov(skey):
        sn = SENS[skey]
        m = sn["h"] / 2000.0
        f = 3.0 * 1000 * m / (1 + m)
        return blur_closed(f, 2.8, 3000.0, 3300.0) / sn["w"], f
    sh1, f1 = share_fov("1in")
    shm, fm = share_fov("mf")
    span_S = shm / sh1
    span_F = max(share(f, 2.8, ff) for f in (24, 35, 50, 85, 135, 200)) / min(share(f, 2.8, ff) for f in (24, 35, 50, 85, 135, 200))
    check("P4", span_N >= 10 and 3 <= span_S <= 6 and span_F <= 1.3,
          "spans: aperture f/1.4..f/16 x%.1f, sensor 1-inch(f=%.1f)..medium format(f=%.1f) x%.2f, focal 24..200 at fixed framing x%.3f" % (span_N, f1, fm, span_S, span_F))
    # P5/P6
    Nb, ratio = best_worst_plane(50, ff, 0.6, 12.0)
    stops = 2 * math.log2(Nb / 2.0)
    check("P5", 2.0 <= ratio <= 3.0 and 30 <= Nb <= 48, "FF 50 mm, 0.6 m..12 m: best f/%.1f leaves worst plane at %.2f circles" % (Nb, ratio))
    check("P6", 8.4 <= stops <= 8.8, "that f-number costs %.2f stops vs f/2" % stops)
    # threshold sweep (assumption exposure) for the Academy positive control and Kane-like case
    Na, ra = best_worst_plane(24, SENS["academy"], 3.0, 1e9)
    check("P7", ra <= 1.0, "Academy 22x16 mm, 24 mm, 3 m..infinity: best f/%.1f, worst plane %.2f circles" % (Na, ra))
    print("--- threshold sweep: reachable deep-focus pairs (near, far) with best worst-plane blur <= tau circles")
    cases = [("FF 50mm", 50, "ff"), ("FF 24mm", 24, "ff"), ("Academy 24mm", 24, "academy"), ("1in 9mm", 9, "1in"), ("MF 80mm", 80, "mf")]
    for name, f, sk in cases:
        row = []
        for near, far in [(0.6, 12), (1.0, 10), (1.5, 1e9), (3.0, 1e9)]:
            Nn, r = best_worst_plane(f, SENS[sk], near, far)
            row.append("%s-%s m: f/%.0f %.1fc" % (near, "inf" if far > 1e8 else far, Nn, r))
        print("   %-13s %s" % (name, " | ".join(row)))
    # P8
    def two_shot(f, N, dpart=0.5):
        s = focus_distance_fixed_framing(f, ff, 2.0)
        # the reference framing is the 35 mm distance, so scale coverage so every lens stands where the 35 does
        return s
    # use framing of 35 mm at 3 m: coverage such that 35 mm lens stands at ~3 m
    cover = 2.0 * focus_distance_fixed_framing(35, ff, 2.0) / 3.0
    s35 = focus_distance_fixed_framing(35, ff, cover)
    s85 = focus_distance_fixed_framing(85, ff, cover)
    a = sep(35, 2.8, s35, s35 + 0.5, ff)
    b = sep(85, 1.4, s85, s85 + 0.5, ff)
    c2 = sep(85, 2.8, s85, s85 + 0.5, ff)
    check("P8", abs(a - 0.70) <= 0.06 and abs(b - 1.54) <= 0.12 and 1.05 <= c2 / a <= 1.20,
          "two-shot, partner 0.5 m behind: 35mm f/2.8 at %.2f m -> %.2f c; 85mm f/1.4 at %.2f m -> %.2f c; 85/35 at f/2.8 x%.3f" % (s35, a, s85, b, c2 / a))
    # P9
    def dist_for(target, front=False):
        lo, hi = 0.0, 2.9 if front else 200.0
        for _ in range(200):
            mid = (lo + hi) / 2
            val = sep(50, 2.0, 3.0, 3.0 - mid if front else 3.0 + mid, ff)
            if val < target:
                lo = mid
            else:
                hi = mid
        return lo
    d1, d3, f1d = dist_for(1), dist_for(3), dist_for(1, True)
    check("P9", abs(d1 - 0.23) <= 0.02 and abs(d3 - 0.81) <= 0.05 and abs(f1d - 0.20) <= 0.02 and f1d < d1,
          "FF 50mm f/2 at 3 m: partner 1 circle at %.3f m behind, 3 circles at %.3f m behind, 1 circle in front at %.3f m" % (d1, d3, f1d))
    # informational table: who is chosen by shallow focus as the pair separates
    print("--- depth gap table: separation of the unfocused partner in circles (tau=3 needed to read as blurred)")
    for name, f, N in [("35mm f/2.8", 35, 2.8), ("85mm f/1.4", 85, 1.4), ("35mm f/8", 35, 8.0)]:
        s = focus_distance_fixed_framing(f, ff, cover)
        row = ["%.1fm:%.2f" % (g, sep(f, N, s, s + g, ff)) for g in (0.1, 0.3, 0.5, 1.0, 2.0, 5.0)]
        print("   %-10s %s" % (name, "  ".join(row)))
    # POST-HOC information lines (added after the first run; not predictions, not counted in the verdict)
    def gap_for(f, N, target):
        s = focus_distance_fixed_framing(f, ff, cover)
        lo, hi = 0.0, 500.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if sep(f, N, s, s + mid, ff) < target:
                lo = mid
            else:
                hi = mid
        return lo if sep(f, N, s, s + 499.0, ff) >= target else math.inf
    print("--- INFO (post-hoc): partner gap behind the subject needed to reach 3 circles of blur, same two-shot framing")
    for name, f, N in [("35mm f/2.8", 35, 2.8), ("85mm f/1.4", 85, 1.4), ("35mm f/8", 35, 8.0), ("85mm f/4", 85, 4.0)]:
        g = gap_for(f, N, 3.0)
        print("   %-10s %s" % (name, "never within 500 m" if math.isinf(g) else "%.2f m" % g))
    m_ff = ff["h"] / 2000.0
    f_ff = 3000.0 * m_ff / (1 + m_ff)
    a_ff = blur_closed(f_ff, 2.8, 3000.0, 3300.0) / ff["w"]
    m_1 = SENS["1in"]["h"] / 2000.0
    f_1 = 3000.0 * m_1 / (1 + m_1)
    a_1 = blur_closed(f_1, 2.8 * SENS["1in"]["w"] / ff["w"], 3000.0, 3300.0) / SENS["1in"]["w"]
    print("--- INFO (post-hoc): equivalence, same field of view and distance: FF f/2.8 share-of-width %.3e vs 1-inch at f/%.2f %.3e (ratio %.3f)" % (a_ff, 2.8 * SENS["1in"]["w"] / ff["w"], a_1, a_1 / a_ff))
    n_ok = sum(results)
    print("RESULT: %s %d/%d prediction checks held" % ("PASS" if n_ok == len(results) else "FAIL", n_ok, len(results)))


main()
