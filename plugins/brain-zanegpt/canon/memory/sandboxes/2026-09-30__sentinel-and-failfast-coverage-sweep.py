# PREDICTION (before run): 12 cases; best-option per case = dict-max of option scores; cases 3,7,10 have no winner (all scores 0 -> None);
# case 5 is deliberately divergent (raises). True: 4 distinct options cover 8 winning cases, 3 no-winner, 1 divergent-error.
# Naive (str-coerce sentinel, fail-fast) aborts at case 5 -> processes 5 of 12, coverage counts phantom 'None' (distinct=4 incl. phantom from case 3).
# Naive-nofailfast still counts phantom: distinct 5 instead of 4. Guarded+continue reports distinct=4, no_winner=3, errors=1.
OPTS=['A','B','C','D']
def scores(i):
    if i in(3,7,10): return {o:0 for o in OPTS}
    if i==5: raise ValueError("divergent witness")
    return {o:(1 if o==OPTS[(i*3)%4] else 0)+ (0 if o!=OPTS[i%4] else 0) for o in OPTS}
def best(i):
    s=scores(i); m=max(s.values())
    return None if m==0 else max(s,key=s.get)
def naive(failfast):
    seen=set(); n=0
    for i in range(12):
        try: w=best(i)
        except ValueError:
            if failfast: break
            continue
        seen.add(str(w)); n+=1
    return n,len(seen),sorted(seen)
def guarded():
    seen=set(); nw=err=n=0
    for i in range(12):
        try: w=best(i)
        except ValueError: err+=1; continue
        n+=1
        if w is None: nw+=1; continue
        seen.add(w)
    return n,len(seen),nw,err,sorted(seen)
a=naive(True); b=naive(False); g=guarded()
print("naive+failfast",a); print("naive",b); print("guarded",g)
ok = a[0]==5 and b[0]==11 and 'None' in b[2] and g[1]==b[1]-1 and g[2]==3 and g[3]==1 and g[0]==11
# breaker: with no no-winner cases the naive and guarded distinct counts agree
def best_nowin(i): return OPTS[i%4]
ok &= len({str(best_nowin(i)) for i in range(12)})==len({best_nowin(i) for i in range(12)})
print("RESULT: %s naive tally counts phantom 'None' (distinct %d vs true %d) and fail-fast covers 5 of 12 cases; guarded covers 11 with no_winner=3 errors=1"%("PASS" if ok else "FAIL",b[1],g[1]))
