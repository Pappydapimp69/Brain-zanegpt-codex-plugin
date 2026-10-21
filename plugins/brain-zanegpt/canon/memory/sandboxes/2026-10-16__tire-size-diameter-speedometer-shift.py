import re
# Tire code W/AR R D : width mm, aspect ratio %, rim inches. Overall diameter = D*25.4 + 2*W*AR/100 (mm).
def dia(code):
    w, ar, d = map(int, re.match(r"(\d+)/(\d+)R(\d+)$", code).groups()); return d*25.4 + 2*w*ar/100
STOCK = "225/45R17"; base = dia(STOCK)
cands = ["235/40R18", "245/40R18", "245/35R18", "255/35R19", "225/40R18", "245/45R17", "265/50R17"]
print("stock %s diameter %.1f mm" % (STOCK, base))
print("size        dia(mm)  diff   true speed at indicated 100   odometer error per 10000 km")
within = []
for s in cands:
    d = dia(s); diff = (d-base)/base*100
    print("%-10s %8.1f %+5.1f%%  %8.1f km/h %24.0f km" % (s, d, diff, 100*d/base, 10000*(d/base-1)))
    if abs(diff) <= 3: within.append(s)
# plus-one rule: rim +1 inch, drop aspect so diameter stays within +-3 percent: how many aspect steps (5-point) qualify?
ok_steps = [ar for ar in range(25, 60, 5) if abs(dia("225/%dR18" % ar)-base)/base*100 <= 3]
print("225-wide on 18 in rim, aspects within 3%:", ok_steps)
# BREAK: width-only change at fixed aspect shifts diameter, more at high aspect
for ar in (35, 45, 55):
    print("width 225->255 at aspect %d: %+.2f%%" % (ar, (dia("255/%dR17" % ar)-dia("225/%dR17" % ar))/dia("225/%dR17" % ar)*100))
hi = (dia("265/50R17")-base)/base*100
ok = len(within) >= 5 and ok_steps == [35, 40] and hi > 3
print("RESULT: %s %d of %d candidate sizes within 3%% of stock; 225-wide on 18 in rim holds only at aspects %s; 265/50R17 reads %+.1f%% (true speed %.1f at indicated 100)" % ("PASS" if ok else "FAIL", len(within), len(cands), ok_steps, hi, 100*dia("265/50R17")/base))
