"""Ceramics: size wet clay by dividing by (1 - shrink), not multiplying by (1 + shrink).
Deterministic, stdlib only."""
def fired(wet, s): return wet * (1 - s)
def correct(target, s): return target / (1 - s)
def naive(target, s): return target * (1 + s)
ok = True
for s in (0.0, 0.06, 0.12, 0.15):   # s=0.0 is the case built to BREAK it (no difference expected)
    t = 100.0
    c, n = fired(correct(t, s), s), fired(naive(t, s), s)
    err = (t - n) / t
    print(f"shrink {s:.0%}: correct->{c:.2f}mm  naive->{n:.2f}mm  short by {err:.2%} (s^2={s*s:.2%})")
    ok &= abs(c - t) < 1e-9 and abs(err - s * s) < 1e-12
print("RESULT: PASS naive multiply fires short by exactly s^2 (1.44% at 12%, 2.25% at 15%); divide hits target" if ok
      else "RESULT: FAIL")
