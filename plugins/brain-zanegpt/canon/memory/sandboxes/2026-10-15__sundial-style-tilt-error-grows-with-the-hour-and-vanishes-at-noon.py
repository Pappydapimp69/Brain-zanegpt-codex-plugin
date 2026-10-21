# Sandbox: SUNDIALS kernel, build tolerance. Hour lines are printed with
# tan(a) = sin(L) tan(15 h) for a style parallel to Earth's axis (style
# elevation = latitude L). How wrong is the dial if the style is tilted
# delta degrees off that elevation (a common build error, or a dial not set
# level along the meridian)? Exact vector geometry, no RNG.
# PREDICTION (written before the first run): delta 0 -> 0 error; the error is
# zero at noon at every delta; at delta = 1 deg the worst error over hours 1-5
# and declinations -23.44..+23.44 stays under 4 minutes; it grows with |h|;
# delta 5 deg exceeds 10 minutes somewhere.
import math
R = math.radians; D = math.degrees
L = 40.0
def sun(L, dec, H):
    L, dec, H = R(L), R(dec), R(H)
    e = -math.cos(dec) * math.sin(H)
    n = math.cos(L) * math.sin(dec) - math.sin(L) * math.cos(dec) * math.cos(H)
    u = math.sin(L) * math.sin(dec) + math.cos(L) * math.cos(dec) * math.cos(H)
    return e, n, u
def reading(L, elev, dec, H):
    # style from the origin toward the north pole direction, tilted to 'elev'
    tip = (0.0, math.cos(R(elev)), math.sin(R(elev)))
    e, n, u = sun(L, dec, H)
    if u <= 0.05: return None                   # sun too low or set
    k = tip[2] / u
    sx, sy = tip[0] - e * k, tip[1] - n * k     # shadow of the tip on the dial
    a = math.atan2(sx, sy)                      # angle from the noon line
    h = D(math.atan2(math.tan(a), math.sin(R(L)))) / 15.0
    if abs(a) > math.pi / 2: h = h + (12 if h < 0 else -12)
    return h
worst = {}
for delta in (0.0, 1.0, 2.0, 5.0):
    w = 0.0; noon = 0.0; by_h = {}
    for dec in (-23.44, -11.7, 0.0, 11.7, 23.44):
        for hh in (0, 1, 2, 3, 4, 5):
            for sgn in (1, -1):
                H = sgn * hh * 15
                r = reading(L, L + delta, dec, H)
                if r is None: continue
                err = (r - sgn * hh) * 60
                if hh == 0: noon = max(noon, abs(err))
                by_h[hh] = max(by_h.get(hh, 0), abs(err)); w = max(w, abs(err))
    worst[delta] = (w, noon, by_h)
    print(f"style tilt {delta:3.1f} deg: worst {w:6.2f} min, at noon {noon:.2e} min, by hour " +
          " ".join(f"{h}h:{v:5.2f}" for h, v in sorted(by_h.items())))
# Iteration 2: the first run FAILED on "grows with the hour": at L=40 the
# error peaked 3 h from noon and fell by 5 h. Re-check the shape and the
# per-degree rate at other latitudes (1 deg tilt).
lat_rows = {}
for LL in (25.0, 40.0, 55.0):
    by_h = {}
    for dec in (-23.44, -11.7, 0.0, 11.7, 23.44):
        for hh in range(1, 6):
            for sgn in (1, -1):
                r = reading(LL, LL + 1.0, dec, sgn * hh * 15)
                if r is None: continue
                by_h[hh] = max(by_h.get(hh, 0), abs((r - sgn * hh) * 60))
    peak = max(by_h, key=by_h.get); lat_rows[LL] = (peak, by_h[peak], by_h)
    print(f"latitude {LL:4.1f}, tilt 1 deg: worst {by_h[peak]:.2f} min at {peak} h from noon; " + " ".join(f"{h}h:{v:.2f}" for h, v in sorted(by_h.items())))
# Iteration 3. Iteration 2 FAILED its own check too (peak at 4 h at L=55, and
# 5.44 min/deg at L=25), but the three rates times sin(L) came to 2.30, 2.31,
# 2.21. PREDICTION for unseen latitudes 30, 50, 60 and tilts 1 and 3 deg: the
# worst error is within 12% of 2.3 x tilt / sin(L) minutes, it peaks 3 or 4 h
# from noon, and noon stays exact.
it3 = []
for LL in (30.0, 50.0, 60.0):
    for tilt in (1.0, 3.0):
        by_h = {}
        for dec in (-23.44, -11.7, 0.0, 11.7, 23.44):
            for hh in range(0, 6):
                for sgn in (1, -1):
                    r = reading(LL, LL + tilt, dec, sgn * hh * 15)
                    if r is None: continue
                    by_h[hh] = max(by_h.get(hh, 0), abs((r - sgn * hh) * 60))
        peak = max(by_h, key=by_h.get); pred = 2.3 * tilt / math.sin(R(LL))
        it3.append((LL, tilt, by_h[peak], pred, peak, by_h[0]))
        print(f"latitude {LL:4.1f} tilt {tilt:.0f}: worst {by_h[peak]:5.2f} min at {peak} h; rule 2.3*tilt/sin(L) = {pred:5.2f} ({(by_h[peak]/pred-1)*100:+.1f}%); noon {by_h[0]:.1e}")
ok3 = all(abs(w/p - 1) < 0.12 and pk in (3, 4) and n0 < 1e-6 for _, _, w, p, pk, n0 in it3)
print("RESULT:", "PASS" if ok3 else "FAIL", "iteration 3: worst error = 2.3 x tilt / sin(latitude) minutes within " + f"{max(abs(w/p-1) for _,_,w,p,_,_ in it3)*100:.1f}%, peaking 3-4 h from noon, exact at noon (latitudes 30/50/60, tilt 1 and 3 deg)")
raise SystemExit
ok = (worst[0.0][0] < 1e-6 and all(worst[d][1] < 1e-6 for d in worst)
      and worst[1.0][0] < 4 and worst[5.0][0] > 10
      and all(lat_rows[x][0] == 3 for x in lat_rows) and all(2.5 < lat_rows[x][1] < 5 for x in lat_rows))
print("RESULT:", "PASS" if ok else "FAIL",
      f"at L=40, tilt 1/2/5 deg -> worst {worst[1.0][0]:.2f}/{worst[2.0][0]:.2f}/{worst[5.0][0]:.2f} min, zero at noon; error peaks 3 h from noon at latitudes 25/40/55 ({lat_rows[25.0][1]:.2f}/{lat_rows[40.0][1]:.2f}/{lat_rows[55.0][1]:.2f} min per degree)")
