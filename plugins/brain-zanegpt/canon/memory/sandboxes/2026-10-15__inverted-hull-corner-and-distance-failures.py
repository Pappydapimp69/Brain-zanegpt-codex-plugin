"""Cel loop 5 - inverted-hull outlines (GGXrd: 'a second set of darker polygons ... expanded
in the normals direction to create the hull'; Delt06 URP toon shader wiki: thickness set
by a scale value, with optional clip-space scaling for perspective).
2-D cross-section model (exact geometry, no RNG):
 (a) a square (cube cross-section, 90-degree corners) hulled by offset w along
     - split normals (hard edges: each face moves along its own normal)
     - averaged normals (corner vertices move along the normalised average)
     - averaged normals scaled by 1/cos(half-angle) (corrected)
   measure: the uncovered gap at a corner, and the line width perpendicular to the face;
 (b) on-screen width of a hull offset w = 0.02 world units at depth z = 2..20 with a
     pinhole camera f = 1000 px, in world space vs clip-space scaled (offset * z / z0).
PREDICTION (written before running): split normals leave a corner gap of length w*sqrt(2)
per corner (the hull faces separate); averaged normals give a face line width of
w*cos45 = 0.707w; the 1/cos correction restores width w; world-space width falls 10x from
z 2 to 20 while clip-space stays within 1%; (added before the second run) at a 30-degree
corner the corrected vertex juts out more than 3.5w."""
import math
w = 1.0
sq = [(-5, -5), (5, -5), (5, 5), (-5, 5)]                 # square, counter-clockwise
def face_normals(poly):
    out = []
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
        out.append((dy / L, -dx / L))                         # outward for CCW
    return out
fn = face_normals(sq)
# split normals: each face edge translated by w*n; at the corner between face i-1 and face i the two
# translated edges end at P + w*n_{i-1} and P + w*n_i: the gap is the distance between those ends
gaps = [math.dist((sq[i][0] + w * fn[i - 1][0], sq[i][1] + w * fn[i - 1][1]),
                  (sq[i][0] + w * fn[i][0], sq[i][1] + w * fn[i][1])) for i in range(4)]
# averaged normals: vertex moves along normalised (n_{i-1} + n_i); the face line's distance from the
# original face = projection of that move onto the face normal
def avg_width(scale_fix):
    widths = []
    for i in range(4):
        a, b = fn[i - 1], fn[i]; m = (a[0] + b[0], a[1] + b[1]); L = math.hypot(*m); m = (m[0] / L, m[1] / L)
        k = w / (m[0] * b[0] + m[1] * b[1]) if scale_fix else w
        widths.append(k * (m[0] * b[0] + m[1] * b[1]))
    return widths
avg, fixed = avg_width(False), avg_width(True)
print(f"split normals: corner gap {gaps[0]:.3f} (w*sqrt2 = {w*math.sqrt(2):.3f}) at each of 4 corners")
print(f"averaged normals: face line width {avg[0]:.3f} w; with 1/cos correction {fixed[0]:.3f} w")
# break case: sweep the corner's interior angle. Averaged-normal width = w*cos(theta/2) where
# theta is the turn between face normals; the 1/cos fix moves the corner vertex w/cos(theta/2)
sweep = {}
for interior in (150, 90, 60, 30):
    turn = math.radians(180 - interior)
    sweep[interior] = (w * math.cos(turn / 2), w / math.cos(turn / 2))
print("corner sweep (interior angle: averaged width, corrected vertex spike):",
      {k: (round(a, 3), round(b, 2)) for k, (a, b) in sweep.items()})
f, wo, z0 = 1000.0, 0.02, 5.0
world = {z: f * wo / z for z in (2, 5, 10, 20)}
clip = {z: f * (wo * z / z0) / z for z in (2, 5, 10, 20)}
print("screen width px  world-space:", {z: round(v, 2) for z, v in world.items()}, " clip-scaled:", {z: round(v, 2) for z, v in clip.items()})
ok = (all(abs(g - w * math.sqrt(2)) < 1e-9 for g in gaps) and abs(avg[0] - math.cos(math.pi / 4)) < 1e-9
      and abs(fixed[0] - 1) < 1e-9 and abs(world[2] / world[20] - 10) < 1e-9 and max(clip.values()) / min(clip.values()) - 1 < 0.01)
ok = ok and sweep[30][1] > 3.5
print(f"RESULT: {'PASS' if ok else 'FAIL'} split normals gap {gaps[0]:.3f}w per corner; averaged normals width {avg[0]:.3f}w, corrected {fixed[0]:.3f}w; "
      f"world-space width {world[2]:.1f}px at z2 vs {world[20]:.1f}px at z20, clip-scaled {clip[2]:.1f}px constant; 30-degree corner: averaged width {sweep[30][0]:.2f}w, corrected spike {sweep[30][1]:.2f}w")
