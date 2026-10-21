"""Trilhas da Clareia em outros estilos além do lo-fi (30 s, 90 bpm, mesma grade do gerar_variacoes.py:
telas de 3, 4 e 5 s trocam sempre numa colcheia). Compostas por código, sem música de terceiros:
livres para Instagram, TikTok e YouTube.

Estilos:
  bossa     violão de nylon com levada de bossa nova, aro e shaker, baixo de surdo: brasileira e leve.
  pulso     sintetizador em arpejo de semicolcheias, bumbo reto e baixo grave em Dó menor: clima de telejornal.
  manchete  cordas em pizzicato, tambores graves e pad em Ré menor: tom de vinheta de notícia, mais sério.
  tarde     batida moderna de meio-tempo, baixo 808, chimbal com rufos e piano elétrico em Lá menor: tom de TikTok.
  reflexao  piano solo com pad suave em Mi bemol, sem bateria: calma, para temas delicados.

Uso: python3 gerar_estilos.py [nome ...]   -> clareia-<nome>-30s.wav e .mp3 nesta pasta
"""
import os, sys, wave, subprocess, numpy as np
from scipy.signal import fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gerar_variacoes import SR, DUR, N, E8, LAST, lp, hp, mtof, env, kick, snare, hat, shaker, bass, epiano, violao, kalimba, vibra, pad
S16 = E8 / 2
# ---------- instrumentos novos ----------
def piano(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for k in range(1, 8):
        fk = f * k * np.sqrt(1 + .0004 * k * k)
        if fk > 9000: break
        y += np.sin(2 * np.pi * fk * tt) / k ** 1.4 * np.exp(-tt / (2.2 / k ** .6))
    rng = np.random.default_rng(m); y += lp(rng.standard_normal(n), 2500) * np.exp(-tt / .008) * .15
    return lp(y * env(n, .002, .25), 5500) * vel * .8
def serra(m, dur, cut=2500, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for d in (-.006, .006):
        for k in range(1, 24):
            if f * k > 12000: break
            y += np.sin(2 * np.pi * f * (1 + d) * k * tt) / k
    return lp(y * .35 * np.exp(-tt / .16) * env(n, .003, .05), cut) * vel
def sub808(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m) * (1 + .6 * np.exp(-tt / .025))
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.8) * np.exp(-tt / .8) * env(n, .002, .12) * vel
def pizz(m, dur, vel=1.0):
    n = int(dur * SR); f = mtof(m); p = int(SR / f); rng = np.random.default_rng(m + 3)
    buf = lp(rng.standard_normal(p), 2200, 2); y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % p]; buf[i % p] = .985 * .5 * (buf[i % p] + buf[(i + 1) % p])
    return lp(y * env(n, .004, .08), 2600) * vel * 1.6
def tambor(f0=72, vel=1.0):
    n = int(.9 * SR); tt = np.arange(n) / SR; f = f0 * (1 + .6 * np.exp(-tt / .03))
    rng = np.random.default_rng(int(f0))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .32) + lp(rng.standard_normal(n), 1200) * np.exp(-tt / .02) * .3
    return lp(np.tanh(y * 1.6), 1500) * vel
def cordas(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m); y = np.zeros(n)
    for d in (-.005, 0, .004):
        ph = 2 * np.pi * f * (1 + d) * tt + .004 * np.sin(2 * np.pi * 5.2 * tt)
        y += sum(np.sin(k * ph) / k for k in range(1, 7))
    return lp(y / 3 * env(n, .5, .6), 2200) * vel
def nylon(notas, dur, vel=1.0):   # acorde de violão com o dedilhar levemente espalhado
    out = np.zeros(int((dur + .05) * SR))
    for k, m in enumerate(notas):
        y = violao(m, dur, vel * (.9 if k else 1)); i = int(k * .012 * SR); out[i:i + len(y)] += y[:len(out) - i]
    return out * .55
# ---------- mixagem ----------
class Mix:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def put(s, y, tt, pan=0., gain=1.):
        i = int(round(tt * SR)); j = min(N, i + len(y))
        if j <= i or i < 0: return
        s.L[i:j] += y[:j - i] * gain * np.cos((pan + 1) * np.pi / 4) * 1.414
        s.R[i:j] += y[:j - i] * gain * np.sin((pan + 1) * np.pi / 4) * 1.414
    def salvar(s, nome, duck_pos=(), duck=.3, brilho=9000, rev=.22):
        d = np.ones(N)
        for tt in duck_pos:
            i = int(tt * SR); k = min(int(.25 * SR), N - i)
            if k > 0: d[i:i + k] = np.minimum(d[i:i + k], 1 - duck * np.exp(-np.arange(k) / (.09 * SR)))
        mix = hp(lp(np.stack([s.L * d, s.R * d]), brilho), 40)
        rng = np.random.default_rng(9); irn = int(1.1 * SR); ir = lp(rng.standard_normal(irn), 4500) * np.exp(-np.arange(irn) / (.3 * SR)); ir /= np.sqrt((ir ** 2).sum())
        mix = mix + rev * np.stack([fftconvolve(mix[0], ir)[:N], fftconvolve(mix[1], ir[::-1].copy())[:N]])
        t = np.arange(N) / SR; fade = np.ones(N); fade[t > DUR - .7] = np.clip((DUR - t[t > DUR - .7]) / .7, 0, 1); fade[t < .05] = t[t < .05] / .05
        mix = np.tanh(mix * fade * 1.3); mix = mix / np.max(np.abs(mix)) * .88
        base = os.path.join(HERE, f'clareia-{nome}-30s')
        with wave.open(base + '.wav', 'w') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-b:a', '192k', base + '.mp3'], check=True)
        print(nome, 'ok')
def g(n): return n * E8
BARS = LAST // 8   # 10 compassos cheios + final
# ---------- estilos ----------
def bossa():
    M = Mix(); kp = []
    ch = [([50, 57, 60, 65], 38), ([43, 53, 59, 64], 43), ([48, 55, 59, 64], 36), ([45, 55, 61, 64], 45)]   # Dm9 G13 Cmaj7 A7
    clave = (0, 3, 6, 10, 13)          # aro, em semicolcheias, a cada compasso
    comp = (0, 3, 6, 8, 11, 14)        # violão
    for bar in range(BARS + 1):
        notas, root = ch[bar % 4]; t0 = g(bar * 8)
        if bar == BARS: break
        for p in comp: M.put(nylon(notas, S16 * 2.2, .8 if p else 1), t0 + p * S16, -.15, .5)
        for p in clave: M.put(snare('rim'), t0 + p * S16, .2, .32)
        for p in range(16): M.put(shaker(), t0 + p * S16 + .01, .35, .08 if p % 2 else .12)
        M.put(bass(root, E8 * 2.6, 600), t0, 0, .62); M.put(bass(root + 7, E8 * 1.6, 600), t0 + g(3), 0, .5)
        M.put(bass(root, E8 * 2.6, 600), t0 + g(4), 0, .55); M.put(bass(root + 7, E8 * 1.4, 600), t0 + g(7), 0, .45)
        M.put(kick(.5), t0, 0, .4); M.put(kick(.45), t0 + g(4), 0, .35); kp += [t0, t0 + g(4)]
        if bar % 2 == 1:
            mel = [72, 69, 67, 69, 72, 74, 72, 69] if bar % 4 == 1 else [71, 67, 64, 67, 69, 71, 69, 64]
            for k, m in enumerate(mel[:6]): M.put(vibra(m, E8 * 1.8, .6), t0 + g(k), .25, .14)
    t = g(LAST); M.put(nylon(ch[0][0], 2.0), t, -.15, .7); M.put(bass(ch[0][1], 1.4, 600), t, 0, .6)
    M.salvar('bossa', kp, .15, 8000, .2)
def pulso():
    M = Mix(); kp = []
    ch = [([48, 51, 55, 58], 36), ([44, 48, 51, 55], 32), ([51, 55, 58, 62], 39), ([46, 50, 53, 58], 34)]   # Cm Ab Eb Bb
    for n16 in range(LAST * 2):
        bar, p = divmod(n16, 16); notas, root = ch[bar % 4]; tt = n16 * S16
        seq = [notas[0] + 12, notas[1] + 12, notas[2] + 12, notas[3] + 12, notas[2] + 12, notas[1] + 12, notas[3], notas[2] + 24]
        cut = 1200 + 2600 * min(1, n16 / 120)
        M.put(serra(seq[p % 8], S16 * 1.6, cut, .9), tt, -.35 + .7 * (p % 4) / 3, .2)
        if p % 4 == 0: M.put(kick(), tt, 0, .75); kp.append(tt)
        if p in (4, 12) and bar > 0: M.put(snare('clap'), tt, .05, .42)
        if p % 4 == 2: M.put(hat(), tt, .3, .18)
        elif bar >= 2: M.put(hat(), tt, -.25, .07)
        if p == 0: M.put(sub808(root - 12 if root > 40 else root, E8 * 7.6, .9), tt, 0, .5)
        if p == 0:
            for k, m in enumerate(notas[:3]): M.put(pad(m, E8 * 8, .9), tt, -.4 + .4 * k, .1)
    t = g(LAST); M.put(kick(), t, 0, .8); M.put(sub808(36, 1.5), t, 0, .5)
    for k, m in enumerate(ch[0][0]): M.put(pad(m, 1.6), t, -.3 + .2 * k, .15)
    M.salvar('pulso', kp, .35, 9000, .18)
def manchete():
    M = Mix(); kp = []
    ch = [([50, 57, 62, 65], 38), ([46, 53, 58, 62], 34), ([48, 55, 60, 64], 36), ([45, 52, 57, 61], 33)]   # Dm Bb C A
    for n in range(LAST):
        bar, p = divmod(n, 8); notas, root = ch[bar % 4]; tt = g(n)
        ost = [notas[0] + 12, notas[2], notas[1] + 12, notas[2]]
        M.put(pizz(ost[p % 4], E8 * 1.2, .9), tt, -.3, .3); M.put(pizz(ost[(p + 2) % 4] + 12, E8, .6), tt + S16, .3, .16)
        if p in (0, 3, 6): M.put(tambor(70 if p == 0 else 82, 1 if p == 0 else .75), tt, 0, .55); kp.append(tt)
        if p == 4 and bar >= 1: M.put(snare(), tt, .05, .3)
        if p == 0:
            for k, m in enumerate(notas): M.put(cordas(m, E8 * 8.2, .8), tt, -.45 + .3 * k, .13)
            M.put(bass(root, E8 * 7, 500), tt, 0, .5)
        if bar >= 4 and bar % 2 == 0 and p in (0, 2, 4):
            M.put(cordas(notas[-1] + 12 + (2 if p == 2 else 0), E8 * 2, .7), tt, .2, .09)
    t = g(LAST); M.put(tambor(65), t, 0, .9)
    for k, m in enumerate(ch[0][0]): M.put(cordas(m, 1.8), t, -.4 + .25 * k, .2)
    M.put(bass(38, 1.5, 500), t, 0, .6)
    M.salvar('manchete', kp, .2, 8000, .3)
def tarde():
    M = Mix(); kp = []
    ch = [([57, 60, 64, 67], 33), ([53, 57, 60, 64], 29), ([48, 52, 55, 59], 36), ([55, 59, 62, 65], 31)]   # Am7 Fmaj7 Cmaj7 G7
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = g(bar * 8)
        M.put(kick(), t0, 0, .75); M.put(kick(.8), t0 + g(3) + S16, 0, .55); kp += [t0, t0 + g(3) + S16]
        M.put(sub808(root, E8 * 3.2), t0, 0, .55); M.put(sub808(root, E8 * 2.5, .85), t0 + g(3) + S16, 0, .45)
        M.put(snare('clap'), t0 + g(4), .05, .5); M.put(snare('snare'), t0 + g(4), -.05, .2)
        for p in range(16):
            M.put(hat(), t0 + p * S16, .25, .12 if p % 2 else .16)
        if bar % 2 == 1:   # rufo de chimbal em tercinas no fim do compasso
            for k in range(6): M.put(hat(), t0 + g(6) + k * (E8 * 2 / 6), .25, .07 + .015 * k)
        for k, m in enumerate(notas): M.put(epiano(m, E8 * 7.6, .8), t0, -.25 + .15 * k, .22)
        if bar >= 2:
            mel = [76, 74, 72, 69] if bar % 2 == 0 else [72, 71, 67, 69]
            for k, m in enumerate(mel): M.put(kalimba(m, E8 * 1.8, .7), t0 + g(1 + k * 1.5), .3, .13)
    t = g(LAST); M.put(kick(), t, 0, .8); M.put(sub808(33, 1.6), t, 0, .55)
    for k, m in enumerate(ch[0][0]): M.put(epiano(m, 1.8), t, -.25 + .15 * k, .3)
    M.salvar('tarde', kp, .3, 9000, .18)
def reflexao():
    M = Mix()
    ch = [([51, 58, 62, 67], 39), ([48, 55, 58, 63], 36), ([44, 51, 55, 60], 32), ([46, 53, 58, 62], 34)]   # Eb Cm Ab Bb
    mel = [70, 72, 74, 72, 70, 67, 70, 72, 74, 75, 74, 72, 70, 74, 72, 70]
    for n in range(LAST):
        bar, p = divmod(n, 8); notas, root = ch[bar % 4]; tt = g(n)
        if p == 0:
            M.put(piano(root, E8 * 8, .9), tt, -.1, .4)
            for k, m in enumerate(notas[:3]): M.put(pad(m, E8 * 8.2, .9), tt, -.4 + .4 * k, .08)
        arp = [notas[0] + 12, notas[1] + 12, notas[2] + 12, notas[3] + 12, notas[2] + 12, notas[1] + 12, notas[0] + 24, notas[1] + 12]
        M.put(piano(arp[p], E8 * 3, .55), tt, -.2 + .4 * (p % 4) / 3, .2)
        if bar >= 2 and p % 2 == 0: M.put(piano(mel[(bar * 4 + p // 2) % 16] + 12, E8 * 2.5, .7), tt, .15, .2)
        if bar >= 4 and p in (0, 4): M.put(kick(.35), tt, 0, .25)
    t = g(LAST); M.put(piano(39, 2.5), t, 0, .5)
    for m in ch[0][0]: M.put(piano(m + 12, 2.2, .6), t, 0, .25)
    M.salvar('reflexao', [], 0, 9000, .3)
ESTILOS = {'bossa': bossa, 'pulso': pulso, 'manchete': manchete, 'tarde': tarde, 'reflexao': reflexao}
if __name__ == '__main__':
    for nome in (sys.argv[1:] or list(ESTILOS)): ESTILOS[nome]()
