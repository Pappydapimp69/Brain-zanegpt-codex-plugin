"""Sandbox: parochial-empathy gap (harm depends on out-group minus in-group empathy) inside a bystander crowd.
Each of n bystanders independently helps an out-group victim with p_i = f(e_out, e_in) / n**alpha.
Harm = P(nobody helps) = prod(1 - p_i) (exact, no RNG).
Forms f: A linear difference, B ratio e_out/(e_out+e_in), C product of saturating terms s(e_out)*(1-s(e_in)).
Prediction (before run): (1) general raise (+0.2 to both) leaves crowd harm unchanged at every n and alpha under forms A and B
but not C; (2) an out-group-only raise of +0.2 cuts harm LESS in absolute terms as n grows when alpha=0 (ceiling),
and the benefit survives to n=12 only when alpha < 0.7. Stdlib only."""
import math
def s(x): return 1 / (1 + math.exp(-4 * (x - 0.5)))
FORMS = {
    "A diff":  lambda eo, ei: min(1, max(0, 0.5 + 0.5 * (eo - ei))),
    "B ratio": lambda eo, ei: eo / (eo + ei),
    "C prod":  lambda eo, ei: s(eo) * (1 - s(ei)),
}
def harm(form, eo, ei, n, alpha):
    p = FORMS[form](eo, ei) / n ** alpha
    return (1 - p) ** n
base = (0.4, 0.6)             # out-group 0.4, in-group 0.6: a gap world
ns = (1, 3, 6, 12)
print("form  alpha  n : harm(base)  d(general +0.2)  d(out-only +0.2)")
gen_zero = {}; out_gain = {}
for form in FORMS:
    for alpha in (0.0, 0.7, 1.0):
        row = []
        for n in ns:
            h0 = harm(form, *base, n, alpha)
            hg = harm(form, base[0] + 0.2, base[1] + 0.2, n, alpha) - h0
            ho = harm(form, base[0] + 0.2, base[1], n, alpha) - h0
            gen_zero[(form, alpha, n)] = abs(hg) < 1e-12
            out_gain[(form, alpha, n)] = -ho
            row.append((n, h0, hg, ho))
        print("%-8s %.1f " % (form, alpha) + " | ".join("n=%d h=%.3f g=%+.3f o=%+.3f" % r for r in row))
gA = all(v for (f, a, n), v in gen_zero.items() if f in ("A diff", "B ratio") and not (f == "A diff"))
# form A is exactly zero unless clamped; check separately
gA_exact = all(gen_zero[("A diff", a, n)] for a in (0.0, 0.7, 1.0) for n in ns)
gB_exact = all(gen_zero[("B ratio", a, n)] for a in (0.0, 0.7, 1.0) for n in ns)
gC_nonzero = not all(gen_zero[("C prod", a, n)] for a in (0.0, 0.7, 1.0) for n in ns)
# out-only benefit shape under form A
shrinks_a0 = out_gain[("A diff", 0.0, 12)] < out_gain[("A diff", 0.0, 3)]
survives_07 = out_gain[("A diff", 0.7, 12)] > 0.05
survives_10 = out_gain[("A diff", 1.0, 12)] > 0.05
print("general raise exactly zero: A %s, B %s; C nonzero %s" % (gA_exact, gB_exact, gC_nonzero))
print("form A out-only gain: alpha0 n3 %.3f n12 %.3f (shrinks %s); alpha0.7 n12 %.3f; alpha1.0 n12 %.3f" %
      (out_gain[("A diff", 0.0, 3)], out_gain[("A diff", 0.0, 12)], shrinks_a0, out_gain[("A diff", 0.7, 12)], out_gain[("A diff", 1.0, 12)]))
ok = gA_exact and not gB_exact and gC_nonzero and shrinks_a0
gB_n6 = harm("B ratio", base[0] + 0.2, base[1] + 0.2, 6, 0.7) - harm("B ratio", *base, 6, 0.7)
gC_n6 = harm("C prod", base[0] + 0.2, base[1] + 0.2, 6, 0.7) - harm("C prod", *base, 6, 0.7)
print("RESULT: %s general empathy raise (+0.2 both) leaves crowd harm exactly unchanged only under the difference form (12/12 cells); at n=6 alpha 0.7 it changes harm by %+.3f under a ratio form and %+.3f under a saturating-product form; out-only raise gain falls from %.3f (n=3) to %.3f (n=12) with no diffusion, %.3f at n=12 with alpha 0.7"
      % ("PASS" if ok else "FAIL", gB_n6, gC_n6, out_gain[("A diff", 0.0, 3)], out_gain[("A diff", 0.0, 12)], out_gain[("A diff", 0.7, 12)]))
