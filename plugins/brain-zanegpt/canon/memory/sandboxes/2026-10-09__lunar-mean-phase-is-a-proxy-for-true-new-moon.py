"""Sandbox: is a mean-synodic-period lunar phase a safe stand-in for the true new moon?

PREDICTION (written before the first run):
  P1. Mean-only new-moon model (JD = 2451550.09766 + 29.530588861*k) vs 17 reference
      new-moon instants (UTC, minute resolution, recalled from published almanac/eclipse
      tables): max |error| between 6 h and 14 h.
  P2. Same model plus Meeus-style anomaly/node terms and a TT->UTC (delta-T) shift:
      max |error| <= 10 minutes, i.e. at least a 40x reduction.
  P3. (break) The dominant term alone (-0.4072 sin M') is NOT enough: its max error stays
      above 1 hour.
  P4. (break) Editing the mean period at the 7th decimal does not move the true error
      (change < 0.01 h), but the naive 29.5-day period drifts by more than 3 h by 2026.
  P5. (break) Calendar-date classification in UTC over 2024-2026: the mean model puts the
      new moon on the wrong date for 3 to 15 of the moons; a fixed -8h offset vs the real
      Los Angeles zone flips the date for 0 to 2 moons, and any flip lies in the 07:00-08:00 UTC window.
  P6. (added after the first run showed 0 flips in 2024-2026; break test of the fixed-offset
      claim) Over 2000-2050 the fixed -8h offset flips the local date for 8 to 30 moons, all inside
      the 07:00-08:00 UTC window, so the hazard is real but rare per year.
"""
import math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

JD_UNIX0 = 2440587.5

def jd_from_dt(dt):
    return JD_UNIX0 + dt.timestamp() / 86400.0

def dt_from_jd(jd):
    return datetime.fromtimestamp((jd - JD_UNIX0) * 86400.0, tz=timezone.utc)

# (UTC instant, delta-T seconds for that year)  -- reference new moons
REFS = [
    ("2000-01-06 18:14", 64), ("2017-08-21 18:30", 69), ("2023-10-14 17:55", 69),
    ("2024-01-11 11:57", 69), ("2024-02-09 22:59", 69), ("2024-03-10 09:00", 69),
    ("2024-04-08 18:21", 69), ("2024-05-08 03:22", 69), ("2024-06-06 12:38", 69),
    ("2024-07-05 22:57", 69), ("2024-08-04 11:13", 69), ("2024-09-03 01:55", 69),
    ("2024-10-02 18:49", 69), ("2024-11-01 12:47", 69), ("2024-12-01 06:21", 69),
    ("2024-12-30 22:27", 69), ("2026-08-12 17:37", 69),
]
REFS = [(datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc), dT) for s, dT in REFS]

def k_for(dt):
    # Meeus: k ~ (year - 2000) * 12.3685, rounded to an integer for new moon
    year = dt.year + (dt.timetuple().tm_yday - 1) / 365.25
    return round((year - 2000.0) * 12.3685)

def mean_jde(k, period=29.530588861):
    T = k / 1236.85
    return 2451550.09766 + period * k + 0.00015437 * T * T

def corrected_jde(k, terms="full"):
    T = k / 1236.85
    E = 1 - 0.002516 * T - 0.0000074 * T * T
    r = math.radians
    M = r((2.5534 + 29.10535670 * k - 0.0000014 * T * T) % 360)
    Mp = r((201.5643 + 385.81693528 * k + 0.0107582 * T * T) % 360)
    F = r((160.7108 + 390.67050284 * k - 0.0016118 * T * T) % 360)
    Om = r((124.7746 - 1.56375588 * k + 0.0020672 * T * T) % 360)
    s = math.sin
    if terms == "dominant":
        corr = -0.40720 * s(Mp)
    else:
        corr = (-0.40720 * s(Mp) + 0.17241 * E * s(M) + 0.01608 * s(2 * Mp)
                + 0.01039 * s(2 * F) + 0.00739 * E * s(Mp - M) - 0.00514 * E * s(Mp + M)
                + 0.00208 * E * E * s(2 * M) - 0.00111 * s(Mp - 2 * F) - 0.00057 * s(Mp + 2 * F)
                + 0.00056 * E * s(2 * Mp + M) - 0.00042 * s(3 * Mp) + 0.00042 * E * s(M + 2 * F)
                + 0.00038 * E * s(M - 2 * F) - 0.00024 * E * s(2 * Mp - M) - 0.00017 * s(Om))
    return mean_jde(k) + corr

def to_utc(jde, dT):
    return dt_from_jd(jde - dT / 86400.0)   # TT -> UTC

def err_h(model_dt, ref_dt):
    return (model_dt - ref_dt).total_seconds() / 3600.0

def run():
    out = {}
    # S1 mean-only (treat mean JDE as if UTC: the naive phase calculation people write)
    e1 = []; e2 = []; e3 = []
    print("event(UTC)           mean_err_h  corrected_err_min")
    for ref, dT in REFS:
        k = k_for(ref)
        e_mean = err_h(dt_from_jd(mean_jde(k)), ref)
        e_cor = err_h(to_utc(corrected_jde(k), dT), ref)
        e_dom = err_h(to_utc(corrected_jde(k, "dominant"), dT), ref)
        e1.append(abs(e_mean)); e2.append(abs(e_cor)); e3.append(abs(e_dom))
        print("%s  %+8.2f   %+8.1f" % (ref.strftime("%Y-%m-%d %H:%M"), e_mean, e_cor * 60))
    out["mean_max_h"] = max(e1); out["cor_max_min"] = max(e2) * 60; out["dom_max_h"] = max(e3)
    out["ratio"] = out["mean_max_h"] * 60 / out["cor_max_min"]

    # S4 proxy edit: refine / degrade the mean period constant
    def mean_max(period):
        return max(abs(err_h(dt_from_jd(mean_jde(k_for(r), period)), r)) for r, _ in REFS)
    base = mean_max(29.530588861)
    out["tweak7_delta_h"] = abs(mean_max(29.530588861 + 4e-7) - base)
    # naive 29.5-day period error at the 2026 reference, anchored at the same epoch
    r26 = REFS[-1][0]
    out["naive295_err_2026_h"] = abs(err_h(dt_from_jd(mean_jde(k_for(r26), 29.5)), r26))

    # S5 date classification over 2024-2026 moons
    la = ZoneInfo("America/Los_Angeles")
    wrong_mean = 0; flips = []; n = 0
    for k in range(k_for(datetime(2024, 1, 1, tzinfo=timezone.utc)), k_for(datetime(2026, 12, 31, tzinfo=timezone.utc)) + 1):
        true_dt = to_utc(corrected_jde(k), 69)
        mean_dt = dt_from_jd(mean_jde(k))
        n += 1
        if mean_dt.date() != true_dt.date():
            wrong_mean += 1
        fixed = (true_dt + timedelta(hours=-8)).date()
        real = true_dt.astimezone(la).date()
        if fixed != real:
            flips.append(true_dt.strftime("%Y-%m-%d %H:%M"))
    # S6 long span
    long_flips = []
    for k in range(k_for(datetime(2000, 1, 1, tzinfo=timezone.utc)), k_for(datetime(2050, 12, 31, tzinfo=timezone.utc)) + 1):
        t = to_utc(corrected_jde(k), 69)
        if (t + timedelta(hours=-8)).date() != t.astimezone(la).date():
            long_flips.append(t.strftime("%Y-%m-%d %H:%M"))
    out["long_flips"] = long_flips
    out["n_moons"] = n; out["wrong_mean_dates"] = wrong_mean; out["la_flips"] = flips
    return out

o = run()
print()
print("S1 mean-only max err      : %.2f h" % o["mean_max_h"])
print("S2 corrected max err      : %.1f min  (reduction x%.0f)" % (o["cor_max_min"], o["ratio"]))
print("S3 dominant-term-only max : %.2f h" % o["dom_max_h"])
print("S4 period 7th-decimal edit: true error moves %.4f h; naive 29.5 d error in 2026: %.2f h" % (o["tweak7_delta_h"], o["naive295_err_2026_h"]))
print("S5 UTC date wrong under mean model: %d of %d moons; fixed -8h vs LA zone flips: %s" % (o["wrong_mean_dates"], o["n_moons"], o["la_flips"]))
print("S6 2000-2050 fixed -8h vs LA zone flips: %d (first %s)" % (len(o["long_flips"]), o["long_flips"][:3]))
long_ok = 8 <= len(o["long_flips"]) <= 30 and all(7 <= int(f[11:13]) < 8 for f in o["long_flips"])
flips_in_window = all(7 <= int(f[11:13]) < 8 for f in o["la_flips"])
checks = {
    "P1": 6 <= o["mean_max_h"] <= 14,
    "P2": o["cor_max_min"] <= 10,
    "P3": o["dom_max_h"] > 1,
    "P4": o["tweak7_delta_h"] < 0.01 and o["naive295_err_2026_h"] > 3,
    "P6": long_ok,
    "P5": 3 <= o["wrong_mean_dates"] <= 15 and len(o["la_flips"]) <= 2 and flips_in_window,
}
print("checks:", checks)
ok = all(checks.values())
print("RESULT: %s mean-only max %.1f h vs corrected %.1f min over %d new moons; dominant-only %.2f h; mean model wrong UTC date %d/%d; LA fixed-offset flips %d (2024-26) / %d (2000-50)" % (
    "PASS" if ok else "FAIL", o["mean_max_h"], o["cor_max_min"], len(REFS), o["dom_max_h"], o["wrong_mean_dates"], o["n_moons"], len(o["la_flips"]), len(o["long_flips"])))
