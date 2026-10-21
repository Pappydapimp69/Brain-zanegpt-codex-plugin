import math
G = 9.81
def drain(h0, A, a, cd=1.0, dt=0.001, stop=None):
    """Euler integrate dh/dt = -cd*(a/A)*sqrt(2 g h); return time to reach each level in stop."""
    h, t, out = h0, 0.0, {}
    pending = sorted(stop, reverse=True)
    while h > 1e-6 and pending:
        h -= cd * (a / A) * math.sqrt(2 * G * h) * dt
        t += dt
        while pending and h <= pending[0]:
            out[pending.pop(0)] = t
    return out
def closed(h0, A, a, cd=1.0):
    return (A / (cd * a)) * math.sqrt(2 * h0 / G)
A, a = 1.0, 0.01
h0 = 1.0
r = drain(h0, A, a, stop=[0.5, 0.25, 0.0001])
T = closed(h0, A, a)
# time to half VOLUME (level h0/2) vs total
frac_half = r[0.5] / T
# scenario 2: double head -> time ratio
T2 = drain(2.0, A, a, stop=[0.0001])[0.0001]
ratio = T2 / r[0.0001]
# scenario 3 (BREAK constant-flow assumption): time at constant initial flow for half = 0.5 T_c where T_c = V/Q0
Tc = (A * h0) / (a * math.sqrt(2 * G * h0))
const_half = 0.5 * Tc
# scenario 4: discharge coefficient scales total time but not the fraction
rc = drain(h0, A, a, cd=0.6, stop=[0.5, 0.0001])
frac_cd = rc[0.5] / rc[0.0001]
print("T closed %.2f sim total %.2f; half-volume time %.2f = %.4f of total; const-flow estimate %.2f; head x2 time ratio %.4f; cd .6 frac %.4f, total %.2f vs %.2f"
      % (T, r[0.0001], r[0.5], frac_half, const_half, ratio, frac_cd, rc[0.0001], closed(h0, A, a, 0.6)))
ok = (abs(frac_half - (1 - 1 / math.sqrt(2))) < 0.005 and abs(ratio - math.sqrt(2)) < 0.01
      and abs(frac_cd - frac_half) < 0.005 and abs(r[0.0001] - T) / T < 0.02 and 0.10 < abs(const_half - r[0.5]) / r[0.5] < 0.20)
print("RESULT: %s half the volume leaves in %.3f of the drain time (theory 0.293), doubling the head costs x%.3f time (theory 1.414), discharge coefficient leaves the fraction at %.3f, constant-flow estimate is off by %.0f%%"
      % ("PASS" if ok else "FAIL", frac_half, ratio, frac_cd, 100 * abs(const_half - r[0.5]) / r[0.5]))
