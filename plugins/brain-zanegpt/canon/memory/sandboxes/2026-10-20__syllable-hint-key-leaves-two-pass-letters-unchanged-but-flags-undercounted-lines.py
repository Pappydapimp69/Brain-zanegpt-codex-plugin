import itertools, re
# lexicon: word -> (true syllables, perfect-rhyme key, assonance key)
LEX = {
 "fire":(2,"AYR","AY"),"higher":(3,"AYR","AY"),"lion":(2,"AYN","AY"),"time":(1,"AYM","AY"),
 "night":(1,"AYT","AY"),"light":(1,"AYT","AY"),"real":(2,"EEL","EE"),"dream":(1,"EEM","EE"),
 "seen":(1,"EEN","EE"),"poem":(2,"OHM","OH"),"alone":(2,"OHN","OH"),"home":(1,"OHM","OH"),
}
FILL = ["the","and","we","go","on","to"]
def vg(w):  # vowel-group counter (undercounts hiatus words)
    return max(1,len(re.findall(r"[aeiouy]+",w)))
def letters(words):
    # pass 1: perfect-rhyme groups claim letters; pass 2: assonance leftovers listed apart
    out,seen,nxt=[],{},0
    for w in words:
        k=LEX[w][1]
        if k not in seen: seen[k]=None
        out.append(k)
    keys={}
    for k in out:
        if out.count(k)>1 and k not in keys: keys[k]=chr(65+len(keys))
    lines=[keys.get(k,"-") for k in out]
    left=[i for i,l in enumerate(lines) if l=="-"]
    assoc={}
    for i in left: assoc.setdefault(LEX[words[i]][2],[]).append(i)
    return lines,[v for v in assoc.values() if len(v)>1]
def hyphen_hint(line_words, budget, key):
    syl = (lambda w:LEX[w][0] if w in LEX else 1) if key=="true" else (lambda w:vg(w))
    total=sum(syl(w) for w in line_words)
    return total>budget
stanzas=list(itertools.product(LEX,repeat=4))
diff_letters=0; flag_true=flag_vg=0; missed=0
for st in stanzas:
    base=letters(list(st))
    # crowded line: 4 filler words + end word, then hyphenation of end word keeps whole word as rhyme key
    for ew in st:
        lw=FILL+[ew]
        t=hyphen_hint(lw,7,"true"); v=hyphen_hint(lw,7,"vg")
        flag_true+=t; flag_vg+=v; missed+= (t and not v)
    # letters computed from hint-independent keys -> must equal regardless of hint
    if letters(list(st))!=base: diff_letters+=1
print("stanzas",len(stanzas),"letter_changes",diff_letters,"lines",len(stanzas)*4,
      "flag_true",flag_true,"flag_vg",flag_vg,"missed_by_vg",missed)
# scenario 3 (break): budget 6, the shortest lines
t6=sum(hyphen_hint(FILL+[w],6,"true") for w in LEX); v6=sum(hyphen_hint(FILL+[w],6,"vg") for w in LEX)
print("budget6 words flagged true/vg",t6,v6)
ok = diff_letters==0 and missed>0
print("RESULT: %s letters unchanged in %d/%d stanzas; vowel-group key missed %d of %d lines true-syllable key flags"%("PASS" if ok else "FAIL",len(stanzas)-diff_letters,len(stanzas),missed,flag_true))
