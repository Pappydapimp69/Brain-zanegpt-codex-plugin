import itertools
# word: (hyphenated segments, whole-word rhyme key from stressed vowel on)
FULL={'going-to':(['go','ing','to'],'u'),'want-to':(['want','to'],'u'),'blue':(['blue'],'u'),'true':(['true'],'u'),
      'got-to':(['got','to'],'u'),'a-lone':(['a','lone'],'on'),'home':(['home'],'om')}
RED={'wan-na':(['wan','na'],'ana'),'gon-na':(['gon','na'],'ana'),'Han-nah':(['Han','nah'],'ana2'),
     'got-ta':(['got','ta'],'ata'),'pas-ta':(['pas','ta'],'asta'),'kin-da':(['kin','da'],'inda'),'sin-ner':(['sin','ner'],'ina'),
     'gon-na-b':(['gon','na'],'ana')}
def pattern(words,key):
    seen={};out=[]
    for w in words:
        k=key(w)
        seen.setdefault(k,chr(65+len(seen)));out.append(seen[k])
    return ''.join(out)
def run(lex,keyfn_bad):
    ws=list(lex);n=bad=0
    for st in itertools.product(ws,repeat=4):
        g=pattern(st,lambda w:lex[w][1]);b=pattern(st,lambda w:keyfn_bad(lex[w][0]))
        n+=1;bad+=(g!=b)
    return n,bad
last=lambda s:s[-1]
last2=lambda s:''.join(s[-2:])
res={}
for name,lex in [('full-forms',FULL),('reduced-forms',RED)]:
    n,b=run(lex,last);res[name]=(n,b);print(name,'last-segment judge miss %d/%d = %.1f%%'%(b,n,100*b/n))
n,b=run(RED,last2);print('reduced last-two-segments judge miss %d/%d = %.1f%%'%(b,n,100*b/n))
# break: a sound-keyed whole-word judge on the same lexicon
n,b0=run(RED,lambda s:RED[[k for k in RED if RED[k][0]==s][0]][1]);print('whole-word judge miss',b0)
ok=res['reduced-forms'][1]>res['full-forms'][1] and b0==0
print('RESULT: %s last-segment judge miscalls %.1f%% of reduced-form stanzas vs %.1f%% full-form; whole-word judge 0; last-two-segments %.1f%%'%(
 'PASS' if ok else 'FAIL',100*res['reduced-forms'][1]/res['reduced-forms'][0],100*res['full-forms'][1]/res['full-forms'][0],100*b/n if False else 100*run(RED,last2)[1]/run(RED,last2)[0]))
