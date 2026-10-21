#!/usr/bin/env python3
"""Sandbox: can an English ad be DUBBED into Spanish by speeding the audio up, or do most lines need a rewrite? Deterministic, stdlib only.
Uses the 22 EN/ES line pairs from the two earlier Spanish sandboxes (12 core lines + 10 hooks), same hand-checked syllable counters, human rates EN 6.2 / ES 7.7 syllables per second.
Time-stretch limit is a parameter: the ideas kernel says only "small-ratio" stretching for a residual gap; common practice is about 10 to 15 percent, tested here at 10, 15 and 25 percent.
Needed speed-up for a line = (Spanish natural duration) / (English natural duration).
PREDICTION (written before first run):
  P1 lines fixable by stretching up to 1.10x: 6 to 9 of 22.
  P2 up to 1.15x: 7 to 10 of 22 (fewer than half).
  P3 up to 1.25x: 13 to 16 of 22.
  P4 (built to break 'dub by stretching') the worst line needs at least 1.5x, so 3 or more lines still need a rewrite even at the generous 1.25x limit.
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


OVR.update({"mop":1,"mops":1,"dog":1,"lose":1,"lunch":1,"costs":1,"less":1,"than":1,"mornings":2,"told":1,"charger":2,
 "could":1,"three":1,"sink":1,"spotless":2,"trainer":2,"skip":1,"talking":2,"nobody":3,"wasted":2,"money":2,"scrolling":2,
 "stop":1,"fixed":1,"dry":1,"changed":1,"gift":1,"dollars":2,"under":2,"best":1,"price":1,"goes":1,"back":1,"buy":1,"why":1,
 "is":1,"i'm":1,"who":1,"your":1,"hair":1,"until":2,"one":1,"every":2,"my":1,"me":1,"it":1,"the":1,"a":1,"and":1,"this":1,"will":1,"over":2,"before":2,"up":1})

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

HOOKS=[
 ("Stop scrolling, this fixed my dry skin.","Deja de hacer scroll, esto arregló mi piel seca."),
 ("I wasted money on every mop until this one.","Gasté dinero en todos los trapeadores hasta este."),
 ("Your dog will lose it over this.","Tu perro se va a volver loco con esto."),
 ("This costs less than lunch, and it changed my mornings.","Esto cuesta menos que el almuerzo y cambió mis mañanas."),
 ("Nobody told me my charger could do this.","Nadie me dijo que mi cargador podía hacer esto."),
 ("Three seconds, and my sink is spotless.","Tres segundos y mi fregadero queda impecable."),
 ("I'm a trainer, and I never skip this.","Soy entrenadora y yo nunca me salto esto."),
 ("Why is nobody talking about this?","¿Por qué nadie habla de esto?"),
 ("Buy it before the price goes back up.","Cómpralo antes de que vuelva a subir el precio."),
 ("Is this the best gift under twenty dollars?","¿Es este el mejor regalo por menos de veinte dólares?"),
]

PAIRS=[(en,es_) for _,en,es_ in CORE]+list(HOOKS)

need=[dur(es_,es_syl,ES_RATE)/dur(en,en_syl,EN_BASE) for en,es_ in PAIRS]
n=len(need)
fx={lim:sum(r<=lim for r in need) for lim in (1.10,1.15,1.25)}
worst=max(need); over25=sum(r>1.25 for r in need)
print("needed speed-up per pair:",[round(r,2) for r in need])
print(f"fixable by stretch <=1.10: {fx[1.10]}/{n}; <=1.15: {fx[1.15]}/{n}; <=1.25: {fx[1.25]}/{n}; worst {worst:.2f}x; lines over 1.25x: {over25}")
p1=6<=fx[1.10]<=9; p2=7<=fx[1.15]<=10 and fx[1.15]<n/2; p3=13<=fx[1.25]<=16; p4=worst>=1.5 and over25>=3
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"dubbing by stretch alone fixes {fx[1.10]}/{n} lines at 1.10x, {fx[1.15]}/{n} at 1.15x, {fx[1.25]}/{n} at 1.25x; worst line needs {worst:.2f}x")
