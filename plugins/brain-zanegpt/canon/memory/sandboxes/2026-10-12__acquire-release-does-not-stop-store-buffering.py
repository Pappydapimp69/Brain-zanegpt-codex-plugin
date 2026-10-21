"""Edge pass: ideas CONCURRENCY/happens-before (without a happens-before edge a write may never be visible)
with sandbox-kernel-concurrency E6 (release/acquire visibility is transitive) and E3 (compilers differ on
plain flags). New angle: the store-buffering (Dekker) litmus test -- T1: x=1; r1=y.  T2: y=1; r2=x.
Release stores and acquire loads create no happens-before edge between a thread's OWN store and its
later load of a DIFFERENT variable, so r1 == r2 == 0 stays allowed; only seq_cst forbids it.
Real system: gcc and clang on this x86-64 machine. Deterministic part: the emitted assembly for the
store in each ordering (a fence/xchg or not). Real-hardware part: 200000 rounds per ordering, threads
released together by a spin barrier; we count rounds with r1 == r2 == 0.
Predictions written before running:
 P1 gcc and clang emit a plain mov for a release store and an xchg (or mov+mfence) for a seq_cst store.
 P2 the hardware shows r1 == r2 == 0 at least once under relaxed AND under release/acquire.
 P3 the hardware never shows it under seq_cst (0 of 200000).
"""
import os, re, subprocess, sys, tempfile

SRC = r'''
#include <stdatomic.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#ifndef ST
#define ST memory_order_relaxed
#define LD memory_order_relaxed
#endif
atomic_int x, y, go1, go2, done1, done2; int r1, r2;
void st_only(void){ atomic_store_explicit(&x, 1, ST); }
static void *t1(void *a){ long n=(long)a; for(long i=0;i<n;i++){ while(atomic_load_explicit(&go1,memory_order_acquire)!=i+1); atomic_store_explicit(&x,1,ST); r1=atomic_load_explicit(&y,LD); atomic_store_explicit(&done1,i+1,memory_order_release);} return 0; }
static void *t2(void *a){ long n=(long)a; for(long i=0;i<n;i++){ while(atomic_load_explicit(&go2,memory_order_acquire)!=i+1); atomic_store_explicit(&y,1,ST); r2=atomic_load_explicit(&x,LD); atomic_store_explicit(&done2,i+1,memory_order_release);} return 0; }
int main(int c, char **v){ long n=atol(v[1]); long both0=0; pthread_t a,b;
  pthread_create(&a,0,t1,(void*)n); pthread_create(&b,0,t2,(void*)n);
  for(long i=0;i<n;i++){ atomic_store(&x,0); atomic_store(&y,0);
    atomic_store_explicit(&go1,i+1,memory_order_release); atomic_store_explicit(&go2,i+1,memory_order_release);
    while(atomic_load_explicit(&done1,memory_order_acquire)!=i+1 || atomic_load_explicit(&done2,memory_order_acquire)!=i+1);
    if(r1==0 && r2==0) both0++; }
  pthread_join(a,0); pthread_join(b,0); printf("%ld\n", both0); return 0; }
'''
ORD = {"relaxed": ("memory_order_relaxed", "memory_order_relaxed"),
       "acqrel": ("memory_order_release", "memory_order_acquire"),
       "seqcst": ("memory_order_seq_cst", "memory_order_seq_cst")}
N = 200000
d = tempfile.mkdtemp()
src = os.path.join(d, "sb.c"); open(src, "w").write(SRC)

def store_asm(cc, o):
    out = subprocess.run([cc, "-O2", "-S", "-o", "-", f"-DST={ORD[o][0]}", f"-DLD={ORD[o][1]}", src],
                         capture_output=True, text=True, check=True).stdout
    body = out.split("st_only:")[1].split("ret")[0]
    return "xchg" in body or "mfence" in body

asm = {(cc, o): store_asm(cc, o) for cc in ("gcc", "clang") for o in ORD}
for (cc, o), fenced in asm.items():
    print(f"{cc:5s} {o:7s} store fenced (xchg/mfence): {fenced}")
hw = {}
for o in ORD:
    exe = os.path.join(d, o)
    subprocess.run(["gcc", "-O2", "-pthread", f"-DST={ORD[o][0]}", f"-DLD={ORD[o][1]}", src, "-o", exe], check=True)
    hw[o] = int(subprocess.run([exe, str(N)], capture_output=True, text=True, check=True).stdout)
    print(f"hardware {o:7s}: r1==r2==0 in {hw[o]} of {N} rounds")
p1 = all(not asm[(cc, "acqrel")] and asm[(cc, "seqcst")] for cc in ("gcc", "clang"))
p2 = hw["relaxed"] > 0 and hw["acqrel"] > 0
p3 = hw["seqcst"] == 0
checks = [("P1 release store unfenced, seq_cst fenced (gcc and clang)", p1), ("P2 SB outcome seen under relaxed and acq/rel", p2), ("P3 never under seq_cst", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; release store fenced gcc/clang {asm[('gcc','acqrel')]}/{asm[('clang','acqrel')]}, "
      f"seq_cst {asm[('gcc','seqcst')]}/{asm[('clang','seqcst')]}; r1=r2=0 relaxed {hw['relaxed']} acqrel {hw['acqrel']} seqcst {hw['seqcst']} of {N}")
