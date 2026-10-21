#!/usr/bin/env python3
"""Sandbox: pack a 12-line ad script into the SMALLEST legal clips (4, 6 or 8 s), English vs Spanish.
Deterministic, stdlib only. One spoken line must live inside ONE clip (a line cannot straddle two
generations), speakable time = clip - 0.5 s lead. Composes the Spanish syllable-budget lesson with the
one-action-per-short-clip shot rule.

PREDICTION (written before first run), human rates ES 7.7 / EN 6.2 syl/s:
  P1 Spanish needs MORE total clip seconds than English for the same 12 lines: ES/EN total between 1.10 and 1.30.
  P2 at least 3 of the 12 lines must move UP a clip size in Spanish (4->6, 6->8) vs English.
  P3 at least 1 Spanish line does not fit even an 8 s clip once it is spoken together with its
     own pause budget at the slow end of the sweep (EN 5.5 irrelevant; ES rate cut to 6.5 syl/s).
  P4 (built to break the 'clip size follows script length' idea) re-assigning clips by the ENGLISH sizes
     (not repacking) overflows at least 2 Spanish lines.
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

SIZES=(4,6,8)
def smallest(d):
    for c in SIZES:
        if d<=c-LEAD: return c
    return None
def plan(rate_es):
    pe=[];ps=[];ov=0;up=0
    for clip0,en,es in CORE:
        ce=smallest(dur(en,en_syl,EN_BASE)); cs=smallest(dur(es,es_syl,rate_es))
        pe.append(ce); ps.append(cs)
    return pe,ps
pe,ps=plan(ES_RATE)
te=sum(pe); ts=sum(c for c in ps if c)
up=sum(1 for a,b in zip(pe,ps) if b and b>a)
print("EN clips",pe,"total",te)
print("ES clips",ps,"total",ts)
print(f"ES/EN total {ts/te:.3f}; lines moving up a size: {up}")
# English-size reuse
over=0
for (clip0,en,es),ce in zip(CORE,pe):
    if dur(es,es_syl,ES_RATE)>ce-LEAD: over+=1
print(f"Spanish lines overflowing the clip size chosen for English: {over}")
pe2,ps2=plan(6.5)
nofit=sum(1 for c in ps2 if c is None)
print(f"at ES 6.5 syl/s: lines fitting no clip {nofit}; clips {ps2}")

# ADDED AFTER RUN 1 (exploratory, not a prediction): how slow must the voice be before Spanish costs real clip time?
print("\nvoice-pace sweep (same pace for both languages, i.e. a slower AI voice):")
for pace in (6.2,5.5,5.0,4.5,4.0):
    ee=[smallest(dur(en,en_syl,pace)) for _,en,_ in CORE]
    ss=[smallest(dur(es,es_syl,pace*ES_RATE/EN_BASE)) for _,_,es in CORE]
    tot_e=sum(c or 12 for c in ee); tot_s=sum(c or 12 for c in ss)
    print(f"  EN {pace} syl/s (ES {pace*ES_RATE/EN_BASE:.1f}): EN {tot_e}s ES {tot_s}s ratio {tot_s/tot_e:.2f}, unfit EN {sum(c is None for c in ee)} ES {sum(c is None for c in ss)}")
p1=1.10<=ts/te<=1.30; p2=up>=3; p3=nofit>=1; p4=over>=2
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+
      f"EN {te}s vs ES {ts}s total clip time ({ts/te:.2f}x), {up}/12 lines move up a size, {over} Spanish lines overflow English clip sizes, ES 6.5 syl/s leaves {nofit} lines unfit")
