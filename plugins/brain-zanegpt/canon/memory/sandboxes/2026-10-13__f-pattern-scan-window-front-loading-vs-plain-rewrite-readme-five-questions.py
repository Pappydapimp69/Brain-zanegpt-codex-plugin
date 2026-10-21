# Toy scanner: sees the first K words of the first L lines (F-pattern). A README must answer 5 questions (what, why, start, help, who).
# Compare: buried-answers draft vs front-loaded draft vs plain-language-shortened draft, over scan budgets (K,L). Deterministic.
Q=['what','why','start','help','who']
def draft_buried():   # each line leads with preamble; the answer word comes late in the line
    return [('Historically this project grew out of many discussions among contributors about tooling and the need for', None),
            ('In the context of the wider ecosystem and several adjacent efforts we believe that it does something', 'what'),
            ('Over time the reasons for building it became clear to everyone, namely that it is useful because', 'why'),
            ('Following installation of the prerequisites listed below, users can eventually get started by running', 'start'),
            ('If anything goes wrong at any point in the process then help is available through the issue tracker', 'help'),
            ('The people who currently maintain and contribute to the codebase are listed in the file AUTHORS', 'who')]
def draft_front():    # same facts, answer first
    return [('What: a tool that does X for Y; the history is in HISTORY.md', 'what'),
            ('Why: it is useful because it saves Z; background follows later in the document', 'why'),
            ('Start: run `tool init`; prerequisites are listed below this line', 'start'),
            ('Help: open an issue; response usually comes within days', 'help'),
            ('Who: maintained by the AUTHORS file; contributions welcome', 'who')]
def draft_plain():    # shorter lines, plain wording, answer first, one extra decorative line first
    return [('Tool X', None)] + [(l[:60], q) for l, q in draft_front()]
def captured(draft, K, L):
    got=set()
    for line,q in draft[:L]:
        words=line.split()[:K]
        key={'what':'What:','why':'Why:','start':'Start:','help':'Help:','who':'Who:'}
        if q in ('what','why','start','help','who'):
            # buried drafts expose the answer only if the answer's cue word is in the first K words
            cue={'what':'does','why':'useful','start':'started','help':'help','who':'maintain'}[q] if draft is DB else key[q]
            if cue in words or cue.rstrip(':') in [w.strip(':,') for w in words]: got.add(q)
    return len(got)
DB,DF,DP=draft_buried(),draft_front(),draft_plain()
rows=[]
for K,L in [(3,3),(3,6),(6,3),(6,6),(12,6)]:
    rows.append((K,L,captured(DB,K,L),captured(DF,K,L),captured(DP,K,L)))
    print('scan K=%d words L=%d lines: buried %d/5 front-loaded %d/5 plain %d/5'%rows[-1])
avg=lambda i: sum(r[i] for r in rows)/len(rows)
low_buried=all(r[2]<=2 for r in rows[:4])
front_wins=all(r[3]>=r[2] for r in rows) and any(r[3]>r[2] for r in rows)
break_case=rows[0][3]==3 and rows[0][4]==2   # tight budget: the 3 lines buy only 3 answers; a decorative top line costs one
plain_costs=rows[0][4]<rows[0][3]
ok = low_buried and front_wins and plain_costs
print('RESULT: %s front-loaded draft captures %.1f/5 vs buried %.1f/5 averaged over 5 scan budgets; a decorative first line costs 1 answer at (K=3,L=3): plain %d vs front %d'%('PASS' if ok else 'FAIL',avg(3),avg(2),rows[0][4],rows[0][3]))
