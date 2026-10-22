"""The aOS 2 teaser's soft score, made from scratch (no samples), timed to the film.

    python3 music.py out.wav

Built like the launch teaser's (launch/make-video/music.py), in F this time. On walnut: a low
pad, a chime for each app as it appears, rising up the scale, and a soft wooden tock for each
roof. Then they gather: a swell, a run of little bells as they land, and the one roof drops on
a soft boom, opening into F major as the ground turns cream. The phone: a gentle plucked
groove, a tap, a whoosh as Weather slides in and out. Ipsy: a bubble pop for the question,
quick sparkles while it thinks, a chime for each app it reaches, and a warm answer. The design
flip: two shimmery turns. The mark: a whistle as the 2 drops, a boom and bounces as it lands,
three plucks for the three little bars, and a last chord.
"""
import sys, wave
import numpy as np

SR, DUR = 44100, 38.0
N = int(SR * DUR)
rng = np.random.default_rng(2026)
L = np.zeros(N); R = np.zeros(N)

# ---- the film's clock (aos2/index.html) ----
POP = [.6 + k * .15 for k in range(14)]
ROOF = [4.6 + k * .08 for k in range(14)]
ROOF_OFF, CARD_IN = 8.0, 8.3
FLY = [8.6 + k * .07 for k in range(14)]
FLIGHT = .75
LANDS = [f + FLIGHT for f in FLY]
BIG_ROOF = 10.35
ROOF_HIT = BIG_ROOF + .25 / 2.75          # the bounce's first touch
MORPH0, MORPH1 = 13.2, 14.1
TAP, OPEN0, OPEN1 = 15.4, 15.5, 16.1
SWIPE0, SWIPE1, ONOW = 17.2, 17.8, 18.0
IPSY0, IPSY1 = 20.6, 21.4
ASK, THINK0, THINK1, ANSWER, IPSY_OUT = 22.3, 23.2, 25.5, 25.7, 27.9
DESIGN0, FLIP1, FLIP2, DESIGN1 = 28.4, 29.4, 30.4, 31.1
MARK0, TWO = 31.3, 32.0
HITS = [TWO + .7 / 2.75, TWO + .7 * 2 / 2.75, TWO + .7 * 2.5 / 2.75]   # the 2 lands, and bounces
END0, PILL = 34.6, 35.45

NOTE = {}
for name, semis in [('C', -9), ('C#', -8), ('D', -7), ('Eb', -6), ('E', -5), ('F', -4), ('F#', -3), ('G', -2), ('A', 0), ('Bb', 1), ('B', 2)]:
    for octv in range(1, 8):
        NOTE[f'{name}{octv}'] = 440 * 2 ** ((semis + 12 * (octv - 4)) / 12)
f = lambda *ns: [NOTE[n] for n in ns]


def place(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    sig = sig[:N - i0] * gain
    a = (pan + 1) * np.pi / 4
    L[i0:i0 + len(sig)] += sig * np.cos(a); R[i0:i0 + len(sig)] += sig * np.sin(a)


def tt(d): return np.arange(int(d * SR)) / SR


def bell(freq, dur=1.6, tau=.7, partials=((1, 1), (2, .28), (3.01, .1), (4.2, .05))):
    t = tt(dur)
    s = sum(a * np.sin(2 * np.pi * freq * h * t) * np.exp(-t / (tau / h ** .5)) for h, a in partials)
    return s * np.minimum(1, t / .004)


def pluck(freq, dur=.6):
    return bell(freq, dur, tau=.22, partials=((1, 1), (2, .35), (3, .12)))


def tock(freq, dur=.25):
    """A soft wooden tock (marimba-ish): a short sine with a hollow overtone."""
    return bell(freq, dur, tau=.06, partials=((1, 1), (3.9, .25), (9.2, .05)))


def pad(freqs, t0, t1, gain, attack=1.2, release=1.5, bright=.12):
    d = t1 - t0 + release
    t = tt(d)
    env = np.minimum(1, t / attack) * np.clip((t1 - t0 + release - t) / release, 0, 1) ** 1.5
    s = np.zeros_like(t)
    for fr in freqs:
        for det, a in ((-.0035, .35), (0, .5), (.004, .35)):
            ph = rng.uniform(0, 2 * np.pi)
            s += a * (np.sin(2 * np.pi * fr * (1 + det) * t + ph) + bright * np.sin(4 * np.pi * fr * (1 + det) * t + ph))
    s *= (1 + .12 * np.sin(2 * np.pi * .23 * t)) / len(freqs)
    place(s * env, t0, gain, -.15); place(s * env * .96, t0 + .011, gain, .15)


def thump(t0, gain, f0=58, f1=42, d=.35):
    t = tt(d)
    fr = f1 + (f0 - f1) * np.exp(-t / .05)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / (d / 3.5)) * np.minimum(1, t / .003)
    place(s, t0, gain)


def tick(t0, gain, pan=0.0, d=.03):
    t = tt(d)
    n = np.diff(rng.standard_normal(len(t) + 1))
    place(n * np.exp(-t / .004) + .5 * np.sin(2 * np.pi * 2900 * t) * np.exp(-t / .006), t0, gain, pan)


def swell(t0, t1, gain, lo0, hi0, lo1, hi1, curve=2.2, tail=0.0):
    """Noise whose band and level rise from t0 to t1 (then, with tail, fall away)."""
    n, hop = 4096, 1024
    total = int((t1 - t0 + tail) * SR)
    out = np.zeros(total + n)
    win = np.hanning(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    for i in range(0, total, hop):
        u = min(1, i / max(1, int((t1 - t0) * SR)))
        lo, hi = lo0 + (lo1 - lo0) * u, hi0 + (hi1 - hi0) * u
        spec = np.fft.rfft(rng.standard_normal(n) * win)
        spec *= (freqs > lo) & (freqs < hi)
        out[i:i + n] += np.fft.irfft(spec) * win
    out = out[:total]
    rise = int((t1 - t0) * SR)
    env = np.ones(total)
    env[:rise] = np.linspace(0, 1, rise) ** curve
    if tail > 0: env[rise:] = np.linspace(1, 0, total - rise) ** 2
    out *= env / (np.abs(out).max() + 1e-9)
    out[-200:] *= np.linspace(1, 0, 200)
    place(out, t0, gain, -.2); place(out * .9, t0 + .007, gain, .2)


def whoosh(t0, d, gain, pan0=.6, pan1=-.6):
    """A soft slide: a band of noise that rises and falls, moving across."""
    n = int(d * SR)
    x = np.diff(rng.standard_normal(n + 1))
    spec = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((np.log(fr + 1) - np.log(1800)) ** 2) / .9)
    x = np.fft.irfft(spec, n)
    u = np.linspace(0, 1, n)
    x *= np.sin(np.pi * u) ** 2 / (np.abs(x).max() + 1e-9)
    half = n // 2
    place(x[:half], t0, gain, pan0); place(x[half:], t0 + half / SR, gain, pan1)


def glide(t0, t1, fa, fb, gain, fade_in=True):
    t = tt(t1 - t0)
    u = t / (t1 - t0)
    fr = fa * (fb / fa) ** (u ** 1.6)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * (u ** 2 if fade_in else (1 - u) ** .5)
    s[-200:] *= np.linspace(1, 0, 200)
    place(s, t0, gain)


# ---- 1. fourteen apps, fourteen homes (on walnut) ----
pad(f('D2', 'A2'), 0.0, 4.6, .18, attack=2.5, release=.8, bright=.05)
pad(f('D3', 'F3', 'A3'), .6, 4.6, .1, attack=2.0, release=.8, bright=.06)
SCALE = f('C4', 'D4', 'F4', 'G4', 'A4', 'C5', 'D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'F6', 'G6')
for k, t in enumerate(POP):
    place(bell(SCALE[k], 1.4, .55), t, .11, -.6 + 1.2 * ((k * 5) % 14) / 13)
pad(f('Bb1', 'F2'), 4.6, 8.3, .18, attack=.6, release=.6, bright=.05)
pad(f('D3', 'F3', 'Bb3'), 4.6, 8.3, .1, attack=.8, release=.6, bright=.06)
TOCKS = f('F4', 'C4', 'A4', 'D4', 'G4', 'C4', 'F4', 'A3', 'D4', 'G4', 'Bb3', 'F4', 'C4', 'A4')
for k, t in enumerate(ROOF):
    place(tock(TOCKS[k]), t + .3, .17, -.6 + 1.2 * ((k * 5) % 14) / 13)
for b in (5.0, 6.0, 7.0):
    thump(b, .12, 54, 42, .3)

# ---- 2. one home ----
swell(7.7, 8.35, .07, 400, 1500, 1500, 6000, curve=2)   # the roofs lift away
for fr in f('F4', 'A4', 'C5'):
    place(bell(fr, 2.0, .9), CARD_IN, .06, rng.uniform(-.3, .3))
pad(f('C2', 'G2', 'C3', 'E3', 'G3'), 8.3, 10.4, .22, attack=1.4, release=.1, bright=.08)
swell(9.0, 10.42, .2, 250, 1100, 2000, 11000, curve=3)
glide(9.2, 10.42, NOTE['C4'], NOTE['C6'], .04)
LANDN = f('F5', 'A5', 'C6', 'F6', 'A5', 'C6', 'F6', 'A6', 'C6', 'F6', 'A6', 'C7', 'F6', 'A6')
for k, t in enumerate(LANDS):
    place(bell(LANDN[k], .5, .12), t, .03, -.5 + k / 13)
thump(ROOF_HIT, .7, 66, 36, 1.6)
crash_t = tt(2.5)
crash = np.diff(rng.standard_normal(len(crash_t) + 1)) * np.exp(-crash_t / .6)
place(crash, ROOF_HIT, .035, -.3); place(np.roll(crash, 300), ROOF_HIT, .035, .3)
for fr in f('F4', 'C5', 'F5', 'A5'):
    place(bell(fr, 3.0, 1.3), ROOF_HIT, .08, rng.uniform(-.4, .4))
pad(f('F2', 'C3', 'F3', 'A3', 'C4', 'G4'), ROOF_HIT, 13.4, .62, attack=.05, release=.9, bright=.16)
SPARK = f('F5', 'G5', 'A5', 'C6', 'D6', 'F6', 'G6', 'A6')
t = ROOF_HIT + .05
while t < 12.6:
    place(bell(rng.choice(SPARK), .6, .16), t, .03 * (1 - (t - ROOF_HIT) / 2.6), rng.uniform(-.8, .8))
    t += .07 + .3 * (t - ROOF_HIT) / 2.2 * rng.uniform(.5, 1.5)
whoosh(MORPH0, .9, .06, -.2, .2)   # the card becomes a phone

# ---- 3. the phone: a gentle groove ----
beat = 60 / 100 / 2
CHORDS = [(14.1, 15.5, ('F2', 'C3', 'A3', 'C4'), ['F4', 'A4', 'C5', 'F5', 'C5', 'A4']),
          (15.5, 17.2, ('Bb1', 'F2', 'D3', 'F3'), ['F4', 'Bb4', 'D5', 'F5', 'D5', 'Bb4']),
          (17.2, 18.0, ('C2', 'G2', 'E3', 'G3'), ['E4', 'G4', 'C5', 'E5', 'C5', 'G4']),
          (18.0, 20.6, ('F2', 'C3', 'A3', 'C4'), ['F4', 'A4', 'C5', 'F5', 'C5', 'A4'])]
for a, b, ch, _ in CHORDS:
    pad(f(*ch), a, b, .3, attack=.4, release=.4 if b < 20.6 else 1.0, bright=.1)
i, t = 0, 14.1
while t < 20.5:
    arp = next(c[3] for c in CHORDS if c[0] <= t < c[1])
    place(pluck(NOTE[arp[i % 6]]), t, .07 * (1 if t < 20 else (20.6 - t) / .6), -.35 if i % 2 else .35)
    if i % 4 == 0: thump(t, .08, 56, 44, .22)
    i += 1; t += beat
tick(TAP, .07, .1)
place(bell(NOTE['C6'], .5, .1), TAP, .04, .2)
whoosh(OPEN0 - .05, .7, .16, .6, -.1)          # Weather slides in from the right
place(bell(NOTE['A5'], .8, .25), OPEN1, .05, -.2)
whoosh(SWIPE0, .65, .14, -.3, .6)              # and back out
place(bell(NOTE['F5'], .5, .12), ONOW, .05, -.4); place(bell(NOTE['C6'], .7, .2), ONOW + .08, .05, -.4)

# ---- 4. Ipsy ----
glide(IPSY0, IPSY1, NOTE['F4'], NOTE['F5'], .05)
swell(IPSY0, IPSY1, .06, 300, 1500, 1500, 7000, curve=2)
place(bell(NOTE['C6'], 1.5, .6), IPSY1, .07); place(bell(NOTE['F6'], 1.5, .6), IPSY1 + .1, .05)
pad(f('Bb1', 'F2', 'D3', 'F3', 'A3'), IPSY1, THINK0, .32, attack=.5, release=.5, bright=.1)
place(pluck(NOTE['G5']), ASK, .1, .5); place(pluck(NOTE['D6']), ASK + .09, .08, .5)   # the question pops up
pad(f('D2', 'A2', 'F3', 'C4', 'E4'), THINK0, ANSWER, .3, attack=.4, release=.4, bright=.12)
t = THINK0 + .1
while t < THINK1:
    place(bell(rng.choice(f('A5', 'C6', 'D6', 'E6', 'F6', 'A6')), .25, .05), t, .022, rng.uniform(-.7, .7))
    t += .06 + .05 * rng.random()
ORB = f('C5', 'D5', 'F5', 'A5', 'C6', 'D6')
for j in range(6):
    at = THINK0 + .25 + j * .12
    place(pluck(ORB[j]), at, .08, np.cos(-np.pi / 2 + j * 2 * np.pi / 6) * .7)
for fr in f('F5', 'A5', 'C6'):
    place(bell(fr, 1.2, .5), THINK0 + 1.4, .05, 0)          # the apps that matter light up
pad(f('C2', 'G2', 'E3', 'G3', 'Bb3'), THINK1 - .2, ANSWER, .2, attack=.2, release=.2)
pad(f('F2', 'C3', 'A3', 'C4', 'F4'), ANSWER, IPSY_OUT + .3, .42, attack=.15, release=.8, bright=.14)
for j, n in enumerate(['C5', 'F5', 'A5', 'C6']):
    place(bell(NOTE[n], 1.4, .5), ANSWER + j * .07, .07, -.4 + j * .25)
i, t = 0, ANSWER + .4
while t < IPSY_OUT:
    place(pluck(NOTE[['F4', 'A4', 'C5', 'F5', 'C5', 'A4'][i % 6]]), t, .06, -.35 if i % 2 else .35)
    i += 1; t += beat

# ---- 5. your design ----
pad(f('G2', 'D3', 'F3', 'Bb3'), DESIGN0, FLIP2, .32, attack=.5, release=.4, bright=.1)
pad(f('C2', 'G2', 'E3', 'Bb3'), FLIP2, MARK0, .3, attack=.3, release=.3, bright=.1)
place(bell(NOTE['F5'], 1.2, .4), DESIGN0 + .1, .06)
for ft, notes in ((FLIP1, ('A5', 'C6', 'E6', 'G6')), (FLIP2, ('G6', 'E6', 'C6', 'A5'))):
    whoosh(ft - .2, .4, .07, -.3, .3)
    for j, n in enumerate(notes):
        place(bell(NOTE[n], .8, .25), ft + j * .05, .04, -.5 + j * .33)
i, t = 0, DESIGN0 + .4
while t < MARK0 - .2:
    place(pluck(NOTE[['D4', 'G4', 'Bb4', 'D5'][i % 4]]), t, .05, -.35 if i % 2 else .35)
    i += 1; t += beat

# ---- 6. the mark ----
swell(MARK0, TWO + .25, .14, 300, 1200, 2500, 12000, curve=3)
glide(TWO, HITS[0], NOTE['C6'], NOTE['C5'], .05, fade_in=False)   # the 2 falls
thump(HITS[0], .7, 64, 34, 1.8)
thump(HITS[1], .2, 70, 46, .3); thump(HITS[2], .1, 74, 50, .25)
crash = np.diff(rng.standard_normal(len(crash_t) + 1)) * np.exp(-crash_t / .7)
place(crash, HITS[0], .04, -.3); place(np.roll(crash, 300), HITS[0], .04, .3)
pad(f('F2', 'C3', 'F3', 'A3', 'C4', 'E4', 'G4'), HITS[0], END0, .7, attack=.05, release=.8, bright=.18)
for fr in f('F4', 'A4', 'C5', 'F5', 'A5'):
    place(bell(fr, 3.0, 1.2), HITS[0], .07, rng.uniform(-.4, .4))
for j, n in enumerate(['A5', 'C6', 'F6']):                 # the three little bars
    place(pluck(NOTE[n]), TWO + .55 + j * .18, .09, -.3 + j * .3)
t = HITS[0] + .05
while t < 34.0:
    place(bell(rng.choice(SPARK), .6, .16), t, .028 * (1 - (t - HITS[0]) / 2), rng.uniform(-.8, .8))
    t += .08 + .3 * (t - HITS[0]) / 1.8 * rng.uniform(.5, 1.5)

# ---- the end card ----
pad(f('Bb1', 'F2', 'D3', 'F3', 'A3', 'C4'), END0, PILL + .35, .48, attack=.5, release=.4, bright=.12)
place(bell(NOTE['C6'], .8, .25), PILL, .07, .2); place(bell(NOTE['F6'], 1.2, .4), PILL + .1, .06, .2)
thump(PILL + .35, .3, 58, 40, 1.2)
pad(f('F2', 'C3', 'F3', 'A3', 'C4', 'G4'), PILL + .35, 37.4, .5, attack=.6, release=1.2, bright=.12)
for fr in f('F5', 'A5', 'C6', 'F6'):
    place(bell(fr, 3.0, 1.3), PILL + .35, .06, rng.uniform(-.4, .4))
for j, n in enumerate(['F6', 'G6', 'A6', 'C7', 'F7']):
    place(bell(NOTE[n], .6, .15), 36.6 + j * .06, .022, -.4 + j * .2)

# ---- reverb, level, fades ----
ir_t = tt(3.0)
def ir(): return rng.standard_normal(len(ir_t)) * np.exp(-ir_t / .8) * np.minimum(1, ir_t / .01)
def conv(x, h):
    m = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)]
wl, wr = conv(L, ir()), conv(R, ir())
k = np.abs(np.concatenate([L, R])).max() / (np.abs(np.concatenate([wl, wr])).max() + 1e-9)
L, R = L + .4 * k * wl, R + .4 * k * wr
fade = np.ones(N); fade[:int(.4 * SR)] = np.linspace(0, 1, int(.4 * SR))
tail = int(1.4 * SR); fade[-tail:] = np.linspace(1, 0, tail) ** 2
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * .84, R / peak * .84
pcm = (np.stack([L, R], 1) * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
