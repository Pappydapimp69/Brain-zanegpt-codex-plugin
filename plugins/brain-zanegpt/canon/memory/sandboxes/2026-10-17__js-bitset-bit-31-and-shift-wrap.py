# Run 1 (prediction above) missed: got naive 2 false negatives (flags 31 and 63, both wrap to bit 31) and 31 false positives (flag 63 hides the 32nd). Run 2 prediction: exactly those counts.
# Runs REAL JavaScript (node) for a 64-flag bitset. Prediction (before run), for flags 0..63:
#  naive: one number, set |= 1<<i, has = (set & (1<<i)) > 0.
#   - set-then-test each flag alone: exactly 1 false negative (flag 31, since 1<<31 is negative so the AND is < 0).
#   - after setting flags 0..31, test flags 32..63: 32 false positives (shift count wraps mod 32, 1<<(i+32) === 1<<i).
#  fixed: two 32-bit words w[i>>5] |= 1<<(i&31), has = (w[i>>5] & (1<<(i&31))) !== 0: 0 false negatives, 0 false positives.
#  hybrid (BREAK): two words but keep the "> 0" test: still 1 false negative (flag 31 and flag 63), i.e. exactly 2 of 64.
# Hidden assumption: the failure is only at bit 31; wrong if the hybrid has other failing flags.
import json, subprocess
JS = r"""
const naive = {set(){return 0;}};
let fn = 0, fp = 0;
for (let i = 0; i < 64; i++) { let s = 0; s |= 1 << i; if (!((s & (1 << i)) > 0)) fn++; }
let s = 0; for (let i = 0; i < 32; i++) s |= 1 << i;
for (let i = 32; i < 64; i++) if ((s & (1 << i)) > 0) fp++;
let fnFix = 0, fpFix = 0, fnHyb = 0;
for (let i = 0; i < 64; i++) {
  const w = [0, 0]; w[i >> 5] |= 1 << (i & 31);
  if (!((w[i >> 5] & (1 << (i & 31))) !== 0)) fnFix++;
  if (!((w[i >> 5] & (1 << (i & 31))) > 0)) fnHyb++;
}
const w2 = [0, 0]; for (let i = 0; i < 32; i++) w2[0] |= 1 << i;
for (let i = 32; i < 64; i++) if ((w2[i >> 5] & (1 << (i & 31))) !== 0) fpFix++;
console.log(JSON.stringify({fn, fp, fnFix, fpFix, fnHyb}));
"""
out = json.loads(subprocess.run(["node", "-e", JS], capture_output=True, text=True, check=True).stdout)
print(out)
ok = out == {"fn": 2, "fp": 31, "fnFix": 0, "fpFix": 0, "fnHyb": 2}
print(f"RESULT: {'PASS' if ok else 'FAIL'} naive false negatives {out['fn']} false positives {out['fp']}; fixed {out['fnFix']}/{out['fpFix']}; hybrid false negatives {out['fnHyb']}")
