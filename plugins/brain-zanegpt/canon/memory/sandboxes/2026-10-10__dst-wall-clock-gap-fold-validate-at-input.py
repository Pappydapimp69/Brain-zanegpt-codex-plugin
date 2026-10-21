# Prediction (written before first run):
# 1) New_York 2024-03-10 02:30 (gap): zoneinfo raises nothing; fold=0 and fold=1 give different UTC
#    (06:30 vs 07:30) and neither round-trips back to 02:30 (both come back 03:30 / 01:30).
# 2) New_York 2024-11-03 01:30 (overlap): fold=0 and fold=1 differ by exactly 3600s; both round-trip.
# 3) Lord_Howe has a 30-min DST shift, so "an hour is skipped" is too narrow: gap is 1800s.
# 4) A fixed -05:00 offset applied to a July date is off by 3600s vs the real zone.
# 5) A roundtrip+fold validator classifies all 3 kinds correctly over a full year scan of 15-min steps.
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
ok = True
def chk(name, cond, detail=""):
    global ok
    ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name, detail)
def utc(dt): return dt.astimezone(timezone.utc)
def classify(naive, tz):
    a = naive.replace(tzinfo=tz, fold=0); b = naive.replace(tzinfo=tz, fold=1)
    ra = utc(a).astimezone(tz).replace(tzinfo=None); rb = utc(b).astimezone(tz).replace(tzinfo=None)
    if ra != naive or rb != naive: return "nonexistent"
    return "ambiguous" if utc(a) != utc(b) else "ok"
NY = ZoneInfo("America/New_York")
# S1 gap
g = datetime(2024,3,10,2,30)
u0, u1 = utc(g.replace(tzinfo=NY,fold=0)), utc(g.replace(tzinfo=NY,fold=1))
chk("S1 gap no error, two UTC answers", u0 != u1, f"{u0:%H:%M} vs {u1:%H:%M}")
r0 = u0.astimezone(NY).replace(tzinfo=None); r1 = u1.astimezone(NY).replace(tzinfo=None)
chk("S1 gap never round-trips", r0 != g and r1 != g, f"{r0:%H:%M} {r1:%H:%M}")
# S2 overlap
o = datetime(2024,11,3,1,30)
d = utc(o.replace(tzinfo=NY,fold=1)) - utc(o.replace(tzinfo=NY,fold=0))
chk("S2 overlap two instants 3600s apart", d == timedelta(hours=1), str(d))
chk("S2 overlap both round-trip", all(utc(o.replace(tzinfo=NY,fold=f)).astimezone(NY).replace(tzinfo=None)==o for f in (0,1)))
# S3 BREAK: gap is not always an hour
LH = ZoneInfo("Australia/Lord_Howe")
n = datetime(2024,10,6,2,15)
gaps = [classify(datetime(2024,10,6,2,0)+timedelta(minutes=m), LH) for m in range(0,60,15)]
chk("S3 Lord_Howe gap is 30 min (2:00,2:15 nonexistent; 2:30 ok)", gaps == ["nonexistent","nonexistent","ok","ok"], str(gaps))
# S4 fixed offset
fixed = timezone(timedelta(hours=-5)); j = datetime(2024,7,1,12,0)
err = utc(j.replace(tzinfo=fixed)) - utc(j.replace(tzinfo=NY))
chk("S4 fixed offset wrong by 1h in summer", abs(err) == timedelta(hours=1), str(err))
# S5 validator year scan
from collections import Counter
c = Counter(); t = datetime(2024,1,1)
while t.year == 2024:
    c[classify(t, NY)] += 1; t += timedelta(minutes=15)
chk("S5 NY year scan: 4 nonexistent, 4 ambiguous slots", c["nonexistent"]==4 and c["ambiguous"]==4, str(dict(c)))
# S6 future rule change: same stored local time, different ruleset -> different instant
m = datetime(2030,10,1,13,0)
dub = ZoneInfo("Europe/Dublin"); alt = timezone(timedelta(hours=0))  # hypothetical: Ireland drops DST
chk("S6 stored local+zone id re-resolves on rule change; frozen offset can't", utc(m.replace(tzinfo=dub)) != utc(m.replace(tzinfo=alt)), f"{utc(m.replace(tzinfo=dub)):%H:%M} vs {utc(m.replace(tzinfo=alt)):%H:%M}")
print("RESULT: " + ("PASS" if ok else "FAIL") + " gap/fold/validator behaviours reproduced; zoneinfo never raises, gap size varies")
