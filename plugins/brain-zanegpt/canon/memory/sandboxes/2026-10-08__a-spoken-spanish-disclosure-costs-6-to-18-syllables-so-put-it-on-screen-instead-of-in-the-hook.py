#!/usr/bin/env python3
"""Sandbox: what does a SPOKEN affiliate disclosure cost inside the first-3-seconds hook window? Deterministic, stdlib only.
Window = 2.8 s of speech (3.0 s minus 0.2 s lead-in), human pace EN 6.2 / ES 7.7 syl/s, 0.25 s per internal pause (same as the hook sandbox).
Disclosure lines are short stock phrasings; on-screen text alternative uses TikTok's guidance of 5-10 words per second (read live 2026-10-08).
PREDICTION (written before first run):
  P1 a short English spoken disclosure ('I got this free.') takes 4 syllables = 0.65 s, i.e. 23% of the 17-syllable English window (20%..27%).
  P2 the Spanish equivalent ('Me lo regalaron.') costs 6 syllables = 0.78 s, 28% of the 21-syllable Spanish window (25%..31%).
  P3 an 11-syllable English hook plus the 4-syllable English disclosure (one pause between) FITS the 2.8 s window.
  P4 (built to break 'a spoken disclosure always fits beside a hook') a longer, plainer Spanish disclosure ('Recibí este producto gratis a cambio de mi opinión.') plus an 11-syllable-hook-equivalent Spanish hook (18 syllables) OVERFLOWS the window.
  P5 an on-screen text disclosure of 4 words needs at most 0.8 s of reading time at 5 words per second and costs 0 spoken syllables.
"""
import re
STRONG=set("aeoáéó"); ACC=set("íú")
def es_syl(word):
    w=word.lower()
    if w=="y": return 1
    w=re.sub(r"(?<=[aeiouáéíóú])y$","i",w); n=0
    for grp in re.findall(r"[aeiouáéíóúü]+",w):
        n+=1
        for a,b in zip(grp,grp[1:]):
            if (a in STRONG or a in ACC) and (b in STRONG or b in ACC): n+=1
            elif a in ACC or b in ACC: n+=1
    return max(n,1)
EN={"i":1,"got":1,"this":1,"free":1,"gift":1,"ad":1,"sponsored":2,"paid":1,"promo":2}
def en_syl(w): return EN.get(w.lower(),1)
words=lambda s:re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+",s)
def dur(s,f,r): 
    p=max(len(re.findall(r"[,.;:?!](?=\s|$)",s))-1,0); return sum(f(w) for w in words(s))/r+0.25*p
CAP=2.8; EN_R,ES_R=6.2,7.7
d_en="I got this free."; d_es="Me lo regalaron."; d_es_long="Recibí este producto gratis a cambio de mi opinión."
s_en=sum(en_syl(w) for w in words(d_en)); s_es=sum(es_syl(w) for w in words(d_es)); s_long=sum(es_syl(w) for w in words(d_es_long))
sh_en=dur(d_en,en_syl,EN_R)/CAP; sh_es=dur(d_es,es_syl,ES_R)/CAP
hook_en_syl=11; combo_en=(hook_en_syl+s_en)/EN_R+0.25            # hook + disclosure with one pause
hook_es_syl=18; combo_es_long=(hook_es_syl+s_long)/ES_R+0.25
read=4/5
print(f"EN disclosure {s_en} syl = {dur(d_en,en_syl,EN_R):.2f}s ({sh_en:.0%} of window); ES {s_es} syl = {dur(d_es,es_syl,ES_R):.2f}s ({sh_es:.0%}); long ES {s_long} syl")
print(f"EN hook(11)+disclosure: {combo_en:.2f}s vs {CAP}s; ES hook(18)+long disclosure: {combo_es_long:.2f}s; on-screen 4 words: {read:.2f}s reading")
p1=s_en==4 and 0.20<=sh_en<=0.27; p2=s_es==6 and 0.25<=sh_es<=0.31; p3=combo_en<=CAP; p4=combo_es_long>CAP; p5=read<=0.8
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"EN disclosure {s_en} syl ({sh_en:.0%} of the window), ES {s_es} syl ({sh_es:.0%}); EN hook+disclosure {combo_en:.2f}s fits, ES hook+long disclosure {combo_es_long:.2f}s overflows {CAP}s; on-screen text {read:.1f}s")
