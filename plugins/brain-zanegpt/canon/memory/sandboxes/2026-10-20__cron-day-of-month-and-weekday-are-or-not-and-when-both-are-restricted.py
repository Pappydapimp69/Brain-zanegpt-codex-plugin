# Sandbox: classic cron (Vixie/ISC semantics, as documented in crontab(5)): when BOTH day-of-month and day-of-week are
# restricted (neither is *), a day matches if EITHER matches (OR). Real calendar via datetime, no RNG, no clock.
# PREDICTION (before run): for "0 0 13 * 5" over calendar 2026 the OR rule fires on 61 days (52 Fridays + 12 thirteenths
# - 3 Friday-13ths: Feb, Mar, Nov) while the intuitive AND rule fires on 3; with day-of-week as * only the 13th fires (12);
# with day-of-month as * only Fridays fire (52). An AND-expecting author therefore gets 58 surprise runs a year.
import datetime
YEAR = 2026
days = [datetime.date(YEAR, 1, 1) + datetime.timedelta(d) for d in range(365)]
def fire(day, dom, dow, mode):
    dom_ok = dom is None or day.day in dom
    dow_ok = dow is None or (day.isoweekday() % 7) in dow   # cron: 0=Sunday, 5=Friday
    if dom is None or dow is None: return dom_ok and dow_ok
    return (dom_ok or dow_ok) if mode == "or" else (dom_ok and dow_ok)
def count(dom, dow, mode): return sum(fire(d, dom, dow, mode) for d in days)
both_or = count({13}, {5}, "or"); both_and = count({13}, {5}, "and")
only_dom = count({13}, None, "or"); only_dow = count(None, {5}, "or")
print("scenario1 '0 0 13 * 5' OR rule=%d AND rule=%d" % (both_or, both_and))
print("scenario2 dow='*': %d   dom='*': %d" % (only_dom, only_dow))
# BREAK: a pair with no overlap year-round (day 31 and Sunday): OR = 7 months*1 + 52 Sundays - overlaps
s31 = count({31}, {0}, "or"); s31and = count({31}, {0}, "and")
print("scenario3 BREAK '31 * Sunday': OR=%d AND=%d" % (s31, s31and))
surprise = both_or - both_and
ok = both_or == 61 and both_and == 3 and only_dom == 12 and only_dow == 52 and surprise == 58
print("RESULT: %s OR=%d AND=%d dom-only=%d dow-only=%d surprise runs=%d; '31 * Sunday' OR=%d AND=%d"
      % ("PASS" if ok else "FAIL", both_or, both_and, only_dom, only_dow, surprise, s31, s31and))
