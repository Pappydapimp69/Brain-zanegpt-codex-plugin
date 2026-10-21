# FILM pipeline kernel: one render(t), one dialogue table, one clock. Push it until it stops holding.
# A "frame" here is a tuple of quantised draw parameters (character x, mouth openness, caption id,
# camera shake) hashed with sha1, standing in for the PNG the canvas page would write.
import hashlib, math, random

FPS = 24
SR = 48000
DIALOGUE = [  # (start seconds, speaker, line)  -- one table drives frames AND audio
    (1.000, "A", "we should not open the box"),
    (4.250, "B", "we are opening the box"),
    (9.130, "A", "the box was a mistake"),
    (40.000, "B", "we are opening the box"),        # callback, frame-aligned start
    (61.010, "B", "we are opening the box"),        # callback, start NOT on the 1/24 s grid
    (222.900, "A", "that was the last box"),
]
CPS = 14.0   # blip-voice characters per second

def line_at(t):
    for s, who, text in DIALOGUE:
        if s <= t < s + len(text) / CPS:
            return s, who, text
    return None

def mouth(t):
    ln = line_at(t)
    if not ln:
        return 0
    s, who, text = ln
    k = int((t - s) * CPS)
    ch = text[k] if k < len(text) else " "
    blip = abs(math.sin(2 * math.pi * 7.0 * (t - s)))       # local-time envelope of the blip voice
    return 0 if ch == " " else round(blip * 8)

def render(t):
    ln = line_at(t)
    who = ln[1] if ln else "-"
    cap = ln[2] if ln else ""
    x = round(100 + 40 * math.sin(2 * math.pi * t / 6.0), 1)
    return (who, cap, mouth(t), x)

def h(fr):
    return hashlib.sha1(repr(fr).encode()).hexdigest()

N = int(230 * FPS)
seq = [h(render(i / FPS)) for i in range(N)]

# S1 pure render(t): shuffled order and a random seek give byte-identical frames
order = list(range(N)); random.Random(7).shuffle(order)
shuf = {i: h(render(i / FPS)) for i in order}
s1_mismatch = sum(1 for i in range(N) if shuf[i] != seq[i])

# S2 stateful renderer (x integrated by dt each call, as in an rAF loop) under the same shuffle
class Stateful:
    def __init__(self): self.x = 100.0; self.last = 0.0
    def render(self, t):
        dt = t - self.last; self.last = t
        self.x += 40 * (2 * math.pi / 6.0) * math.cos(2 * math.pi * t / 6.0) * dt
        ln = line_at(t)
        return (ln[1] if ln else "-", ln[2] if ln else "", mouth(t), round(self.x, 1))
st = Stateful(); st_seq = [h(st.render(i / FPS)) for i in range(N)]
st2 = Stateful(); st_shuf = {i: h(st2.render(i / FPS)) for i in order}
s2_mismatch = sum(1 for i in range(N) if st_shuf[i] != st_seq[i])
s2_vs_pure = sum(1 for i in range(N) if st_seq[i] != seq[i])

# S3 one clock: audio sample offset and frame index both derived from the table start time
def av_err_ms(quant):
    errs = []
    for s, _, _ in DIALOGUE:
        f = quant(s * FPS); a = round(s * SR)
        errs.append(abs(f / FPS - a / SR) * 1000)
    return max(errs)
round_err = av_err_ms(round)
floor_err = av_err_ms(int)
worst_round = 1000 / FPS / 2; worst_floor = 1000 / FPS

# S4 BREAK: frames rendered for 24 fps but muxed as 24000/1001; audio keeps its own 48 kHz clock
mux = 24000 / 1001
def lead_ms(s):   # audio lead = where the frame is shown minus where the audio plays
    f = round(s * FPS)
    return (f / mux - round(s * SR) / SR) * 1000
leads = [(s, lead_ms(s)) for s, _, _ in DIALOGUE]
cross45 = 45 / ((FPS / mux - 1) * 1000)    # seconds until drift alone reaches 45 ms

# S5 callbacks: does the repeated line re-render the first occurrence verbatim?
def clip(start, text):
    n = math.ceil(len(text) / CPS * FPS)
    f0 = math.ceil(start * FPS - 1e-9)
    return [h(render(i / FPS)[:3]) for i in range(f0, f0 + n)]   # ignore camera x, compare the performance
first = clip(4.250, DIALOGUE[1][2])
cb_aligned = clip(40.000, DIALOGUE[3][2])
cb_off = clip(61.010, DIALOGUE[4][2])
same_aligned = sum(a == b for a, b in zip(first, cb_aligned))
same_off = sum(a == b for a, b in zip(first, cb_off))
# start phase as a fraction of a frame (0.0 = on the 1/24 s grid); 4.250 s is 102 frames, on grid
phase = {s: round((s * FPS) % 1, 4) for s, _, _ in DIALOGUE}

print("S1 pure render shuffled vs sequential mismatched frames: %d/%d" % (s1_mismatch, N))
print("S2 stateful render shuffled vs sequential mismatched: %d/%d; stateful vs pure (sequential): %d/%d"
      % (s2_mismatch, N, s2_vs_pure, N))
print("S3 max A/V offset round() %.2f ms (bound %.1f), int() %.2f ms (bound %.1f)"
      % (round_err, worst_round, floor_err, worst_floor))
print("S4 24 fps muxed as 23.976: lead at each line", [(s, round(l, 1)) for s, l in leads],
      "; drift alone hits 45 ms at %.1f s" % cross45)
print("S5 start phases (frac of a frame):", phase)
print("S5 callback frames identical to first occurrence: aligned %d/%d, off-grid +10 ms %d/%d"
      % (same_aligned, len(first), same_off, len(first)))

ok = (s1_mismatch == 0 and s2_mismatch > N // 2 and round_err <= worst_round + 1e-9 and floor_err <= worst_floor
      and same_aligned == len(first) and same_off < len(first) and leads[-1][1] > 45)
print("RESULT: %s pure shuffle mismatch %d/%d, stateful %d/%d; A/V round %.1f ms int %.1f ms; 23.976 mux lead %.0f ms at %.0f s (45 ms at %.0f s); callback aligned %d/%d off-grid %d/%d"
      % ("PASS" if ok else "FAIL", s1_mismatch, N, s2_mismatch, N, round_err, floor_err, leads[-1][1], leads[-1][0],
         cross45, same_aligned, len(first), same_off, len(first)))
