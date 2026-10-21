# Own fixture: 12 rules, 3 classes x 4; window = 4 candidate fixes per class (one per rule). Counted guard calls only.
RULES=[(c,i) for c in range(3) for i in range(4)]
def guard_calls(rule,fmt):
    calls=1                                   # the refused action itself
    if fmt=="RULE": return calls+1            # name+remedy -> one corrected action passes
    cls=rule[0]; cands=[(cls,i) for i in range(4)]
    for k,c in enumerate(cands,1):            # actor tries class candidates in fixed order
        calls+=1
        if c==rule: return calls
    raise AssertionError
cat=sum(guard_calls(r,"CAT") for r in RULES)/12; rl=sum(guard_calls(r,"RULE") for r in RULES)/12
ratio=rl/cat
# secret numeric threshold T in 1..100: operand-free message = binary search on pass/fail; matched value = read directly
def probes_secret(T,leak):
    if leak: return 1
    lo,hi,n=1,100,0
    while lo<hi:
        mid=(lo+hi)//2; n+=1
        if mid>=T: hi=mid
        else: lo=mid+1
    return n
mean_noleak=sum(probes_secret(T,False) for T in range(1,101))/100
mean_leak=sum(probes_secret(T,True) for T in range(1,101))/100
# hidden flag: rule 9 only fires when flag set. a message listing EVERY matched rule reveals flag; first-match only does not.
def flag_leak(flag,list_all):
    matched=[5] + ([9] if flag else [])
    shown=matched if list_all else matched[:1]
    return (9 in shown)==flag, 9 in shown
inf_all=sum(flag_leak(f,True)[1]==f for f in (False,True))
inf_first=[flag_leak(f,False)[1] for f in (False,True)]
print("calls CAT",cat,"RULE",rl,"ratio",round(ratio,3))
print("secret probes no-operand",mean_noleak,"matched-value",mean_leak)
print("flag inferable with list-all:",inf_all==2,"; with first-match shown values:",inf_first)
ok=(abs(ratio-0.571)<0.01 and mean_noleak/mean_leak>=5 and inf_all==2 and inf_first==[False,False])
print(f"RESULT: {'PASS' if ok else 'FAIL'} rule/cat guard-call ratio {ratio:.3f} (window 4); secret threshold {mean_noleak:.1f} probes vs {mean_leak:.0f} with operand leaked; list-all leaks hidden flag, first-match does not")
