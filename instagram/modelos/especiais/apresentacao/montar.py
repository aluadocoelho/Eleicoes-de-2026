#!/usr/bin/env python3
"""Vídeo longo narrado "Eu sou a Clareia" (pedido do dono em 21/10).
Sem música: só a narração e sons suaves de entrada (bolhinha) e saída (madeira abafada), nada estridente.
Cada cena dura o tempo da sua fala: com os áudios em narracao/<id>.wav (ou .mp3/.m4a) usa a duração real;
sem áudio, estima pela quantidade de palavras (prévia). Legendas queimadas, sincronizadas por trecho (acessibilidade).
Caixas sempre com borda escura e sombra dura (identidade da Clareia).

Uso: python3 montar.py [pasta_dos_audios] saida/      (gera reels.mp4 e capa.jpg)
"""
import os, sys, json, html, asyncio, tempfile, shutil, subprocess, wave, glob
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(os.path.dirname(AQUI)); sys.path.insert(0, MOD)
import marca as M, familias as F
E = html.escape
ROXO, AM, T, LAV = '#3E2492', '#FFD43B', '#16181D', '#EEE8FA'
SR = 44100; RITMO = 2.6; FOLGA = .9
FONTES = os.path.join(MOD, 'fontes'); LOGO = os.path.abspath(os.path.join(MOD, '..', '..', 'marca', 'clareia-eleicoes-roxo.svg'))
IC = dict(F.IC)
IC.update({
 'relogio': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
 'busca': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 20 20"/>',
 'escudo': '<path d="M12 3.2 19 6v5.6c0 4.3-3 7.6-7 9.2-4-1.6-7-4.9-7-9.2V6z"/><path d="m8.8 12 2.2 2.2 4.2-4.4"/>',
 'link': '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 'aovivo': '<circle cx="12" cy="12" r="2.4"/><path d="M7.8 7.8a6 6 0 0 0 0 8.4M16.2 7.8a6 6 0 0 1 0 8.4M5 5a10 10 0 0 0 0 14M19 5a10 10 0 0 1 0 14"/>',
 'revisao': '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 4v4.5h-4.5"/><path d="m8.8 12.2 2.2 2.2 4.2-4.4"/>',
 'errata': '<path d="M5 19.5h4l10-10-4-4-10 10z"/><path d="m13.5 7 4 4"/>',
 'libras': '<path d="M8 13V6.5a1.5 1.5 0 0 1 3 0V11"/><path d="M11 10.5V5a1.5 1.5 0 0 1 3 0v5.5"/><path d="M14 10.5V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-.5A5.5 5.5 0 0 1 5 14.5V12a1.5 1.5 0 0 1 3 0"/>',
 'ouvir': '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>',
 'contraste': '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v17A8.5 8.5 0 0 0 12 3.5z" fill="#fff"/>',
 'espaco': '<path d="M4 6h16M4 12h16M4 18h16"/><path d="M20 3.5v2.5M20 18v2.5"/>',
 'tabela': '<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="M3.5 10h17M3.5 14.5h17M10 5v14"/>',
 'idiomas': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.6 3.6 5.4 3.6 8.5s-1.1 5.9-3.6 8.5c-2.5-2.6-3.6-5.4-3.6-8.5s1.1-5.9 3.6-8.5z"/>',
 'ia': '<path d="M12 3.5l1.8 4.7 4.7 1.8-4.7 1.8L12 16.5l-1.8-4.7L5.5 10l4.7-1.8z"/><path d="M18.5 15.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
 'pessoa': '<circle cx="10" cy="8" r="3.8"/><path d="M3.5 20a6.5 6.5 0 0 1 13 0"/><path d="m15.5 12.5 2 2 3.8-4"/>',
})

def ico(nome, px, cor='#fff'):
    return f'<svg width="{px}" height="{px}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{IC[nome]}</svg>'

def caixa(sombra=AM):
    return f'background:#fff;color:{T};border:5px solid {T};border-radius:30px;box-shadow:12px 12px 0 {sombra}'

# ---------- tempos ----------
def dividir(arquivo, n, pasta_saida):
    """Um arquivo só com a narração inteira: corta nas n-1 maiores pausas (uma por troca de cena) e grava <id>.wav."""
    wavp = os.path.join(pasta_saida, '_todo.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', arquivo, '-ac', '1', '-ar', str(SR), wavp], check=True)
    w = wave.open(wavp); v = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768
    jan = int(.02 * SR); en = np.sqrt(np.convolve(v ** 2, np.ones(jan) / jan, 'same'))
    lim = max(en.max() * .04, 1e-4); quieto = en < lim
    pausas = []; i = 0
    while i < len(v):
        if quieto[i]:
            j = i
            while j < len(v) and quieto[j]: j += 1
            if i > 0 and j < len(v): pausas.append((j - i, (i + j) // 2))
            i = j
        else: i += 1
    cortes = sorted(c for _, c in sorted(pausas, reverse=True)[:n - 1])
    if len(cortes) < n - 1: raise SystemExit(f'achei só {len(cortes) + 1} trechos na narração; esperava {n}')
    bordas = [0] + cortes + [len(v)]; arquivos = []
    for k in range(n):
        seg = v[bordas[k]:bordas[k + 1]]; q = np.where(np.abs(seg) > lim)[0]
        seg = seg[max(0, q[0] - int(.05 * SR)):q[-1] + int(.1 * SR)] if len(q) else seg
        arquivos.append(seg)
    return arquivos

def duracoes(r, pasta):
    out = []
    if pasta:   # narração num arquivo só (narracao.*): divide pelas pausas
        unico = [p for p in glob.glob(os.path.join(pasta, 'narracao.*'))]
        if unico:
            segs = dividir(unico[0], len(r['cenas']), pasta)
            for c, seg in zip(r['cenas'], segs):
                p = os.path.join(pasta, f"{c['id']}.wav")
                with wave.open(p, 'w') as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(seg, -1, 1) * 32767).astype('<i2').tobytes())
    for c in r['cenas']:
        aud = None
        if pasta:
            for ext in ('wav', 'mp3', 'm4a', 'ogg'):
                p = os.path.join(pasta, f"{c['id']}.{ext}")
                if os.path.exists(p): aud = p; break
        if aud:
            d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', aud]).strip())
            out.append((d + FOLGA, aud, d))
        else:
            d = len(c['fala'].split()) / RITMO
            out.append((d + FOLGA, None, d))
    return out

def trechos(fala, n=7):
    """legenda em pedaços de até n palavras"""
    w = fala.split(); out = []; cur = []
    for x in w:
        cur.append(x)
        if len(cur) >= n or x.endswith(('.', '?', '!', ',')) and len(cur) >= 4:
            out.append(' '.join(cur)); cur = []
    if cur: out.append(' '.join(cur))
    return out

# ---------- página (motion: fundo que troca de cor, lâmpada que passeia, formas que crescem e encolhem) ----------
IC.update({'letra': '<path d="M3.5 19 8.5 5l5 14M5.3 14h6.4"/><path d="M17.5 8v6M14.5 11h6"/>',
           'pausa': '<rect x="6" y="5" width="4" height="14" rx="1.5"/><rect x="14" y="5" width="4" height="14" rx="1.5"/>'})
CLARO = '#F7F4FF'
# fundo e cor do texto de cada cena (cores da marca; azul e vermelho só para os lados dos candidatos)
FUNDO = {'01': (ROXO, '#fff'), '02': (LAV, T), '03': (T, '#fff'), '04': (AM, T), '05': (ROXO, '#fff'), '06': (LAV, T),
         '07': (T, '#fff'), '08': (CLARO, T), '09': (CLARO, T), '10': (ROXO, '#fff'), '11': (ROXO, '#fff')}
# lâmpada da marca: x, y (centro), escala, giro, opacidade — no começo e no fim ela é a estrela, no meio passeia ao fundo
LAMP = {'01': (540, 700, 2.3, 0, 1), '02': (900, 1480, 1.3, 8, .12), '03': (170, 1560, 1.6, -10, .10), '04': (880, 1560, 1.1, 6, .14),
        '05': (190, 1480, 1.7, -6, .10), '06': (890, 1470, 1.2, 12, .12), '07': (540, 980, 3.6, 0, .06), '08': (900, 1620, 1.0, -8, .10),
        '09': (180, 1620, 1.0, 8, .10), '10': (170, 1530, 1.5, -12, .10), '11': (540, 640, 2.3, 0, 1)}
SOMBRA = lambda fundo: T if fundo in (AM, LAV, CLARO) else AM

CSS = """
.f{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'Public Sans'}
.sc{position:absolute;inset:0;visibility:hidden}
.ab{position:absolute}
.lg{position:absolute;left:60px;right:60px;bottom:190px;display:flex;justify-content:center;visibility:hidden;z-index:9}
.lg span{background:rgba(22,24,29,.9);color:#fff;font:700 46px/1.3 'Public Sans';padding:16px 26px;border-radius:18px;text-align:center;max-width:900px}
@keyframes show{from{visibility:hidden}to{visibility:visible}}
@keyframes hide{to{visibility:hidden}}
@keyframes foco{from{opacity:0;filter:blur(16px);transform:translateY(30px)}to{opacity:1;filter:blur(0);transform:none}}
@keyframes sair{to{opacity:0;filter:blur(14px);transform:scale(.96)}}
@keyframes pop{0%%{opacity:0;transform:scale(.2)}55%%{opacity:1;transform:scale(1.12)}78%%{transform:scale(.95)}100%%{transform:scale(1)}}
@keyframes cresce{from{transform:scale(0)}to{transform:scale(1)}}
@keyframes giro{to{transform:rotate(360deg)}}
@keyframes flutua{0%%,100%%{transform:translateY(0) rotate(-3deg)}50%%{transform:translateY(-26px) rotate(3deg)}}
@keyframes pulsa{0%%,100%%{transform:scale(1);opacity:.55}50%%{transform:scale(1.18);opacity:.15}}
@keyframes onda{from{transform:scale(.3);opacity:.7}to{transform:scale(2.6);opacity:0}}
@keyframes traco{from{stroke-dashoffset:var(--L)}to{stroke-dashoffset:0}}
@keyframes entraD{from{opacity:0;transform:translateX(320px)}to{opacity:1;transform:none}}
@keyframes realce{0%%{transform:scale(1)}30%%{transform:scale(1.28)}100%%{transform:scale(1.12)}}
@keyframes apaga{to{transform:scale(1);opacity:.6}}
@keyframes balanca{0%%{transform:rotate(-14deg)}60%%{transform:rotate(5deg)}80%%{transform:rotate(-2deg)}100%%{transform:rotate(0)}}
@keyframes luz{from{transform:scale(0);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes logo{0%%{transform:scale(.4);opacity:0}70%%{transform:scale(1.08);opacity:1}100%%{transform:scale(1)}}
"""

def kf(nome, pontos, total):
    """keyframes a partir de [(tempo, css)]"""
    linhas = [f'{min(100, max(0, t / total * 100)):.3f}%{{{c}}}' for t, c in pontos]
    return f'@keyframes {nome}{{' + ''.join(linhas) + '}'

def circ(px, fundo, borda=T, sombra=AM, extra=''):
    return f'width:{px}px;height:{px}px;border-radius:50%;background:{fundo};border:5px solid {borda};box-shadow:10px 10px 0 {sombra};display:grid;place-items:center;{extra}'

def pagina(r, durs):
    cenas = r['cenas']; inicio = [0.0]
    for d in durs: inicio.append(inicio[-1] + d[0])
    total = inicio[-1]
    blocos, eventos = [], []
    # fundo e lâmpada animados por keyframes nas trocas de cena
    pf, pl, pw, pp = [], [], [], []
    for k, c in enumerate(cenas):
        t = inicio[k]; f, _ = FUNDO[c['id']]; x, y, sc, rt, op = LAMP[c['id']]
        claro = f in (LAV, CLARO, AM)
        tr = f'transform:translate({x - 540}px,{y - 960}px) scale({sc}) rotate({rt}deg)'
        for tt in ((t, t + .8) if k else (0, .01)):
            pass
        a, b2 = (max(t - .05, 0), t + .75) if k else (0, 0)
        if k: pf.append((a, f'background:{FUNDO[cenas[k - 1]["id"]][0]}')); pl.append((a, pl[-1][1])); pw.append((a, pw[-1][1])); pp.append((a, pp[-1][1]))
        pf.append((b2, f'background:{f}')); pl.append((b2, tr))
        pw.append((b2, f'opacity:{0 if claro else op}')); pp.append((b2, f'opacity:{op if claro else 0}'))
    estilo = (kf('bgc', pf + [(total, pf[-1][1])], total) + kf('lamp', pl + [(total, pl[-1][1])], total)
              + kf('lampw', pw + [(total, pw[-1][1])], total) + kf('lampp', pp + [(total, pp[-1][1])], total))
    lamp = lambda cor: f'<svg width="140" height="140" viewBox="0 0 140 140" style="overflow:visible">{M.simbolo(cor)}</svg>'
    fundo = (f'<div class="ab" style="inset:0;animation:bgc {total:.2f}s linear both"></div>'
             f'<div class="ab" style="left:470px;top:890px;width:140px;height:140px;animation:lamp {total:.2f}s cubic-bezier(.6,0,.3,1) both;z-index:2">'
             f'<div style="animation:flutua 4.5s ease-in-out infinite">'
             f'<div class="ab" style="inset:0;animation:lampw {total:.2f}s linear both">{lamp("#fff")}</div>'
             f'<div class="ab" style="inset:0;animation:lampp {total:.2f}s linear both">{lamp(ROXO)}</div></div></div>')
    for k, (c, (dur, _, fd)) in enumerate(zip(cenas, durs)):
        t0 = inicio[k]; ult = k == len(cenas) - 1; cid = c['id']; f, fg = FUNDO[cid]; sh = SOMBRA(f)
        anim = f'show 0s linear {t0:.2f}s both' + ('' if ult else f',sair .45s ease-in {t0 + dur - .45:.2f}s forwards,hide 0s linear {t0 + dur:.2f}s forwards')
        at = lambda x, t0=t0: f'{t0 + x:.2f}'
        A = lambda nome, d, x, ease='cubic-bezier(.2,.8,.3,1)': f'animation:{nome} {d}s {ease} {at(x)}s both'
        its = c.get('itens', []); passo = max(.6, (fd - 1.4) / max(len(its), 1)); ti = [1.2 + passo * i for i in range(len(its))]
        serif = lambda fs, cor=fg: f"font:900 {fs}px/1.04 'Source Serif 4';letter-spacing:-.02em;color:{cor}"
        def titulo(y, fs=104, x0=.25, centro=True):
            al = 'center' if centro else 'left'
            return (f'<div class="ab" style="left:76px;right:76px;top:{y}px;text-align:{al};{A("foco", .7, x0)};{serif(fs)}">{E(c["titulo"])}'
                    + (f'<br><span style="color:{ROXO if f in (AM, LAV, CLARO) else AM}">{E(c["destaque"])}</span>' if c.get('destaque') else '') + '</div>')
        def chip(y=330):
            if not c.get('chip'): return ''
            bg, cor = (T, AM) if f in (AM, LAV, CLARO) else (AM, T)
            return (f'<div class="ab" style="left:0;right:0;top:{y}px;display:flex;justify-content:center"><span style="{A("pop", .6, .05)};background:{bg};color:{cor};'
                    f'border-radius:999px;padding:10px 28px;font:900 32px \'Public Sans\';letter-spacing:.12em;text-transform:uppercase">{E(c["chip"])}</span></div>')
        h = ''; eventos.append((t0 + .2, 'in'))
        if cid in ('01', '11'):
            # raios de luz girando atrás da lâmpada (que é a estrela no começo e no fim)
            cy = 700 if cid == '01' else 640
            raios = ''.join(f'<rect x="-9" y="-390" width="18" height="110" rx="9" fill="{AM}" transform="rotate({i * 30})"/>' for i in range(12))
            h += (f'<div class="ab" style="left:540px;top:{cy}px;width:0;height:0">'
                  f'<svg class="ab" style="left:-480px;top:-480px;{A("luz", .9, .1)}" width="960" height="960" viewBox="-480 -480 960 960"><g style="transform-origin:0 0;animation:giro 18s linear infinite">{raios}</g></svg>'
                  + ''.join(f'<div class="ab" style="left:-200px;top:-200px;width:400px;height:400px;border-radius:50%;border:6px solid {AM};animation:onda 2.6s ease-out {at(.4 + i * .85)}s infinite"></div>' for i in range(3))
                  + '</div>')
            if cid == '01':
                h += (f'<div class="ab" style="left:0;right:0;top:1130px;text-align:center"><div style="{A("foco", .7, .5)};{serif(110)}">Oi! Eu sou a</div>'
                      f'<div style="{A("pop", .8, 1.3)};{serif(190, AM)};margin-top:6px">Clareia.</div></div>')
                eventos.append((t0 + 1.3, 'in'))
            else:
                h += (f'<div class="ab" style="left:76px;right:76px;top:1070px;display:flex;flex-direction:column;align-items:center;gap:34px">'
                      f'<div style="{A("foco", .7, .3)};{serif(84)};text-align:center">Tudo com fonte em</div>'
                      f'<div style="{A("pop", .7, .9)};background:#fff;color:{ROXO};border:5px solid {T};box-shadow:12px 12px 0 {AM};border-radius:999px;padding:24px 40px;font:900 58px \'Public Sans\'">{E(c["titulo"])}</div>'
                      f'<div style="display:flex;gap:26px"><span style="{A("pop", .7, 1.8)};background:{AM};color:{T};border:5px solid {T};box-shadow:8px 8px 0 {T};border-radius:999px;padding:18px 38px;font:900 46px \'Public Sans\'">Link na bio</span>'
                      f'<span style="{A("pop", .7, 2.6)};background:#fff;color:{ROXO};border:5px solid {T};box-shadow:8px 8px 0 {AM};border-radius:999px;padding:18px 38px;font:900 46px \'Public Sans\'">Siga</span></div></div>')
                eventos += [(t0 + .9, 'in'), (t0 + 1.8, 'in'), (t0 + 2.6, 'in')]
        elif cid == '02':
            # bolha central e quatro bolhas em volta, ligadas por linhas que se desenham
            cx, cy = 540, 1020; pos = [(260, 760), (820, 760), (260, 1290), (820, 1290)]
            linhas = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{T}" stroke-width="5" stroke-dasharray="14 12" style="--L:700;stroke-dashoffset:0;opacity:0;animation:foco .5s ease {at(ti[i] - .1)}s both"/>' for i, (x, y) in enumerate(pos))
            h += chip() + titulo(420, 96) + f'<svg class="ab" style="left:0;top:0" width="1080" height="1920">{linhas}</svg>'
            h += f'<div class="ab" style="left:{cx - 160}px;top:{cy - 160}px;{circ(320, "#fff", sombra=ROXO)};{A("pop", .8, .7)}"><span style="{serif(54, ROXO)};text-align:center">num<br>lugar só</span></div>'
            for i, ((x, y), it) in enumerate(zip(pos, its)):
                h += (f'<div class="ab" style="left:{x - 110}px;top:{y - 110}px;width:220px;display:flex;flex-direction:column;align-items:center;gap:16px;{A("pop", .7, ti[i])}">'
                      f'<div style="{circ(200, ROXO, sombra=AM)}">{ico(it["icone"], 100)}</div>'
                      f'<b style="font:900 40px/1.1 \'Public Sans\';color:{T};text-align:center;width:300px">{E(it["titulo"])}</b></div>')
                eventos.append((t0 + ti[i], 'in'))
        elif cid == '03':
            # anel que se completa como um relógio e as palavras chegando da direita
            L = 2 * 3.1416 * 230
            h += chip() + titulo(420, 110)
            h += (f'<svg class="ab" style="left:290px;top:600px" width="500" height="500" viewBox="0 0 500 500"><circle cx="250" cy="250" r="230" fill="none" stroke="#2E3240" stroke-width="26"/>'
                  f'<circle cx="250" cy="250" r="230" fill="none" stroke="{AM}" stroke-width="26" stroke-linecap="round" transform="rotate(-90 250 250)" stroke-dasharray="{L:.0f}" style="--L:{L:.0f};animation:traco {fd:.1f}s linear {at(.6)}s both"/></svg>'
                  f'<div class="ab" style="left:290px;top:600px;width:500px;height:500px;display:flex;flex-direction:column;align-items:center;justify-content:center;{A("pop", .7, .9)}">'
                  f'<span style="font:900 40px \'Public Sans\';color:#C9C4D6">de hora em hora</span><span style="{serif(118, AM)}">7h-23h</span></div>')
            pal = ['Pesquisas', 'Checagens', 'Boatos', 'Agenda']
            for i, w in enumerate(pal):
                tt = 2.2 + (fd - 2.6) / 4 * i
                h += (f'<div class="ab" style="left:{140 + (i % 2) * 420}px;top:{1170 + (i // 2) * 130}px;{A("entraD", .6, tt)}"><span style="display:inline-block;background:#fff;color:{T};border:5px solid {T};'
                      f'box-shadow:8px 8px 0 {AM};border-radius:999px;padding:14px 34px;font:900 46px \'Public Sans\'">{w}</span></div>')
                eventos.append((t0 + tt, 'in'))
        elif cid == '04':
            # círculo que cresce e o visto que se desenha; depois o elo do link balançando
            h += chip() + titulo(420, 110)
            h += (f'<div class="ab" style="left:310px;top:610px;{circ(460, "#fff", sombra=T)};{A("pop", .8, .6)}">'
                  f'<svg width="300" height="300" viewBox="0 0 24 24" fill="none" stroke="{ROXO}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" stroke-dasharray="24" style="--L:24;animation:traco .8s ease {at(1.3)}s both"/></svg></div>')
            h += (f'<div class="ab" style="left:76px;right:76px;top:1150px;text-align:center;{A("foco", .7, ti[0])};{serif(70)}">Só entra o que tem fonte.</div>'
                  f'<div class="ab" style="left:0;right:0;top:1290px;display:flex;justify-content:center;align-items:center;gap:22px;{A("pop", .7, ti[1])}">'
                  f'<span style="{circ(120, ROXO, sombra=T)}">{ico("link", 70)}</span><span style="font:900 50px/1.2 \'Public Sans\';color:{T}">e o link de<br>quem publicou</span></div>')
            eventos += [(t0 + 1.3, 'in'), (t0 + ti[0], 'in'), (t0 + ti[1], 'in')]
        elif cid == '05':
            # balança que se equilibra: mesmo critério para os dois lados
            h += chip() + titulo(420, 92)
            h += (f'<div class="ab" style="left:240px;top:700px;width:600px;height:420px;{A("pop", .8, .6)}">'
                  f'<div class="ab" style="left:290px;top:60px;width:20px;height:340px;background:#fff;border-radius:10px"></div>'
                  f'<div class="ab" style="left:200px;top:390px;width:200px;height:24px;background:#fff;border-radius:12px"></div>'
                  f'<div class="ab" style="left:0;top:40px;width:600px;height:240px;transform-origin:300px 30px;animation:balanca 1.6s cubic-bezier(.3,1.2,.5,1) {at(1.2)}s both">'
                  f'<div class="ab" style="left:20px;top:20px;width:560px;height:20px;background:#fff;border-radius:10px"></div>'
                  + ''.join(f'<div class="ab" style="left:{x}px;top:40px;width:4px;height:120px;background:#fff"></div><div class="ab" style="left:{x - 70}px;top:150px;{circ(144, "#fff", sombra=AM)}"><i style="width:56px;height:56px;border-radius:50%;background:{cor}"></i></div>'
                            for x, cor in ((60, '#1F4FA8'), (540, '#D62B2B'))) + '</div></div>')
            for i, it in enumerate(its):
                h += (f'<div class="ab" style="left:0;right:0;top:{1170 + i * 112}px;display:flex;justify-content:center;{A("pop", .6, ti[i] + .6)}"><span style="background:#fff;color:{T};border:5px solid {T};'
                      f'box-shadow:8px 8px 0 {AM};border-radius:999px;padding:12px 34px;font:800 42px \'Public Sans\'">{E(it["titulo"])}</span></div>')
                eventos.append((t0 + ti[i] + .6, 'in'))
        elif cid == '06':
            # setas girando em volta de um 4x que pulsa; depois o lápis da errata
            h += chip() + titulo(420, 110)
            h += (f'<div class="ab" style="left:340px;top:600px;width:400px;height:400px;{A("pop", .8, .6)}">'
                  f'<svg class="ab" style="inset:0;animation:giro 6s linear infinite" width="400" height="400" viewBox="0 0 24 24" fill="none" stroke="{ROXO}" stroke-width="1.3" stroke-linecap="round"><path d="M20 12a8 8 0 0 1-13.7 5.6M4 12a8 8 0 0 1 13.7-5.6"/><path d="M17.7 3v3.6h-3.6M6.3 21v-3.6h3.6"/></svg>'
                  f'<div class="ab" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><span style="{serif(150, ROXO)}">4x</span><span style="font:900 38px \'Public Sans\';color:{T}">por dia</span></div></div>')
            h += (f'<div class="ab" style="left:76px;right:76px;top:1110px;text-align:center;{A("foco", .7, ti[1])}"><span style="{serif(84)}">Errei? Corrijo.</span>'
                  f'<svg style="display:block;margin:8px auto 0" width="560" height="40" viewBox="0 0 560 40"><path d="M10 26 C150 6 380 6 550 24" fill="none" stroke="{AM}" stroke-width="12" stroke-linecap="round" stroke-dasharray="560" style="--L:560;animation:traco .7s ease {at(ti[1] + .5)}s both"/></svg></div>'
                  f'<div class="ab" style="left:0;right:0;top:1330px;display:flex;justify-content:center;gap:20px;align-items:center;{A("pop", .6, ti[1] + 1)}">'
                  f'<span style="background:#fff;border:5px solid {T};box-shadow:8px 8px 0 {T};border-radius:999px;padding:12px 30px;font:800 40px \'Public Sans\';color:{T};text-decoration:line-through">antes</span>'
                  f'<span style="font:900 54px \'Public Sans\';color:{T}">→</span>'
                  f'<span style="background:{AM};border:5px solid {T};box-shadow:8px 8px 0 {T};border-radius:999px;padding:12px 30px;font:800 40px \'Public Sans\';color:{T}">depois</span></div>')
            eventos += [(t0 + ti[1], 'in'), (t0 + ti[1] + 1, 'in')]
        elif cid == '07':
            # o momento mais importante: holofote que se abre
            h += (f'<div class="ab" style="left:-260px;top:300px;width:1600px;height:1600px;border-radius:50%;background:radial-gradient(circle,rgba(255,212,59,.35),rgba(255,212,59,0) 62%);{A("luz", 1.2, .1)}"></div>'
                  f'<div class="ab" style="left:76px;right:76px;top:720px;text-align:center"><div style="{A("foco", .7, .3)};{serif(110)}">{E(c["titulo"])}</div>'
                  f'<div style="{A("pop", .9, 1.6)};{serif(150, AM)};margin-top:30px">{E(c["destaque"])}</div></div>')
            eventos.append((t0 + 1.6, 'in'))
        elif cid in ('08', '09'):
            # anel de ícones girando devagar; cada um cresce quando é citado e o nome aparece no centro
            cx, cy, R = 540, 1010, 330
            import math
            h += chip() + titulo(420, 96)
            h += f'<div class="ab" style="left:{cx - R - 110}px;top:{cy - R - 110}px;width:{2 * R + 220}px;height:{2 * R + 220}px;{A("cresce", .8, .5)}">'
            h += f'<div class="ab" style="inset:110px;border-radius:50%;border:5px dashed {ROXO};opacity:.35;animation:giro 30s linear infinite"></div>'
            for i, it in enumerate(its):
                ang = -90 + i * 90; x = R + 110 + R * math.cos(math.radians(ang)); y = R + 110 + R * math.sin(math.radians(ang))
                fim = ti[i + 1] if i + 1 < len(its) else fd + .5
                h += (f'<div class="ab" style="left:{x - 95}px;top:{y - 95}px;{A("pop", .6, .7 + .15 * i)}"><div style="{circ(190, ROXO, sombra=AM)};'
                      f'animation:realce .5s ease {at(ti[i])}s both,apaga .4s ease {at(fim)}s forwards">{ico(it["icone"], 96)}</div></div>')
                h += (f'<div class="ab" style="left:{R + 110 - 220}px;top:{R + 110 - 80}px;width:440px;height:160px;display:flex;align-items:center;justify-content:center;text-align:center;'
                      f'opacity:0;animation:foco .4s ease {at(ti[i])}s both{"" if i + 1 == len(its) else f",sair .3s ease {at(fim - .2)}s forwards"};{serif(56, ROXO)}">{E(it["titulo"])}</div>')
                eventos.append((t0 + ti[i], 'in'))
            h += '</div>'
        elif cid == '10':
            # dois nós ligados por uma linha: a IA organiza, uma pessoa aprova
            h += chip() + titulo(420, 100)
            nos = [(270, 820, 'ia', 'IA busca e organiza'), (810, 820, 'pessoa', 'Uma pessoa aprova')]
            h += (f'<svg class="ab" style="left:0;top:0" width="1080" height="1920"><path d="M270 820 C420 700 660 700 810 820" fill="none" stroke="{AM}" stroke-width="10" stroke-linecap="round" stroke-dasharray="620" style="--L:620;animation:traco .8s ease {at(ti[1] - .3)}s both"/></svg>')
            for i, (x, y, ic, txt) in enumerate(nos):
                h += (f'<div class="ab" style="left:{x - 170}px;top:{y - 115}px;width:340px;display:flex;flex-direction:column;align-items:center;gap:20px;{A("pop", .7, ti[i])}">'
                      f'<div style="{circ(230, "#fff", sombra=AM)}">{ico(ic, 120, ROXO)}</div><b style="font:900 42px/1.15 \'Public Sans\';color:#fff;text-align:center">{txt}</b></div>')
                eventos.append((t0 + ti[i], 'in'))
            h += (f'<div class="ab" style="left:0;right:0;top:1200px;display:flex;justify-content:center;{A("pop", .7, ti[2])}"><span style="display:inline-flex;align-items:center;gap:18px;background:{AM};color:{T};'
                  f'border:5px solid {T};box-shadow:10px 10px 0 {T};border-radius:999px;padding:18px 38px;font:900 46px \'Public Sans\'">{ico("ouvir", 56, T)}Voz gerada por IA</span></div>')
            eventos.append((t0 + ti[2], 'in'))
        blocos.append(f'<div class="sc" style="animation:{anim}">{h}</div>')
        ts = trechos(c.get('legenda', c['fala'])); tot = sum(len(x.split()) for x in ts); tt = t0 + .15
        for j, x in enumerate(ts):
            d = fd * len(x.split()) / tot; fim = tt + d if (j < len(ts) - 1 or not ult) else 9999
            blocos.append(f'<div class="lg" style="animation:show 0s linear {tt:.2f}s both,hide 0s linear {fim:.2f}s forwards"><span>{E(x)}</span></div>')
            tt += d
        if not ult: eventos.append((t0 + dur - .45, 'out'))
    selo = (f'<span class="ab" style="right:76px;top:150px;background:rgba(22,24,29,.55);border-radius:999px;padding:8px 18px;font:700 26px \'Public Sans\';color:#fff;z-index:8">Voz gerada por IA</span>') if r.get('voz_ia') else ''
    topo = (f'<div class="ab" style="left:0;right:0;top:0;height:22px;display:flex;z-index:8"><i style="flex:1;background:#1F4FA8"></i><i style="flex:1;background:#D62B2B"></i></div>'
            f'<div class="ab" style="left:66px;top:110px;padding:10px 16px;border-radius:24px;background:{ROXO};z-index:8"><img src="file://{LOGO}" style="height:96px;display:block;animation:logo .6s cubic-bezier(.2,.9,.3,1.3) 0s both;transform-origin:left center"></div>{selo}')
    css = (f"@font-face{{font-family:'Public Sans';src:url('file://{FONTES}/PublicSans.ttf');font-weight:100 900}}"
           f"@font-face{{font-family:'Source Serif 4';src:url('file://{FONTES}/SourceSerif4.ttf');font-weight:200 900}}body{{margin:0}}" + CSS + estilo)
    return f'<!doctype html><meta charset="utf-8"><style>{css}</style><div class="f">{fundo}{topo}{"".join(blocos)}</div>', total, eventos

# ---------- som: narração + sopros ----------
def bolha():
    """entrada: bolhinha macia, com a nota subindo (escolhida pelo dono em 21/10)"""
    d = .16; n = int(d * SR); t = np.arange(n) / SR; f = 500 * np.exp(t / d * np.log(1.9))
    e = np.ones(n); e[:int(.004 * SR)] = np.linspace(0, 1, int(.004 * SR)); e[-int(.03 * SR):] *= np.linspace(1, 0, int(.03 * SR))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .05) * e * .22

def madeira():
    """saída: toque de madeira abafado, bem discreto (escolhido pelo dono em 21/10)"""
    d = .12; n = int(d * SR); t = np.arange(n) / SR; y = np.sin(2 * np.pi * 560 * t) * np.exp(-t / .025)
    k = np.exp(-np.arange(40) / 8.0); k /= k.sum(); return np.convolve(y, k, 'same') * .26

def audio(durs, eventos, total, saida):
    mix = np.zeros(int((total + 1) * SR))
    t0 = 0.0
    for dur, aud, _ in durs:
        if aud:
            wavp = os.path.join(tempfile.gettempdir(), 'nar.wav')
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', aud, '-ac', '1', '-ar', str(SR), wavp], check=True)
            w = wave.open(wavp); v = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768
            v = v / (np.abs(v).max() + 1e-9) * .8
            i = int((t0 + .15) * SR); mix[i:i + len(v)] += v[:len(mix) - i]
        t0 += dur
    si, so = bolha(), madeira()
    for t, k in eventos:
        y = si if k == 'in' else so; i = int(t * SR); j = min(len(mix), i + len(y)); mix[i:j] += y[:j - i]
    mix = mix[:int(total * SR)]; mix = np.clip(mix, -.98, .98)
    with wave.open(saida, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())

async def gerar(pasta, saida, fps=30):
    from playwright.async_api import async_playwright
    from PIL import Image
    r = json.load(open(os.path.join(AQUI, 'roteiro.json')))
    durs = duracoes(r, pasta)
    doc, total, eventos = pagina(r, durs)
    os.makedirs(saida, exist_ok=True); tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, 'v.html'), 'w').write(doc)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        await pg.goto('file://' + os.path.join(tmp, 'v.html')); await pg.wait_for_timeout(600)
        for i in range(int(round(fps * total))):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / fps}}})")
            await pg.screenshot(path=os.path.join(tmp, f'f{i:05d}.jpg'), type='jpeg', quality=88)
        await b.close()
    Image.open(os.path.join(tmp, f'f{int(fps * 2.4):05d}.jpg')).convert('RGB').save(os.path.join(saida, 'capa.jpg'), quality=92)
    audio(durs, eventos, total, os.path.join(tmp, 'a.wav'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, 'f%05d.jpg'), '-i', os.path.join(tmp, 'a.wav'),
                    '-c:a', 'aac', '-b:a', '160k', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-movflags', '+faststart', '-shortest',
                    os.path.join(saida, 'reels.mp4')], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('duração', round(total, 1), 's;', sum(1 for d in durs if d[1]), 'cenas com áudio')

def so_audio(pasta, video, saida):
    """refaz só o som de um vídeo já montado (mesmo roteiro e mesmos áudios)"""
    r = json.load(open(os.path.join(AQUI, 'roteiro.json'))); durs = duracoes(r, pasta); _, total, eventos = pagina(r, durs)
    tmp = tempfile.mkdtemp(); audio(durs, eventos, total, os.path.join(tmp, 'a.wav'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', os.path.join(tmp, 'a.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', saida], check=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--so-audio':
        so_audio(sys.argv[2], sys.argv[3], sys.argv[4]); sys.exit()
    a = sys.argv[1:]
    asyncio.run(gerar(a[0] if len(a) > 1 else None, a[-1]))
