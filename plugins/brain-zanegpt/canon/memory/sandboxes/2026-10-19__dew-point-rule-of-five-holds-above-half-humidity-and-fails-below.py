"""Dew point from temperature and relative humidity: Magnus formula (a=17.625, b=243.04 C)
versus the rule of thumb Td ~= T - (100-RH)/5. Stdlib only, deterministic."""
from math import log, exp

A, B = 17.625, 243.04

def dew_point(t, rh):
    g = log(rh / 100.0) + A * t / (B + t)
    return B * g / (A - g)

def rh_from_dew(t, td):                       # inverse, to check the formula round-trips
    return 100.0 * exp(A * td / (B + td) - A * t / (B + t))

def rule(t, rh):
    return t - (100 - rh) / 5.0

temps = range(0, 36)
worst_ge50 = max((abs(rule(t, rh) - dew_point(t, rh)), t, rh) for t in temps for rh in range(50, 101))
worst_lt50 = max((abs(rule(t, rh) - dew_point(t, rh)), t, rh) for t in temps for rh in range(10, 50))
# BREAK: the rule at 30 C as humidity falls
first_bad = next(rh for rh in range(100, 0, -1) if abs(rule(30, rh) - dew_point(30, rh)) > 1.0)
roundtrip = max(abs(rh_from_dew(t, dew_point(t, rh)) - rh) for t in temps for rh in range(10, 101, 5))
at100 = max(abs(dew_point(t, 100) - t) for t in temps)
cold = max(abs(rule(t, rh) - dew_point(t, rh)) for t in range(-10, 0) for rh in range(50, 101))
safe_rh = next(r for r in range(1, 101) if all(abs(rule(t, r2) - dew_point(t, r2)) <= 1.0 for t in temps for r2 in range(r, 101)))
print(f"lowest RH from which the rule stays within 1C at every T in 0..35: {safe_rh}")
print(f"worst error RH>=50 (0..35C): {worst_ge50[0]:.2f}C at T={worst_ge50[1]} RH={worst_ge50[2]}")
print(f"worst error RH<50: {worst_lt50[0]:.2f}C at T={worst_lt50[1]} RH={worst_lt50[2]}")
print(f"at 30C the rule first exceeds 1C error at RH={first_bad}; roundtrip RH err {roundtrip:.1e}; RH=100 gives Td=T within {at100:.1e}")
print(f"below freezing (-10..-1C, RH>=50) worst error {cold:.2f}C")
ok = safe_rh <= 50 and worst_ge50[0] <= 1.0 and worst_lt50[0] > 1.0 and roundtrip < 1e-9 and at100 < 1e-9
print(f"RESULT: {'PASS' if ok else 'FAIL'} rule within {worst_ge50[0]:.2f}C for RH>=50 over 0..35C but off by up to {worst_lt50[0]:.2f}C below 50; at 30C first >1C at RH={first_bad}; within 1C only from RH={safe_rh}")
