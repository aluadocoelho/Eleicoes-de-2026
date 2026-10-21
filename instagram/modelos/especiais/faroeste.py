#!/usr/bin/env python3
"""Reels especial "faroeste" (pedido do dono em 21/10): a briga dos sigilos contada como um duelo no velho oeste.
Sem pessoas (regra do TSE de 22/10 21h a 26/10): só cenário desenhado (pôr do sol, cactos, feno rolando) e dois chapéus,
vermelho para Lula e azul para Flávio. Trilha clareia-faroeste-30s (gerar_dinamicas.py faroeste), 120 bpm, drop aos 3 s.

Uso: python3 instagram/modelos/especiais/faroeste.py roteiro.json pasta/   (gera reels.mp4 e capa.jpg)
roteiro.json: {"faltam": 4, "titulo": "...", "cenas": [{"chip", "titulo", "cartoes": [{"rotulo", "texto", "lado"}]} ou
              {"chip", "titulo", "barras": [{"rotulo", "valor", "lado"}], "nota"}], "final": {"titulo", "destaque"}, "rodape"}
"""
import os, sys, json, html, asyncio, tempfile, shutil, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(AQUI); sys.path.insert(0, MOD)
import marca as M
E = html.escape
FONTES = os.path.join(MOD, 'fontes'); MARCA = os.path.abspath(os.path.join(MOD, '..', '..', 'marca'))
TRILHA = os.path.join(MOD, 'trilhas', 'clareia-faroeste-30s.wav')
ROXO, AM, T, AZ, VM = '#3E2492', '#FFD43B', '#16181D', '#1F4FA8', '#D62B2B'
PAPEL, MADEIRA, TERRA = '#F4E6C6', '#6B4426', '#2A1A10'
SERIF, SANS = "'Source Serif 4',Georgia,serif", "'Public Sans',system-ui,sans-serif"
COR = {'lula': VM, 'flavio': AZ, 'neutro': ROXO}
ABRE, FINAL, CURTA, LONGA = 3.0, 3.0, 4.0, 5.0

def chapeu(cor, x, flip=False, atraso=0):
    return (f'<svg class="hat" style="position:absolute;left:{x}px;bottom:300px;width:300px;height:170px;animation-delay:{atraso}s;{"transform:scaleX(-1)" if flip else ""}" viewBox="0 0 300 170">'
            f'<ellipse cx="150" cy="150" rx="146" ry="16" fill="#000" opacity=".25"/>'
            f'<path d="M8 118 Q40 140 150 140 Q260 140 292 118 Q270 104 240 112 Q150 132 60 112 Q30 104 8 118Z" fill="{cor}" stroke="{TERRA}" stroke-width="5"/>'
            f'<path d="M84 116 C80 80 86 44 104 36 C118 30 128 44 150 44 C172 44 182 30 196 36 C214 44 220 80 216 116 Q150 128 84 116Z" fill="{cor}" stroke="{TERRA}" stroke-width="5"/>'
            f'<path d="M150 46 C146 70 148 90 150 104" fill="none" stroke="{TERRA}" stroke-width="4" opacity=".5"/>'
            f'<path d="M80 100 Q150 114 220 100 L222 116 Q150 128 78 116Z" fill="{TERRA}" opacity=".55"/></svg>')

def cacto(x, h, esc=1):
    return (f'<svg style="position:absolute;left:{x}px;bottom:{330 - 10 * esc}px;width:{120 * esc}px;height:{h}px" viewBox="0 0 120 260" preserveAspectRatio="xMidYMax meet">'
            f'<path d="M48 260V40a12 12 0 0 1 24 0v220Z M48 150H26a10 10 0 0 1-10-10V95a10 10 0 0 1 20 0v35h12 M72 120h22v-45a10 10 0 0 1 20 0v55a10 10 0 0 1-10 10H72" fill="{TERRA}" stroke="{TERRA}" stroke-width="4" stroke-linejoin="round"/></svg>')

FENO = (f'<svg width="150" height="150" viewBox="0 0 100 100"><g fill="none" stroke="#8A5A2B" stroke-width="3" stroke-linecap="round">'
        + ''.join(f'<path d="M50 50 m{-30 + k * 7} {-20 + (k * 13) % 40} q{20 - k} {30 - k * 3} {40 - k * 2} {-10 + k}"/>' for k in range(9))
        + '<circle cx="50" cy="50" r="38"/><circle cx="50" cy="50" r="26"/></g></svg>')

def telas(r):
    out = [('abre', r, ABRE)]
    for c in r['cenas']:
        chars = len(c.get('titulo', '')) + sum(len(x.get('texto', '')) + len(x.get('rotulo', '')) for x in c.get('cartoes', [])) + len(c.get('nota', ''))
        out.append(('cena', c, LONGA if chars > 120 else CURTA))
    out.append(('final', r['final'], FINAL))
    return out

CSS = """
.f{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:%s;color:%s}
.sc{position:absolute;left:0;right:0;top:300px;bottom:520px;display:flex;flex-direction:column;justify-content:center;padding:0 70px;visibility:hidden;z-index:4}
@keyframes show{from{visibility:hidden}to{visibility:visible}}
@keyframes hide{to{visibility:hidden}}
@keyframes cai{0%%{transform:translateY(-900px) rotate(-6deg)}60%%{transform:translateY(30px) rotate(2deg)}78%%{transform:translateY(-14px) rotate(-1deg)}100%%{transform:none}}
@keyframes foco{from{opacity:0;filter:blur(16px);transform:translateY(24px)}to{opacity:1;filter:blur(0);transform:none}}
@keyframes card{from{opacity:0;transform:translateY(80px) rotate(-2deg)}to{opacity:1;transform:none}}
@keyframes sair{to{opacity:0;filter:blur(12px);transform:scale(1.02)}}
@keyframes rola{from{transform:translateX(-260px) rotate(0)}to{transform:translateX(1340px) rotate(1080deg)}}
@keyframes pula{0%%,100%%{margin-bottom:0}50%%{margin-bottom:46px}}
@keyframes hat{0%%{opacity:0;translate:0 60px}100%%{opacity:1;translate:0 0}}
@keyframes sol{from{transform:translateY(80px)}to{transform:none}}
@keyframes barra{from{width:0}}
@keyframes poeira{from{opacity:.0;transform:translateX(0)}30%%{opacity:.5}to{opacity:0;transform:translateX(220px)}}
@keyframes logo{0%%{transform:scale(.4);opacity:0}70%%{transform:scale(1.08);opacity:1}100%%{transform:scale(1)}}
.foco{animation:foco .7s cubic-bezier(.2,.8,.3,1) both}
.card{animation:card .65s cubic-bezier(.2,.8,.3,1) both}
.hat{animation:hat .8s cubic-bezier(.2,.8,.3,1) both}
""" % (SANS, T)

def placa(txt, fs, extra=''):
    """letreiro de madeira com pregos"""
    return (f'<div style="position:relative;background:linear-gradient(180deg,#8A5A33,#6B4426);border:6px solid {TERRA};border-radius:14px;padding:26px 46px;'
            f'box-shadow:0 14px 0 rgba(0,0,0,.25);{extra}">'
            + ''.join(f'<i style="position:absolute;{p};width:16px;height:16px;border-radius:50%;background:#D8C8A8;border:3px solid {TERRA}"></i>' for p in ('left:14px;top:14px', 'right:14px;top:14px', 'left:14px;bottom:14px', 'right:14px;bottom:14px'))
            + f'<div style="font:900 {fs}px/1 {SERIF};color:{AM};letter-spacing:.06em;text-transform:uppercase;text-align:center;text-shadow:4px 4px 0 {TERRA}">{txt}</div></div>')

def cartaz(inner, pad=40):
    """papel de cartaz antigo"""
    return (f'<div style="background:{PAPEL};border:5px solid {TERRA};border-radius:10px;padding:{pad}px;box-shadow:12px 12px 0 rgba(42,26,16,.55);'
            f'background-image:radial-gradient(rgba(107,68,38,.10) 1px,transparent 1.5px);background-size:9px 9px">{inner}</div>')

def pagina(r):
    blocos, t0 = [], 0.0
    for tipo, d, dur in telas(r):
        anim = [f'show 0s linear {t0:.2f}s both']
        if tipo == 'cena': anim.append(f'sair .45s ease-in {t0 + dur - .45:.2f}s forwards')
        if tipo != 'final': anim.append(f'hide 0s linear {t0 + dur:.2f}s forwards')
        vis = 'animation:' + ','.join(anim); at = lambda x, t0=t0: f'{t0 + x:.2f}'
        if tipo == 'abre':
            n = int(r['faltam'])
            blocos.append(
                f'<div class="sc" style="{vis};align-items:center;gap:44px">'
                f'<div style="animation:cai .9s cubic-bezier(.3,1.2,.5,1) {at(.1)}s both">{placa(f"Faltam {n} dias", 120)}</div>'
                f'<div class="foco" style="animation-delay:{at(.9)}s;font:900 96px/1.02 {SERIF};text-align:center;color:#fff;text-shadow:5px 5px 0 {TERRA}">{E(r["titulo"])}<br>'
                f'<span style="color:{AM}">{E(r.get("destaque", ""))}</span></div></div>')
        elif tipo == 'cena':
            corpo = ''
            for k, c in enumerate(d.get('cartoes', [])):
                cor = COR.get(c.get('lado', 'neutro'), ROXO)
                corpo += (f'<div class="card" style="animation-delay:{at(.7 + .35 * k)}s;margin-top:30px">' + cartaz(
                    f'<div style="display:flex;align-items:center;gap:18px"><i style="width:30px;height:30px;border-radius:50%;background:{cor};border:4px solid {TERRA}"></i>'
                    f'<b style="font:900 36px {SANS};letter-spacing:.08em;text-transform:uppercase">{E(c["rotulo"])}</b></div>'
                    f'<div style="font:600 46px/1.32 {SANS};margin-top:16px">{E(c["texto"])}</div>', 38) + '</div>')
            if d.get('barras'):
                mx = max(b['valor'] for b in d['barras'])
                bs = ''.join(f'<div style="margin-top:{0 if k == 0 else 34}px"><div style="display:flex;justify-content:space-between;align-items:baseline;font:800 40px {SANS}"><span>{E(b["rotulo"])}</span>'
                             f'<span style="font:900 96px/1 {SERIF}">{b["valor"]}</span></div><div style="height:56px;background:#E4D2AC;border:4px solid {TERRA};border-radius:10px;margin-top:10px;overflow:hidden">'
                             f'<i style="display:block;height:100%;width:{b["valor"] / mx * 100:.1f}%;background:{COR[b["lado"]]};animation:barra .9s cubic-bezier(.2,.8,.3,1) {at(1 + .3 * k)}s both"></i></div></div>'
                             for k, b in enumerate(d['barras']))
                nota = f'<div style="font:500 30px/1.38 {SANS};color:#5A3E26;margin-top:26px;border-top:3px dashed #B9A07A;padding-top:20px">{E(d["nota"])}</div>' if d.get('nota') else ''
                corpo += f'<div class="card" style="animation-delay:{at(.6)}s;margin-top:30px">' + cartaz(bs + nota, 40) + '</div>'
            blocos.append(
                f'<div class="sc" style="{vis}">'
                f'<div class="foco" style="animation-delay:{at(.1)}s;align-self:flex-start">{placa(E(d["chip"]), 40, "padding:18px 58px")}</div>'
                f'<div class="foco" style="animation-delay:{at(.35)}s;font:900 {92 if len(d["titulo"]) < 26 else 78}px/1.02 {SERIF};color:#fff;text-shadow:5px 5px 0 {TERRA};margin-top:34px">{E(d["titulo"])}</div>'
                f'{corpo}</div>')
        else:
            blocos.append(
                f'<div class="sc" style="{vis};gap:40px">'
                f'<div class="foco" style="animation-delay:{at(.1)}s;font:900 104px/1.02 {SERIF};color:#fff;text-shadow:5px 5px 0 {TERRA}">{E(d["titulo"])}<br><span style="color:{AM}">{E(d.get("destaque", ""))}</span></div>'
                f'<div style="display:flex;justify-content:space-between;align-items:center;gap:26px">'
                f'<div class="foco" style="animation-delay:{at(.5)}s;font:600 30px/1.4 {SANS};color:#FFF3DA;max-width:560px;text-shadow:2px 2px 0 {TERRA}">{E(r.get("rodape", ""))}</div>'
                f'<div style="animation:cai .8s cubic-bezier(.3,1.2,.5,1) {at(.35)}s both;flex:none;background:{AM};color:{T};border:5px solid {TERRA};box-shadow:8px 8px 0 {TERRA};border-radius:22px;padding:24px 34px;font:900 46px {SANS};white-space:nowrap">Link na bio</div></div></div>')
        t0 += dur
    total = t0
    # feno rolando nas trocas de tela
    fenos = ''.join(f'<div style="position:absolute;left:0;bottom:318px;z-index:3;animation:rola 2.6s linear {t:.2f}s both"><div style="animation:pula .45s ease-in-out infinite">{FENO}</div></div>'
                    for t in (1.2, 8.2, 16.4))
    poeira = ''.join(f'<i style="position:absolute;left:{x}px;bottom:{y}px;width:{w}px;height:{w // 3}px;border-radius:50%;background:#F1C88E;filter:blur(8px);animation:poeira 3s ease-out {d:.1f}s infinite;z-index:3"></i>'
                     for x, y, w, d in ((120, 330, 160, 0), (520, 320, 220, 1.1), (820, 340, 140, 2.0), (300, 350, 120, 2.6)))
    cenario = (f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,{ROXO} 0%,#7A2E6E 30%,#D9542F 55%,#F2A541 70%,#F6C26B 76%)"></div>'
               f'<div style="position:absolute;left:290px;bottom:330px;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle,#FFE680 0%,{AM} 55%,#F7B733 100%);animation:sol 3s ease-out 0s both;box-shadow:0 0 160px 60px rgba(255,212,59,.45)"></div>'
               f'<svg style="position:absolute;left:0;bottom:330px" width="1080" height="260" viewBox="0 0 1080 260" preserveAspectRatio="none"><path d="M0 260V150L90 120L170 140L230 70L320 60L360 110L470 130L560 90L640 100L700 40L820 30L860 90L960 110L1080 80V260Z" fill="#7A3B2A" opacity=".85"/></svg>'
               f'<div style="position:absolute;left:0;right:0;bottom:0;height:340px;background:linear-gradient(180deg,#C98B4B,#9C6233)"></div>'
               f'<svg style="position:absolute;left:0;bottom:0" width="1080" height="340" viewBox="0 0 1080 340" preserveAspectRatio="none"><path d="M0 40Q270 0 540 30T1080 20V340H0Z" fill="#B37641"/><path d="M0 140Q300 100 600 150T1080 120V340H0Z" fill="#8E5A2E"/></svg>'
               + cacto(40, 260) + cacto(930, 200, .8) + cacto(760, 130, .55)
               + chapeu(VM, 70, False, .3) + chapeu(AZ, 710, True, .5) +
               f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 55%,rgba(30,12,4,.55));z-index:5;pointer-events:none"></div>')
    topo = (f'<div style="position:absolute;left:0;right:0;top:0;display:flex;height:22px;z-index:7"><i style="flex:1;background:{AZ}"></i><i style="flex:1;background:{VM}"></i></div>'
            f'<div style="position:absolute;left:70px;right:70px;top:120px;display:flex;align-items:center;justify-content:space-between;z-index:7">'
            f'<img src="file://{MARCA}/clareia-eleicoes-roxo.svg" style="height:110px;animation:logo .6s cubic-bezier(.2,.9,.3,1.3) 0s both;transform-origin:left center">'
            f'<span style="font:800 30px {SANS};color:#F1E8FF">{M.ARROBA}</span></div>')
    css = (f"@font-face{{font-family:'Public Sans';src:url('file://{FONTES}/PublicSans.ttf');font-weight:100 900}}"
           f"@font-face{{font-family:'Source Serif 4';src:url('file://{FONTES}/SourceSerif4.ttf');font-weight:200 900}}body{{margin:0}}" + CSS)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="f">{cenario}{poeira}{fenos}{topo}{"".join(blocos)}</div></body></html>'), total

async def gerar(r, saida, fps=30):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True); tmp = tempfile.mkdtemp()
    doc, dur = pagina(r); open(os.path.join(tmp, 'v.html'), 'w').write(doc)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        await pg.goto('file://' + os.path.join(tmp, 'v.html')); await pg.wait_for_timeout(500)
        for i in range(int(round(fps * dur))):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / fps}}})")
            await pg.screenshot(path=os.path.join(tmp, f'f{i:04d}.jpg'), type='jpeg', quality=90)
        await b.close()
    Image.open(os.path.join(tmp, f'f{int(fps * 2.6):04d}.jpg')).convert('RGB').save(os.path.join(saida, 'capa.jpg'), quality=92)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, 'f%04d.jpg'), '-i', TRILHA,
                    '-af', f'afade=t=out:st={dur - 1.2:.2f}:d=1.2', '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.2f}',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(saida, 'reels.mp4')], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print('duração', dur)

if __name__ == '__main__':
    asyncio.run(gerar(json.load(open(sys.argv[1])), sys.argv[2]))
