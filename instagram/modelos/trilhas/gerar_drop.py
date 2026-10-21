"""Versões com drop das trilhas da Clareia: durante a tela de abertura (0 a 3 s) a música vem abafada e sobe
(filtro abrindo, ruído subindo, rufo de caixa acelerando); aos 3,0 s, quando entra a primeira tela de conteúdo,
a batida entra cheia com impacto (bumbo, grave longo e prato). Como a abertura tem sempre 3 s, o drop cai
sempre na troca de tela. Depois do drop a trilha segue normal, desde o começo do compasso.

Uso: python3 gerar_drop.py [nome ...]   -> clareia-<nome>-drop-30s.wav e .mp3
Nomes: praca, noite, jornal (lo-fi) e bossa, pulso, manchete, tarde (gerar_estilos.py).
"""
import os, sys, wave, subprocess, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gerar_variacoes import SR, lp, hp, mtof, kick, snare
from gerar_estilos import sub808
DROP = 3.0; DUR = 30.0; N = int(DUR * SR)
TOM = {'praca': 43, 'noite': 33, 'jornal': 39, 'bossa': 38, 'pulso': 36, 'manchete': 38, 'tarde': 33}
def ler(nome):
    f = f'clareia-lofi-{nome}-30s.wav' if nome in ('praca', 'noite', 'jornal') else f'clareia-{nome}-30s.wav'
    with wave.open(os.path.join(HERE, f)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32767
    return x.reshape(-1, 2).T
def varredura(x, cortes, curva):
    """Filtro passa-baixa que abre com o tempo: mistura versões filtradas conforme a curva (0..1)."""
    vs = [np.stack([lp(c, fc) for c in x]) if fc else x for fc in cortes]
    pos = curva * (len(cortes) - 1); i = np.clip(np.floor(pos).astype(int), 0, len(cortes) - 2); fr = pos - i
    out = np.zeros_like(x)
    for k in range(len(cortes) - 1):
        m = i == k; out[:, m] = vs[k][:, m] * (1 - fr[m]) + vs[k + 1][:, m] * fr[m]
    return out
def gerar(nome):
    x = ler(nome); nd = int(DROP * SR)
    out = np.zeros((2, N))
    # depois do drop: a trilha desde o começo
    corpo = x[:, :N - nd].copy(); out[:, nd:] = corpo
    # abertura: o primeiro compasso, abafado e abrindo
    intro = x[:, :nd].copy(); t = np.arange(nd) / SR
    curva = (t / DROP) ** 2.2
    intro = varredura(intro, [260, 420, 700, 1200, 2200], curva) * (.32 + .5 * curva)
    gap = int(.12 * SR); intro[:, -gap:] *= np.linspace(1, 0, gap) ** 2       # respiro antes do drop
    out[:, :nd] = intro
    rng = np.random.default_rng(4)
    # ruído subindo (riser)
    rz = rng.standard_normal(nd); rz = varredura(np.stack([rz, np.roll(rz, 91)]), [500, 1000, 2000, 4000, 8000], curva)
    rz = hp(rz, 300) * (curva ** 1.5) * .12; rz[:, -gap:] *= 0; out[:, :nd] += rz
    # rufo de caixa acelerando: colcheias, semicolcheias, fusas
    e8 = 1 / 3; tt = 1.0; hits = []
    while tt < DROP - .14:
        hits.append(tt); tt += e8 if tt < 1.67 else (e8 / 2 if tt < 2.34 else e8 / 4)
    for h in hits:
        y = snare('snare') * (.08 + .3 * (h / DROP) ** 2); i = int(h * SR); j = min(nd - gap, i + len(y))
        if j > i: out[:, i:j] += y[:j - i]
    # impacto no drop
    imp = np.zeros(int(2.5 * SR)); k = kick(); imp[:len(k)] += k * 1.0
    s = sub808(TOM[nome], 1.6, 1.0); imp[:len(s)] += s * .55
    n = int(1.8 * SR); tc = np.arange(n) / SR
    crash = hp(lp(rng.standard_normal(n), 9000), 3000) * np.exp(-tc / .55) * .22; imp[:n] += crash
    ir = lp(rng.standard_normal(int(1.2 * SR)), 4000) * np.exp(-np.arange(int(1.2 * SR)) / (.35 * SR)); ir /= np.sqrt((ir ** 2).sum())
    imp = imp + .25 * fftconvolve(imp, ir)[:len(imp)]
    j = min(N, nd + len(imp)); out[0, nd:j] += imp[:j - nd]; out[1, nd:j] += np.roll(imp, 40)[:j - nd]
    # final e volume
    t2 = np.arange(N) / SR; fade = np.ones(N); fade[t2 > DUR - .8] = np.clip((DUR - t2[t2 > DUR - .8]) / .8, 0, 1)
    out = np.tanh(out * fade * 1.15); out = out / np.max(np.abs(out)) * .89
    base = os.path.join(HERE, f'clareia-{nome}-drop-30s')
    with wave.open(base + '.wav', 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out.T * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-b:a', '192k', base + '.mp3'], check=True)
    print(nome, 'ok')
if __name__ == '__main__':
    for nome in (sys.argv[1:] or list(TOM)): gerar(nome)
