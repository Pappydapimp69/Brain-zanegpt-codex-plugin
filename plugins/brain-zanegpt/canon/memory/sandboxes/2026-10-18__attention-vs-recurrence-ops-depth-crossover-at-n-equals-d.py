# Deterministic op-and-depth counter. Values carry a ready-time (critical path). One "mac" = one multiply-add.
# Recurrent layer: h_t = f(W h_{t-1} + U x_t): d*d + d*d macs per step, depends on h_{t-1}.
# Self-attention layer: scores (n*n*d macs), weighted sum (n*n*d macs), all scores depend only on inputs.
class Ctr:
    def __init__(s): s.macs = 0
def rnn(n, d):
    c = Ctr(); t_h = 0; first_reaches_last = 0
    for t in range(n):
        c.macs += 2*d*d
        t_h = max(t_h, 0) + 1            # needs previous hidden state -> chain
    return c.macs, t_h, n                 # macs, sequential depth, path length token1->tokenn
def attn(n, d):
    c = Ctr(); c.macs += 2*n*n*d
    return c.macs, 3, 1                   # QK^T, softmax, AV in sequence = depth 3; every token sees every token in 1 hop
res = {}
for d in (16, 64, 256):
    cross = next((n for n in range(1, 4096) if attn(n, d)[0] > rnn(n, d)[0]), None)
    res[d] = cross
    print(f"d={d}: attention macs exceed recurrent macs first at n={cross}")
n = 512
for d in (64,):
    a, r = attn(n, d), rnn(n, d)
    print(f"n={n} d={d}: attn macs={a[0]} depth={a[1]} path={a[2]} | rnn macs={r[0]} depth={r[1]} path={r[2]}")
# Chinchilla-style training budget C = 6*N_params*D_tokens, D = 20*N: at fixed C, depth per token-step is what parallelism can hide.
C = 1e21; Nopt = (C/(6*20))**0.5; Dopt = 20*Nopt
print(f"compute-optimal at C=1e21: params={Nopt:.3e} tokens={Dopt:.3e} ratio={Dopt/Nopt:.0f}")
# Break scenario: long contexts. Attention loses on macs once n>d, while its depth win remains.
a_long, r_long = attn(4096, 64), rnn(4096, 64)
print(f"n=4096 d=64: attn macs / rnn macs = {a_long[0]/r_long[0]:.1f}, depth ratio rnn/attn = {r_long[1]/a_long[1]:.0f}")
ok = all(res[d] == d + 1 for d in res) and a_long[0] > r_long[0] and r_long[1] > a_long[1] and abs(Dopt/Nopt-20) < 1e-9
print(f"RESULT: {'PASS' if ok else 'FAIL'} attention macs overtake recurrent exactly at n=d+1 ({res}); n=4096,d=64 attention costs {a_long[0]/r_long[0]:.0f}x the macs but rnn depth is {r_long[1]/a_long[1]:.0f}x deeper")
