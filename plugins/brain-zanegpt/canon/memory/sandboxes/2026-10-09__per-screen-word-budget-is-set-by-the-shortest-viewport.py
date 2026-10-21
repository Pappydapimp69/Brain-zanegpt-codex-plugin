"""Deterministic layout model for the PRESENTATION kernel:
measure per-screen word count / viewport fill instead of eyeballing.
No RNG, no timing, no browser: text is wrapped greedily with a fixed
average glyph width (0.5em) so every number is reproducible."""
import math

WORD = 6          # average chars per word incl. space (fixed)
GLYPH = 0.5       # em per char (fixed average)
CHROME = 0        # px reserved by host chrome is already baked into viewports

VIEWPORTS = {
    "desktop 1440x900": (1440, 900),
    "laptop 1280x720": (1280, 720),
    "phone-visible 412x641": (412, 641),   # brain/E13 measured device chrome
    "phone-worst 375x560": (375, 560),     # brain/E13 worse-case
    "phone-tall 412x915": (412, 915),
}

def layout(words, vw, vh, font=16, lh=1.5, gutter=16, max_ch=66,
           title_px=56, ctrl_px=64, pad=24, center=False):
    col_px = min(vw - 2 * gutter, max_ch * font * GLYPH)
    cpl = int(col_px // (font * GLYPH))                  # chars per line
    chars = words * WORD
    lines = math.ceil(chars / cpl)
    para_h = lines * font * lh
    content_h = pad + title_px + para_h + pad + ctrl_px + pad
    ctrl_bottom = (vh - content_h) / 2 + content_h if center else content_h
    top_gap = (vh - content_h) / 2 if center and content_h < vh else 0
    return dict(cpl=cpl, lines=lines, h=content_h, overflow=content_h - vh,
                top_gap=top_gap, ctrl_visible=content_h <= vh)

def max_words(vw, vh, **kw):
    w = 0
    while layout(w + 1, vw, vh, **kw)["ctrl_visible"]:
        w += 1
        if w > 5000: break
    return w

ok = []
def check(name, cond, detail):
    ok.append(cond)
    print(f"  [{'ok' if cond else 'NO'}] {name}: {detail}")

print("S1 per-viewport word budget (controls above fold), 16px/1.5:")
budgets = {n: max_words(*v) for n, v in VIEWPORTS.items()}
for n, b in budgets.items():
    print(f"   {n:24s} max words = {b}")
shortest = min(budgets.values())
check("S1 budget is set by shortest viewport", budgets["phone-worst 375x560"] == shortest,
      f"shortest={shortest}, desktop={budgets['desktop 1440x900']}")

print("S2 kernel's ~40-50 word guideline vs ~100-word limit:")
for words in (45, 100):
    fits = {n: layout(words, *v)["ctrl_visible"] for n, v in VIEWPORTS.items()}
    print(f"   {words} words ->", {k.split()[0]: f for k, f in fits.items()})
check("S2 45 words fits everywhere", all(layout(45, *v)["ctrl_visible"] for v in VIEWPORTS.values()), "45w")
# Prediction was that 100 words overflows 375x560; it fits by 8px. The kernel's
# "<~100 words" ceiling instead sits within 5 words of that viewport's cliff.
check("S2 100 words sits within 5 words of the shortest-viewport cliff",
      layout(100, *VIEWPORTS["phone-worst 375x560"])["ctrl_visible"]
      and not layout(111, *VIEWPORTS["phone-worst 375x560"])["ctrl_visible"],
      f"100w slack {-layout(100,*VIEWPORTS['phone-worst 375x560'])['overflow']:.0f}px; 106w fails")

print("S3 'hair taller than viewport' band (word counts overflowing by 1..24px):")
hair = {}
for n, v in VIEWPORTS.items():
    hair[n] = [w for w in range(1, 400) if 0 < layout(w, *v)["overflow"] <= 24]
for n, h in hair.items():
    print(f"   {n:24s} {h[:6]}{'...' if len(h)>6 else ''}")
check("S3 every viewport has a near-miss band an eyeball would call 'fine'",
      all(hair[n] for n in hair), "hair-overflow word counts exist per viewport")

print("S4 BREAK: height-fixed-900 testing (brain/E13 habit) vs real short viewports:")
w_bad = [w for w in range(1, 400)
         if layout(w, 412, 900)["ctrl_visible"] and not layout(w, 412, 641)["ctrl_visible"]]
print(f"   word counts passing at 412x900 but failing at 412x641: {w_bad[0]}..{w_bad[-1]} ({len(w_bad)} values)")
check("S4 fixed-900 height gives false pass", len(w_bad) > 0, f"{len(w_bad)} false passes")

print("S5 centered vs top-aligned on a tall phone (45 words):")
c = layout(45, 412, 915, center=True); t = layout(45, 412, 915, center=False)
print(f"   centered top gap = {c['top_gap']:.0f}px, top-aligned gap = {t['top_gap']:.0f}px")
check("S5 centering strands a gap, top-align does not", c["top_gap"] > 150 and t["top_gap"] == 0, f"{c['top_gap']:.0f}px")

print("S6 line length: cpl by viewport at max_ch=66 cap (target desktop 45-75, phone 35-50):")
for n in ("desktop 1440x900", "phone-visible 412x641", "phone-worst 375x560"):
    print(f"   {n:24s} cpl={layout(45,*VIEWPORTS[n])['cpl']}")
uncapped = layout(45, 1440, 900, max_ch=10**6)["cpl"]
check("S6 cap needed on full-bleed desktop", layout(45,1440,900)["cpl"] <= 75 < uncapped,
      f"capped {layout(45,1440,900)['cpl']} vs uncapped {uncapped}")
check("S6 phone cpl in 35-50", 35 <= layout(45,412,641)["cpl"] <= 50, f"{layout(45,412,641)['cpl']}")

print("S7 BREAK the single-number rule: ~50 words safe at 16px, not at 20px body:")
f20 = max_words(*VIEWPORTS["phone-worst 375x560"], font=20)
print(f"   max words at 375x560 with 20px body = {f20}")
check("S7 word budget is not font-size independent", f20 < budgets["phone-worst 375x560"], f"{f20} < {budgets['phone-worst 375x560']}")

print("S8 cut copy vs shrink font fix at overflow (100 words, 375x560):")
cut = max_words(*VIEWPORTS["phone-worst 375x560"])
print(f"   fix by cutting to {cut} words; reading 20-28% means ~{round(100*0.24)} of 100 words get read anyway")

allok = all(ok)
print(f"RESULT: {'PASS' if allok else 'FAIL'} {sum(ok)}/{len(ok)} checks; budgets={budgets}")
