# EAN-13 check digit (weights 1,3 alternating) vs an unweighted digit-sum mod 10 check. Exhaustive over a fixed code set.
def ean(d12): return (10-sum(int(c)*(3 if i%2 else 1) for i,c in enumerate(d12))%10)%10
def plain(d12): return (10-sum(int(c) for c in d12)%10)%10
codes=['%012d'%n for n in range(0,10**12,999999937)][:1000]   # deterministic spread, 1000 codes
def single_errors(f):
    miss=tot=0
    for c in codes:
        full=c+str(f(c))
        for i in range(13):
            for r in '0123456789':
                if r==full[i]: continue
                mut=full[:i]+r+full[i+1:]
                tot+=1; miss+= f(mut[:12])==int(mut[12]) if i<12 else mut[12]==str(f(c))
    return miss,tot
def swaps(f):
    miss=tot=0; byd={}
    for c in codes:
        full=c+str(f(c))
        for i in range(12):
            if full[i]==full[i+1]: continue
            mut=full[:i]+full[i+1]+full[i]+full[i+2:]
            tot+=1; m = f(mut[:12])==int(mut[12]); miss+=m
            k=abs(int(full[i])-int(full[i+1])); byd[k]=byd.get(k,[0,0]); byd[k][0]+=m; byd[k][1]+=1
    return miss,tot,byd
se,sn=single_errors(ean)[0],single_errors(ean)[1]
pe=single_errors(plain)[0]
em,et,byd=swaps(ean); pm,pt,_=swaps(plain)
only5=all((v[0]==v[1]) if k==5 else v[0]==0 for k,v in byd.items())
print('single-digit errors: ean missed',se,'of',sn,'; plain-sum missed',pe)
print('adjacent swaps (unequal digits): ean missed %d/%d = %.3f ; plain-sum missed %d/%d'%(em,et,em/et,pm,pt))
print('ean misses by digit gap',{k:tuple(v) for k,v in sorted(byd.items())})
ok = se==0 and pe==0 and only5 and pm==pt and 0.09<em/et<0.14
print('RESULT: %s EAN-13 missed %d/%d single-digit errors and %d/%d adjacent swaps, all with digit gap 5; unweighted sum missed %d/%d swaps'%('PASS' if ok else 'FAIL',se,sn,em,et,pm,pt))
