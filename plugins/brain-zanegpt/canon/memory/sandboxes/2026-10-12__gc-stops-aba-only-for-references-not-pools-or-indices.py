"""Edge pass: ideas CONCURRENCY/definition-and-aba (lock-free is a progress guarantee; ABA breaks CAS)
with sandbox-kernel-concurrency E2 and E4 (version tags fail when changes wrap the tag). New angle: the
common claim that a garbage-collected language is immune to ABA. Deterministic, exhaustive: a Treiber
stack holding A -> B -> C. T1 starts pop(): reads head = A and next = B, then stalls. T2 runs EVERY
sequence of 1..5 operations from {pop, push(new)}; then T1 does CAS(head, A, B). Corruption = the CAS
succeeds although the stack changed (head is A again, but B is no longer A's successor / has been freed).
Allocation modes for T2's push(new):
  gc       a fresh object; the old A cannot be reused while T1 still references it
  pool     nodes recycled from a free list (LIFO), as object pools in GC languages do
  index    nodes are slots in a preallocated array; CAS compares slot numbers; freed slots recycled
  tag4     pool plus a 4-bit version tag on head (E2/E4), compared with the slot
  (iteration 2: pools/indices recycle FIFO -- a LIFO free list under a LIFO stack rebuilt the same chain in
   every sequence, an artefact; 'gc-repush' lets T2 push back an object it popped, which GC allows.)
Predictions written before running:
 P1 gc mode: 0 corrupt CAS successes over all sequences.
 P2 pool and index modes: > 0, and equal (an index IS a recycled identity).
 P3 the 4-bit tag removes every corruption at these short lengths (<= 5 head changes < 16).
"""
from itertools import product

def run(seq, mode, fifo=True):
    nodes = {"A": "B", "B": "C", "C": None}       # id -> next
    head, tag = "A", 0
    free, fresh = [], 0
    t1_head, t1_next, t1_tag = head, nodes[head], tag
    for op in seq:
        if op == "pop":
            if head is None: continue
            old = head; head = nodes[old]; tag = (tag + 1) % 16
            free.append(old) if mode != "gc" else None
            del nodes[old]
        else:
            if mode == "gc-repush" and free and op == "repush":
                nid = free.pop(0)
            elif mode in ("gc", "gc-repush") or not free:
                fresh += 1; nid = f"N{fresh}"
            else:
                nid = free.pop(0) if fifo else free.pop()
            nodes[nid] = head; head = nid; tag = (tag + 1) % 16
    # T1's CAS
    match = head == t1_head and (mode != "tag4" or tag == t1_tag)
    if not match:
        return False
    # success: is it corrupt? correct only if the stack is unchanged (A still head AND A.next still B and B alive)
    unchanged = nodes.get(t1_head) == t1_next and t1_next in nodes
    return not unchanged

res = {}
for mode in ("gc", "pool", "index", "tag4", "pool-lifo", "gc-repush"):
    bad = total = 0
    ops = ("pop", "push", "repush") if mode == "gc-repush" else ("pop", "push")
    for L in range(1, 6):
        for seq in product(ops, repeat=L):
            total += 1
            m = {"index": "pool", "pool-lifo": "pool"}.get(mode, mode)
            bad += run(seq, m, fifo=(mode != "pool-lifo"))
    res[mode] = (bad, total)
    print(f"{mode:5s}: corrupt CAS successes {bad} of {total} interfering sequences")
p1 = res["gc"][0] == 0
p2 = res["pool"][0] > 0 and res["pool"][0] == res["index"][0]
p3 = res["tag4"][0] == 0
checks = [("P1 gc has no ABA", p1), ("P2 pool and index both corrupt, equally", p2), ("P3 4-bit tag clears short runs", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; corrupt of {res['gc'][1]}: gc {res['gc'][0]} pool(fifo) {res['pool'][0]} index {res['index'][0]} tag4 {res['tag4'][0]} pool-lifo {res['pool-lifo'][0]}; gc-repush {res['gc-repush'][0]} of {res['gc-repush'][1]}")
