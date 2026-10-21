# Does a second positive result rescue a low-prevalence posterior? Exact fractions, no RNG. Stdlib only.
# Independent repeat: false positives are independent across tests. Correlated repeat: with prob rho the second
# test just repeats the first test's outcome (same pipeline / same p-hacked analysis), else it is independent.
from fractions import Fraction as F

def post(prev, sens, fpr, rho):
    # P(two positives | H) and P(two positives | not H) with copy-probability rho
    tp = sens * (rho + (1 - rho) * sens)
    fp = fpr * (rho + (1 - rho) * fpr)
    num = prev * tp
    return num / (num + (1 - prev) * fp)

def single(prev, sens, fpr):
    return prev * sens / (prev * sens + (1 - prev) * fpr)

cases = {  # (prev, sens, fpr)
    'casscells 1/1000, fpr 5%':        (F(1, 1000), F(1), F(5, 100)),
    'gynecologists 1%, 90%, 9%':       (F(1, 100), F(9, 10), F(9, 100)),
    'p-hacked 10%, sens 80%, fpr 60.7%': (F(1, 10), F(8, 10), F(607, 1000)),
}
res = {}
for name, (p, s, f) in cases.items():
    one = single(p, s, f)
    ind = post(p, s, f, F(0))
    half = post(p, s, f, F(1, 2))
    full = post(p, s, f, F(1))
    res[name] = (one, ind, half, full)
    print('%-36s one=%.4f  two-indep=%.4f  two-rho.5=%.4f  two-rho1=%.4f' % ((name,) + tuple(float(x) for x in res[name])))
# how many independent positives to reach 50% for each case, vs correlated rho=1 (never moves)
def needed(p, s, f, rho_full=False, cap=40):
    cur = p
    for n in range(1, cap + 1):
        cur = cur * s / (cur * s + (1 - cur) * f)
        if cur >= F(1, 2): return n
        if rho_full: break
    return None
for name, (p, s, f) in cases.items():
    print('%-36s independent positives to reach 50%%: %s ; fully-correlated repeats: %s'
          % (name, needed(p, s, f), 'never (stays %.4f)' % float(single(p, s, f))))
# break: a p-hacked pipeline's repeat with a LOW prior never gets there even independently?
n_ph = needed(*cases['p-hacked 10%, sens 80%, fpr 60.7%'])
ok = (res['gynecologists 1%, 90%, 9%'][1] > 4 * res['gynecologists 1%, 90%, 9%'][0] / 2     # two independent roughly doubles+ the posterior
      and res['gynecologists 1%, 90%, 9%'][3] == res['gynecologists 1%, 90%, 9%'][0]        # rho=1 adds nothing, exactly
      and res['casscells 1/1000, fpr 5%'][3] == res['casscells 1/1000, fpr 5%'][0]
      and res['p-hacked 10%, sens 80%, fpr 60.7%'][1] < F(1, 2) and n_ph is not None and n_ph > 2)
print('RESULT: %s two independent positives lift the gynecologist posterior %.3f -> %.3f and Casscells %.4f -> %.4f but a fully correlated repeat leaves every posterior exactly unchanged; the p-hacked case at 10%% prior stays %.3f after two independent positives and needs %s'
      % ('PASS' if ok else 'FAIL',
         float(res['gynecologists 1%, 90%, 9%'][0]), float(res['gynecologists 1%, 90%, 9%'][1]),
         float(res['casscells 1/1000, fpr 5%'][0]), float(res['casscells 1/1000, fpr 5%'][1]),
         float(res['p-hacked 10%, sens 80%, fpr 60.7%'][1]), n_ph))
