"""Sandbox: localization expansion budgets written in CHARACTERS vs pixel fit.

Composes two lessons:
 - localization-expansion/E1: German UI labels run -28%..+98% wider; measure real strings.
 - typography-measure/E1: width from average char width is wrong per string, because
   proportional glyph widths differ ~4x (i vs W).
Common practice expresses the expansion budget in characters: a translator max-length
of ceil(1.3 * len(EN)), or pseudo-localization that pads the English with +30% characters.
Question: does a character budget agree with a pixel budget of 1.3 x the English width?

Widths: Helvetica AFM advance widths (1/1000 em), which Arial / Liberation Sans match
metrically. Cross-check against the measured value in localization-expansion/E1:
'Einstellungen' at 16px measured 96.07 px in real Chromium.
Pure stdlib, deterministic.
"""
import math

W = dict(zip("abcdefghijklmnopqrstuvwxyz",
             [556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500]))
W.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
             [667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611]))
W.update({"ä": 556, "ö": 556, "ü": 556, "Ä": 667, "Ö": 778, "Ü": 722, "ß": 611,
          " ": 278, "!": 278, "~": 584, "[": 278, "]": 278, "-": 333})

def px(s, size=16, mono=False):
    return sum((600 if mono else W[c]) for c in s) * size / 1000

PAIRS = [("Settings", "Einstellungen"), ("Save", "Speichern"), ("Cancel", "Abbrechen"),
         ("Back", "Zurück"), ("Continue", "Weiter"), ("Delete", "Löschen"),
         ("Language", "Sprache"), ("Search", "Suchen"), ("Open", "Öffnen"),
         ("Close", "Schließen"), ("Print", "Drucken"), ("Help", "Hilfe"),
         ("Edit", "Bearbeiten"), ("View", "Ansicht"), ("Share", "Teilen"),
         ("Download", "Herunterladen"), ("Sign in", "Anmelden"), ("Log out", "Abmelden"),
         ("Next", "Weiter"), ("Undo", "Rückgängig"), ("Options", "Optionen"),
         ("Account", "Konto"), ("Send", "Senden"), ("Apply", "Anwenden"), ("Retry", "Wiederholen")]

def compare(mono=False, factor=1.3, integer=False):
    """Char budget: len(DE) <= factor*len(EN) (exact ratio) or <= ceil(factor*len(EN)) (the integer
    max-length a translator is given). Pixel truth: px(DE) <= factor*px(EN)."""
    fp, fr, rows = [], [], []
    for en, de in PAIRS:
        lim = math.ceil(factor * len(en)) if integer else factor * len(en)
        char_ok = len(de) <= lim
        px_ok = px(de, mono=mono) <= factor * px(en, mono=mono)
        if char_ok and not px_ok: fp.append(de)
        if px_ok and not char_ok: fr.append(de)
        rows.append((en, de, char_ok, px_ok))
    return fp, fr, rows

anchor = px("Einstellungen")
print(f"anchor: 'Einstellungen' 16px = {anchor:.2f} px (Chromium measured 96.07)")

de_px = [(px(d) / px(e) - 1) * 100 for e, d in PAIRS]
de_ch = [(len(d) / len(e) - 1) * 100 for e, d in PAIRS]
print(f"German growth: chars mean {sum(de_ch)/len(de_ch):+.1f}%  pixels mean {sum(de_px)/len(de_px):+.1f}%  "
      f"(px range {min(de_px):+.0f}..{max(de_px):+.0f}%)")

fp, fr, rows = compare()
print(f"S1 proportional font, exact 1.3x char ratio vs 1.3x px: false passes {len(fp)} {fp}; false rejects {len(fr)} {fr}")
fpi, fri, _ = compare(integer=True)
print(f"S1b integer max-length ceil(1.3*len): false passes {len(fpi)} {fpi}; false rejects {len(fri)} {fri}")

# S2 pseudo-localization: pad EN with +30% chars of a filler, see how much width it adds
def pseudo(en, filler):
    n = math.ceil(0.3 * len(en))
    return "[" + en + filler * n + "]"
de_over = [d for e, d in PAIRS if px(d) > 1.3 * px(e)]
for filler in ("!", "~", "W"):
    grow = [(px(pseudo(e, filler)) / px(e) - 1) * 100 for e, _ in PAIRS]
    pseudo_over = [e for e, _ in PAIRS if px(pseudo(e, filler)) > 1.3 * px(e)]
    # labels German overflows at EN+30% px that the pseudo string did NOT flag
    missed = [d for e, d in PAIRS if px(d) > 1.3 * px(e) and px(pseudo(e, filler)) <= 1.3 * px(e)]
    print(f"S2 pseudo-loc filler '{filler}': mean px growth {sum(grow)/len(grow):+.1f}%  flags {len(pseudo_over)}/25  "
          f"German overflows {len(de_over)}/25, missed by pseudo {len(missed)}")
    if filler == "!": bang_grow, bang_missed = sum(grow) / len(grow), len(missed)
    if filler == "~": tilde_grow = sum(grow) / len(grow)

# S2b (added after first run) long English strings: '!' padding without the fixed bracket overhead
LONG = ["Your changes have been saved", "Unable to connect to the server", "Remember me on this device"]
W.update({"'": 191})
long_grow = [(px(e + "!" * math.ceil(0.3 * len(e))) / px(e) - 1) * 100 for e in LONG]
print(f"S2b long strings, '!' x30% chars no brackets: px growth {[round(g,1) for g in long_grow]}")

# S3 BREAK: monospace font -> char budget and px budget must agree exactly
fpm, frm, _ = compare(mono=True)
print(f"S3 BREAK monospace: false passes {len(fpm)}, false rejects {len(frm)}")

# S4 the size of the mismatch: same character count, different pixels
same = [(a, b, px(a), px(b)) for a in ("Illinois", "Wiederholen") for b in ("Download", "Herunterladen") if len(a) == len(b)]
print(f"S4 equal-length pairs: {[(a, b, round(pa,1), round(pb,1)) for a,b,pa,pb in same]}")
print(f"S4 'Hilfe' {px('Hilfe'):.1f}px vs 'Konto' {px('Konto'):.1f}px (both 5 chars)")

checks = {
    "anchor within 0.2 px of 96.07": abs(anchor - 96.07) < 0.2,
    "P1 char budget >=2 false passes": len(fp) >= 2,
    "P1 char budget >=2 false rejects": len(fr) >= 2,
    "P1b (added after run 1) integer limit adds false passes": len(fpi) > len(fp),
    "P2 '!' pseudo-loc px growth < 20%": bang_grow < 20,
    "P2 '!' pseudo-loc misses >=1 German overflow": bang_missed >= 1,
    "P3 monospace 0 disagreements": len(fpm) == 0 and len(frm) == 0,
}
for k, v in checks.items():
    print(f"  {'ok ' if v else 'MISS'} {k}")
print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} 1.3x char ratio vs 1.3x px: {len(fp)} false passes, "
      f"{len(fr)} false rejects of 25 DE labels (integer ceil limit: {len(fpi)} false passes); bracketed '!' pseudo-loc +30% chars grows {bang_grow:.1f}% px and misses "
      f"{bang_missed}/{len(de_over)} German overflows; '~' grows {tilde_grow:.1f}%; long-string '!' growth {min(long_grow):.1f}-{max(long_grow):.1f}%; monospace {len(fpm)}/{len(frm)}")
