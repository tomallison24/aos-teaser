"""The launch teaser's soft score, made from scratch (no samples), timed to the film.

    python3 music.py out.wav

In the dark: a low drone, a clock ticking with the ticks, a heartbeat. The date:
a soft boom and a bell. The core apps: a chime for each, rising up the scale,
over Bm - G - D - A. Then a swell, a breath of silence, and D major at the flash:
sparkles for the confetti, a gentle arpeggio for the invite, and a last chord.
"""
import sys, wave
import numpy as np

SR, DUR = 44100, 30.0
N = int(SR * DUR)
rng = np.random.default_rng(1010)
L = np.zeros(N); R = np.zeros(N)

# ---- the film's clock (launch/index.html) ----
C0, DURS = 11.85, [.95, .8, .7, .62, .56, .52, .48, .45, .43, .42, .44]
ST = list(np.cumsum([C0] + DURS[:-1]))
C_END = ST[-1] + DURS[-1]
LAND = [s + d + .55 for s, d in zip(ST, DURS)]
AOS_LAND = C_END + .55
TICKS = [.8 + 6.2 * (i / 60) ** (1 / 1.55) for i in range(1, 61)]
HEART = [(2.6, .1), (4.6, .17), (6.1, .26), (6.85, .34)]

NOTE = {}
for name, semis in [('C', -9), ('C#', -8), ('D', -7), ('E', -5), ('F', -4), ('F#', -3), ('G', -2), ('A', 0), ('B', 2)]:
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


def swell(t0, t1, gain, lo0, hi0, lo1, hi1, curve=2.2):
    """Noise whose band and level rise from t0 to t1, cut off at t1."""
    n, hop = 4096, 1024
    total = int((t1 - t0) * SR)
    out = np.zeros(total + n)
    win = np.hanning(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    for i in range(0, total, hop):
        u = i / total
        lo, hi = lo0 + (lo1 - lo0) * u, hi0 + (hi1 - hi0) * u
        spec = np.fft.rfft(rng.standard_normal(n) * win)
        spec *= (freqs > lo) & (freqs < hi)
        out[i:i + n] += np.fft.irfft(spec) * win
    out = out[:total]
    u = np.linspace(0, 1, total)
    out *= u ** curve / (np.abs(out).max() + 1e-9)
    out[-200:] *= np.linspace(1, 0, 200)
    place(out, t0, gain, -.2); place(out * .9, t0 + .007, gain, .2)


def glide(t0, t1, fa, fb, gain):
    t = tt(t1 - t0)
    u = t / (t1 - t0)
    fr = fa * (fb / fa) ** (u ** 1.6)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * u ** 2
    s[-200:] *= np.linspace(1, 0, 200)
    place(s, t0, gain)


# ---- 1. the wait ----
pad(f('D2', 'A2'), 0.0, 7.9, .16, attack=3.5, release=.6, bright=.05)
pad(f('D3', 'F3'), 3.0, 7.9, .08, attack=3.0, release=.6, bright=.05)
for i, tk in enumerate(TICKS):
    tick(tk, .025 + .035 * i / 60, pan=.25 if i % 2 else -.25)
for b, amp in HEART:
    thump(b, amp * 1.1); thump(b + .24, amp * .65)
swell(5.6, 8.08, .16, 200, 900, 1500, 9000)
glide(6.0, 8.08, NOTE['D3'], NOTE['D5'], .05)

# ---- 2. the date ----
thump(8.1, .55, 70, 38, 1.4)
for fr in f('D4', 'A4', 'E5'):
    place(bell(fr, 3.5, 1.4), 8.1, .1, rng.uniform(-.3, .3))
pad(f('D3', 'A3', 'E4'), 8.1, 12.0, .26, attack=.8)
for i in [0, 1, 3, 4, 6, 7]:
    place(bell(NOTE['A5'] if i % 2 else NOTE['D6'], .5, .12), 8.9 + i * .07 + .7 + i * .06, .035, -.5 + i / 7)

# ---- 3. the core apps ----
for chord, a, b, g in [(('B2', 'F#3', 'B3', 'D4'), 11.85, 14.1, .3), (('G2', 'D3', 'G3', 'B3'), 14.1, 16.0, .32),
                       (('D3', 'A3', 'D4', 'F#4'), 16.0, 17.6, .34), (('A2', 'E3', 'A3', 'C#4'), 17.6, 20.05, .36)]:
    pad(f(*chord), a, b, g, attack=.5, release=.4 if b < 20 else .05)
SCALE = f('D4', 'E4', 'F#4', 'A4', 'B4', 'D5', 'E5', 'F#5', 'A5', 'B5', 'D6')
for k, s in enumerate(ST):
    pan = np.cos(-np.pi / 2 + (k + 1) * 2 * np.pi / 12) * .6
    place(bell(SCALE[k], 1.8, .8), s, .16, pan)
    thump(s, .18, 60, 44, .25)
    place(bell(SCALE[k] * 2, .5, .1), LAND[k], .03, pan)
for fr in f('D5', 'F#5', 'A5'):
    place(bell(fr, 2.5, 1.0), AOS_LAND, .08, 0)

# the build, a breath, and the drop
swell(18.7, 20.1, .3, 300, 1200, 2500, 14000, curve=3)
glide(18.9, 20.1, NOTE['A3'], NOTE['A5'], .06)
thump(20.2, .7, 64, 36, 1.8)
crash_t = tt(3.0)
crash = np.diff(rng.standard_normal(len(crash_t) + 1)) * np.exp(-crash_t / .7)
place(crash, 20.2, .05, -.3); place(np.roll(crash, 300), 20.2, .05, .3)

# ---- 4. the invite ----
pad(f('D2', 'A2', 'D3', 'F#3', 'A3', 'D4', 'E4'), 20.2, 22.6, .8, attack=.06, release=.8, bright=.18)
pad(f('D2', 'G3', 'B3', 'D4', 'G4'), 22.6, 24.4, .62, attack=.6, release=.8, bright=.15)
pad(f('D2', 'A2', 'F#3', 'A3', 'D4', 'E4'), 24.4, 26.8, .62, attack=.6, release=.6, bright=.15)
SPARK = f('D5', 'E5', 'F#5', 'A5', 'B5', 'D6', 'E6', 'F#6', 'A6')
t = 20.25
while t < 25.5:
    place(bell(rng.choice(SPARK), .7, .18), t, .035 * (1 - (t - 20.25) / 6), rng.uniform(-.8, .8))
    t += .05 + .25 * (t - 20.25) / 5 * rng.uniform(.5, 1.5)
beat = 60 / 112 / 2
ARP = {0: ['D4', 'F#4', 'A4', 'D5', 'A4', 'F#4'], 1: ['D4', 'G4', 'B4', 'D5', 'B4', 'G4']}
i, t = 0, 21.0
while t < 26.4:
    ch = 1 if 22.6 <= t < 24.4 else 0
    place(pluck(NOTE[ARP[ch][i % 6]]), t, .09, -.35 if i % 2 else .35)
    i += 1; t += beat
for s in (22.6, 23.6, 24.6, 25.6):
    tick(s, .03, .1)
place(bell(NOTE['A5'], .8, .2), 21.4, .08, .2); place(bell(NOTE['D6'], 1.2, .3), 21.52, .08, .2)   # the invite notice appears

# ---- 5. the end ----
thump(26.85, .35, 60, 40, 1.2)
for fr in f('D5', 'F#5', 'A5', 'D6'):
    place(bell(fr, 3.0, 1.2), 26.85, .07, rng.uniform(-.4, .4))
pad(f('D2', 'A2', 'F#3', 'A3', 'C#4', 'E4'), 26.85, 29.2, .5, attack=.8, release=.8, bright=.12)
for j, n in enumerate(['D6', 'E6', 'F#6', 'A6', 'D7']):
    place(bell(NOTE[n], .6, .15), 28.1 + j * .06, .025, -.4 + j * .2)

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
tail = int(1.2 * SR); fade[-tail:] = np.linspace(1, 0, tail) ** 2
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * .84, R / peak * .84
pcm = (np.stack([L, R], 1) * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
