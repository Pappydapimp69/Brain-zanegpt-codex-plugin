"""Gap: the open SEVEN tension 'psychosis as horror vs as experience' had no
evidence. Two real experiments exist (read this session):
 Ferchaud, Seibert, Sellers & Escobar Salazar 2020, Frontiers in Psychology
 (PMC7509402): N = 198 students, randomized and yoked, ~45 min of Hellblade
 played vs watched; playing -> transportation -> identification -> LOWER social
 distance (significant indirect path); NO effect on stereotyping, including
 'those with mental illness are dangerous'.
 Mason & Westhead 2025, Journal of Mental Health: n = 37, pre/post; attitudes
 to schizophrenia improved; empathy and social distance did not.
Question: are the nulls (stereotyping, dangerousness, social distance in the
second study) evidence of NO effect, or just too small to see?
Normal-approximation power, stdlib only (statistics.NormalDist), alpha .05
two-sided, power .80. Ferchaud: two arms of 99; Mason: paired, n 37.
PREDICTION (written before running): minimum detectable d about 0.40 for
Ferchaud (two-sample) and about 0.47 for Mason (paired); for a small media-
attitude effect of d = 0.2 (assumed typical) power is below 0.30 in Ferchaud and
below 0.30 in Mason, so both nulls are uninformative about small effects and
neither study tested a horror framing (pole A) at all.
"""
import sys
from statistics import NormalDist
print("python", sys.version.split()[0])
Z = NormalDist()
za, zb = Z.inv_cdf(0.975), Z.inv_cdf(0.80)
def mdd_two(n_per): return (za + zb) * (2 / n_per) ** 0.5
def mdd_paired(n): return (za + zb) / n ** 0.5
def power_two(d, n_per): return 1 - Z.cdf(za - d / (2 / n_per) ** 0.5)
def power_paired(d, n): return 1 - Z.cdf(za - d * n ** 0.5)
m_f, m_m = mdd_two(99), mdd_paired(37)
print(f"minimum detectable d (80% power): Ferchaud two-arm 99/99 {m_f:.3f}; Mason paired n37 {m_m:.3f}")
for d in (0.1, 0.2, 0.3, 0.5):
    print(f"d {d}: power Ferchaud {power_two(d, 99):.3f}, Mason {power_paired(d, 37):.3f}")
n_needed = ((za + zb) / 0.2) ** 2 * 2
print(f"two-arm N per arm to detect d 0.2: {n_needed:.0f}")
c = [abs(m_f - 0.40) < 0.02, abs(m_m - 0.47) < 0.02, power_two(0.2, 99) < 0.30, power_paired(0.2, 37) < 0.30]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; MDD Ferchaud {m_f:.2f}, Mason {m_m:.2f}; power at d 0.2: {power_two(0.2,99):.2f} / {power_paired(0.2,37):.2f}; {n_needed:.0f} per arm needed for d 0.2")
