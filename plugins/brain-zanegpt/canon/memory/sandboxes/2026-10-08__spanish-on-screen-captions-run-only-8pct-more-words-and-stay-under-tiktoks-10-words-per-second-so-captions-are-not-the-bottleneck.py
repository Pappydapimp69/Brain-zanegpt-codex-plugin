#!/usr/bin/env python3
"""Sandbox: on-screen captions in Spanish vs English, counted in WORDS per second against TikTok's text guidance. Deterministic, stdlib only.
TikTok Creative Best Practices (read live 2026-10-08): "We recommend displaying 5-10 words per second when using text." Same 22 EN/ES pairs as the dubbing sandbox.
Caption is shown for the English spoken duration (the clip's timing is fixed by the English edit).
PREDICTION (written before first run):
  P1 mean word-count ratio ES/EN is 1.15 to 1.30 (words grow more than characters, which grew only 6% on the 12 core lines).
  P2 at the English duration, at most 3 of 22 Spanish captions exceed 10 words per second.
  P3 the Spanish caption mean words/second is higher than the English one by 10 to 30 percent.
  P4 (built to break 'captions can just be translated') at least 1 Spanish caption exceeds 10 words per second while its English one does not.
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

wc=lambda s:len(words(s))
rat=[wc(es_)/wc(en) for en,es_ in PAIRS]
wps_en=[wc(en)/dur(en,en_syl,EN_BASE) for en,es_ in PAIRS]
wps_es=[wc(es_)/dur(en,en_syl,EN_BASE) for en,es_ in PAIRS]
mr=sum(rat)/len(rat); over_es=sum(x>10 for x in wps_es); over_en=sum(x>10 for x in wps_en)
flip=sum(1 for a,b in zip(wps_en,wps_es) if b>10>=a)
me,ms=sum(wps_en)/len(wps_en),sum(wps_es)/len(wps_es)
print(f"mean word ratio {mr:.2f}; mean wps EN {me:.2f} ES {ms:.2f} ({(ms/me-1)*100:+.0f}%); >10 wps: EN {over_en}, ES {over_es}; newly over limit in Spanish: {flip}")
p1=1.15<=mr<=1.30; p2=over_es<=3; p3=1.10<=ms/me<=1.30; p4=flip>=1
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4}")
print(("RESULT: PASS " if all((p1,p2,p3,p4)) else "RESULT: FAIL ")+f"Spanish captions: words x{mr:.2f}, words/sec {ms:.2f} vs {me:.2f} English, {over_es} over 10 wps ({flip} newly over)")
