"""Sandbox: how a note store should treat a NEW observation that contradicts a stored rule.

Scenario: a builder bot learns a block-rotation rule from screenshots. Observations arrive one at a
time; some are misleading (bad angle) and say the opposite. Policies keep one current belief:
  overwrite   - latest observation replaces the rule (last writer wins)
  first       - first rule kept, contradictions ignored
  hold-all    - contradiction opens a tension; flip only when ALL-TIME counts favour the other side by K
  hold-recent - contradiction opens a tension; flip only when the last W observations favour it by K
Measured: share of steps the belief is wrong, and number of flips. Deterministic: fixed noise lists.
"""
K,W=3,6
def run(obs,policy,truth=None):
    truth=truth or ['A']*len(obs);belief=None;wrong=0;flips=0;hist=[]
    for i,o in enumerate(obs):
        hist.append(o);prev=belief
        if policy=='overwrite':belief=o
        elif policy=='first':belief=belief or o
        else:
            h=hist if policy=='hold-all' else hist[-W:]
            a=h.count('A');b=h.count('B')
            if belief is None:belief=o
            elif belief=='A' and b-a>=K:belief='B'
            elif belief=='B' and a-b>=K:belief='A'
        if prev is not None and belief!=prev:flips+=1
        wrong+=belief!=truth[i]
    return round(wrong/len(obs),3),flips
seq=lambda n,bad:['B' if i in bad else 'A' for i in range(n)]
S={'1 sparse noise 10%':(seq(40,{5,15,25,35}),None),
   '2 noisy 30%':(seq(40,{1,4,7,10,13,16,19,22,25,28,31,34}),None),
   '3 first observation wrong':(seq(40,{0,6,20}),None),
   '4 BREAK: rule really changes at step 20':(['A']*20+['B']*20,['A']*20+['B']*20)}
P=('overwrite','first','hold-all','hold-recent');R={}
for n,(o,t) in S.items():
    R[n]={p:run(o,p,t) for p in P};print(n,R[n])
ok=(R['2 noisy 30%']['overwrite'][1]>=20 and R['2 noisy 30%']['hold-recent'][1]==0
    and R['3 first observation wrong']['first'][0]==1.0 and R['3 first observation wrong']['hold-recent'][0]<=0.1
    and R['4 BREAK: rule really changes at step 20']['hold-all'][0]==0.5
    and R['4 BREAK: rule really changes at step 20']['hold-recent'][0]<=0.15)
lag=round(R['4 BREAK: rule really changes at step 20']['hold-recent'][0]*40)
print('RESULT: '+('PASS' if ok else 'FAIL')+f" holding a contradiction open until recent evidence (last {W}) outvotes it by {K}: 0 flips under 30% noise (last-writer-wins 24), recovers a wrong first note, follows a real change {lag} steps late; counting ALL history never followed the change (wrong 50%)")
