# Prediction (first): stacking 12 pure fifths (3/2) overshoots 7 octaves by the Pythagorean comma, 23.46 cents (+-0.01);
# closing the circle by flattening every fifth equally gives 12-TET fifth 700.00 cents; keeping 11 pure fifths pushes the whole
# error into one wolf fifth of 678.49 cents; quarter-comma meantone (fifth 696.58) makes the major third pure (386.31)
# but its wolf fifth is ~737.64 cents (built to BREAK "less wolf with smaller tempering": narrower fifths make the wolf WORSE).
from math import log2
def cents(r): return 1200*log2(r)
pure_fifth=cents(1.5)
comma=12*pure_fifth-7*1200
print(f"pure fifth {pure_fifth:.3f}; 12 fifths - 7 octaves = {comma:.3f} cents")
wolf_pyth=pure_fifth-comma
print(f"pythagorean wolf fifth {wolf_pyth:.3f}")
et=700.0
print(f"12-TET fifth {et:.3f}, each fifth flattened by {pure_fifth-et:.3f}")
qc=1200*log2(5**0.25)   # quarter-comma meantone fifth: four fifths = 2 octaves + pure major third (5/4)
wolf_qc=7*1200-11*qc
third_qc=4*qc-2*1200
print(f"quarter-comma fifth {qc:.3f}, 4 fifths-2 oct = third {third_qc:.3f} (pure {cents(1.25):.3f}), wolf {wolf_qc:.3f}")
# major third from 4 stacked fifths in each system
third_pyth=4*pure_fifth-2*1200; third_et=4*et-2400
print(f"major third: pythagorean {third_pyth:.2f}, 12-TET {third_et:.2f}, qc meantone {third_qc:.2f}, pure {cents(1.25):.2f}")
# total tempering of the 11 stacked fifths vs wolf deviation from pure fifth
dev_pyth=abs(wolf_pyth-pure_fifth); dev_qc=abs(wolf_qc-pure_fifth)
ok=abs(comma-23.46)<0.01 and abs(wolf_pyth-678.49)<0.01 and abs(third_qc-386.31)<0.01 and abs(wolf_qc-737.64)<0.01 and dev_qc>dev_pyth
print("RESULT:","PASS" if ok else "FAIL",f"comma {comma:.2f}c; Pythagorean wolf {wolf_pyth:.2f}c ({dev_pyth:.2f} off pure); quarter-comma wolf {wolf_qc:.2f}c ({dev_qc:.2f} off) though its thirds are pure")
