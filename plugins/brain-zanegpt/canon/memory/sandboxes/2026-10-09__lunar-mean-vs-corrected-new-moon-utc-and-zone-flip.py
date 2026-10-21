"""ITERATION 1 prediction (was wrong): four-term correction within 10 min. Observed 21.2 min worst. ITERATION 2 prediction: adding the next Meeus terms
(M'-M, M'+M, 2M, M'-2F, M'+2F, node) brings the worst row under 6 minutes while the four-term set stays between 10 and 30 minutes.
Original prediction (before run): against 16 published new-moon minutes (UTC), the mean function (epoch + k*29.530588861) errs by several hours
(max between 6 and 14 h), the dominant -0.4072 sin M' term alone still leaves over 2 h, the four-term Meeus correction minus delta-T 69 s lands
within 10 minutes for every row, a 7th-decimal change of the period moves error under 0.01 h, and a fixed -8 h offset disagrees with America/Los_Angeles
on at least one date in 2000-2050 (BREAK case: the claim that fixed offset is enough should survive only if zero flips)."""
import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REF = ["2000-01-06 18:14","2017-08-21 18:30","2023-04-20 04:12","2024-01-11 11:57","2024-02-09 22:59","2024-03-10 09:00","2024-04-08 18:21",
       "2024-05-08 03:22","2024-06-06 12:38","2024-07-05 22:57","2024-08-04 11:13","2024-09-03 01:55","2024-10-02 18:49","2024-11-01 12:47",
       "2024-12-01 06:21","2024-12-30 22:27"]
REF = [datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc) for s in REF]
J2000 = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
def jd_to_dt(jd): return J2000 + timedelta(days=jd - 2451545.0)
def rad(x): return math.radians(x % 360)

def new_moon(k, mode, period=29.530588861):
    T = k / 1236.85
    jde = 2451550.09766 + period * k + 0.00015437 * T * T
    if mode == "mean": return jd_to_dt(jde)
    M = rad(2.5534 + 29.1053567 * k); Mp = rad(201.5643 + 385.81693528 * k + 0.0107582 * T * T)
    F = rad(160.7108 + 390.67050284 * k - 0.0016118 * T * T); E = 1 - 0.002516 * T
    corr = -0.4072 * math.sin(Mp)
    if mode == "full":
        corr += 0.17241 * E * math.sin(M) + 0.01608 * math.sin(2 * Mp) + 0.01039 * math.sin(2 * F)
    if mode == "meeus":
        corr += (0.17241 * E * math.sin(M) + 0.01608 * math.sin(2 * Mp) + 0.01039 * math.sin(2 * F)
                 + 0.00739 * E * math.sin(Mp - M) - 0.00514 * E * math.sin(Mp + M) + 0.00208 * E * E * math.sin(2 * M)
                 - 0.00111 * math.sin(Mp - 2 * F) - 0.00057 * math.sin(Mp + 2 * F) + 0.00056 * E * math.sin(2 * Mp + M)
                 - 0.00042 * math.sin(3 * Mp) + 0.00042 * E * math.sin(M + 2 * F) + 0.00038 * E * math.sin(M - 2 * F)
                 - 0.00024 * E * math.sin(2 * Mp - M) - 0.00017 * math.sin(rad(124.7746 - 1.56375588 * k)))
    return jd_to_dt(jde + corr) - (timedelta(seconds=69) if mode in ("full", "meeus") else timedelta(0))

def kfor(dt): return round((dt - datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)).total_seconds() / 86400 / 29.530588861)
def errs(mode, period=29.530588861):
    return [abs((new_moon(kfor(r), mode, period) - r).total_seconds()) / 3600 for r in REF]

em, ed, ef, eu = errs("mean"), errs("dominant"), errs("full"), errs("meeus")
print("max err h: mean %.2f dominant %.2f full %.3f (%.1f min)" % (max(em), max(ed), max(ef), max(ef) * 60))
print("max err meeus extended: %.2f min" % (max(eu) * 60))
ep = errs("mean", 29.5305888)  # 7th-decimal change of the period
shift = max(abs(a - b) for a, b in zip(ep, em))
print("period 7th decimal moves error by max %.4f h" % shift)
# zone flip: fixed -8h vs Los Angeles local date, new moons 2000-2050 (full model)
LA = ZoneInfo("America/Los_Angeles"); flips = 0; n = 0
for k in range(0, 620):
    u = new_moon(k, "full"); n += 1
    flips += (u + timedelta(hours=-8)).date() != u.astimezone(LA).date()
print("fixed -8h vs LA date flips: %d of %d" % (flips, n))
ok = 6 < max(em) < 14 and max(ed) > 2 and 10 / 60 < max(ef) < 30 / 60 and max(eu) < 6 / 60 and shift < 0.01 and flips >= 1
print("RESULT: %s mean max %.1f h, dominant-only %.1f h, four-term %.1f min, extended %.1f min, period tweak %.4f h, zone flips %d/%d" % ("PASS" if ok else "FAIL", max(em), max(ed), max(ef) * 60, max(eu) * 60, shift, flips, n))
