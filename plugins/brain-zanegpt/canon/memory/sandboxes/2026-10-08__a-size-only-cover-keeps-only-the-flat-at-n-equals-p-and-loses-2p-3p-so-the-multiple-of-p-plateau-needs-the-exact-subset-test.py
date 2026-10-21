#!/usr/bin/env python3
"""Sandbox: does the size-only ("sloppy") cover keep the flats? Deterministic.
PREDICTION (written before the check): the size-only cover (cut decided by comparing landing counts) ALSO has flats at every multiple of P for P in 5..12 (the plateau pattern is independent of the cover rule), but its total at N=P differs from the exact cover for every P.
Model (verbatim from the recorded family): lands(P,T,w,L)=[t+L for t in range(T) if t%P>=w or (t+L)%P<w]; for each width w in 1..P-1 and lag pair a<b<=N: last = b if V[b] else (a if V[a] else 0); cut = b if not covered(V[b],V[a]) else (a if V[a] else 0); shadow += (last!=cut); total = sum over T=base+r, r in range(P). average = total/P. Implemented in C (bitsets), needs gcc. "Flat at N" means total[N]==total[N-1].
"""
import os, subprocess, tempfile
from fractions import Fraction as F
C_SRC = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
// usage: cover P base Nmax  -> prints N total (sum over r in [0,P), w in [1,P), pairs a<b<=N of last!=cut with exact subset cover)
int main(int argc,char**argv){
  int P=atoi(argv[1]); long base=atol(argv[2]); int Nmax=atoi(argv[3]); int mode=argc>4?atoi(argv[4]):0;
  long *tot=calloc(Nmax+2,sizeof(long));
  for(int r=0;r<P;r++){
    long T=base+r; long nbits=T+Nmax+2; long W=nbits/64+1;
    uint64_t *V=calloc((size_t)(Nmax+1)*W,sizeof(uint64_t)); long *cnt=calloc(Nmax+1,sizeof(long));
    for(int w=1;w<P;w++){
      memset(V,0,(size_t)(Nmax+1)*W*sizeof(uint64_t)); memset(cnt,0,(Nmax+1)*sizeof(long));
      for(int L=1;L<=Nmax;L++) for(long t=0;t<T;t++){ if((t%P)>=w || ((t+L)%P)<w){ long pos=t+L; V[(size_t)L*W+pos/64]|=(uint64_t)1<<(pos%64); cnt[L]++; } }
      for(int b=2;b<=Nmax;b++){
        long add=0;
        for(int a=1;a<b;a++){
          int last = cnt[b]? b : (cnt[a]? a : 0);
          int sub=1; for(long k=0;k<W;k++){ if(V[(size_t)b*W+k] & ~V[(size_t)a*W+k]){sub=0;break;} }
          if(mode==1) sub = (cnt[b]<=cnt[a]); int cut = !sub ? b : (cnt[a]? a : 0);
          add += (last!=cut);
        }
        tot[b]+=add;   // pairs with this b; cumulative handled below
      }
    }
    free(V); free(cnt);
  }
  long run=0; for(int N=1;N<=Nmax;N++){ run+=tot[N]; printf("%d %ld\n",N,run); }
  return 0; }
'''
_exe=None
def build():
    global _exe
    if _exe: return _exe
    d=tempfile.mkdtemp(); open(os.path.join(d,"c.c"),"w").write(C_SRC); _exe=os.path.join(d,"c")
    subprocess.run(["gcc","-O2","-o",_exe,os.path.join(d,"c.c")],check=True); return _exe
def run(P,base,Nmax,mode=0):
    out=subprocess.run([build(),str(P),str(base),str(Nmax),str(mode)],capture_output=True,text=True,check=True).stdout.split("\n")
    return {int(l.split()[0]):int(l.split()[1]) for l in out if l.strip()}
def flats(d,Nmax): return [N for N in range(2,Nmax+1) if d[N]==d[N-1]]
def solve(xs,ys):
    n=len(xs); A=[[F(x)**k for k in range(n)]+[F(y)] for x,y in zip(xs,ys)]
    for i in range(n):
        p=next(r for r in range(i,n) if A[r][i]!=0); A[i],A[p]=A[p],A[i]; A[i]=[v/A[i][i] for v in A[i]]
        for r in range(n):
            if r!=i: A[r]=[a-A[r][i]*b for a,b in zip(A[r],A[i])]
    return [A[i][n] for i in range(n)]
def ev(c,x): return sum(ci*F(x)**k for k,ci in enumerate(c))

fl_all=True; differ=True; rows={}
for P in range(5,13):
    Nm=4*P+1; ex=run(P,5051,Nm,0); sl=run(P,5051,Nm,1)
    f=flats(sl,Nm); rows[P]=f
    fl_all&=(f==[k*P for k in range(1,5)]); differ&=(sl[P]!=ex[P])
print("sloppy flats:",{P:rows[P] for P in (5,8,12)},"| differs at N=P for all P:",differ)
print(("RESULT: PASS " if fl_all and differ else "RESULT: FAIL ")+f"size-only cover keeps flats at every multiple of P: {fl_all} (it has a single flat at N=P: {all(rows[P]==[P] for P in rows)}); its total at N=P differs from the exact cover for every P: {differ}")
