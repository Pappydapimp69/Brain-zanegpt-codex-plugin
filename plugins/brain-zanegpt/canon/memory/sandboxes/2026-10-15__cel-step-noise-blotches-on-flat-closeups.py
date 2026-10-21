"""Cel loop 1 - a step threshold turns tiny normal noise into large shading changes, and
how large depends on how slowly N.L varies across the surface. Source: Motomura, GGXrd
GDC 2015 slides: cel shading is a step on N.L; 'every little noise on the surface will
become extremely distracting. The slightest difference in the surface normal may end
up as a huge blotch'; fix: hand-edited normals.
Model: 128x128 view of a sphere of radius R px (R = 56 whole head; R = 400 a close-up of
a gently curved cheek). Normal = analytic + deterministic noise (sum of sines, amplitude
eps). Light from the upper left. Metrics: pixels whose lit/shaded state flips vs the
clean (proxy) normals, as a share of the view; detached shadow islands (8-connected,
not touching the main shadow, wholly inside the disc); max Lambert brightness change.
Iterations 1-3 counted islands only and found none on the whole head (the terminator
just wiggles), so this run measures flipped area and adds the flat close-up case.
PREDICTION (written before this run): with eps giving under 3% Lambert change, flipped
area on the close-up (R 400) is at least 5x the whole-head (R 56) share, and the close-up
shows detached islands while proxy normals show none."""
import math
N = 128
L = (-0.5, -0.5, 0.707); ln = math.sqrt(sum(c * c for c in L)); L = tuple(c / ln for c in L)
def normal(x, y, eps, R, cx, cy):
    dx, dy = (x - cx) / R, (y - cy) / R
    r2 = dx * dx + dy * dy
    if r2 >= 0.98: return None
    n = [dx, dy, math.sqrt(1 - r2)]
    n[0] += eps * (math.sin(0.9 * x) * math.cos(0.7 * y) + 0.5 * math.sin(2.3 * x + 1.1 * y))
    n[1] += eps * (math.cos(1.3 * y) * math.sin(0.5 * x) + 0.5 * math.cos(1.7 * x - 2.9 * y))
    k = math.sqrt(sum(c * c for c in n)); return [c / k for c in n]
ndl = lambda n: sum(a * b for a, b in zip(n, L))
def run(eps, R):
    # centre the view on the terminator so both cases look at the light/shadow boundary
    t = 0.0                                              # threshold
    # the terminator point along the light's screen direction: N.L = 0 at offset s*R
    cx = cy = N / 2 - 0.5 * R * 0.0
    if R > 100:                                          # close-up: shift the sphere so the terminator crosses the view centre
        s = math.atan2(0.707, 0.707) ; off = R * 0.70
        cx = cy = N / 2 - off * 0.707
    flips = tot = 0; maxdl = 0.0; sh = [[False] * N for _ in range(N)]; ok = [[False] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            n0 = normal(x, y, 0.0, R, cx, cy)
            if n0 is None: continue
            n = normal(x, y, eps, R, cx, cy); tot += 1; ok[y][x] = True
            d, d0 = ndl(n), ndl(n0)
            flips += (d < t) != (d0 < t); maxdl = max(maxdl, abs(max(d, 0) - max(d0, 0)))
            sh[y][x] = d < t
    seen = [[False] * N for _ in range(N)]; comps = []
    for y in range(N):
        for x in range(N):
            if sh[y][x] and not seen[y][x]:
                st = [(y, x)]; seen[y][x] = True; size = 0; edge = False
                while st:
                    a, b = st.pop(); size += 1
                    for c, d in ((a+1,b),(a-1,b),(a,b+1),(a,b-1),(a+1,b+1),(a+1,b-1),(a-1,b+1),(a-1,b-1)):
                        if not (0 <= c < N and 0 <= d < N) or not ok[c][d]: edge = True; continue
                        if sh[c][d] and not seen[c][d]: seen[c][d] = True; st.append((c, d))
                comps.append((size, edge))
    comps.sort(reverse=True)
    islands = sum(1 for s_, e_ in comps[1:] if not e_)
    return flips / tot, islands, maxdl
res = {}
for R in (56, 400):
    for eps in (0.0, 0.01, 0.02):
        res[(R, eps)] = run(eps, R)
        f, k, dl = res[(R, eps)]
        print(f"R {R:3d} eps {eps:.2f}: flipped {f:6.2%} of view, detached islands {k:3d}, max Lambert change {dl:.3f}")
e = 0.01
ratio = res[(400, e)][0] / max(res[(56, e)][0], 1e-9)
ok = res[(400, e)][2] < 0.03 and ratio >= 5 and res[(400, e)][1] > 0 and res[(400, 0.0)][1] == 0 and res[(56, 0.0)][1] == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} eps {e} (Lambert change {res[(400, e)][2]:.3f}): close-up flipped {res[(400, e)][0]:.2%} "
      f"vs whole head {res[(56, e)][0]:.2%} ({ratio:.1f}x); close-up islands {res[(400, e)][1]}, proxy normals 0/0")
