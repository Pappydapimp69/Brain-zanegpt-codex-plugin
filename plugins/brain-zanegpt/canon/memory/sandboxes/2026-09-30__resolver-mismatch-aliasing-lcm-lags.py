# PREDICTION (before run): resolver picks highest-priority available role among B (window 5 of 15) and C (window 4 of 20, offset 3), else A.
# Resolved action repeats with lcm(15,20)=60. Mismatch(hint vs action now) flags 0/600 at L=60,120 but >0 at L=15,20,30,40,45.
# Age tag (L>2) flags 600/600 at all of them. Breaker: L=2 age tag flags 0 (within threshold).
N=600
def act(t):
    if (t%20)>=3 and (t%20)<7: return 'C'
    if (t%15)<5: return 'B'
    return 'A'
def mism(L): return sum(1 for t in range(N) if act(t)!=act(t+L))
def age(L): return N if L>2 else 0
ok=True
for L in (2,15,20,30,40,45,60,120):
    print(L,"mismatch",mism(L),"age",age(L))
ok&=mism(60)==0 and mism(120)==0
ok&=all(mism(L)>0 for L in(15,20,30,40,45))
ok&=all(age(L)==N for L in(15,20,30,40,45,60,120)) and age(2)==0
print("RESULT: %s resolved-action mismatch aliases to 0 at lcm multiples 60,120 (>0 at 15..45); age tag flags all 600"%("PASS" if ok else "FAIL"))
