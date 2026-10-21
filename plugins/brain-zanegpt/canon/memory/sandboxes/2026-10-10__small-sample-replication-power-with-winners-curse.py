# Deterministic: replication power of a z=2.23 (n=20) result at follow-up n=10, one-tailed .05.
import math
def Phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
ZC=1.6449  # one-tailed .05
def power(delta_per_root_n, n): return 1-Phi(ZC-delta_per_root_n*math.sqrt(n))
z_obs, n0, n1 = 2.23, 20, 10
d_hat = z_obs/math.sqrt(n0)           # observed standardized effect
# S1: take observed effect as truth (Tversky-Kahneman's reasonable answer)
p1 = power(d_hat, n1)
# S2: replication effect = half the original (OSC 2015 average decline)
p2 = power(d_hat/2, n1)
# S3: winner's curse, deterministic grid posterior: prior N(0, tau) on true effect, condition on z_obs
def posterior_power(tau, n1=10):
    grid=[i*0.001 for i in range(-1500,1501)]
    sd0=1/math.sqrt(n0)
    num=den=0.0
    for d in grid:
        lik=math.exp(-0.5*((d_hat-d)/sd0)**2)
        pri=math.exp(-0.5*(d/tau)**2)
        w=lik*pri
        den+=w; num+=w*power(d,n1)
    return num/den
p3 = posterior_power(0.3)   # skeptical prior: most true effects small
p3b = posterior_power(5.0)  # nearly flat prior -> should approach S1
# S4 (break): same n replication, and tiny/huge n1 limits
p4 = power(d_hat, 20); p5 = power(d_hat, 80)
print(f"S1 point-estimate n=10 power={p1:.3f}")
print(f"S2 half-effect n=10 power={p2:.3f}")
print(f"S3 skeptical-prior posterior power={p3:.3f}; flat-prior={p3b:.3f}")
print(f"S4 same-n={p4:.3f} n=80={p5:.3f}")
ok = abs(p1-0.48)<0.03 and p2<0.30 and p3<p1-0.1 and abs(p3b-p1)<0.06
print(f"RESULT: {'PASS' if ok else 'FAIL'} point={p1:.2f} half-effect={p2:.2f} skeptical={p3:.2f} flat={p3b:.2f} vs median human guess .85")
