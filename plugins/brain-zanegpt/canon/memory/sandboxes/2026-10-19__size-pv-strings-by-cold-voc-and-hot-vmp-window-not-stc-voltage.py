"""Sandbox: PV string length window (stdlib, deterministic). Module Voc/Vmp at STC with %/degC coefficients.
Cold-morning open-circuit voltage must stay under the inverter max; hot-afternoon Vmp must stay above the MPPT floor."""
VOC, VMP = 41.5, 34.0           # volts at 25 C cell temperature
B_VOC, B_VMP = -0.0027, -0.0035 # per degC (typical mono-Si datasheet values)
INV_MAX, MPPT_MIN = 600.0, 250.0
T_MIN, T_HOT_CELL = -20.0, 70.0  # record low ambient; cell temp on a hot day
def voc(t): return VOC*(1+B_VOC*(t-25))
def vmp(t): return VMP*(1+B_VMP*(t-25))
def window():
    ok=[n for n in range(1,40) if n*voc(T_MIN)<=INV_MAX and n*vmp(T_HOT_CELL)>=MPPT_MIN]
    return ok
stc_max = int(INV_MAX//VOC)       # naive: size on the STC label
cold_max = int(INV_MAX//voc(T_MIN))
w = window()
# year of daily minimum ambient: deterministic sinusoid, mean 5C, amplitude 25C, 365 days, coldest dawn at day 0
import math
mins=[5-25*math.cos(2*math.pi*d/365) for d in range(365)]   # -20 C on day 0, +30 C mid-year
def over_days(n): return sum(1 for m in mins if n*voc(m)>INV_MAX)
print(f"STC label size: {stc_max} modules = {stc_max*VOC:.0f} V; cold Voc/module {voc(T_MIN):.2f} V -> cold max {cold_max}")
print(f"string at STC size on the -20C morning: {stc_max*voc(T_MIN):.0f} V vs limit {INV_MAX:.0f}; days over limit in the year: {over_days(stc_max)}; at cold size: {over_days(cold_max)}")
print(f"valid window of string lengths (cold Voc and hot Vmp): {w[0]}..{w[-1]} (width {len(w)})")
# milder site: T_MIN +5 -> window widens
T_MIN2=5.0
w2=[n for n in range(1,40) if n*voc(T_MIN2)<=INV_MAX and n*vmp(T_HOT_CELL)>=MPPT_MIN]
# break case: hot cell 85 C with a low MPPT floor 300 V shrinks window
w3=[n for n in range(1,40) if n*voc(T_MIN)<=INV_MAX and n*(VMP*(1+B_VMP*(85-25)))>=300]
print(f"mild site low +5C window {w2[0]}..{w2[-1]}; hot 85C cell / 300 V floor window: {(str(w3[0])+'..'+str(w3[-1])) if w3 else 'EMPTY'}")
ok = stc_max==14 and cold_max==12 and stc_max*voc(T_MIN)>INV_MAX and over_days(stc_max)>0 and over_days(cold_max)==0 and w[-1]==cold_max and w2[-1]>cold_max and (not w3 or len(w3)<len(w))
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" STC size {stc_max} reads {stc_max*voc(T_MIN):.0f} V cold vs {INV_MAX:.0f} limit; cold-sized {cold_max}; window {w[0]}..{w[-1]}; mild site max {w2[-1]}; hot/300V window {len(w3)} wide")
