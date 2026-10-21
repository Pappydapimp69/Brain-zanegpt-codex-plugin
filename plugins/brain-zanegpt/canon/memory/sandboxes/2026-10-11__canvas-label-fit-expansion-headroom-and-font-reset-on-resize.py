"""Deterministic model composing sandbox-localization-expansion/E1 (German labels
run wider than English, fixed-width boxes overflow) with sandbox-edges/E? canvas
size lesson (canvas default 300x150 / size set after the fact).
Glyph widths: Arial-like per-char em widths (approximation, assumed). A Canvas
model resets font to 10px sans-serif when width/height is assigned (real browser
rule: assigning width/height resets context state). Label fits if measured
width <= box width - 2*PAD."""
W = {c: 0.5 for c in "abcdefghijklmnopqrstuvwxyzäöüß"}
W.update({c: 0.28 for c in "ilj.t f"}); W.update({c: 0.28 for c in "ilj.tf "})
W.update({c: 0.83 for c in "mw"}); W.update({c: 0.72 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})
W.update({c: 0.28 for c in "I"})
def width(s, px): return sum(W.get(c, 0.55) for c in s) * px
PAIRS = [("Settings","Einstellungen"),("Save","Speichern"),("Cancel","Abbrechen"),
         ("Back","Zurück"),("Continue","Weiter"),("Delete","Löschen"),
         ("Language","Sprache"),("Search","Suchen")]
PAD = 8
class Canvas:
    def __init__(s): s.width, s.font_px = 300, 10
    def set_width(s, w): s.width, s.font_px = w, 10      # state reset
    def set_font(s, px): s.font_px = px
    def measure(s, t): return width(t, s.font_px)
def fits(box, label, px=16): return width(label, px) <= box - 2*PAD
res = {}
en_max = max(width(e,16) for e,_ in PAIRS)
# S1 box sized to longest English label + pad
box_en = round(en_max) + 2*PAD
res["S1 overflow_de_at_en_box"] = sum(not fits(box_en, d) for _, d in PAIRS)
res["S1 overflow_en_at_en_box"] = sum(not fits(box_en, e) for e, _ in PAIRS)
# S2 headroom factors over the English box (built to find the knee)
de_need = max(width(d,16) for _, d in PAIRS) + 2*PAD
knee = next(f for f in [x/100 for x in range(100, 200)] if round(box_en*f) >= de_need)
res["S2 knee_factor"] = knee
res["S2 overflow_de_at_30pct"] = sum(not fits(round(box_en*1.30), d) for _, d in PAIRS)
res["S2 overflow_de_at_knee"] = sum(not fits(round(box_en*knee), d) for _, d in PAIRS)
# S3 measure-before-resize vs after: font reset makes fit check pass wrongly
def check(order):
    c = Canvas(); bad = 0
    if order == "font_then_width":
        c.set_font(16); c.set_width(box_en)   # reset -> measured at 10px
    else:
        c.set_width(box_en); c.set_font(16)
    for _, d in PAIRS:
        if c.measure(d) <= box_en - 2*PAD and not fits(box_en, d): bad += 1  # false pass
    return bad
res["S3 false_pass_font_then_width"] = check("font_then_width")
res["S3 false_pass_width_then_font"] = check("width_then_font")
for k, v in res.items(): print(f"{k}: {v}")
ok = (res["S1 overflow_de_at_en_box"] >= 1 and res["S1 overflow_en_at_en_box"] == 0
      and res["S2 overflow_de_at_30pct"] >= 1 and res["S2 overflow_de_at_knee"] == 0
      and res["S3 false_pass_font_then_width"] >= 1 and res["S3 false_pass_width_then_font"] == 0)
print("RESULT:", "PASS" if ok else "FAIL",
      f"EN box {box_en}px overflows {res['S1 overflow_de_at_en_box']} DE labels; flat +30% still {res['S2 overflow_de_at_30pct']}; knee x{knee}; "
      f"font-reset false passes {res['S3 false_pass_font_then_width']} vs {res['S3 false_pass_width_then_font']}")
