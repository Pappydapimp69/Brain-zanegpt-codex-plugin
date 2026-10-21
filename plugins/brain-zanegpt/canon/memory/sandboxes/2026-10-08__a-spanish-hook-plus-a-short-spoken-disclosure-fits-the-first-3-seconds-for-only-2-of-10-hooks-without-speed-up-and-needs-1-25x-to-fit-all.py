#!/usr/bin/env python3
"""Sandbox (edge): can a Spanish hook plus a short spoken disclosure still land in the first 3 seconds, with and without a dubbing speed-up? Deterministic, stdlib only.
Composes tiktok-shop lessons E3 (10 hook pairs; Spanish ~1.55x English syllables; window 2.8 s of speech), E9 (short spoken disclosure: 4 English / 6 Spanish syllables) and E17 (speed-up limits for dubbing: 1.10, 1.15, 1.25).
Counting rule: hook duration + pause 0.25 s + disclosure duration must fit 2.8 s; a speed-up divides the whole spoken duration.
PREDICTION (written before first run), human rates EN 6.2 / ES 7.7 syl/s:
  P1 English hook + 4-syllable disclosure fits 2.8 s for 7 to 9 of 10 hooks.
  P2 Spanish hook + 6-syllable disclosure fits for only 1 to 3 of 10 hooks with no speed-up.
  P3 allowing a 1.15x speed-up raises the Spanish count to 4 to 7 of 10.
  P4 a 1.25x speed-up fits at least 9 of 10 Spanish hooks (but is the dubbing limit where artifacts appear).
  P5 (built to break 'a short disclosure always fits beside a hook') the longest Spanish hook (18 syllables) plus the disclosure overflows 2.8 s at 1.0x and at 1.10x.
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

CAP=2.8
DIS_EN="I got this free."; DIS_ES="Me lo regalaron."
dis_en=syl(DIS_EN,en_syl)/EN_BASE; dis_es=syl(DIS_ES,es_syl)/ES_RATE
tot_en=[dur(en,en_syl,EN_BASE)+0.25+dis_en for en,_ in HOOKS]
tot_es=[dur(es_,es_syl,ES_RATE)+0.25+dis_es for _,es_ in HOOKS]
fit=lambda tot,f:sum(t/f<=CAP for t in tot)
print("EN totals",[round(t,2) for t in tot_en]); print("ES totals",[round(t,2) for t in tot_es])
r=dict(en=fit(tot_en,1.0),es1=fit(tot_es,1.0),es110=fit(tot_es,1.10),es115=fit(tot_es,1.15),es125=fit(tot_es,1.25))
longest=max(range(10),key=lambda i:syl(HOOKS[i][1],es_syl)); lt=tot_es[longest]
print(r, f"longest ES hook total {lt:.2f}s")
p1=7<=r['en']<=9; p2=1<=r['es1']<=3; p3=4<=r['es115']<=7; p4=r['es125']>=9; p5=lt>CAP and lt/1.10>CAP
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"hook + short spoken disclosure in 2.8 s: EN {r['en']}/10; ES {r['es1']}/10 at 1.0x, {r['es110']}/10 at 1.10x, {r['es115']}/10 at 1.15x, {r['es125']}/10 at 1.25x")
