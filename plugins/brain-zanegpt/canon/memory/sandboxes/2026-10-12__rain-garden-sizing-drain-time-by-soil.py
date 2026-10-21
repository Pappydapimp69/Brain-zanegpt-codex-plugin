# Deterministic sandbox: rain garden sized roof/6 (clay) or roof/8 (sand), 6in ponding depth.
# Does a sink sized by the kernel's divisor drain a design storm within 48h?
# Constants are assumed, illustrative (infiltration in/h): sand 2.0, loam 0.5, clay 0.1 (compacted 0.03).
INF = {"sand": 2.0, "loam": 0.5, "clay": 0.1, "compacted_clay": 0.03}
DIV = {"sand": 8, "loam": 7, "clay": 6, "compacted_clay": 6}
ROOF = 1000.0  # sq ft
POND = 6.0     # in max ponding depth
def run(soil, storm_in, mulch=False, divisor=None, barrel_gal=0.0):
    area = ROOF / (divisor or DIV[soil])
    # runoff volume in cubic ft over garden area-equivalent depth (inches over garden)
    roof_gal = ROOF * storm_in * 0.623 - barrel_gal
    roof_gal = max(roof_gal, 0)
    in_depth = roof_gal / 0.623 / area  # inches over garden
    ponded = min(in_depth, POND)
    overflow_in = in_depth - ponded
    rate = INF[soil] * (1.0 if not mulch else 1.0)  # mulch does not change basin infiltration here
    hours = ponded / rate
    return area, in_depth, hours, overflow_in * area * 0.623 / 0.623 * 0.623
print("PREDICTION: roof/6 clay and roof/8 sand drain a 1in storm in <48h; clay roof/6 with 3in storm overflows; compacted clay fails even at 1in; barrel 55gal changes depth <0.1in")
res = {}
for soil in INF:
    for storm in (1.0, 3.0):
        a, d, h, o = run(soil, storm)
        res[(soil, storm)] = h
        print(f"{soil:15s} storm={storm}in area={a:6.1f}sqft depth={d:5.2f}in drain={h:7.1f}h overflow_gal={o:7.1f}")
a, d0, h0, _ = run("clay", 1.0)
a, d1, h1, _ = run("clay", 1.0, barrel_gal=55)
print(f"barrel 55gal depth change = {d0-d1:.3f}in")
# BREAK case: apply the sand divisor (8) to clay
a, d, h, o = run("clay", 1.0, divisor=8)
print(f"BREAK clay with /8: area={a:.1f} depth={d:.2f}in drain={h:.1f}h")
ok = (res[("clay",1.0)] < 48 and res[("sand",1.0)] < 48 and res[("clay",3.0)] > 48
      and res[("compacted_clay",1.0)] > 48 and (d0-d1) < 0.1 and h > res[("clay",1.0)])
print("RESULT: " + ("PASS" if ok else "FAIL") + f" clay/6 1in={res[('clay',1.0)]:.1f}h 3in={res[('clay',3.0)]:.1f}h sand/8 1in={res[('sand',1.0)]:.1f}h compacted 1in={res[('compacted_clay',1.0)]:.1f}h barrel55={d0-d1:.3f}in clay/8={h:.1f}h")
