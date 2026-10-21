#!/usr/bin/env python3
"""Sandbox: does an English->Spanish ad line fit the same clip? Deterministic, stdlib only.

PREDICTION (written before first run):
  Core corpus = 12 lines (4 clips of 4 s, 4 of 6 s, 4 of 8 s), each EN with a transcreated ES.
  P1 mean syllable expansion ES/EN is +15%..+30%  (the written-text expansion sources say +15..+30%).
  P2 at ES 7.7 syl/s and EN 6.2 syl/s the mean spoken-duration ratio ES/EN is 0.90..1.10
     (faster Spanish speech cancels the extra syllables).
  P3 >= 11 of 12 lines that fit their clip in English also fit in Spanish.
  P4 the '+25% on EN duration' headroom rule falsely REJECTS >= 3 Spanish lines that really fit.
  P5 (built to break) a short technical phrase ('Dishwasher safe') expands > 1.5x in duration
     and fails a 4 s clip: expansion is per-phrase, not a constant.
Rates: ES 7.7 syl/s is the press-reported Coupe et al. 2019 figure; EN rate is NOT verified,
so it is swept 5.5..6.8 and conclusions must hold across the sweep or be reported as not.
"""
import re

LEAD = 0.5            # s of silence per clip (assumed)
PAUSE = 0.25          # s per internal punctuation mark (assumed, same both languages)
ES_RATE = 7.7
EN_BASE = 6.2

# ---- syllable counters -------------------------------------------------
STRONG = set("aeoáéó"); WEAK = set("iuü"); ACC_WEAK = set("íú")
def es_syl(word):
    w = word.lower()
    if w == "y": return 1
    w = re.sub(r"(?<=[aeiouáéíóú])y$", "i", w)  # final y after a vowel is a weak vowel
    n = 0
    for grp in re.findall(r"[aeiouáéíóúü]+", w):
        n += 1
        for a, b in zip(grp, grp[1:]):
            if (a in STRONG or a in ACC_WEAK) and (b in STRONG or b in ACC_WEAK): n += 1
            elif a in ACC_WEAK or b in ACC_WEAK: n += 1
    return max(n, 1)

OVR = {"everything":3,"tried":1,"skeptical":4,"completely":3,"actually":4,"twenty":2,"minutes":3,
       "lightweight":2,"gift":1,"their":1,"they'll":1,"i've":1,"it's":1,"link's":1,"i'm":1,"yours":1,
       "stain":1,"gone":1,"folds":1,"flat":1,"week":1,"sells":1,"smooth":1,"felt":1,"never":2,
       "dishwasher":3,"safe":1,"charges":2,"lasts":1,"below":2,"before":2,"happens":2,"watch":1,
       "kitchen":2,"cleaned":1,"nothing":2,"spray":1,"thirty":2,"seconds":2,"found":1,"tiktok":2,
       "shop":1,"grab":1,"wait":1,"works":1,"this":1,"bio":2,"sale":1,"right":1,"now":1,"skin":1,
       "first":1,"after":2,"sold":1,"want":1,"use":1,"tap":1,"long":1,"day":1,"all":1,"and":1,"fits":1}
def en_syl(word):
    w = re.sub(r"[^a-z']", "", word.lower())
    if w in OVR: return OVR[w]
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le","ee")) and n > 1: n -= 1
    return max(n, 1)

def words(s): return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+", s)
def syl(s, f): return sum(f(w) for w in words(s))
def pauses(s): return len(re.findall(r"[,.;:?!](?=\s|$)", s)) - 1 if len(re.findall(r"[,.;:?!](?=\s|$)", s)) else 0
def dur(s, f, rate): return syl(s, f) / rate + PAUSE * max(pauses(s), 0)

# ---- self-test: hand-counted gold ----------------------------------------
GOLD_EN = {"actually":4,"everything":3,"skeptical":4,"completely":3,"twenty":2,"minutes":3,
           "dishwasher":3,"charges":2,"kitchen":2,"lightweight":2,"never":2,"tiktok":2}
GOLD_ES = {"encontré":3,"desaparece":5,"convencida":4,"funciona":3,"día":2,"lavavajillas":5,
           "enlace":3,"perfil":2,"había":3,"mancha":2,"dudaba":3,"semana":3,"agote":3,"oferta":3,
           "creía":3,"estoy":2,"cabe":2,"piel":1,"cocina":3,"suave":2,"enlace":3,"muy":1,"hoy":1}
bad = [w for w,k in GOLD_EN.items() if en_syl(w)!=k] + [w for w,k in GOLD_ES.items() if es_syl(w)!=k]
assert not bad, f"counter mismatches: {bad}"

# ---- corpus: (clip_seconds, EN, ES, role) ---------------------------------
CORE = [
 (4,"Wait, this actually works?","¿Espera, esto de verdad funciona?"),
 (4,"I found it on TikTok Shop.","Lo encontré en TikTok Shop."),
 (4,"Watch what happens next.","Mira lo que pasa ahora."),
 (4,"Grab yours before it sells out.","Consigue el tuyo antes de que se agote."),
 (6,"I've tried everything, and nothing cleaned my kitchen like this.","Lo he probado todo y nada limpió mi cocina como esto."),
 (6,"One spray, thirty seconds, and the stain is gone.","Un rociado, treinta segundos, y la mancha desaparece."),
 (6,"It's lightweight, it folds flat, and it fits in my bag.","Es ligero, se pliega y cabe en mi bolso."),
 (6,"My skin has never felt this smooth.","Mi piel nunca se había sentido tan suave."),
 (8,"I was skeptical at first, but after one week I'm completely sold.","Al principio dudaba, pero después de una semana estoy totalmente convencida."),
 (8,"If you want a gift they'll actually use, tap the link below.","Si quieres un regalo que de verdad usen, toca el enlace de abajo."),
 (8,"It charges in twenty minutes and lasts all day long.","Se carga en veinte minutos y dura todo el día."),
 (8,"Link's in my bio, and it's on sale right now.","El enlace está en mi perfil y está en oferta ahora mismo."),
]
BREAK = (4,"Dishwasher safe.","Se puede lavar en el lavavajillas.")

def fits(d, clip): return d <= clip - LEAD

def run(en_rate):
    rows=[]
    for clip,en,es in CORE:
        de, ds = dur(en,en_syl,en_rate), dur(es,es_syl,ES_RATE)
        rows.append((clip,en,es,syl(en,en_syl),syl(es,es_syl),de,ds))
    return rows

rows = run(EN_BASE)
print(f"{'clip':>4} {'enSyl':>5} {'esSyl':>5} {'syl+%':>6} {'chr+%':>6} {'enS':>5} {'esS':>5} {'ratio':>5} enFit esFit heurOK")
sx=cx=0; fit_en=fit_both=falsrej=0; ratios=[]
for clip,en,es,se,ss,de,ds in rows:
    syl_x=ss/se-1; chr_x=len(es)/len(en)-1; r=ds/de
    fe,fs = fits(de,clip), fits(ds,clip)
    heur = fits(de*1.25,clip)          # rule: Spanish needs 25% headroom over English duration
    sx+=syl_x; cx+=chr_x; ratios.append(r)
    fit_en+=fe; fit_both+=(fe and fs); falsrej+=(fs and not heur)
    print(f"{clip:>4} {se:>5} {ss:>5} {syl_x*100:>+6.0f} {chr_x*100:>+6.0f} {de:>5.2f} {ds:>5.2f} {r:>5.2f} {str(fe):>5} {str(fs):>5} {str(heur):>6}")
n=len(rows); msx=sx/n; mcx=cx/n; mr=sum(ratios)/n
print(f"\nmean syllable expansion {msx*100:+.1f}%  mean char expansion {mcx*100:+.1f}%  mean duration ratio {mr:.3f}")
print(f"EN-fit lines also fitting in ES: {fit_both}/{fit_en}   heuristic false-rejects (ES fits, rule says no): {falsrej}")

# sensitivity: EN rate unverified
print("\nEN-rate sweep (ES fixed 7.7):")
sweep={}
for er in (5.5,5.8,6.2,6.5,6.8):
    rr=run(er); m=sum(ds/de for *_,de,ds in rr)/len(rr)
    both=sum(1 for c,_,_,_,_,de,ds in rr if fits(de,c) and fits(ds,c)); fe=sum(1 for c,_,_,_,_,de,ds in rr if fits(de,c))
    sweep[er]=(m,both,fe); print(f"  EN {er}: mean ratio {m:.3f}  fit {both}/{fe}")

# ADDED AFTER RUN 1 (exploratory, not a prediction): per-line spread of the ratio decides the planning rule.
rmax=max(ratios); rmin=min(ratios)
print(f"\nper-line duration ratio ES/EN: min {rmin:.2f} max {rmax:.2f}; EN may fill at most {100/rmax:.0f}% of a clip's speakable time to guarantee every line fits in ES")
print(f"chars per syllable: EN {sum(len(en) for _,en,_ in CORE)/sum(syl(en,en_syl) for _,en,_ in CORE):.2f}  ES {sum(len(es) for *_,es in CORE)/sum(syl(es,es_syl) for *_,es in CORE):.2f}")

clip,en,es = BREAK
de,ds = dur(en,en_syl,EN_BASE), dur(es,es_syl,ES_RATE)
print(f"\nBREAK '{en}' -> '{es}': EN {syl(en,en_syl)} syl {de:.2f}s, ES {syl(es,es_syl)} syl {ds:.2f}s, ratio {ds/de:.2f}, fits 4s clip: {fits(ds,clip)}")

p1 = 0.15 <= msx <= 0.30
p2 = 0.90 <= mr <= 1.10
p3 = fit_both >= 11
p4 = falsrej >= 3
p5 = (ds/de) > 1.5 and not fits(ds,clip)
print(f"\nP1 {p1}  P2 {p2}  P3 {p3}  P4 {p4}  P5 {p5}")
allp = all((p1,p2,p3,p4,p5))
print(("RESULT: PASS " if allp else "RESULT: FAIL ")+
      f"syl {msx*100:+.0f}%, chars {mcx*100:+.0f}%, dur ratio {mr:.2f} (sweep {min(v[0] for v in sweep.values()):.2f}-{max(v[0] for v in sweep.values()):.2f}), "
      f"fit {fit_both}/{fit_en}, heuristic false-rejects {falsrej}, break ratio {ds/de:.2f}")
