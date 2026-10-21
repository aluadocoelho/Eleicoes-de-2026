#!/usr/bin/env python3
"""Reels de engajamento (curta, compartilhe, reposte, comente), simples e com os MESMOS cartões do feed e do story
(identidade/destaques_e_engajamento.py). Pedido do dono em 21/10: menos texto, sem repetir o nome da Clareia.
Telas: abertura 3 s, dois cartões por tela (4 s cada), final 3 s com o botão Siga. Trilha do engajamento (funkpop por padrão).
Uso: python3 instagram/modelos/especiais/engajamento.py pasta/   (gera reels.mp4 e capa.jpg)
"""
import os, sys, asyncio, tempfile, shutil, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(AQUI)
sys.path.insert(0, MOD); sys.path.insert(0, os.path.join(MOD, 'identidade'))
import destaques_e_engajamento as D
import marca as M
TRILHA = os.path.join(MOD, 'trilhas', os.environ.get('TRILHA', 'clareia-funkpop-30s.wav'))
ROXO, AM, T = D.ROXO, D.AM, D.T
TEMPOS = [3.0, 4.0, 4.0, 3.0]

CSS = """
.f{width:1080px;height:1920px;position:relative;overflow:hidden;background:%s;color:#fff;font-family:'Public Sans'}
.sc{position:absolute;left:80px;right:80px;top:300px;bottom:340px;display:flex;flex-direction:column;justify-content:center;gap:44px;visibility:hidden}
@keyframes show{from{visibility:hidden}to{visibility:visible}}
@keyframes hide{to{visibility:hidden}}
@keyframes foco{from{opacity:0;filter:blur(16px);transform:translateY(24px)}to{opacity:1;filter:blur(0);transform:none}}
@keyframes card{from{opacity:0;transform:translateY(90px)}to{opacity:1;transform:none}}
@keyframes sair{to{opacity:0;filter:blur(12px)}}
@keyframes pop{0%%{opacity:0;transform:scale(.4)}60%%{opacity:1;transform:scale(1.1)}80%%{transform:scale(.96)}100%%{transform:scale(1)}}
@keyframes logo{0%%{transform:scale(.4);opacity:0}70%%{transform:scale(1.08);opacity:1}100%%{transform:scale(1)}}
.foco{animation:foco .7s cubic-bezier(.2,.8,.3,1) both}
.card{animation:card .65s cubic-bezier(.2,.8,.3,1) both}
""" % ROXO

def pagina():
    t = [0]
    for d in TEMPOS: t.append(t[-1] + d)
    vis = lambda k, sai=True: ('animation:' + f'show 0s linear {t[k]:.2f}s both'
                               + (f',sair .4s ease-in {t[k + 1] - .4:.2f}s forwards,hide 0s linear {t[k + 1]:.2f}s forwards' if sai else ''))
    at = lambda k, x: f'{t[k] + x:.2f}'
    tit = lambda a, b, fs=124: (f'<div style="font:900 {fs}px/1.02 \'Source Serif 4\';letter-spacing:-.02em">{a}<br><span style="color:{AM}">{b}</span></div>')
    telas = [f'<div class="sc" style="{vis(0)}"><div class="foco" style="animation-delay:{at(0, .3)}s">{tit("Gostou do conteúdo?", "Ajude a clarear.")}</div></div>']
    for k, par in ((1, D.ACOES[:2]), (2, D.ACOES[2:])):
        telas.append(f'<div class="sc" style="{vis(k)}">' + ''.join(
            f'<div class="card" style="animation-delay:{at(k, .15 + .35 * i)}s">{D.cartao(a, d, ic, 1.14)}</div>' for i, (a, d, ic, c) in enumerate(par)) + '</div>')
    telas.append(f'<div class="sc" style="{vis(3, False)};align-items:flex-start">'
                 f'<div class="foco" style="animation-delay:{at(3, .15)}s">{tit("Siga para não perder", "nada até domingo.", 104)}</div>'
                 f'<span style="animation:pop .7s cubic-bezier(.3,1.3,.5,1) {at(3, .6)}s both;background:{AM};color:{T};border:5px solid {T};box-shadow:8px 8px 0 {T};'
                 f'border-radius:999px;padding:22px 52px;font:900 52px \'Public Sans\'">Siga</span></div>')
    topo = (f'<div style="position:absolute;left:0;right:0;top:0;height:22px;display:flex"><i style="flex:1;background:#1F4FA8"></i><i style="flex:1;background:#D62B2B"></i></div>'
            f'<svg style="position:absolute;right:-220px;bottom:120px;opacity:.08" width="720" height="720" viewBox="0 0 140 140">{M.simbolo()}</svg>'
            f'<img src="file://{os.path.abspath(os.path.join(MOD, "..", "..", "marca", "clareia-eleicoes-roxo.svg"))}" '
            f'style="position:absolute;left:80px;top:120px;height:110px;animation:logo .6s cubic-bezier(.2,.9,.3,1.3) 0s both;transform-origin:left center">')
    return (f'<!doctype html><meta charset="utf-8"><style>{D.CSS}{CSS}</style><div class="f">{topo}{"".join(telas)}</div>'), t[-1]

async def gerar(saida, fps=30):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True); tmp = tempfile.mkdtemp()
    doc, dur = pagina(); open(os.path.join(tmp, 'v.html'), 'w').write(doc)
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
    shutil.rmtree(tmp, ignore_errors=True); print('duração', dur)

if __name__ == '__main__':
    asyncio.run(gerar(sys.argv[1]))
