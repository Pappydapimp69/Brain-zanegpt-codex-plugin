"""Rebuild of local sandbox-localization-expansion E1 (German UI labels ~31%
wider on average, -28%..+98% per string; a button sized for English overflows;
measure real translations, a flat +30% is not safe).
NOT fully blind: I audited this entry earlier this session and saw its 8 pairs.
So my fixture avoids them: 20 OTHER common UI labels (game/menu vocabulary)
with standard German and French translations, measured with real
CanvasRenderingContext2D.measureText in headless Chromium (Playwright via
node, called from this stdlib script), 16px sans-serif. A button is sized to
the widest ENGLISH label + 12 px padding; a 'flat +30%' budget is each English
width x 1.30.
PREDICTION (written before running): German mean expansion 20-40%; range spans
below 0% to above +60%; at least 1 German label overflows the English-sized
button; at least 2 German labels exceed their own English width x 1.30; French
mean expansion is smaller than German.
"""
import json, os, subprocess, sys, tempfile, shutil
print("python", sys.version.split()[0])
PAIRS = [("New Game", "Neues Spiel", "Nouvelle partie"), ("Load", "Laden", "Charger"), ("Options", "Optionen", "Options"),
 ("Quit", "Beenden", "Quitter"), ("Resume", "Fortsetzen", "Reprendre"), ("Controls", "Steuerung", "Commandes"),
 ("Audio", "Audio", "Audio"), ("Volume", "Lautstärke", "Volume"), ("Brightness", "Helligkeit", "Luminosité"),
 ("Difficulty", "Schwierigkeitsgrad", "Difficulté"), ("Inventory", "Inventar", "Inventaire"), ("Map", "Karte", "Carte"),
 ("Help", "Hilfe", "Aide"), ("Credits", "Mitwirkende", "Crédits"), ("Yes", "Ja", "Oui"), ("No", "Nein", "Non"),
 ("Apply", "Übernehmen", "Appliquer"), ("Reset", "Zurücksetzen", "Réinitialiser"), ("Subtitles", "Untertitel", "Sous-titres"),
 ("Main Menu", "Hauptmenü", "Menu principal")]
JS = r"""
const { chromium } = require(process.env.PW);
(async () => {
  const b = await chromium.launch({ args: ['--headless=new'] });
  const p = await b.newPage();
  const r = await p.evaluate((pairs) => { const c = document.createElement('canvas').getContext('2d'); c.font = '16px sans-serif';
    return pairs.map(t => t.map(s => c.measureText(s).width)); }, JSON.parse(process.env.PAIRS));
  console.log(JSON.stringify(r)); await b.close(); })();
"""
node = shutil.which("node")
pw = None
for cand in ("/opt/node22/lib/node_modules/playwright", os.path.join(os.path.dirname(os.path.dirname(node or "/x/x")), "lib/node_modules/playwright")):
    if os.path.isdir(cand): pw = cand; break
if not (node and pw):
    print("RESULT: FAIL could not find node + playwright to measure a real browser"); sys.exit(0)
with tempfile.TemporaryDirectory() as d:
    f = os.path.join(d, "m.js"); open(f, "w").write(JS)
    out = subprocess.run([node, f], capture_output=True, text=True, timeout=60,
                         env=dict(os.environ, PW=pw, PAIRS=json.dumps(PAIRS))).stdout
W = json.loads(out.strip().splitlines()[-1])
de = [(g / e - 1) * 100 for e, g, f in W]; fr = [(f / e - 1) * 100 for e, g, f in W]
btn = max(e for e, g, f in W) + 12
over = [PAIRS[i][1] for i, (e, g, f) in enumerate(W) if g > btn]
flat = [PAIRS[i][1] for i, (e, g, f) in enumerate(W) if g > e * 1.30]
for (en, ge, fr_), (e, g, f) in zip(PAIRS, W):
    print(f"{en:11s} {e:6.1f} | {ge:18s} {g:6.1f} ({(g/e-1)*100:+6.1f}%) | {fr_:15s} {f:6.1f} ({(f/e-1)*100:+6.1f}%)")
mde, mfr = sum(de) / len(de), sum(fr) / len(fr)
print(f"German mean {mde:+.1f}% range {min(de):+.1f}..{max(de):+.1f}; French mean {mfr:+.1f}%; button {btn:.1f}px overflowed by {over}; over flat +30%: {len(flat)} {flat}")
c = [20 <= mde <= 40, min(de) < 0 and max(de) > 60, len(over) >= 1, len(flat) >= 2, mfr < mde]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/5; German mean {mde:+.1f}% ({min(de):+.0f}..{max(de):+.0f}); French {mfr:+.1f}%; English-sized button overflowed by {len(over)} German labels; {len(flat)} exceed a flat +30%")
