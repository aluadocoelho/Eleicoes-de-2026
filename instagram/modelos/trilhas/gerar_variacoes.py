"""Variações da trilha lo-fi da Clareia (20 s, 85,7 bpm, mesmo grid de cortes 0,7 / 5,6 / 12,6 s).

Cada variação muda harmonia, instrumento principal, batida e textura, para os vídeos não soarem sempre iguais.
Uso: python3 gerar_variacoes.py            -> gera todas em clareia-lofi-<nome>-20s.wav e .mp3
     python3 gerar_variacoes.py <nome>     -> gera só uma
Composta por código (sem música de terceiros): livre para Instagram, TikTok e YouTube.
"""
import os, sys, wave, subprocess, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
SR = 44100; DUR = 20.0; N = int(DUR * SR); HERE = os.path.dirname(os.path.abspath(__file__))
E8 = 0.35; T0 = 0.7; LAST = 52; CUT2, CUT3 = 14, 34
def g(n): return T0 + n * E8
def lp(x, fc, o=4): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=.006, r=.06):
    e = np.ones(n); ka = max(1, int(a * SR)); kr = min(n, int(r * SR))
    e[:ka] = np.linspace(0, 1, ka); e[-kr:] *= np.linspace(1, 0, kr); return e
# ---------- instrumentos ----------
def kick(soft=1.0):
    n = int(.5 * SR); tt = np.arange(n) / SR; f = 50 + 70 * np.exp(-tt / .04)
    return lp(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .2) * 2.2), 900) * .95 * soft
def snare(kind='snare'):
    n = int(.32 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(5)
    if kind == 'rim':   # aro: seco e curto
        return (np.sin(2 * np.pi * 820 * tt) * np.exp(-tt / .012) * .7 + lp(hp(rng.standard_normal(n), 1500), 5000) * np.exp(-tt / .015) * .4)
    if kind == 'clap':
        nz = lp(hp(rng.standard_normal(n), 700), 3000)
        e = sum(np.exp(-np.clip(tt - d, 0, None) / .02) * (tt >= d) for d in (0, .011, .022)) / 3 + np.exp(-tt / .12) * .5
        return nz * e * .75
    body = np.sin(2 * np.pi * 185 * tt) * np.exp(-tt / .05)
    return (body * .6 + lp(hp(rng.standard_normal(n), 300), 2200) * np.exp(-tt / .09) * .9) * .8
def hat(open_=False):
    n = int((.25 if open_ else .09) * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(11)
    return lp(hp(rng.standard_normal(n), 3500), 7000) * np.exp(-tt / (.08 if open_ else .025))
def shaker():
    n = int(.12 * SR); tt = np.arange(n) / SR; rng = np.random.default_rng(13)
    return lp(hp(rng.standard_normal(n), 4500), 8000) * np.sin(np.pi * np.clip(tt / .12, 0, 1)) * .6
def bass(m, dur, tone=700):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / .15)
    return lp(np.tanh(y * 1.3) * np.exp(-tt / 1.2) * env(n, .008, .08), tone)
def epiano(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    ph = 2 * np.pi * f * np.cumsum(1 + .0035 * np.sin(2 * np.pi * .45 * tt + m)) / SR
    y = np.sin(ph + (1.2 * np.exp(-tt / .35) + .15) * np.sin(ph)) * np.exp(-tt / 1.6) + .25 * np.sin(2 * ph) * np.exp(-tt / .5)
    return lp(y * (1 + .12 * np.sin(2 * np.pi * 4.2 * tt)) * env(n, .006, .15), 3800) * vel
def violao(m, dur, vel=1.0):   # corda dedilhada (Karplus-Strong), quente
    n = int(dur * SR); f = mtof(m); p = int(SR / f); rng = np.random.default_rng(m)
    buf = lp(rng.standard_normal(p), 3000, 2); y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % p]; buf[i % p] = .996 * .5 * (buf[i % p] + buf[(i + 1) % p])
    return lp(y * env(n, .002, .1), 3200) * vel * 1.4
def kalimba(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt / .9) + .35 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / .06)
    return lp(y * env(n, .002, .1), 4200) * vel
def vibra(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = (np.sin(2 * np.pi * f * tt) + .2 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt / .2)) * np.exp(-tt / 1.4)
    return lp(y * (1 + .25 * np.sin(2 * np.pi * 5.5 * tt)) * env(n, .003, .15), 4500) * vel
def pad(m, dur, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = mtof(m)
    y = sum(np.sin(2 * np.pi * f * (1 + d) * tt + k) for k, d in enumerate((-.004, 0, .005))) / 3
    return lp(y * env(n, .4, .5), 1800) * vel
INSTR = {'epiano': epiano, 'violao': violao, 'kalimba': kalimba, 'vibra': vibra}
# ---------- variações ----------
V = {
 'amanhecer': dict(desc='Violão dedilhado em Ré maior, aro em vez de caixa, shaker: clara e acolhedora.',
   ch=[([50, 57, 62, 66, 69], 38), ([47, 54, 59, 62, 66], 35), ([43, 50, 55, 59, 62], 31), ([45, 52, 57, 61, 64], 33)],
   inst='violao', arpejo=True, caixa='rim', perc='shaker', pad=False, melodia=None, crackle=.0, brilho=7500),
 'praca': dict(desc='Kalimba e baixo saltitante em Sol maior, palmas: leve e otimista.',
   ch=[([55, 59, 62, 66], 43), ([52, 55, 59, 62], 40), ([48, 52, 55, 59], 36), ([50, 54, 57, 60], 38)],
   inst='kalimba', arpejo=True, caixa='clap', perc='hat', pad=True, melodia=[74, 71, 69, 67, 69, 71, 74, 76], crackle=.0, brilho=7500),
 'noite': dict(desc='Vibrafone e pad em Lá menor, batida mais espaçada e chiado de vinil: calma, para noite e checagens.',
   ch=[([57, 60, 64, 67], 33), ([53, 57, 60, 64], 41), ([55, 59, 62, 65], 43), ([52, 56, 59, 62], 40)],
   inst='vibra', arpejo=False, caixa='snare', perc=None, pad=True, melodia=None, crackle=.012, brilho=6000),
 'jornal': dict(desc='Piano elétrico em Mi bemol com melodia curta e chimbal aberto: mais firme, para pesquisas e números.',
   ch=[([51, 55, 58, 62], 39), ([48, 51, 55, 58], 36), ([53, 56, 60, 63], 41), ([46, 50, 53, 56], 34)],
   inst='epiano', arpejo=False, caixa='snare', perc='hat_open', pad=False, melodia=[70, 72, 74, 72, 70, 67, 70, 72], crackle=.006, brilho=7000),
 'domingo': dict(desc='Violão e vibrafone em Fá maior, só aro e shaker, sem bumbo forte: a mais suave, para o dia da votação.',
   ch=[([53, 57, 60, 64], 41), ([50, 53, 57, 60], 38), ([46, 50, 53, 57], 34), ([48, 52, 55, 58], 36)],
   inst='violao', arpejo=True, caixa='rim', perc='shaker', pad=True, melodia=[72, 69, 67, 65, 67, 69, 72, 69], crackle=.004, brilho=7000, kick_soft=.55),
}
def gerar(nome):
    v = V[nome]; L = np.zeros(N); R = np.zeros(N)
    def put(y, tt, pan=0., gain=1.):
        i = int(round(tt * SR)); j = min(N, i + len(y))
        if j <= i or i < 0: return
        L[i:j] += y[:j-i] * gain * np.cos((pan + 1) * np.pi / 4) * 1.414; R[i:j] += y[:j-i] * gain * np.sin((pan + 1) * np.pi / 4) * 1.414
    ins = INSTR[v['inst']]; ks = v.get('kick_soft', 1.0); ch = v['ch']
    for k, m in enumerate(ch[0][0]): put(ins(m, 1.5, .5), 0.0, -.2 + .1 * k, .3)
    for n in range(LAST):
        bar, pos = divmod(n, 8); notes, root = ch[bar % 4]; tt = g(n)
        breath = n in (CUT2 - 2, CUT2 - 1, CUT3 - 2, CUT3 - 1)
        if not breath:
            if pos in ((0, 5) if nome == 'noite' else (0, 3, 5)): put(kick(ks), tt, 0, .7)
            if pos in (2, 6): put(snare(v['caixa']), tt, .05, .5 if v['caixa'] != 'rim' else .45)
            if v['perc'] == 'shaker': put(shaker(), tt + .04, .3, .14)
            if v['perc'] == 'hat' and pos % 2 == 1: put(hat(), tt, .25, .16)
            if v['perc'] == 'hat_open' and pos % 2 == 1: put(hat(pos == 7), tt, .25, .15)
        if pos == 0: put(bass(root, E8 * 2.8), tt, 0, .6)
        if pos == 4: put(bass(root + 7, E8 * 1.8), tt, 0, .46)
        if pos in (3, 7) and not breath and nome == 'praca': put(bass(root + 12, E8 * .8, 900), tt, 0, .3)
        if pos == 7 and not breath and nome != 'praca': put(bass(root + 2, E8 * .9), tt, 0, .34)
        if v['arpejo']:
            seq = notes + notes[-2:0:-1]
            put(ins(seq[pos % len(seq)], E8 * 3, .8), tt, -.3 + .6 * (pos % 4) / 3, .26)
        else:
            if pos == 0:
                for k, m in enumerate(notes): put(ins(m, E8 * 7.5, .9), tt, -.25 + .12 * k, .28)
            if pos == 5:
                for k, m in enumerate(notes[1:4]): put(ins(m, E8 * 2.6, .5), tt, -.1 + .1 * k, .22)
        if v['pad'] and pos == 0:
            for k, m in enumerate(notes[:3]): put(pad(m - 12 if m > 60 else m, E8 * 8, .9), tt, -.4 + .4 * k, .12)
        if v['melodia'] and bar % 2 == 1 and n < CUT3 + 8 or (v['melodia'] and n >= 40 and bar % 2 == 1):
            if pos % 2 == 0: put((kalimba if v['inst'] != 'kalimba' else vibra)(v['melodia'][(bar * 4 + pos // 2) % 8], E8 * 2, .7), tt, .2, .16)
    for n in (0, CUT2, CUT3): put(kick(ks), g(n), 0, .5)
    for k, m in enumerate(ch[0][0]): put(ins(m, 1.6, .9), g(LAST), -.25 + .12 * k, .32)
    put(bass(ch[0][1], 1.1), g(LAST), 0, .6); put(kick(ks), g(LAST), 0, .8)
    duck = np.ones(N)
    for n in range(LAST + 1):
        if n % 8 in (0, 3, 5):
            i = int(g(n) * SR); k = min(int(.25 * SR), N - i)
            if k > 0: duck[i:i+k] = np.minimum(duck[i:i+k], 1 - .28 * ks * np.exp(-np.arange(k) / (.08 * SR)))
    mix = np.stack([L * duck, R * duck])
    if v['crackle']:
        rng = np.random.default_rng(21); c = (rng.random(N) > .9993) * rng.standard_normal(N) * 6 + rng.standard_normal(N) * .15
        c = lp(hp(c, 900), 5000) * v['crackle']; mix += np.stack([c, np.roll(c, 37)])
    mix = hp(lp(mix, v['brilho']), 55)
    rng = np.random.default_rng(9); irn = int(.7 * SR); ir = lp(rng.standard_normal(irn), 4000) * np.exp(-np.arange(irn) / (.2 * SR)); ir /= np.sqrt((ir ** 2).sum())
    mix = mix + .2 * np.stack([fftconvolve(mix[0], ir)[:N], fftconvolve(mix[1], ir[::-1].copy())[:N]])
    t = np.arange(N) / SR; fade = np.ones(N); fade[t > 19.3] = np.clip((20 - t[t > 19.3]) / .7, 0, 1); fade[t < .4] = t[t < .4] / .4
    mix = np.tanh(mix * fade * 1.4); mix = mix / np.max(np.abs(mix)) * .88
    base = os.path.join(HERE, f'clareia-lofi-{nome}-20s')
    with wave.open(base + '.wav', 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-b:a', '192k', base + '.mp3'], check=True)
    print(nome, 'ok')
if __name__ == '__main__':
    for nome in (sys.argv[1:] or V): gerar(nome)
