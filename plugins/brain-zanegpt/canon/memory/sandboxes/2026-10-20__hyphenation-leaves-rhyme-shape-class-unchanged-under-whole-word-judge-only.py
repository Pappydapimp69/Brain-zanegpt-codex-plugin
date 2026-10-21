import itertools
# whole-word rimes
W={'sorrow':'orow','tomorrow':'orow','follow':'orow','hollow':'orow','go':'oh','row':'oh','low':'oh',
   'river':'iver','shiver':'iver','over':'over','clover':'over','tender':'ender','remember':'ender','ember':'ender','flower':'ower','power':'ower'}
H={'sorrow':'sor-row','tomorrow':'to-mor-row','follow':'fol-low','hollow':'hol-low','river':'riv-er','shiver':'shiv-er','over':'o-ver',
   'clover':'clo-ver','tender':'ten-der','remember':'re-mem-ber','ember':'em-ber','flower':'flow-er','power':'pow-er'}
SEG={'row':'oh','low':'oh','er':'er','ver':'er','der':'er','ber':'er'}  # last-segment lookups
def key_whole(w): return W[w.replace('-','')]
def key_last(w): return SEG.get(w.split('-')[-1], w.split('-')[-1])
def letters(ws,key):
    m={};o=''
    for w in ws:
        k=key(w)
        if k not in m: m[k]='ABCD'[len(m)]
        o+=m[k]
    return o
def shape(l):  # emotional-motion class from letters: stops = adjacent equal-letter pairs
    if l[0]==l[1] and l[2]==l[3] and l[0]!=l[2]: return 'AABB stop-4'
    if l[0]==l[2] and l[1]==l[3] and l[0]!=l[1]: return 'ABAB flow'
    if l[0]==l[3] and l[1]==l[2] and l[0]!=l[1]: return 'ABBA open'
    return 'other'
words=['sorrow','tomorrow','follow','river','shiver','over','tender','ember','flower','power']
def hy(w): return H.get(w,w)
n=0;bw=bl=0;lw=0
for c in itertools.product(words,repeat=4):
    n+=1
    plain=shape(letters(c,key_whole))
    hw=shape(letters([hy(w) for w in c],key_whole))
    hl=shape(letters([hy(w) for w in c],key_last))
    pl=shape(letters(c,key_whole))
    if hw!=plain: bw+=1
    if hl!=plain: bl+=1
print('stanzas',n)
print('shape class changed by hyphenation: whole-word judge',bw,'last-segment judge',bl,'(%.1f%%)'%(100*bl/n))
# break: hyphenated plain-vowel words where last segment collides
brk=['sorrow','follow','go','low']
print('BREAK set shapes whole/last:',shape(letters([hy(w) for w in brk],key_whole)),'/',shape(letters([hy(w) for w in brk],key_last)))
print(('RESULT: PASS' if bw==0 and bl>0 else 'RESULT: FAIL')+' whole-word judge kept shape class %d/%d; last-segment judge changed %d/%d (%.1f%%)'%(n-bw,n,bl,n,100*bl/n))
