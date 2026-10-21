"""Train kernel (GARDEN): re-verify ideas:GARDEN/rain-barrel-sizing (gallons =
roof sq ft x rainfall in x 0.623; first flush 0.5 L/m2 clean to 2 mm dirty),
then compose with ideas:GARDEN/passive-landscape-water-harvesting (rain garden
= drainage area / 6 to / 8) and ideas:GARDEN/drip-irrigation-efficiency (0.5-1
gph emitters) to ask: how much of a year's roof runoff does one barrel catch,
and how long does a full barrel run a drip bed?
Exact arithmetic, no RNG. Storm mix (ASSUMED, a temperate year of 40 in over
70 storms): 30 storms of 0.1 in, 20 of 0.3 in, 12 of 0.8 in, 6 of 1.5 in,
2 of 3.0 in (total 40.6 in). Roof 1,000 sq ft; barrel empty at each storm
(best case: used between storms). Net yield after 10% gutter loss and a
12.5 gal first flush per storm.
PREDICTION (written before running): 0.623 reproduces from US gallon volume
within 0.001; a 55 gal barrel catches under 15% of net annual runoff; a 500
gal tank under 60%; one full 55 gal barrel runs a 10-emitter 1 gph drip bed
for under 6 hours.
"""
STORMS = [(30, 0.1), (20, 0.3), (12, 0.8), (6, 1.5), (2, 3.0)]
ROOF = 1000.0


def main():
    factor = 144.0 / 231.0   # cubic inches in 1 sq ft x 1 in / cubic inches per US gallon
    print(f"conversion factor {factor:.4f} (kernel says 0.623)")
    ff_clean = 0.5 * (ROOF * 0.092903) / 3.78541
    ff_dirty = 2.0 * (ROOF * 0.092903) / 3.78541
    print(f"first flush for 1,000 sq ft: clean {ff_clean:.1f} gal, dirty {ff_dirty:.1f} gal (kernel: 12.5-50)")
    res = {}
    for cap in (55, 200, 500):
        net_total = caught = 0.0
        for count, inch in STORMS:
            gross = ROOF * inch * factor
            net = max(gross * 0.9 - 12.5, 0.0)
            net_total += count * net
            caught += count * min(net, cap)
        res[cap] = caught / net_total
        print(f"barrel {cap:3d} gal: catches {res[cap]:.1%} of net annual runoff ({net_total:.0f} gal)")
    hours = 55 / (10 * 1.0)
    garden_lo, garden_hi = ROOF / 8, ROOF / 6
    print(f"one full 55 gal barrel runs 10 x 1 gph emitters for {hours:.1f} h; rain garden for the overflow "
          f"{garden_lo:.0f}-{garden_hi:.0f} sq ft (area/8 sandy to /6 clay)")
    checks = [
        ("0.623 reproduces within 0.001", abs(factor - 0.623) < 0.001),
        ("first-flush range matches the kernel's 12.5-50 gal within 1 gal",
         abs(ff_clean - 12.5) < 1 and abs(ff_dirty - 50) < 1.5),
        ("a 55 gal barrel catches under 15% of net runoff", res[55] < 0.15),
        ("a 500 gal tank catches under 60%", res[500] < 0.60),
        ("a full 55 gal barrel runs the drip bed under 6 hours", hours < 6),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; factor {factor:.4f}; first flush "
          f"{ff_clean:.1f}/{ff_dirty:.1f} gal; caught 55 {res[55]:.1%} 200 {res[200]:.1%} 500 {res[500]:.1%}; drip {hours:.1f} h")


if __name__ == "__main__":
    main()
