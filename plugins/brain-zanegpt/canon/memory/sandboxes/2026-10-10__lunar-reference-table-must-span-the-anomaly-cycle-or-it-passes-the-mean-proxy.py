"""Sandbox: is the kernel's "17-row reference table doubles as its regression test" a claim-directed test,
or an easy-half (cheap oracle) test that a mean-period proxy can pass?  Stdlib only, no RNG, no timing.

PREDICTION (written before the first run; each could come out wrong):
 P1 over all 620 lunations 2000-2050 (corrected model as truth) the mean-period model's max error is 14-16.5 h
    (above the kernel's 'about 12 h'), and more than 85% of lunations are off by more than 1 h.
 P2 a cheap-oracle suite (spacing 29-30 d, strictly increasing, right year) passes the mean model while a
    claim-directed tolerance test (<= 10 min vs the reference table) fails it and passes the corrected model.
 P3 BREAK: a 17-row table sampled every 14th lunation (the anomalistic month beats against the synodic month:
    14 * 25.8169 deg ~ 361.4 deg) can be placed so the mean model's max error is under 3 h, i.e. it passes a
    3 h tolerance; a 17-row CONTIGUOUS window never gets below 8 h for the mean model. The shortest contiguous
    window that forces the mean model above 8 h at every start is at most 14 lunations.
 P4 with only the four terms the kernel names the worst reference error is 15-30 min (E39 found 21 min);
    skipping the ~69 s TT-to-UTC shift adds up to ~1.15 min, so a 2 min tolerance passes with it and fails without.

ITERATION 1 (run before any edit): P1 held on the range (14.13 h) and on the 92.7% share; P2 held; P4 held (21.2 min, 2.36 min w/o dT).
P3 was REFUTED: the best stride-14 17-row placement left the mean model 4.82 h off (not <3) and the best contiguous 17-row
window left 5.88 h (not >=8); no window length forces >8 h. Revised P3: no placement of 7 or more consecutive lunations can hide
the mean model below 5 h, but a 1-3 row table can (<=2.5 h), so what matters is row count, not stride aliasing.
Added P5 (before its first run): the mean model's max error depends on where the epoch is anchored: anchoring on the real
2000-01-06 18:14 UTC moon (the first reference row) instead of the Meeus mean epoch changes the 620-moon max by more than 1 h,
and a table whose first row IS the anchor scores ~0 error on that row by construction.
"""
import math
from datetime import datetime, timedelta, timezone
UTC = timezone.utc
P = 29.530588861
JD0 = 2451550.09766
# 16 reference new-moon minutes (UTC), recalled from published tables, copied from the stored sandbox
# 2026-10-10__lunar-mean-vs-meeus-own-fixture-2024-refs.py (not fetched here); each may carry ~1 min of error.
REFS = [(2000,1,6,18,14),(2017,8,21,18,30),(2023,4,20,4,12),
 (2024,1,11,11,57),(2024,2,9,22,59),(2024,3,10,9,0),(2024,4,8,18,21),(2024,5,8,3,22),(2024,6,6,12,38),
 (2024,7,5,22,57),(2024,8,4,11,13),(2024,9,3,1,55),(2024,10,2,18,49),(2024,11,1,12,47),(2024,12,1,6,21),(2024,12,30,22,27)]
REFS = [datetime(*r, tzinfo=UTC) for r in REFS]
J2000 = datetime(2000,1,1,12,tzinfo=UTC)

def jde(k, mode):
    T = k/1236.85; r = math.radians
    j = JD0 + P*k + 0.00015437*T*T
    if mode == "mean": return j
    E = 1 - 0.002516*T - 0.0000074*T*T
    M = r(2.5534 + 29.10535670*k); Mp = r(201.5643 + 385.81693528*k + 0.0107582*T*T); F = r(160.7108 + 390.67050284*k - 0.0016118*T*T)
    s = math.sin
    c = -0.40720*s(Mp) + 0.17241*E*s(M) + 0.01608*s(2*Mp) + 0.01039*s(2*F)   # the four kernel terms
    if mode == "four": return j + c
    c += 0.00739*E*s(Mp-M) - 0.00514*E*s(Mp+M) + 0.00208*E*E*s(2*M) - 0.00111*s(Mp-2*F) - 0.00057*s(Mp+2*F) \
         + 0.00056*E*s(2*Mp+M) - 0.00042*s(3*Mp) + 0.00042*E*s(M+2*F) + 0.00038*E*s(M-2*F) - 0.00024*E*s(2*Mp-M)
    return j + c                                                              # extended

def utc(k, mode, delta_t=True):
    j = jde(k, mode)
    dt = (64 if j < 2455000 else 69) if delta_t else 0
    return J2000 + timedelta(days=j-2451545.0, seconds=-dt)

def kref(r): return round((r - utc(0,"mean",False)).total_seconds()/86400/P)
def eh(a, b): return abs((a-b).total_seconds())/3600

N = 620
mean_err = [abs(jde(k,"mean")-jde(k,"ext"))*24 for k in range(N)]      # hours, truth = extended model
# ---- S1 distribution over 620 lunations
mx = max(mean_err); over1 = sum(e > 1 for e in mean_err)/N
print("S1 mean-vs-corrected over %d lunations: max %.2f h, share >1h %.1f%%, share >6h %.1f%%" % (N, mx, 100*over1, 100*sum(e>6 for e in mean_err)/N))
sp = [jde(k+1,"ext")-jde(k,"ext") for k in range(N-1)]
print("   corrected spacing %.3f..%.3f d (mean model: %.6f d every time)" % (min(sp), max(sp), P))

# ---- S2 cheap oracle vs claim-directed test on the 16-row table
ks = [kref(r) for r in REFS]
def cheap_suite(mode):
    t = [utc(k, mode) for k in range(0, 40)]
    sp = [(b-a).total_seconds()/86400 for a, b in zip(t, t[1:])]
    return all(29.0 < d < 30.0 for d in sp) and all(d > 0 for d in sp) and utc(ks[3], mode).year == 2024
def claim_suite(mode, tol_min=10, delta_t=True):
    return max(eh(utc(k, mode, delta_t), r)*60 for k, r in zip(ks, REFS)) <= tol_min
print("S2 cheap suite: mean %s corrected %s | claim suite (<=10 min): mean %s four-term %s extended %s" %
      (cheap_suite("mean"), cheap_suite("ext"), claim_suite("mean"), claim_suite("four"), claim_suite("ext")))

# ---- S3 BREAK: how the table is sampled
def table_max(klist): return max(mean_err[k] for k in klist)
best14 = min((table_max([k0 + 14*i for i in range(17)]), k0) for k0 in range(0, N - 14*16))
best1  = min((table_max([k0 + i for i in range(17)]), k0) for k0 in range(0, N - 16))
print("S3 17-row table, stride 14 lunations: best start k0=%d -> mean-model max error %.2f h (aliasing)" % (best14[1], best14[0]))
print("   17-row contiguous window: best start k0=%d -> mean-model max error %.2f h" % (best1[1], best1[0]))
shortest = None
for L in range(1, 21):
    floor = min(table_max(range(k0, k0+L)) for k0 in range(0, N-L))
    if L in (1,2,3,5,7,14,17): print("   contiguous window of %2d lunations: the easiest placement still leaves the mean model %.2f h off" % (L, floor))
    if shortest is None and floor > 8: shortest = L
print("   shortest contiguous window forcing >8 h at every placement: %s lunations" % shortest)
rowsE = [("annual stride 12", 12), ("stride 13", 13), ("stride 14", 14), ("stride 15", 15)]
for name, st in rowsE:
    b = min((table_max([k0 + st*i for i in range(17)]), k0) for k0 in range(0, N - st*16))
    print("   %s: easiest 17-row placement -> mean max %.2f h" % (name, b[0]))

# ---- S5 epoch anchoring (P5)
anchor_shift_h = (utc(0,"ext",True) - utc(0,"mean",True)).total_seconds()/3600   # real moon k=0 minus Meeus mean epoch
def err_with_shift(sh): return [abs((jde(k,"mean")+sh/24) - jde(k,"ext"))*24 for k in range(N)]
e_meeus = max(err_with_shift(0)); e_real = max(err_with_shift(anchor_shift_h))
signed = [(jde(k,"mean")-jde(k,"ext"))*24 for k in range(N)]
e_best = (max(signed) - min(signed))/2
print("S5 anchor: real 2000-01-06 moon is %.2f h after the Meeus mean epoch; 620-moon mean max: Meeus epoch %.2f h | anchored on real moon %.2f h | best constant offset %.2f h" % (anchor_shift_h, e_meeus, e_real, e_best))
row0 = abs((jde(0,"mean")+anchor_shift_h/24) - jde(0,"ext"))*24
print("   anchored table row 0 error %.3f h (self-confirming); 16-row table max with Meeus epoch %.2f h vs 620-moon max %.2f h" % (row0, max(mean_err[k] for k in ks), mx))

# ---- S4 term set and delta-T on the reference table
def refmax(mode, dtt=True): return max(eh(utc(k, mode, dtt), r)*60 for k, r in zip(ks, REFS))
print("S4 reference max error (min): mean %.0f | four-term %.1f | extended %.2f | extended w/o dT %.2f" %
      (refmax("mean"), refmax("four"), refmax("ext"), refmax("ext", False)))
print("   2-minute claim test: with dT %s, without dT %s" % (claim_suite("ext", 2, True), claim_suite("ext", 2, False)))

floor7 = min(table_max(range(k0, k0+7)) for k0 in range(0, N-7))
floor3 = min(table_max(range(k0, k0+3)) for k0 in range(0, N-3))
ok = (14 <= mx <= 16.5 and over1 > 0.85
      and cheap_suite("mean") and not claim_suite("mean") and claim_suite("ext")
      and floor3 <= 2.5 and floor7 >= 5 and best14[0] > 3 and best1[0] > 5   # revised P3 (original P3 refuted, see header)
      and abs(e_real - e_meeus) > 1 and row0 < 0.01
      and max(mean_err[k] for k in ks) < mx
      and 15 <= refmax("four") <= 30 and claim_suite("ext", 2, True) and not claim_suite("ext", 2, False))
print("RESULT: %s mean max %.1fh/620 moons (16-row table sees %.1fh); cheap suite passes mean=%s; easiest 3-row table %.1fh, 7-row %.1fh, 17-row %.1fh; anchor swing %.1fh->%.1fh; four-term %.0f min" %
      ("PASS" if ok else "FAIL", mx, max(mean_err[k] for k in ks), cheap_suite("mean"), floor3, floor7, best1[0], e_meeus, e_real, refmax("four")))
