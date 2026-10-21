"""Sandbox (train edge): sandbox-weather-vfx/E1 (canvas beats one DOM node per
particle above ~150 particles; recorded mean ms per frame) x sandbox-edges/E7
(canvas contexts are capped and the OLDEST is evicted silently; a mis-sized canvas
stays alive but renders small). Model, no RNG, no real timing: a weather effect
of L layers (rain, snow, fog, lightning, dust...), each with n particles.
Per-frame cost uses E1's RECORDED means (not re-measured here): canvas 0.069 ms
at 150 particles, 0.23 ms at 1200; DOM 1.39 ms at 150, 3.02 ms at 1200
(linear interpolation between). Context cap C=3 as in E7's model.
Layouts: PER_LAYER canvas, ONE shared canvas, and the naive 'fix' PER_LAYER+DOM
fallback for layers beyond the cap.
PREDICTION (before run): with L=5, C=3 PER_LAYER leaves 2 layers black (the
oldest two) while its summed cost looks cheapest; ONE canvas keeps 5/5 live at
about the same total ms; the DOM fallback keeps 5/5 live but costs several times
more at n=1200. BREAK: L<=C makes all layouts live, so the lesson is conditional
on layers exceeding the cap."""
CAP = 3
PTS = [(150, 0.069, 1.39), (1200, 0.23, 3.02)]

def cost(kind, n):
    (n0, c0, d0), (n1, c1, d1) = PTS
    t = (n - n0) / (n1 - n0)
    return (c0 + (c1 - c0) * t) if kind == "canvas" else (d0 + (d1 - d0) * t)

def mount(layers, layout, cap=CAP):
    live, order, ms = {}, [], 0.0
    if layout == "one":
        live = {i: True for i in range(len(layers))}
        return live, sum(cost("canvas", n) for n in layers)
    for i, n in enumerate(layers):
        order.append(i)
        live[i] = "canvas"
        if len(order) > cap:                      # oldest context evicted silently
            live[order.pop(0)] = None
    ms = 0.0
    for i, n in enumerate(layers):
        if live[i] == "canvas":
            ms += cost("canvas", n)
        elif layout == "dom":
            live[i] = "dom"; ms += cost("dom", n)
    return {i: bool(v) for i, v in live.items()}, ms

def report(L, n):
    layers = [n] * L
    out = {}
    for lay in ("per", "one", "dom"):
        live, ms = mount(layers, "dom" if lay == "dom" else lay)
        out[lay] = (sum(live.values()), ms)
    return out

for L, n in [(5, 1200), (5, 150), (3, 1200), (2, 300)]:
    r = report(L, n)
    print(f"L={L} n={n}: " + "  ".join(f"{k}: live {v[0]}/{L} {v[1]:.2f}ms" for k, v in r.items()))

a = report(5, 1200); b = report(3, 1200); c = report(5, 150)
ok = (a["per"][0] == 3 and a["one"][0] == 5 and abs(a["one"][1] - 5 * cost("canvas", 1200)) < 1e-9
      and a["dom"][0] == 5 and a["dom"][1] > 2 * a["one"][1]
      and b["per"][0] == 3 and b["dom"][0] == 3 and abs(b["per"][1] - b["one"][1]) < 1e-9
      and a["per"][1] < a["one"][1])
print(f"RESULT: {'PASS' if ok else 'FAIL'} L=5 cap=3: per-layer {a['per'][0]}/5 live ({a['per'][1]:.2f}ms, cheapest because 2 layers never draw); one canvas 5/5 {a['one'][1]:.2f}ms; DOM fallback 5/5 {a['dom'][1]:.2f}ms; L=3 all layouts 3/3")
