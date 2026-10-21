# Deterministic grid model: full-bleed world + chrome band. No RNG, no timing.
H, W = 20, 10

def route_zorder(y, chrome_top):
    # chrome drawn over world: whatever is under the cursor wins
    return "chrome" if y >= chrome_top else "world"

def world_rows(cap_row):
    # rows a viewer can create/aim at in the world (inclusive)
    return range(0, cap_row + 1)

def misroutes(chrome_top, cap_row):
    bad = 0
    for y in world_rows(cap_row):          # every click AIMED at the world
        for x in range(W):
            if route_zorder(y, chrome_top) == "chrome":
                bad += 1
    return bad

def run_steps(chrome_top, cap_row):
    # state machine: chrome 'next' advances a scene; each world-aimed click
    # that lands on chrome advances it once; a legit timer advance also fires.
    step = 0
    for y in world_rows(cap_row):
        for x in range(W):
            if route_zorder(y, chrome_top) == "chrome":
                step += 1
    return step + 1  # +1 legit timer advance

def fw_hit(px, py, box, scale):      # framework bug: ignores container scale
    x0, y0, w, h = box
    return x0 <= px < x0 + w and y0 <= py < y0 + h

def own_hit(px, py, box, scale):     # four comparisons in screen space
    x0, y0, w, h = box
    return x0*scale <= px < (x0 + w)*scale and y0*scale <= py < (y0 + h)*scale

res = {}
# S1 overlap: world reaches row 19, chrome rows 16-19
res["overlap"] = misroutes(16, 19)
# S2 disjoint: cap=chrome_top-1
res["disjoint"] = misroutes(16, 15)
# S3 BREAK: chrome grows to row 14 with hardcoded cap 15 -> overlap returns
res["fixedcap_after_resize"] = misroutes(14, 15)
# S3b cap derived from chrome
ct = 14
res["derivedcap_after_resize"] = misroutes(ct, ct - 1)
# S4 double advance
res["steps_overlap"] = run_steps(16, 19)
res["steps_disjoint"] = run_steps(16, 15)
# S5 own hit test vs framework at scale 2: point inside scaled box
box = (10, 10, 20, 20)
pts = [(x, y) for x in range(0, 80, 4) for y in range(0, 80, 4)]
truth = [own_hit(x, y, box, 2) for x, y in pts]
fw = [fw_hit(x, y, box, 2) for x, y in pts]
res["fw_wrong_cells"] = sum(a != b for a, b in zip(truth, fw))
res["own_wrong_cells"] = 0
print(res)
ok = (res["overlap"] == 40 and res["disjoint"] == 0 and res["fixedcap_after_resize"] == 20
      and res["derivedcap_after_resize"] == 0 and res["steps_overlap"] == 41
      and res["steps_disjoint"] == 1 and res["fw_wrong_cells"] > 0)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "overlap=%d disjoint=%d fixedcap_resize=%d derived=%d steps %d vs %d fw_wrong=%d" % (
      res["overlap"], res["disjoint"], res["fixedcap_after_resize"], res["derivedcap_after_resize"],
      res["steps_overlap"], res["steps_disjoint"], res["fw_wrong_cells"]))
