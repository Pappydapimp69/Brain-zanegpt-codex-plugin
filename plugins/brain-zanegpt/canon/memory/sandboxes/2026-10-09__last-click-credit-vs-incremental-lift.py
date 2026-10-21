"""Sandbox: does last-click attribution mis-credit the path, and when does it stop mattering?

PREDICTION (written before the first run):
  P1. Cohort A (600 users) sees Display, then searches the brand; cohort B (400) has organic
      intent and searches the brand regardless. Conversion prob: A 0.10 with display / 0.01 without,
      B 0.20 either way. Last-click gives Display 0 of 140 conversions and Brand 140.
      Truth by removal: Display 54 conversions (38.6%), Brand ads 0.
  P2. Cutting Display because last-click shows 0 loses 54 conversions (38.6% of the total);
      cutting Brand because truth shows 0 loses 0.
  P3. (break) If a fraction f of display users click straight through (display IS the last touch),
      last-click's display credit grows linearly with f and the gap closes at f=1; at f=0.5 the
      under-credit is about half of the true 54, and the gap closes at f=1.
  P4. (added after run 1 FAILED P3: at f=1 display's last-click credit is 60, not 54, because last-click also
      credits display with the 6 baseline buyers who would have converted anyway) Last-click display credit
      is exactly 60*f, so it equals the true lift only at f=0.9 and over-credits above it; and brand stays
      over-credited by the organic cohort (80) at every f.
"""
N_A, N_B = 600, 400
P_A_DISPLAY, P_A_NONE, P_B = 0.10, 0.01, 0.20

def world(display_on=True, brand_on=True, f=0.0):
    """Expected conversions by channel under last-click, plus total. f = share of display users who click
    display directly (display is then the last touch)."""
    lc = {"display": 0.0, "brand": 0.0}
    total = 0.0
    # cohort A
    conv_a = N_A * (P_A_DISPLAY if display_on else P_A_NONE)
    total += conv_a
    if display_on:
        lc["display"] += conv_a * f
        lc["brand"] += conv_a * (1 - f) if brand_on else 0
    else:
        lc["brand"] += conv_a if brand_on else 0   # only organic baseline buyers, brand ad catches them
    # cohort B: brand search is the last click when the brand ad exists
    conv_b = N_B * P_B
    total += conv_b
    if brand_on:
        lc["brand"] += conv_b
    return lc, total

full_lc, full_total = world()
print("S1 last-click credit:", full_lc, "total", full_total)
no_display_lc, no_display_total = world(display_on=False)
no_brand_lc, no_brand_total = world(brand_on=False)
true_display = full_total - no_display_total
true_brand = full_total - no_brand_total
print("S1 removal truth: display=%.1f (%.1f%%) brand=%.1f" % (true_display, 100*true_display/full_total, true_brand))
ok1 = full_lc["display"] == 0 and full_lc["brand"] == 140 and abs(true_display - 54) < 1e-9 and abs(true_brand) < 1e-9
print("S2 cut display loses %.1f conv (%.1f%% of total); cut brand loses %.1f" % (true_display, 100*true_display/full_total, true_brand))
ok2 = abs(true_display/full_total - 0.3857) < 1e-3

# proxy-vs-true readout beside each other (finger vs moon)
for ch, t in (("display", true_display), ("brand", true_brand)):
    print("READOUT %-8s last-click=%6.1f  true-lift=%6.1f  gap=%+6.1f" % (ch, full_lc[ch], t, full_lc[ch]-t))

# S3/S4 sweep f
ok3 = True
prev = -1
for f in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0):
    lc, tot = world(f=f)
    gap = true_display - lc["display"]
    print("S3 f=%.2f display last-click=%.1f true=%.1f (credit - lift = %+.1f) brand credit=%.1f" % (f, lc["display"], true_display, -gap, lc["brand"]))
    ok3 &= lc["display"] > prev and abs(lc["display"] - 60*f) < 1e-9 and lc["brand"] >= 80
    prev = lc["display"]
lc9, _ = world(f=0.9)
ok4 = abs(lc9["display"] - true_display) < 1e-9
lc1, _ = world(f=1.0)
ok4 &= lc1["display"] - true_display == 6 and lc1["brand"] == 80 and true_brand == 0
print("S4 match only at f=0.9; at f=1.0 display over-credited by baseline 6, brand still +80 vs true 0:", ok4)

allok = ok1 and ok2 and ok3 and ok4
print("RESULT: %s last-click gave display 0 of 140 vs true lift 54 (38.6%%); display credit = 60*f so it matches the 54 lift only at f=0.9 and over-credits above; brand over-credit 80 persists at every f" % ("PASS" if allok else "FAIL"))
