import random
titles=["alpha rule","beta rule","gamma rule","delta rule","epsilon rule","zeta rule","eta rule","theta rule"]
headers={55+i:t for i,t in enumerate(titles)}           # id -> title, from project file headers
def positional(index_lines):   # assign ids by order of appearance
    return {t:55+i for i,t in enumerate(index_lines)}
def by_text(index_lines):      # match the title text against headers
    inv={t:i for i,t in headers.items()}
    return {t:inv[t] for t in index_lines}
truth={t:i for i,t in headers.items()}
def wrong(m): return sum(m[t]!=truth[t] for t in m)
orders={'in order':list(titles),'reversed':titles[::-1],'swap first two':[titles[1],titles[0]]+titles[2:],
        'rotate by 3':titles[3:]+titles[:3]}
tot=0
for k,o in orders.items():
    p,b=wrong(positional(o)),wrong(by_text(o)); tot+=b
    print(k,'positional wrong',p,'by-text wrong',b)
ok=wrong(positional(orders['in order']))==0 and wrong(positional(orders['reversed']))==8 and wrong(positional(orders['rotate by 3']))==8 and wrong(positional(orders['swap first two']))==2 and tot==0
print('RESULT: %s positional wrong 0/8 in order, 8/8 reversed, 8/8 rotated, 2/8 one swap; by-text wrong %d'%('PASS' if ok else 'FAIL',tot))
