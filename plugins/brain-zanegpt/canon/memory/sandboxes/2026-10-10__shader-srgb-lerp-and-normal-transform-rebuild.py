"""Rebuild, own fixture. Prediction (before run):
A) sRGB-space midpoint of 0.0 and 1.0, decoded to linear light = 0.5^2.4-ish ~0.2140 (vs 0.5 linear-light lerp).
B) Decode-error of the 50% blend vs true linear lerp grows monotonically with the gap d between two grays centred
   at 0.5 sRGB: <0.002 at d=0.02, >0.02 at d=0.3, max at d=1 (>0.28).
C) Normal transformed by model matrix M=diag(3,1,2) rotated 30deg about z is NOT perpendicular to the transformed tangent
   (|dot|>0.05 for a tilted tangent); inverse-transpose gives |dot|<1e-12. Under uniform scale 2 and under pure rotation
   BOTH are perpendicular (model-matrix is only wrong under non-uniform scale).
D) Built to break: lit output with a light along the surface-normal-symmetric direction hides the bug (equal intensity)
   although the normals differ, so a perpendicularity test is the right check.
Stdlib only, deterministic."""
import math

def dec(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def enc(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

ok = True
def chk(n, c, d=""):
    global ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n, d)

# A
mid = dec(0.5 * 0.0 + 0.5 * 1.0)
chk("A srgb-space 50% blend decodes to ~0.214", abs(mid - 0.2140) < 0.001, f"{mid:.4f} vs 0.5")
chk("A linear-light 50% blend re-encodes to ~0.735", abs(enc(0.5) - 0.7354) < 0.001, f"{enc(0.5):.4f}")
# B
errs = []
for d in (0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0):
    a, b = 0.5 - d / 2, 0.5 + d / 2
    wrong = dec(0.5 * a + 0.5 * b); right = 0.5 * dec(a) + 0.5 * dec(b)
    errs.append((d, right - wrong))
print("  error by gap:", ", ".join(f"{d}:{e:.4f}" for d, e in errs))
chk("B error <0.002 at d=0.02", errs[0][1] < 0.002)
chk("B error monotonic in d", all(errs[i][1] < errs[i + 1][1] for i in range(len(errs) - 1)))
chk("B error >0.02 at d=0.3", dict(errs)[0.3] > 0.02)
# gap 1.0 centred at 0.5 is black-vs-white
chk("B error at d=1 >0.28", dict(errs)[1.0] > 0.28, f"{dict(errs)[1.0]:.4f}")
# C
def matmul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]
def T(A): return [[A[j][i] for j in range(3)] for i in range(3)]
def inv(A):
    a, b, c = A[0]; d, e, f = A[1]; g, h, i = A[2]
    det = a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)
    adj = [[e*i-f*h, c*h-b*i, b*f-c*e], [f*g-d*i, a*i-c*g, c*d-a*f], [d*h-e*g, b*g-a*h, a*e-b*d]]
    return [[adj[r][s] / det for s in range(3)] for r in range(3)]
def dot(u, v): return sum(x * y for x, y in zip(u, v))
def norm(v): n = math.sqrt(dot(v, v)); return [x / n for x in v]
th = math.radians(30)
R = [[math.cos(th), -math.sin(th), 0], [math.sin(th), math.cos(th), 0], [0, 0, 1]]
def case(M):
    t = [1, 1, 0]; n = [1, -1, 0]; assert dot(t, n) == 0   # tilted tangent, its normal
    mt = mv(M, t)
    n_model = norm(mv(M, n)); n_it = norm(mv(T(inv(M)), n))
    return abs(dot(n_model, norm(mt))), abs(dot(n_it, norm(mt)))
nonuni = matmul(R, [[3, 0, 0], [0, 1, 0], [0, 0, 2]])
for name, M, expect_bad in (("non-uniform+rot", nonuni, True), ("uniform x2", [[2,0,0],[0,2,0],[0,0,2]], False), ("pure rotation", R, False)):
    m, it = case(M)
    chk(f"C {name}: model-matrix |dot|={m:.4f} inv-transpose |dot|={it:.1e}", (m > 0.05) == expect_bad and it < 1e-12)
# D
L = norm([1, 0, 0]); n = [1, -1, 0]
M = [[3, 0, 0], [0, 1, 0], [0, 0, 1]]
a = dot(norm(mv(M, n)), L); b = dot(norm(mv(T(inv(M)), n)), L)
n2 = [0, 1, 0]
sym = [abs(dot(norm(mv(M, n2)), [0, 1, 0])), abs(dot(norm(mv(T(inv(M)), n2)), [0, 1, 0]))]
chk("D axis-aligned normal + symmetric light hides the bug (identical lit value)", abs(sym[0] - sym[1]) < 1e-12, f"{sym}")
chk("D tilted normal + light differs (bug visible)", abs(a - b) > 0.05, f"{a:.3f} vs {b:.3f}")
print("RESULT: " + ("PASS" if ok else "FAIL") + f" midpoint {mid:.4f}; err d=.02 {errs[0][1]:.5f}, d=1 {errs[-1][1]:.3f}; model-matrix normal wrong only under non-uniform scale")
