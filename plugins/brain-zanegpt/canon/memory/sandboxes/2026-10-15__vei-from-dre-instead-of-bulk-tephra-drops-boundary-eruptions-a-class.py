# Sandbox: Volcanic Explosivity Index (Newhall & Self 1982) is binned on BULK tephra
# volume; dense-rock-equivalent (DRE) volume is 2-4x smaller. Feeding DRE into the VEI
# table drops eruptions sitting within that factor above a decade boundary by one class.
# The mass-based magnitude scale (Pyle: M = log10(mass kg) - 7) is insensitive to the
# bulk-vs-DRE choice as long as the matching density is used.
# Eruption volumes are values recalled from memory (not fetched in this session).
import math

def vei(bulk_m3):
    # VEI 0 <1e4; 1: 1e4-1e6; 2: 1e6-1e7; then one class per decade to VEI 8 at >=1e12
    if bulk_m3 < 1e4: return 0
    if bulk_m3 < 1e6: return 1
    return min(8, 2 + int(math.floor(math.log10(bulk_m3) - 6 + 1e-12)))

def magnitude(mass_kg):
    return math.log10(mass_kg) - 7

KM3 = 1e9
RHO_DEPOSIT, RHO_MAGMA = 1000.0, 2500.0   # typical bulk fall deposit vs magma (assumed)
# name: (bulk km3, DRE km3, listed VEI)
ERUPTIONS = {
    "Mount St. Helens 1980": (1.1, 0.25, 5),
    "Pinatubo 1991 (high bulk est.)": (10.4, 5.3, 6),
    "Pinatubo 1991 (low bulk est.)": (8.4, 3.7, 6),
    "Tambora 1815": (150.0, 30.0, 7),
    "Krakatau 1883": (20.0, 10.0, 6),
    "Eyjafjallajokull 2010": (0.27, 0.12, 4),
}

# Table sanity: boundaries
assert [vei(v) for v in (9e3, 1e4, 9.9e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12, 1e13)] == [0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8]

bulk_match = 0; dre_drops = []; m_gaps = []; listed_n = 0
for name, (bulk, dre, listed) in ERUPTIONS.items():
    vb, vd = vei(bulk * KM3), vei(dre * KM3)
    mb, md = magnitude(bulk * KM3 * RHO_DEPOSIT), magnitude(dre * KM3 * RHO_MAGMA)
    m_gaps.append(abs(mb - md))
    if "low bulk" not in name:
        listed_n += 1; bulk_match += vb == listed
        if vd < vb: dre_drops.append(name)
    print("%-32s bulk %7.2f km3 -> VEI %d | DRE %6.2f km3 -> VEI %d | listed %d | M bulk %.2f DRE %.2f"
          % (name, bulk, vb, dre, vd, listed, mb, md))

# Population view: log-uniform eruptions 1e6..1e12 m3, DRE = bulk / f
def shifted_fraction(f, lo=6.0, hi=12.0, n=60000):
    k = 0
    for i in range(n):
        b = 10 ** (lo + (hi - lo) * (i + 0.5) / n)
        k += vei(b / f) != vei(b)
    return k / n
fracs = {f: shifted_fraction(f) for f in (2.0, 2.5, 4.0)}
print("log-uniform 1e6..1e12 m3, fraction whose VEI changes when DRE (bulk/f) is used:",
      {f: round(v, 3) for f, v in fracs.items()})

# BREAK case 1: the 'one step = 10x' reading of VEI. VEI 1 spans two decades.
span_v1 = math.log10(1e6 / 1e4)
print("VEI 1 spans %.0f decades of volume; a 1e4 m3 and a 9.9e5 m3 eruption are both VEI 1 (ratio %.0fx)"
      % (span_v1, 9.9e5 / 1e4))
# BREAK case 2: Pinatubo's own listed class depends on which bulk estimate is used
pin_low = vei(8.4 * KM3); pin_high = vei(10.4 * KM3)
print("Pinatubo bulk estimate 8.4 km3 -> VEI %d, 10.4 km3 -> VEI %d" % (pin_low, pin_high))

ok = (bulk_match == listed_n and len(dre_drops) == 3 and max(m_gaps) < 0.3
      and abs(fracs[2.5] - math.log10(2.5)) < 0.01)
print("RESULT: %s bulk volume reproduces listed VEI %d/%d; DRE drops %d (%s); magnitude bulk-vs-DRE gap max %.2f; log-uniform fraction shifted by DRE at f=2.5: %.3f; Pinatubo low/high bulk VEI %d/%d"
      % ("PASS" if ok else "FAIL", bulk_match, listed_n, len(dre_drops), ", ".join(dre_drops), max(m_gaps), fracs[2.5], pin_low, pin_high))
