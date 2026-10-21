"""Gap (no Brain lessons on 'post-process' or 'fillrate'): what do full-screen
hallucination effects (blur, vignette, chromatic split) cost on a phone, and
what is the cheapest lever? A memory-bandwidth model, exact, no rng.
Cost of a full-screen pass = pixels x (taps read + 1 write) x 4 bytes / B.
ASSUMED inputs (not measured): phone viewport 390x844 CSS px; effective GPU
bandwidth for a canvas pass 10 GB/s (mid phone, shared memory) and 40 GB/s
(flagship); desktop 1920x1080 at DPR 1 with 200 GB/s; a 4 ms post budget inside
a 16.7 ms frame. Effects: vignette (1 tap), chromatic split (3 taps), 9-tap
separable blur as 2 passes of 9 taps.
PREDICTION (written before running): at DPR 3 on the mid phone the three effects
exceed the 4 ms budget (> 8 ms); rendering post at DPR 1 cuts cost 9x and fits;
half-resolution blur alone recovers most of it; fusing vignette + chroma into
one pass saves less than dropping DPR; break case: the desktop at DPR 1 runs
everything under 0.5 ms, so desktop testing hides the phone cost.
"""
import sys
print("python", sys.version.split()[0])
EFFECTS = {"vignette": [1], "chroma": [3], "blur9": [9, 9]}
def cost_ms(w, h, dpr, bw_gbs, passes, scale=1.0):
    px = w * dpr * h * dpr * scale * scale
    return sum(px * (t + 1) * 4 for t in passes) / (bw_gbs * 1e9) * 1e3
def total(w, h, dpr, bw, blur_scale=1.0, fused=False):
    c = cost_ms(w, h, dpr, bw, EFFECTS["blur9"], blur_scale)
    if fused: c += cost_ms(w, h, dpr, bw, [1 + 3])
    else: c += cost_ms(w, h, dpr, bw, EFFECTS["vignette"]) + cost_ms(w, h, dpr, bw, EFFECTS["chroma"])
    return c
P = (390, 844)
rows = {}
for name, args in {
    "mid DPR3": (P[0], P[1], 3, 10), "mid DPR2": (P[0], P[1], 2, 10), "mid DPR1": (P[0], P[1], 1, 10),
    "flag DPR3": (P[0], P[1], 3, 40), "desktop DPR1": (1920, 1080, 1, 200)}.items():
    rows[name] = (total(*args), total(*args, blur_scale=0.5), total(*args, fused=True))
    print(f"{name:12s}: all {rows[name][0]:6.2f} ms | half-res blur {rows[name][1]:6.2f} | fused vig+chroma {rows[name][2]:6.2f}")
m3 = rows["mid DPR3"]
c = [m3[0] > 8, rows["mid DPR1"][0] < 4 and abs(m3[0] / rows["mid DPR1"][0] - 9) < 1e-9,
     (m3[0] - m3[1]) / m3[0] > 0.5, (m3[0] - m3[2]) < (m3[0] - rows["mid DPR1"][0]),
     rows["desktop DPR1"][0] < 0.5]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} mid phone DPR3 {m3[0]:.2f} ms (budget 4), DPR1 {rows['mid DPR1'][0]:.2f}; half-res blur {m3[1]:.2f}; fused {m3[2]:.2f}; flagship DPR3 {rows['flag DPR3'][0]:.2f}; desktop {rows['desktop DPR1'][0]:.2f} ms")
