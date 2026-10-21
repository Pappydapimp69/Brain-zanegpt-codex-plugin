import math
# deterministic grid population: in-group and out-group empathy on 0..1
pop=[(i/9,j/9) for i in range(10) for j in range(10)]
def corr(x,y):
    n=len(x);mx=sum(x)/n;my=sum(y)/n
    sx=math.sqrt(sum((a-mx)**2 for a in x));sy=math.sqrt(sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/(sx*sy) if sx*sy else 0
def sig(z): return 1/(1+math.exp(-z))
procs={
 'gap_driven':lambda ei,eo: sig(6*(ei-eo)-1),
 'out_level_driven':lambda ei,eo: sig(6*(0.5-eo)),
 'in_level_driven':lambda ei,eo: sig(6*(ei-0.5)),  # BREAK: in-level alone drives harm
}
ins=[p[0] for p in pop];outs=[p[1] for p in pop];gaps=[a-b for a,b in pop]
res={}
for name,f in procs.items():
    h=[f(*p) for p in pop]
    res[name]=(corr(gaps,h),corr(outs,h),corr(ins,h))
    print(name,'r(gap,out,in)=%.2f %.2f %.2f'%res[name])
# crowd helping: per-person help prob = 1 - harm; group acts if any of n acts
def crowd(f,n):
    return sum(1-math.prod(f(*p) for _ in range(n)) for p in pop)/len(pop)
for n in (1,3,10):
    print('n',n,'P(someone helps) gap_driven=%.3f'%crowd(procs['gap_driven'],n))
ok=(res['gap_driven'][0]>abs(res['gap_driven'][1]) and res['gap_driven'][0]>abs(res['gap_driven'][2])
    and abs(res['in_level_driven'][0])<abs(res['in_level_driven'][2])+1e-9
    and crowd(procs['gap_driven'],10)>crowd(procs['gap_driven'],1))
print('RESULT: %s gap beats level only under gap-driven harm (r=%.2f vs out %.2f); level-driven worlds make gap a proxy (in-level r=%.2f); crowd of 10 raises help %.3f->%.3f'%(
 'PASS' if ok else 'FAIL',res['gap_driven'][0],res['gap_driven'][1],res['in_level_driven'][0],crowd(procs['gap_driven'],1),crowd(procs['gap_driven'],10)))
