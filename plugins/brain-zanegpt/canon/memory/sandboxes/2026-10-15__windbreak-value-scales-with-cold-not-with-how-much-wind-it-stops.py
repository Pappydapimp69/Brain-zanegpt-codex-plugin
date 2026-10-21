"""Gap (brain query hypothermia: 0 records). SEVEN's night 'takes the exposed
first'. Real source: the US National Weather Service / Environment Canada wind
chill formula (2001, JAG/TI):
  WCT(F) = 35.74 + 0.6215 T - 35.75 V^0.16 + 0.4275 T V^0.16, T in F, V in mph,
valid for T <= 50 F and V >= 3 mph (calm counts as V = 3).
Question for a game's shelter mechanic: where does cutting wind buy the most?
Exact arithmetic, no rng.
PREDICTION (written before running): because V^0.16 is steep near zero, a
windbreak that takes 15 mph to calm (3) gains more felt warmth (> 10 F at
T = 20 F) than one that takes a 40 mph gale down to 15 (< 8 F); halving the
wind from 30 to 15 gains under 6 F; so shelter should be modeled as
near-all-or-nothing - a partial windbreak in strong wind barely helps. Break
case: at T = 50 F the formula still says calm vs 15 mph matters by < 5 F, so
wind only matters much when it is cold.
"""
import sys
print("python", sys.version.split()[0])
def wct(T, V):
    V = max(V, 3.0)
    return 35.74 + 0.6215 * T - 35.75 * V ** 0.16 + 0.4275 * T * V ** 0.16
rows = {}
for T in (50, 32, 20, 0, -10):
    rows[T] = {
        "15->calm": wct(T, 3) - wct(T, 15), "40->15": wct(T, 15) - wct(T, 40),
        "30->15": wct(T, 15) - wct(T, 30), "6->3": wct(T, 3) - wct(T, 6)}
    print(f"T {T:4d} F: WCT at 3/15/30/40 mph = {wct(T,3):6.1f} {wct(T,15):6.1f} {wct(T,30):6.1f} {wct(T,40):6.1f};  gain 15->calm {rows[T]['15->calm']:5.1f}, 40->15 {rows[T]['40->15']:5.1f}, 30->15 {rows[T]['30->15']:5.1f}, 6->3 {rows[T]['6->3']:4.1f}")
r20 = rows[20]
c = [r20["15->calm"] > 10, r20["40->15"] < 8, r20["30->15"] < 6, rows[50]["15->calm"] < 5]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; at 20 F calm vs 15 mph +{r20['15->calm']:.1f} F, 40->15 +{r20['40->15']:.1f}, 30->15 +{r20['30->15']:.1f}; at 50 F 15->calm +{rows[50]['15->calm']:.1f}; at -10 F 15->calm +{rows[-10]['15->calm']:.1f}")
