"""Trilhas dinâmicas da Clareia: mais rápidas e contagiantes, sem ser eufóricas (30 s, 120 bpm).
A 120 bpm cada tempo dura 0,5 s, então telas de 3, 4 e 5 s trocam sempre num tempo.
Todas têm drop aos 3 s: a abertura vem abafada e subindo, e a batida entra cheia junto com a primeira tela de conteúdo.
Compostas por código, sem música de terceiros: livres para Instagram, TikTok e YouTube.

  pulsar     house leve: bumbo reto, chimbal aberto no contratempo, acordes curtos de sintetizador, baixo no contratempo (Lá menor).
  tamborzao  batida de funk carioca suavizada (o "tamborzão" em palmas e tambores), baixo grave e sintetizador curto (Ré menor).
  estrada    pop rock indie: baixo em colcheias, bateria firme e guitarra dedilhada brilhante (Ré maior).
  batuque    pop com batucada: surdo, caixa e agogô à brasileira, marimba na melodia (Sol maior).

Uso: python3 gerar_dinamicas.py [nome ...]   -> clareia-<nome>-30s.wav e .mp3
"""
import os, sys, wave, subprocess, numpy as np
from scipy.signal import fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gerar_variacoes import SR, lp, hp, mtof, env, kick, snare, hat, shaker, bass, epiano, violao, kalimba, pad
from gerar_estilos import serra, sub808, pizz, tambor, piano
DUR = float(os.environ.get('DUR', '30')); N = int(DUR * SR); BEAT = .5; E8 = .25; S16 = .125; BAR = 2.0; DROP = 3.0
BARS = int((DUR - 3) // 2) + 1   # depois do drop: 3 s + compassos de 2 s até o fim
def marimba(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt / .35) + .5 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt / .05) + .2 * np.sin(2 * np.pi * f * 10 * tt) * np.exp(-tt / .015)
    return lp(y * env(n, .001, .05), 6000) * vel
def agogo(alto=True):
    n = int(.25 * SR); tt = np.arange(n) / SR; f = 1400 if alto else 1050
    return (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt / .07) * .5
def surdo(vel=1.0, abafado=False):
    n = int(.8 * SR); tt = np.arange(n) / SR; f = 62 * (1 + .25 * np.exp(-tt / .04))
    return lp(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.6) * np.exp(-tt / (.12 if abafado else .45)), 900) * vel
def guitarra(m, dur, vel=1.0):
    y = violao(m, dur, vel); return lp(np.tanh(y * 2.2) * .6, 4200)
def acorde_curto(notas, dur, cut=3200, vel=1.0):
    return sum(serra(m, dur, cut, vel) for m in notas) * .45
def tamborim(vel=1.0):   # tamborim: batida seca e aguda
    n = int(.12 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(7)
    y = np.sin(2 * np.pi * 520 * tt) * np.exp(-tt / .018) + hp(lp(rng.standard_normal(n), 6000), 1500) * np.exp(-tt / .01) * .6
    return y * vel * .8
def pandeiro(forte=False):   # platinelas (chiado metálico) + couro
    n = int(.16 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(17)
    pl = hp(lp(rng.standard_normal(n), 11000), 5000) * np.exp(-tt / .05) * (.7 if forte else .4)
    co = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt / .04) * (.6 if forte else 0)
    return pl + co
def cuica(alto=True):   # cuíca: glissando curto
    n = int(.22 * SR); tt = np.arange(n) / SR; f = (520 if alto else 380) * (1 + .35 * np.sin(np.pi * tt / .22))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / .22) ** 2 * .35
def cavaco(notas, dur, vel=1.0):   # cavaquinho: acorde agudo bem curto, como no pagode
    out = np.zeros(int((dur + .05) * SR))
    for k, m in enumerate(sorted(notas)):
        y = violao(m + 12, dur, vel) * np.exp(-np.arange(int(dur * SR)) / SR / .12); i = int(k * .006 * SR); out[i:i + len(y)] += y[:len(out) - i]
    return lp(out * .5, 6500)
TELECOTECO = (0, 2, 3, 5, 7, 8, 10, 12, 13, 15)   # levada do tamborim em semicolcheias
def camada_br(M, t0, bar, leve=False):
    for p in range(16):
        M.put(pandeiro(p % 4 == 0), t0 + p * S16, .35, .13 if leve else .16)
        if p in TELECOTECO: M.put(tamborim(.9 if p % 4 == 0 else .7), t0 + p * S16, -.35, .12 if leve else .17)
    if bar % 2 == 1: M.put(cuica(True), t0 + 3 * BEAT + S16, .2, .2); M.put(cuica(False), t0 + 3 * BEAT + 3 * S16, .2, .16)
class Mix:
    def __init__(s): s.L = np.zeros(N + 4 * SR); s.R = np.zeros(N + 4 * SR)
    def put(s, y, tt, pan=0., g=1.):
        i = int(round(tt * SR)); j = min(len(s.L), i + len(y))
        if j <= i or i < 0: return
        s.L[i:j] += y[:j - i] * g * np.cos((pan + 1) * np.pi / 4) * 1.414; s.R[i:j] += y[:j - i] * g * np.sin((pan + 1) * np.pi / 4) * 1.414
def pulsar(M, kp):
    ch = [([57, 60, 64], 33), ([53, 57, 60], 29), ([48, 52, 55], 36), ([55, 59, 62], 31)]   # Am F C G
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        for b in range(4):
            t = t0 + b * BEAT; M.put(kick(), t, 0, .8); kp.append(t)
            M.put(hat(True), t + E8, .25, .16); M.put(bass(root + 12 if b % 2 else root, E8 * .9, 900), t + E8, 0, .5)
            M.put(hat(), t + S16, -.2, .06); M.put(hat(), t + 3 * S16, -.2, .06)
            if b in (1, 3): M.put(snare('clap'), t, .05, .45)
        for p in (1, 3, 6, 7, 10, 14):   # acordes curtos em semicolcheias sincopadas
            M.put(acorde_curto(notas, S16 * 1.6, 2600 + 800 * (bar % 2)), t0 + p * S16, -.2 + .1 * (p % 3), .26)
        if bar % 2 == 1:
            for k, m in enumerate([76, 74, 72, 74]): M.put(kalimba(m, E8 * 2, .6), t0 + k * BEAT + E8, .3, .12)
        M.put(pad(notas[0], BAR, .7), t0, -.3, .07)
    return ch[0][1]
def tamborzao(M, kp):
    ch = [([50, 53, 57], 38), ([46, 50, 53], 34), ([48, 52, 55], 36), ([45, 49, 52], 33)]   # Dm Bb C A
    # tamborzão em semicolcheias (16 por compasso): bumbo/tambor e palma
    K = (0, 3, 6, 10, 11); C = (4, 12); TB = (7, 14)
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        for p in range(16):
            t = t0 + p * S16
            if p in K: M.put(kick(.9), t, 0, .75); kp.append(t)
            if p in C: M.put(snare('clap'), t, 0, .5); M.put(snare('rim'), t, .2, .2)
            if p in TB: M.put(tambor(150, .7), t, -.25, .3)
            if p % 2 == 0: M.put(hat(), t, .3, .09)
        M.put(sub808(root, BEAT * 1.4, .9), t0, 0, .5); M.put(sub808(root, BEAT * .9, .8), t0 + 6 * S16, 0, .4); M.put(sub808(root + 3, BEAT * .9, .8), t0 + 10 * S16, 0, .4)
        for p in (2, 8, 13): M.put(acorde_curto(notas, S16 * 1.4, 2400), t0 + p * S16, .2, .22)
        if bar % 4 == 3:
            for k in range(4): M.put(tambor(120 + 15 * k, .6), t0 + 3 * BEAT + k * S16, 0, .3)
    return ch[0][1]
def estrada(M, kp):
    ch = [([50, 57, 62, 66], 38), ([47, 54, 59, 62], 35), ([43, 50, 55, 59], 31), ([45, 52, 57, 61], 33)]   # D Bm G A
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        for e in range(8):
            t = t0 + e * E8
            M.put(bass(root, E8 * .95, 1100), t, 0, .45)
            M.put(hat(e % 2 == 1 and e == 7), t, .25, .12 if e % 2 else .16)
            M.put(guitarra((notas + notas[-2:0:-1])[e % 6] + 12, E8 * 2.2, .7), t, -.35 + .7 * (e % 4) / 3, .2)
        for b in (0, 2): M.put(kick(), t0 + b * BEAT, 0, .8); kp.append(t0 + b * BEAT)
        M.put(kick(.8), t0 + 2 * BEAT + E8, 0, .5)
        for b in (1, 3): M.put(snare('snare'), t0 + b * BEAT, .05, .5)
        if bar % 4 == 3: [M.put(snare('snare'), t0 + 3 * BEAT + k * S16, -.1, .18 + .05 * k) for k in range(4)]
        M.put(pad(notas[1], BAR, .6), t0, .3, .06)
    return ch[0][1]
def batuque(M, kp):
    ch = [([55, 59, 62], 43), ([52, 55, 59], 40), ([48, 52, 55], 36), ([50, 54, 57], 38)]   # G Em C D
    mel = [74, 71, 74, 76, 79, 76, 74, 71, 72, 74, 76, 74, 71, 69, 67, 69]
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        M.put(surdo(1.0), t0 + BEAT, 0, .7); M.put(surdo(.9), t0 + 3 * BEAT, 0, .7)       # surdo de resposta nos tempos 2 e 4
        M.put(surdo(.7, True), t0, 0, .5); M.put(surdo(.7, True), t0 + 2 * BEAT, 0, .5)
        kp += [t0 + BEAT, t0 + 3 * BEAT]
        for p in range(16):
            M.put(snare('rim') if p % 4 in (1, 3) else shaker(), t0 + p * S16, .3 if p % 2 else -.3, .14 if p % 4 in (1, 3) else .12)
        for p, alto in ((0, True), (3, False), (6, True), (8, True), (10, False), (12, True), (14, False)): M.put(agogo(alto), t0 + p * S16, -.4, .2)
        M.put(bass(root, BEAT * 1.4, 800), t0, 0, .5); M.put(bass(root + 7, BEAT * .9, 800), t0 + 3 * E8, 0, .4); M.put(bass(root + 12, BEAT * .9, 800), t0 + 2 * BEAT, 0, .4)
        for p in (2, 6, 10, 14): M.put(nyl := acorde_curto(notas, S16 * 1.5, 2000, .7), t0 + p * S16, .15, .15)
        if bar >= 1:
            for k in range(8): M.put(marimba(mel[(bar * 8 + k) % 16], E8 * 1.6, .8), t0 + k * E8 + (S16 if k % 4 == 3 else 0), .25, .2)
    return ch[0][1]
def pulsarbr(M, kp):   # o pulsar com batucada por cima: tamborim no telecoteco, pandeiro e cuíca
    tom = pulsar(M, kp)
    for bar in range(BARS): camada_br(M, bar * BAR, bar)
    return tom
def pagode(M, kp):   # pop com pagode: surdo de marcação, tantã, pandeiro, cavaquinho e piano elétrico (Dó maior)
    ch = [([48, 52, 55, 59], 36), ([45, 48, 52, 55], 33), ([50, 53, 57, 60], 38), ([43, 47, 50, 53], 31)]   # Cmaj7 Am7 Dm7 G7
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        M.put(surdo(.8, True), t0, 0, .45); M.put(surdo(1.0), t0 + BEAT, 0, .7); M.put(surdo(.8, True), t0 + 2 * BEAT, 0, .45); M.put(surdo(1.0), t0 + 3 * BEAT, 0, .7)
        kp += [t0 + BEAT, t0 + 3 * BEAT]
        for p in (0, 3, 6, 8, 11, 14): M.put(tambor(110, .5), t0 + p * S16, -.15, .25)   # tantã
        for p in (1, 3, 6, 9, 11, 14): M.put(cavaco(notas, S16 * 1.3, .8), t0 + p * S16, .25, .3)
        for k, m in enumerate(notas): M.put(epiano(m, BAR * .95, .6), t0, -.3 + .15 * k, .12)
        M.put(bass(root, BEAT * 1.5, 800), t0, 0, .5); M.put(bass(root + 7, BEAT * .9, 800), t0 + 3 * E8, 0, .4); M.put(bass(root, BEAT * .9, 800), t0 + 2 * BEAT, 0, .45); M.put(bass(root + 5, BEAT * .9, 800), t0 + 3 * BEAT + E8, 0, .4)
        M.put(snare('rim'), t0 + BEAT, .1, .3); M.put(snare('rim'), t0 + 3 * BEAT, .1, .3)
        camada_br(M, t0, bar, leve=True)
    return ch[0][1]
def funkpop(M, kp):   # pop com batida de funk carioca bem leve e palmas, baixo grave e sintetizador (Fá menor)
    ch = [([53, 56, 60], 41), ([49, 53, 56], 37), ([51, 55, 58], 39), ([48, 52, 55], 36)]   # Fm Db Eb C
    K = (0, 3, 6, 10, 11); C = (4, 12)
    for bar in range(BARS):
        notas, root = ch[bar % 4]; t0 = bar * BAR
        for p in range(16):
            t = t0 + p * S16
            if p in K: M.put(kick(.85), t, 0, .7); kp.append(t)
            if p in C: M.put(snare('clap'), t, 0, .5)
            if p % 2 == 0: M.put(hat(), t, .3, .08)
            if p in (2, 7, 9, 14): M.put(tamborim(.7), t, -.3, .12)
        M.put(sub808(root - 12 if root > 40 else root, BEAT * 1.2), t0, 0, .5); M.put(sub808(root - 12 if root > 40 else root, BEAT * .8, .8), t0 + 6 * S16, 0, .4)
        for p in (2, 8, 13): M.put(acorde_curto([n + 12 for n in notas], S16 * 1.2, 3000), t0 + p * S16, .2, .2)
        if bar % 2 == 1:
            for k, m in enumerate([77, 75, 72, 75]): M.put(marimba(m, E8 * 1.5, .7), t0 + k * BEAT + E8, .3, .14)
    return ch[0][1]
ESTILOS = {'pulsarbr': pulsarbr, 'pagode': pagode, 'funkpop': funkpop, 'pulsar': pulsar, 'tamborzao': tamborzao, 'estrada': estrada, 'batuque': batuque}
def finalizar(nome, M, kp, tom):
    # trilha "cheia", que começa no drop
    d = np.ones(len(M.L))
    for tt in kp:
        i = int(tt * SR); k = min(int(.2 * SR), len(d) - i)
        if k > 0: d[i:i + k] = np.minimum(d[i:i + k], 1 - .3 * np.exp(-np.arange(k) / (.07 * SR)))
    x = hp(lp(np.stack([M.L * d, M.R * d]), 11000), 35)
    rng = np.random.default_rng(9); irn = int(.8 * SR); ir = lp(rng.standard_normal(irn), 5000) * np.exp(-np.arange(irn) / (.22 * SR)); ir /= np.sqrt((ir ** 2).sum())
    x = x + .14 * np.stack([fftconvolve(x[0], ir)[:x.shape[1]], fftconvolve(x[1], ir[::-1].copy())[:x.shape[1]]])
    nd = int(DROP * SR); out = np.zeros((2, N)); out[:, nd:] = x[:, :N - nd]
    # abertura: o primeiro trecho, abafado e abrindo, com ruído subindo e rufo acelerando
    t = np.arange(nd) / SR; curva = (t / DROP) ** 2.2
    intro = x[:, :nd].copy()
    cortes = [280, 500, 900, 1600, 3000]; vs = [np.stack([lp(c, fc) for c in intro]) for fc in cortes]
    pos = curva * (len(cortes) - 1); i0 = np.clip(np.floor(pos).astype(int), 0, len(cortes) - 2); fr = pos - i0
    filt = np.zeros_like(intro)
    for k in range(len(cortes) - 1):
        m = i0 == k; filt[:, m] = vs[k][:, m] * (1 - fr[m]) + vs[k + 1][:, m] * fr[m]
    gap = int(.1 * SR); filt *= (.3 + .5 * curva); filt[:, -gap:] *= np.linspace(1, 0, gap) ** 2
    rz = hp(lp(rng.standard_normal(nd), 9000), 1500) * curva ** 2 * .1; rz[-gap:] = 0
    out[:, :nd] = filt + np.stack([rz, np.roll(rz, 77)])
    tt = 1.0
    while tt < DROP - .12:
        y = snare('snare') * (.06 + .3 * (tt / DROP) ** 2); i = int(tt * SR); j = min(nd - gap, i + len(y))
        if j > i: out[:, i:j] += y[:j - i]
        tt += E8 if tt < 2.0 else (S16 if tt < 2.5 else S16 / 2)
    imp = np.zeros(int(2 * SR)); k = kick(); imp[:len(k)] += k; s = sub808(tom, 1.2); imp[:len(s)] += s * .5
    n = int(1.5 * SR); imp[:n] += hp(lp(rng.standard_normal(n), 10000), 3500) * np.exp(-np.arange(n) / SR / .5) * .2
    out[0, nd:nd + len(imp)] += imp; out[1, nd:nd + len(imp)] += np.roll(imp, 40)
    t2 = np.arange(N) / SR; fade = np.ones(N); fade[t2 > DUR - .8] = np.clip((DUR - t2[t2 > DUR - .8]) / .8, 0, 1)
    out = np.tanh(out * fade * 1.25); out = out / np.max(np.abs(out)) * .89
    base = os.environ.get('SAIDA') or os.path.join(HERE, f'clareia-{nome}-30s')
    with wave.open(base + '.wav', 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out.T * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-b:a', '192k', base + '.mp3'], check=True)
    print(nome, 'ok')
if __name__ == '__main__':
    for nome in (sys.argv[1:] or list(ESTILOS)):
        M = Mix(); kp = []; tom = ESTILOS[nome](M, kp); finalizar(nome, M, kp, tom)
