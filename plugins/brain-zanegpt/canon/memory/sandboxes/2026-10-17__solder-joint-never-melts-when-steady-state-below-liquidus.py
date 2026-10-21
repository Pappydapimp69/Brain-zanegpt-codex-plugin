# Lumped joint: C dT/dt = Gt (Ttip - T) + Gb (Tamb - T). Steady state T* = (Gt Ttip + Gb Tamb)/(Gt+Gb).
# SAC305 liquidus ~ 217 C. Prediction (before run): small pad (Gb=0.1 W/K) melts in ~1 s at 350 C tip;
# ground-plane pad (Gb=0.5) has T*=187.5 C < 217 so it NEVER melts at any dwell, and raising dwell from 3 s to 30 s changes nothing;
# preheating the board to 100 C lifts T* to 225 and melts in <5 s (break case: preheat alone, tip unchanged).
import math
Gt, C, TM = 0.5, 0.3, 217.0
def tss(Gb, Ttip, Tamb): return (Gt*Ttip + Gb*Tamb)/(Gt+Gb)
def t_melt(Gb, Ttip, Tamb):
    ts = tss(Gb, Ttip, Tamb)
    if ts <= TM: return None
    tau = C/(Gt+Gb)
    return -tau*math.log(1-(TM-Tamb)/(ts-Tamb)) if False else -tau*math.log((ts-TM)/(ts-Tamb))
rows = {}
for name, Gb, Ttip, Tamb in [("small pad",0.1,350,25),("ground plane",0.5,350,25),("ground plane hot tip 400",0.5,400,25),("ground plane preheat 100",0.5,350,100)]:
    rows[name] = (round(tss(Gb,Ttip,Tamb),1), t_melt(Gb,Ttip,Tamb))
    print(name, "steady state", rows[name][0], "C; time to melt", None if rows[name][1] is None else round(rows[name][1],2), "s")
ok = (rows["small pad"][1] is not None and rows["small pad"][1] < 1.5
      and rows["ground plane"][1] is None and rows["ground plane hot tip 400"][1] is None
      and rows["ground plane preheat 100"][1] is not None and rows["ground plane preheat 100"][1] < 5)
print("RESULT: %s small pad melts %.2f s; ground plane steady %.1f C never melts (400 C tip %.1f C); preheat melts %.2f s" % (
 "PASS" if ok else "FAIL", rows["small pad"][1], rows["ground plane"][0], rows["ground plane hot tip 400"][0], rows["ground plane preheat 100"][1] or -1))
