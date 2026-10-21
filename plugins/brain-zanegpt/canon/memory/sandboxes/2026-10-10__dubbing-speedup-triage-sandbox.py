import re
# Scripts: SHOT / DIALOGUE / SFX blocks, EN vs ES (author-written, n=12)
PAIRS = [
 ("Stop scrolling, this mop changes everything.", "Deja de desplazarte, este trapeador lo cambia todo."),
 ("It dries in ten seconds.", "Se seca en diez segundos."),
 ("I bought it yesterday.", "Lo compré ayer."),
 ("No more sore knees from scrubbing.", "Se acabaron las rodillas adoloridas de tanto fregar."),
 ("Watch this.", "Mira esto."),
 ("The pad snaps off in one move.", "La almohadilla se desprende con un solo movimiento."),
 ("Link is in my bio.", "El enlace está en mi perfil."),
 ("Fifteen dollars, free shipping today only.", "Quince dólares, envío gratis solo por hoy."),
 ("My kitchen has never looked cleaner.", "Mi cocina nunca ha estado más limpia."),
 ("Try it.", "Pruébalo."),
 ("It works on tile, wood and stone.", "Funciona en azulejo, madera y piedra."),
 ("Grab yours before they sell out.", "Consigue el tuyo antes de que se agoten."),
]
def script(lines, col):
    out=[]
    for i,p in enumerate(lines):
        out.append("SHOT: close-up mop %d\nDIALOGUE: \"%s\"\nSFX: swish %d" % (i,p[col],i))
    return "\n".join(out)
def quoted(s): return re.findall(r'DIALOGUE: "([^"]*)"', s)
def strip_dialogue(s): return re.sub(r'DIALOGUE: "[^"]*"', 'DIALOGUE: ""', s)
en_s, es_s = script(PAIRS,0), script(PAIRS,1)
# kernel 1: translate only quoted block -> everything else byte-identical
assert strip_dialogue(en_s)==strip_dialogue(es_s)
en, es = quoted(en_s), quoted(es_s)
def syl_en(w):
    w=w.lower(); n=len(re.findall(r'[aeiouy]+',w))
    if w.endswith('e') and not w.endswith('le') and n>1: n-=1
    return max(n,1)
def syl_es(w):
    w=w.lower()
    # strong vowels split, weak+strong merge (diphthong); accented i/u stays strong
    return max(len(re.findall(r'[iuü]?[aeoáéó][iuü]?|[íú]|[iu]',w)),1)
def syl(line,f): return sum(f(w) for w in re.findall(r"[A-Za-zÀ-ÿ]+",line))
def run(en_rate, es_rate, thr=(1.10,1.15,1.25)):
    need=[]
    for e,s in zip(en,es):
        t_en=syl(e,syl_en)/en_rate; t_es=syl(s,syl_es)/es_rate
        need.append(t_es/t_en)
    return need
def fixable(need):
    return [sum(1 for n in need if n<=t) for t in (1.10,1.15,1.25)]
print("pairs",len(en))
print("syllables EN",sum(syl(e,syl_en) for e in en),"ES",sum(syl(s,syl_es) for s in es))
res={}
for name,(er,sr) in {"base 6.2/7.7":(6.2,7.7),"en fast 6.8/7.7":(6.8,7.7),"en slow 5.5/7.7":(5.5,7.7),"equal rates 6.2/6.2 (BREAK)":(6.2,6.2)}.items():
    need=run(er,sr); f=fixable(need)
    over=sum(1 for n in need if n>1.25)
    res[name]=(f,over)
    print("%-30s min %.2f max %.2f fix@1.10/1.15/1.25 = %s over1.25 = %d (%.0f%%)"%(name,min(need),max(need),f,over,100*over/len(need)))
f,over=res["base 6.2/7.7"]
ok_base = 0.15<=over/len(en)<=0.5 and f[0]<f[1]<=f[2]<len(en)
# claim "speed-up fixes only the small residual": at base, a bounded share needs rewriting
ok_break = res["equal rates 6.2/6.2 (BREAK)"][1]/len(en) > res["base 6.2/7.7"][1]/len(en)
print("RESULT:", "PASS" if ok_base and ok_break else "FAIL",
 "base over-1.25 lines %d/12, fixable counts %s; share depends on rate ratio (equal rates -> %d over)"%(over,f,res["equal rates 6.2/6.2 (BREAK)"][1]))
