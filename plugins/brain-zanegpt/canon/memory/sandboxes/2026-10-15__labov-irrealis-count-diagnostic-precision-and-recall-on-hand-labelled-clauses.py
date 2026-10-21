# Labov kernel: evaluation = irrealis clauses (negatives, conditionals, futures) concentrated before the critical event.
# Fixture labels were assigned by hand BEFORE writing the detector. Prediction: a regex irrealis detector reaches
# recall >=0.8 on evaluation clauses but precision <=0.6 because negatives in orientation/complication are irrealis in form.
import re
N=[ # (clause, function)  A=orientation C=complication E=evaluation R=resolution
("We were driving home after midnight","O"),("There wasn't another car on the road","O"),("I didn't have my phone","O"),
("Something ran out of the dark","C"),("I slammed the brakes","C"),
("If I had been going any faster I would have hit it","E"),("It could have gone through the windshield","E"),("I was terrified","E"),
("My brother said we'd never have made it","E"),("The truck stopped an inch from the deer","C"),("The deer walked off","R"),
("We never took that road again","R"),
("She opened the door","C"),("Nobody was home","O"),("The kitchen smelled of smoke","O"),("I didn't hear the alarm","C"),
("Had the neighbour not called we wouldn't be here","E"),("It might have been the whole house","E"),("Firefighters arrived at two","R"),
("We will always owe her","E"),
]
IRR=re.compile(r"\b(n't|not|never|nobody|no one|nothing|if|had been|had the|could have|would have|might have|will|would|'d)\b|n't",re.I)
tp=fp=fn=0;fps=[];fns=[]
for c,f in N:
    pred=bool(IRR.search(c)); gold=(f=="E")
    if pred and gold: tp+=1
    elif pred and not gold: fp+=1; fps.append((c,f))
    elif gold and not pred: fn+=1; fns.append(c)
prec=tp/(tp+fp); rec=tp/(tp+fn)
print('tp %d fp %d fn %d precision %.2f recall %.2f'%(tp,fp,fn,prec,rec))
print('false positives:',fps); print('misses:',fns)
# diagnostic: count irrealis BEFORE the climax clause vs after, flat vs evaluated cut of story 1
story1=N[:12]; flat=[x for x in story1 if x[1]!="E"]
def pre_climax(st):
    idx=[i for i,(c,f) in enumerate(st) if "stopped an inch" in c][0]
    return sum(bool(IRR.search(c)) for c,f in st[:idx])
print('pre-climax irrealis flat %d vs full %d'%(pre_climax(flat),pre_climax(story1)))
ok=rec>=0.8 and prec<=0.6
print('RESULT: %s irrealis detector precision %.2f recall %.2f; orientation/complication negatives are %d of %d false positives; pre-climax count flat %d vs full %d'%('PASS' if ok else 'FAIL',prec,rec,sum(f in 'OC' for _,f in fps),fp,pre_climax(flat),pre_climax(story1)))
