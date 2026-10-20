"""Trilha lo-fi "média": 85,7 bpm, mais clara e leve que a original (tom maior, piano no registro médio), sem agudos estridentes."""
import os, numpy as np, wave
from scipy.signal import butter, sosfilt
SR = 44100; DUR = 20.0; N = int(DUR * SR)
HERE = os.path.dirname(os.path.abspath(__file__))
E8 = 0.35; T0 = 0.7                      # colcheia de 0,35 s: cai em 0,7 / 5,6 / 12,6 s
def g(n): return T0 + n * E8
t = np.arange(N) / SR
def lp(x, fc, o=4): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
L = np.zeros(N); R = np.zeros(N)
def put(y, tt, pan=0.0, gain=1.0):
    i = int(round(tt * SR)); j = min(N, i + len(y))
    if j <= i or i < 0: return
    l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    L[i:j] += y[:j-i] * gain * l; R[i:j] += y[:j-i] * gain * r
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def rel(y, r=.06):
    k = min(len(y), int(r * SR)); y[-k:] *= np.linspace(1, 0, k); return y
# ---------- instrumentos ----------
def kick():
    n = int(.5 * SR); tt = np.arange(n) / SR
    f = 50 + 70 * np.exp(-tt / .04)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .2)
    return lp(np.tanh(y * 2.2), 900) * .95
def snare():
    n = int(.32 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(5)
    body = np.sin(2 * np.pi * 185 * tt) * np.exp(-tt / .05)
    nz = lp(hp(rng.standard_normal(n), 300), 2200) * np.exp(-tt / .09)
    return (body * .6 + nz * .9) * .8
def epiano(m, dur, vel=1.0):
    # piano elétrico (estilo Rhodes) com FM suave e leve oscilação de fita
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    wob = 1 + .0035 * np.sin(2 * np.pi * .45 * tt + m)
    ph = 2 * np.pi * f * np.cumsum(wob) / SR
    idx = 1.2 * np.exp(-tt / .35) + .15
    y = np.sin(ph + idx * np.sin(ph)) * np.exp(-tt / 1.6)
    y += .25 * np.sin(2 * ph) * np.exp(-tt / .5)
    trem = 1 + .12 * np.sin(2 * np.pi * 4.2 * tt)
    a = int(.006 * SR); y[:a] *= np.linspace(0, 1, a)
    return lp(rel(y * trem, .15), 3800) * vel
def hat():
    n = int(.09 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(11)
    return lp(hp(rng.standard_normal(n), 3500), 7000) * np.exp(-tt / .025)
def bass(m, dur):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / .15)
    a = int(.008 * SR); y[:a] *= np.linspace(0, 1, a)
    return lp(rel(np.tanh(y * 1.3) * np.exp(-tt / 1.2), .08), 700)
# ---------- harmonia (um acorde por compasso de 8 colcheias) ----------
CH = [('Fmaj9', [53, 57, 60, 64, 67], 41), ('Em7', [52, 55, 59, 62], 40),
      ('Dm9', [53, 57, 60, 62, 64], 38), ('Cadd9', [52, 55, 60, 62], 36)]
LAST = 52                                  # colcheia do acorde final (18,9 s)
cut2, cut3 = 14, 34                        # cortes do vídeo (5,6 s e 12,6 s)
# introdução: acorde suave antes do primeiro impacto
for k, m in enumerate(CH[0][1]): put(epiano(m, 1.5, .5), 0.0, -.2 + .1 * k, .32)
for n in range(0, LAST):
    bar, pos = divmod(n, 8); name, notes, root = CH[bar % 4]
    tt = g(n)
    breath = n in (cut2 - 2, cut2 - 1, cut3 - 2, cut3 - 1)      # meio tempo de respiro antes de cada corte
    # bateria boom bap
    if pos in (0, 3, 5) and not breath: put(kick(), tt, 0, .7)
    if pos in (2, 6) and not breath: put(snare(), tt, .05, .55)
    # baixo: tônica, quinta e nota de passagem
    if pos == 0: put(bass(root, E8 * 2.8), tt, 0, .6)
    if pos == 4: put(bass(root + 7, E8 * 1.8), tt, 0, .48)
    if pos == 7 and not breath: put(bass(root + 2, E8 * .9), tt, 0, .36)
    # chimbal macio nos contratempos (brilho leve, sem chiado)
    if pos % 2 == 1 and not breath: put(hat(), tt, .25, .16)
    # piano elétrico: acorde no 1, toque leve no "e" do 3
    if pos == 0:
        for k, m in enumerate(notes): put(epiano(m, E8 * 7.5, .9), tt, -.25 + .12 * k, .3)
    if pos == 5:
        for k, m in enumerate(notes[1:4]): put(epiano(m, E8 * 2.6, .5), tt, -.1 + .1 * k, .25)
# impactos nos cortes: bumbo + acorde cheio
for n in (0, cut2, cut3):
    put(kick(), g(n), 0, .5)
# final: acorde segurado
for k, m in enumerate(CH[0][1]): put(epiano(m, 1.6, .9), g(LAST), -.25 + .12 * k, .34)
put(bass(41, 1.1), g(LAST), 0, .6); put(kick(), g(LAST), 0, .9)
# ---------- textura e mixagem ----------
duck = np.ones(N)
for n in range(0, LAST + 1):
    if n % 8 in (0, 3, 5):
        i = int(g(n) * SR); k = int(.25 * SR)
        if i < N: duck[i:i+k] = np.minimum(duck[i:i+k], 1 - .3 * np.exp(-np.arange(min(k, N - i)) / (.08 * SR)))
L *= duck; R *= duck
mix = np.stack([L, R])
mix = lp(mix, 7000); mix = hp(mix, 55)
# "sala" curta e escura para dar o calor de lo-fi
rng = np.random.default_rng(9); irn = int(.6 * SR); ir = lp(rng.standard_normal(irn), 4000) * np.exp(-np.arange(irn) / (.18 * SR))
ir /= np.sqrt((ir ** 2).sum())
from scipy.signal import fftconvolve
mix = mix + .18 * np.stack([fftconvolve(mix[0], ir)[:N], fftconvolve(mix[1], ir[::-1].copy())[:N]])
fade = np.ones(N); fade[t > 19.3] = np.clip((20 - t[t > 19.3]) / .7, 0, 1); fade[t < .4] = t[t < .4] / .4
mix = mix * fade
mix = np.tanh(mix * 1.5); mix = mix / np.max(np.abs(mix)) * .88
with wave.open(os.path.join(HERE, 'verita-lofi-media-20s.wav'), 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('ok')
