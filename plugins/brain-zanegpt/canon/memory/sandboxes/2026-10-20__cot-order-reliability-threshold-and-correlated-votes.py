from math import comb
D=6; G=0.1
SIZES={'S':(1,0.55),'M':(2,0.80),'L':(4,0.93),'XL':(8,0.99)}   # (steps per forward pass k, per-step reliability r)
def answer_first(k,r,d=D): return r**min(d,k)*G**max(0,d-k)
def cot_before(k,r,d=D): return r**d                         # reasoning tokens carry every step
def cot_after(k,r,d=D): return answer_first(k,r,d)           # rationale written after the answer cannot change it
print('size  ans-first  cot-before  cot-after  gain')
gains={}
for n,(k,r) in SIZES.items():
    a,b,c=answer_first(k,r),cot_before(k,r),cot_after(k,r);gains[n]=b-a
    print('%-4s  %.4f      %.4f      %.4f    %+.4f'%(n,a,b,c,b-a))
# self-consistency: m votes on a chain; errors are independent per sample vs share a root (same wrong first step)
def majority(p,m): return sum(comb(m,i)*p**i*(1-p)**(m-i) for i in range(m//2+1,m+1))
k,r=SIZES['L'];p=cot_before(k,r)
indep=majority(p,5)
shared=0.7*p+0.3*majority(p,5)   # 30% of chains hit a shared wrong root that every sample inherits; then all 5 agree on wrong
print('L single %.4f  5-vote independent %.4f  5-vote shared-root %.4f'%(p,indep,shared))
# the shared-root case cannot exceed 1-0.3 + ... : cap
cap=0.7+0.3*majority(p,5)
order_ok = cot_after(*SIZES['L'])==answer_first(*SIZES['L']) and shared<indep and indep>p
monotone = gains['S']<gains['M']<gains['L']<gains['XL']       # the kernel's "gains scale sharply with size"
print('RESULT: %s kernel claim of gains growing with size %s: gains S %+.2f M %+.2f L %+.2f XL %+.2f at depth %d (hump, zero once k>=depth); order claim %s (cot-after = answer-first); 5 votes lift L %.2f->%.2f independent but only %.2f with a shared root'%(
 'PASS' if (monotone and order_ok) else 'FAIL','holds' if monotone else 'does not hold',gains['S'],gains['M'],gains['L'],gains['XL'],D,'holds' if order_ok else 'fails',p,indep,shared))
