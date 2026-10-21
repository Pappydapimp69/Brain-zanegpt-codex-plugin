# Prediction (before run): a "monthly on day 31" rule over 2025-2027 (36 months) fires in exactly 21
# months under skip semantics (iCal RRULE style: months with <31 days are skipped: 7 of 12 months have 31 days
# -> 7*3=21), 36 under clamp-to-last-day, and the clamp rule drifts: a "carry forward from the last fire"
# implementation (add one month to the previous clamped date) lands on day 28 forever after February (day-of-month
# ratchets down). Assumption: everyone means skip or clamp, not carry. BREAK: day 29 over 2025-2027 -> leap year
# 2028 absent, so skip fires 33 of 36 (Feb skipped all three years); carry drifts from Feb onward.
import calendar, datetime as dt
def months(y0, n):
    y, m = y0, 1
    for _ in range(n):
        yield y, m
        m += 1
        if m == 13: y, m = y + 1, 1
def skip(day, n=36):
    return [dt.date(y, m, day) for y, m in months(2025, n) if day <= calendar.monthrange(y, m)[1]]
def clamp(day, n=36):
    return [dt.date(y, m, min(day, calendar.monthrange(y, m)[1])) for y, m in months(2025, n)]
def carry(day, n=36):
    out = [dt.date(2025, 1, day)]
    for _ in range(n - 1):
        p = out[-1]; y, m = (p.year, p.month + 1) if p.month < 12 else (p.year + 1, 1)
        out.append(dt.date(y, m, min(p.day, calendar.monthrange(y, m)[1])))
    return out
r = {}
for day in (31, 30, 29, 15):
    r[day] = (len(skip(day)), len(clamp(day)), len(carry(day)), sorted({d.day for d in carry(day)[3:]}), len({d.day for d in clamp(day)}))
    print(day, "skip", r[day][0], "clamp", r[day][1], "carry", r[day][2], "carry days after Feb", r[day][3], "clamp distinct days", r[day][4])
ok = r[31][0] == 21 and r[31][1] == 36 and r[31][3] == [28] and r[29][0] == 33 and r[15][0] == 36 and r[15][3] == [15]
print(f"RESULT: {'PASS' if ok else 'FAIL'} day31 skip {r[31][0]} clamp {r[31][1]} carry-days-after-Feb {r[31][3]}; day29 skip {r[29][0]}; day15 control skip {r[15][0]}")
