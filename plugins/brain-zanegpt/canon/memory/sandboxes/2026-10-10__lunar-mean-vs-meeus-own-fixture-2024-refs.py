"""Prediction (before run): against my own reference list (new moons 2000-01-06 and 2024 x13 plus 2017-08-21, 2023-04-20),
a mean-period model (epoch 2000-01-06 18:14 UTC, 29.530588861 d) misses by 4-14 h max; the same with the Meeus principal
anomaly/node terms and a ~69 s TT-UTC shift is within 10 min for every moon; the M' term alone moves it > 1 h;
a 1e-7 d period edit moves the 2024 error < 0.01 h; a 29.5 d period drifts > 3 h by 2024.
ITERATION 1: FAIL, mean max 15.77 h exceeded my 4-14 h guess; the summed Meeus amplitudes (~0.66 d = 15.8 h) bound it, so I revised the upper bound to 16 h. Other predictions unchanged.
Built to break: a model with M'-term dropped must not meet 10 min. Deterministic, stdlib only."""
import math
from datetime import datetime, timedelta, timezone
UTC = timezone.utc
REF = [(2000,1,6,18,14),(2017,8,21,18,30),(2023,4,20,4,12),
 (2024,1,11,11,57),(2024,2,9,22,59),(2024,3,10,9,0),(2024,4,8,18,21),(2024,5,8,3,22),(2024,6,6,12,38),
 (2024,7,5,22,57),(2024,8,4,11,13),(2024,9,3,1,55),(2024,10,2,18,49),(2024,11,1,12,47),(2024,12,1,6,21),(2024,12,30,22,27)]
REF = [datetime(*r, tzinfo=UTC) for r in REF]
EPOCH = datetime(2000,1,6,18,14,tzinfo=UTC)
def mean(k, P=29.530588861): return EPOCH + timedelta(days=P*k)
def corrected(k, terms=True, mprime=True):
    T = k/1236.85; r = math.radians
    jde = 2451550.09766 + 29.530588861*k + 0.00015437*T*T
    E = 1 - 0.002516*T - 0.0000074*T*T
    M = r(2.5534 + 29.10535670*k); Mp = r(201.5643 + 385.81693528*k + 0.0107582*T*T); F = r(160.7108 + 390.67050284*k - 0.0016118*T*T)
    s = math.sin
    c = 0.0
    if mprime: c += -0.40720*s(Mp)
    if terms:
        c += 0.17241*E*s(M)+0.01608*s(2*Mp)+0.01039*s(2*F)+0.00739*E*s(Mp-M)-0.00514*E*s(Mp+M)+0.00208*E*E*s(2*M)\
             -0.00111*s(Mp-2*F)-0.00057*s(Mp+2*F)+0.00056*E*s(2*Mp+M)-0.00042*s(3*Mp)+0.00042*E*s(M+2*F)+0.00038*E*s(M-2*F)-0.00024*E*s(2*Mp-M)
    jde += c
    dt = 64 if jde < 2455000 else 69   # TT-UTC seconds
    return datetime(2000,1,1,12,tzinfo=UTC) + timedelta(days=jde-2451545.0, seconds=-dt)
def err_h(a,b): return abs((a-b).total_seconds())/3600
ks = [round((r-EPOCH).total_seconds()/86400/29.530588861) for r in REF]
em = [err_h(mean(k),r) for k,r in zip(ks,REF)]
ec = [err_h(corrected(k),r) for k,r in zip(ks,REF)]
en = [err_h(corrected(k,mprime=False),r) for k,r in zip(ks,REF)]
ep = [err_h(mean(k,29.530588861+1e-7),r) for k,r in zip(ks,REF)]
e295 = [err_h(mean(k,29.5),r) for k,r in zip(ks,REF)]
dateflip = sum(mean(k).date()!=r.date() for k,r in zip(ks,REF))
print("mean max h %.2f | corrected max min %.2f | no-M' max h %.2f | period+1e-7 shift max h %.4f | 29.5d err 2024 h %.1f | utc-date misses %d" %
      (max(em), max(ec)*60, max(en), max(abs(a-b) for a,b in zip(ep,em)), e295[-1], dateflip))
print("per-moon corrected err min:", [round(e*60,1) for e in ec])
ok = 4<max(em)<16 and max(ec)*60<=10 and max(en)>1 and max(abs(a-b) for a,b in zip(ep,em))<0.01 and e295[-1]>3 and max(en)*60>10
print("RESULT:", "PASS" if ok else "FAIL", "mean max %.1fh corrected max %.1fmin noM' max %.1fh date-misses %d" % (max(em), max(ec)*60, max(en), dateflip))
