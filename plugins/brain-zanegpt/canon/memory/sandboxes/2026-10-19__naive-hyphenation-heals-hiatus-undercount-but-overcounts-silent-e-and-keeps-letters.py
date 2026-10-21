"""Sandbox: naive vowel-group hyphenate() + vowel-group counter + two-pass whole-word letters (stdlib, deterministic)."""
import re
# word: (true syllables, rhyme tail)
W={'quiet':(3,'iet'),'diet':(3,'iet'),'riot':(3,'iet'),'poem':(2,'oem'),'piano':(3,'ano'),'idea':(3,'ea'),'fluid':(2,'uid'),
   'desire':(3,'ire'),'fire':(2,'ire'),'hire':(2,'ire'),'alone':(2,'one'),'stone':(1,'one'),'home':(1,'ome'),'dome':(1,'ome'),
   'night':(1,'ight'),'light':(1,'ight'),'heart':(1,'art'),'apart':(2,'art'),'tonight':(2,'ight'),'beautiful':(3,'ful'),
   'ocean':(2,'ean'),'science':(2,'ence'),'real':(1,'eal'),'seal':(1,'eal'),'lion':(2,'ion'),'create':(2,'ate'),'late':(1,'ate'),'tear':(1,'ear')}
# NOTE: hand-assigned true counts; poem/idea/fluid etc. are hiatus words, quiet/diet/riot/lion too.
def count(w):   # vowel-group counter used by the builder; silent final e removed
    w=w.replace('-','').lower(); n=len(re.findall(r'[aeiouy]+',w))
    if w.endswith('e') and not w.endswith(('le','ee')) and n>1: n-=1
    return max(1,n)
def count_h(w): # counter run on a hyphenated word: each hyphen part counts at least 1
    return sum(max(1,len(re.findall(r'[aeiouy]+',p))) for p in w.split('-'))
def hyph(w):    # naive: break after each vowel group (silent e becomes its own part)
    parts=re.findall(r'[^aeiouy]*[aeiouy]+|[^aeiouy]+$',w)
    out=[]
    for p in parts:
        if out and re.fullmatch(r'[^aeiouy]+',p): out[-1]+=p
        else: out.append(p)
    return '-'.join(out)
H=lambda w:w.count('-')
words=list(W)
plain_ok=sum(count(w)==W[w][0] for w in words)
hy_ok=sum(count_h(hyph(w))==W[w][0] for w in words)
hy_changed=[w for w in words if count_h(hyph(w))!=count(w)]
raised=[w for w in hy_changed if count_h(hyph(w))>count(w)]
fixed=[w for w in words if count(w)!=W[w][0] and count_h(hyph(w))==W[w][0]]
broken=[w for w in words if count(w)==W[w][0] and count_h(hyph(w))!=W[w][0]]
print(f"words {len(words)}: plain counter exact {plain_ok}, after naive hyphenation exact {hy_ok}")
print(f"fixed by hyphenation {len(fixed)} {fixed}")
print(f"broken by hyphenation {len(broken)} {broken}")
# two-pass whole-word letters on stanzas of 4 end words from the table; AABB / ABAB / ABBA by tail
import itertools
tails={}
for w in words: tails.setdefault(W[w][1],[]).append(w)
groups=[g for g in tails.values() if len(g)>=2]
stanzas=[]
for g1,g2 in itertools.permutations(groups,2):
    for pat in ('ABAB','AABB','ABBA'):
        seq=[];i1=i2=0
        for c in pat:
            if c=='A': seq.append(g1[i1%len(g1)]);i1+=1
            else: seq.append(g2[i2%len(g2)]);i2+=1
        stanzas.append(seq)
def lettering(seq,key):
    d={};return tuple(d.setdefault(key(w),len(d)) for w in seq)
whole=lambda w:W[w.replace('-','')][1]
last=lambda w:w.split('-')[-1]
same_whole=sum(lettering(s,lambda w:W[w][1])==lettering([hyph(x) for x in s],whole) for s in stanzas)
same_last=sum(lettering(s,lambda w:W[w][1])==lettering([hyph(x) for x in s],lambda w:(W[w.replace('-','')][1] if '-' not in w else last(w))) for s in stanzas)
print(f"stanzas {len(stanzas)}: letters kept after hyphenating end words: whole-word judge {same_whole}, last-segment judge {same_last}")
ok = len(fixed)>0 and len(broken)>0 and same_whole==len(stanzas) and same_last<len(stanzas) and hy_ok<len(words)
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" counter exact plain {plain_ok}/{len(words)} -> hyphenated {hy_ok}/{len(words)} (fixed {len(fixed)}, broken {len(broken)}); letters kept whole {same_whole}/{len(stanzas)} last-seg {same_last}/{len(stanzas)}")
