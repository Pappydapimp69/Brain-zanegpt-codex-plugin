# Tilt-shift: true defocus blur = K*|1/zf - 1/z| (Held et al. 2010). Is a vertical linear gradient exact for a ground plane,
# and what does it do to upright sprites (a standing titan/hero)?
import math
F, H, PITCH = 800.0, 10.0, math.radians(35)       # camera height H, looking down by PITCH
K, ZF = 40.0, None
def cam(X, Y, Zw):                                 # world: Y up, Zw forward; camera at (0,H,0) pitched down
    y, z = Y - H, Zw
    yc = y * math.cos(PITCH) + z * math.sin(PITCH); zc = -y * math.sin(PITCH) + z * math.cos(PITCH)
    return F * X / zc, -F * yc / zc, zc             # screen x, screen y (down +), depth
ZF = cam(0, 0, 30)[2]
def blur(z): return K * abs(1 / ZF - 1 / z)
# ground samples: blur vs screen y, signed (in front of focus negative)
pts = [cam(X, 0, Zw) for Zw in (8, 12, 18, 30, 50, 90, 200) for X in (-20, 0, 20)]
sb = [(sy, K * (1 / ZF - 1 / z)) for sx, sy, z in pts]
n = len(sb); mx = sum(a for a, _ in sb) / n; my = sum(b for _, b in sb) / n
slope = sum((a - mx) * (b - my) for a, b in sb) / sum((a - mx) ** 2 for a, _ in sb); icp = my - slope * mx
resid = max(abs(b - (slope * a + icp)) for a, b in sb)
print(f"1) ground plane: signed blur linear in screen y, max residual {resid:.2e} px (blur range {min(b for _,b in sb):.1f}..{max(b for _,b in sb):.1f})")
res = [resid < 1e-9]
# 2) horizontal gradient: on a level ground plane, blur is constant along screen x at fixed y -> x carries no depth
xs = [blur(z) for _, _, z in [cam(X, 0, 50) for X in (-40, 0, 40)]]
print(f"2) same ground row at X=-40/0/40: blur {xs[0]:.3f}/{xs[1]:.3f}/{xs[2]:.3f} (constant: a horizontal gradient would invent depth)")
res.append(max(xs) - min(xs) < 1e-9)
# 3) BREAK: upright titan standing at Zw=200 (height 60) - gradient by screen y vs true blur of its constant depth
foot, head = cam(0, 0, 200), cam(0, 60, 200)
true_ = blur(foot[2]); grad_head = abs(slope * head[1] + icp); grad_foot = abs(slope * foot[1] + icp)
print(f"3) titan: true blur at its depth {true_:.2f}px (foot {blur(foot[2]):.2f}, head {blur(head[2]):.2f}); y-gradient gives foot {grad_foot:.2f} head {grad_head:.2f}")
res.append(abs(grad_foot - true_) < .01 and grad_head > 2 * true_)
# 4) inverse-depth vs linear-depth blur: far layers saturate
lin = [abs(z - 30) / 30 * K / 3 for z in (60, 120, 1e6)]; inv = [K * abs(1/30 - 1/z) for z in (60, 120, 1e6)]
print(f"4) layers at 60/120/inf: inverse-depth blur {inv[0]:.2f}/{inv[1]:.2f}/{inv[2]:.2f} (caps at K/zf={K/30:.2f}); linear-in-z {lin[0]:.1f}/{lin[1]:.1f}/{lin[2]:.0f}")
res.append(inv[2] < 1.4 and lin[2] > 1000)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" ground blur linear in screen y (resid {resid:.0e}); constant along x; upright titan: y-gradient gives head {grad_head:.1f}px vs true {true_:.2f}px; far blur caps at K/zf")
