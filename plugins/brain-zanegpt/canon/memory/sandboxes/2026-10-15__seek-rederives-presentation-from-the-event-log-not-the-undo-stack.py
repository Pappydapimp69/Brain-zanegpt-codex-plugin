"""Sandbox: compose rpg-progression#E3 (animation/presentation state lives OUTSIDE the
undo history, so undo/redo never touch it) with edge-draft-opticon-scrub#E1 (on seek,
every stateful presentation stage must be RE-DERIVED, not carried).

A game session is recorded as a timestamped command log (move, cast, pull, undo, redo).
A replay viewer scrubs it. Authoritative state at time t is the history stack after
folding the log to t. The animation FSM (walk loop, attack once -> idle, idle loop;
play() resets on a clip change, same-clip play is a no-op) is driven by move/cast and is
never touched by undo/redo (E3's fix).

Seek strategies compared against continuous per-frame playback at every frame:
  carry      keep the animation as it was at the old playhead (no re-derivation)
  stack      re-derive from the AUTHORITATIVE state at t: replay play() over the
             commands currently on the history stack (undone ones are gone)
  log        re-derive from the RAW command log to t: replay play() over every move/cast
             ever issued, undone or not
Break scenario: playback advances the anim with a float accumulator (dt = 1/60) while
the closed form counts integer ticks; does the log re-derivation stay exact?
Deterministic: fixed seeds, integer frames, stdlib only.
"""
import random

CLIPS = {'walk': (4, 6, True), 'attack': (5, 4, False), 'idle': (2, 15, True)}  # frames, ticks/frame, loop
ATTACK_LEN = 5 * 4


class Anim:
    def __init__(self, use_float=False):
        self.clip, self.frame, self.acc, self.facc = 'idle', 0, 0, 0.0
        self.use_float = use_float

    def play(self, clip):
        if clip == self.clip:
            return
        self.clip, self.frame, self.acc, self.facc = clip, 0, 0, 0.0

    def tick(self):
        n, tpf, loop = CLIPS[self.clip]
        if self.use_float:
            self.facc += 1 / 60
            adv = self.facc >= tpf / 60
            if adv:
                self.facc -= tpf / 60
        else:
            self.acc += 1
            adv = self.acc >= tpf
            if adv:
                self.acc -= tpf
        if adv:
            self.frame += 1
            if self.frame >= n:
                if loop:
                    self.frame = 0
                else:
                    self.play('idle')

    def view(self):
        return (self.clip, self.frame)


def closed_form(transitions, t):
    """transitions: ordered list of (frame, clip) play() calls; state AFTER tick at frame t."""
    clip, start = 'idle', -1
    for f, c in transitions:
        if f > t:
            break
        # resolve auto attack->idle before applying this play
        if clip == 'attack' and f - start >= ATTACK_LEN:
            clip, start = 'idle', start + ATTACK_LEN
        if c != clip:
            clip, start = c, f
    # the tick that finishes the attack (ticks == ATTACK_LEN) already shows idle frame 0
    if clip == 'attack' and t - start >= ATTACK_LEN - 1:
        clip, start = 'idle', start + ATTACK_LEN
    n, tpf, loop = CLIPS[clip]
    # play at frame f happens before that frame's tick, so elapsed ticks = t - start + 1
    ticks = t + 1 if start < 0 else t - start + 1
    idx = ticks // tpf
    return (clip, idx % n if loop else min(idx, n - 1))


def make_log(seed, frames=600):
    rng = random.Random(seed)
    log, f = [], 0
    while True:
        f += rng.randint(3, 25)
        if f >= frames:
            break
        log.append((f, rng.choice(['move', 'cast', 'pull', 'undo', 'undo', 'redo'])))
    return log


def run_seed(seed, frames=600, use_float=False):
    log = make_log(seed, frames)
    anim = Anim(use_float)
    stack, redo = [], []
    play_frames, stack_at, log_moves_at = [], [], []
    ev = {f: c for f, c in log}
    raw = []
    undo_touching = 0
    for t in range(frames):
        c = ev.get(t)
        if c in ('move', 'cast', 'pull'):
            stack.append((t, c)); redo.clear(); raw.append((t, c))
            if c == 'move':
                anim.play('walk')
            elif c == 'cast':
                anim.play('attack')
        elif c == 'undo' and stack:
            u = stack.pop(); redo.append(u)
            undo_touching += u[1] in ('move', 'cast')
        elif c == 'redo' and redo:
            stack.append(redo.pop())
        anim.tick()
        play_frames.append(anim.view())
        stack_at.append(list(stack))
        log_moves_at.append(list(raw))
    playhead_view = play_frames[-1]
    res = {'carry': 0, 'stack': 0, 'log': 0}
    for t in range(frames):
        truth = play_frames[t]
        res['carry'] += playhead_view == truth
        st = [(f, 'walk' if c == 'move' else 'attack') for f, c in stack_at[t] if c != 'pull']
        res['stack'] += closed_form(st, t) == truth
        lg = [(f, 'walk' if c == 'move' else 'attack') for f, c in log_moves_at[t] if c != 'pull']
        res['log'] += closed_form(lg, t) == truth
    return res, undo_touching


def sweep(seeds, use_float=False, only_no_undo=False):
    tot = {'carry': 0, 'stack': 0, 'log': 0}
    n, undos = 0, 0
    for s in seeds:
        r, u = run_seed(s, use_float=use_float)
        for k in tot:
            tot[k] += r[k]
        n += 600; undos += u
    return tot, n, undos


def run_no_undo(seeds):
    # control: same generator but undo/redo replaced by pull
    global make_log
    orig = make_log

    def no_undo(seed, frames=600):
        return [(f, 'pull' if c in ('undo', 'redo') else c) for f, c in orig(seed, frames)]
    make_log = no_undo
    try:
        return sweep(seeds)
    finally:
        make_log = orig


if __name__ == '__main__':
    seeds = range(20)
    tot, n, undos = sweep(seeds)
    print(f'S1 integer ticks, 20 seeds x 600 frames, undos of move/cast: {undos}')
    for k, v in tot.items():
        print(f'   {k:6s} seek matches playback {v}/{n} ({100*v/n:.1f}%)')
    tot0, n0, _ = run_no_undo(seeds)
    print('S2 control: same logs with undo/redo replaced by pull')
    for k, v in tot0.items():
        print(f'   {k:6s} seek matches playback {v}/{n0} ({100*v/n0:.1f}%)')
    totf, nf, _ = sweep(seeds, use_float=True)
    print('S3 BREAK: playback uses float accumulator dt=1/60')
    for k, v in totf.items():
        print(f'   {k:6s} seek matches playback {v}/{nf} ({100*v/nf:.1f}%)')
    ok = tot['log'] == n and tot['stack'] < n and tot0['stack'] == n0
    print(f"RESULT: {'PASS' if ok else 'FAIL'} log re-derivation {tot['log']}/{n}, stack re-derivation {tot['stack']}/{n}, "
          f"carry {tot['carry']}/{n}; no-undo control stack {tot0['stack']}/{n0}; float-accumulator playback log {totf['log']}/{nf}")
