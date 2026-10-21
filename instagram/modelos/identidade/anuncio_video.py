"""Reels de 20 s anunciando a nova marca: Clareia Eleições + clareiaeleicoes.com.br"""
import sys, os, asyncio, tempfile, subprocess, shutil
M_DIR = '/home/claude/eleicoes-2026-dados/instagram/modelos'
sys.path.insert(0, M_DIR)
import marca as M
F = M_DIR + '/fontes'
TRILHA = M_DIR + '/trilhas/verita-lofi-media-20s.wav'
ROXO, AM, AZ, VM, T = M.ROXO, M.AMARELO, M.AZUL, M.VERM, '#16181D'
FI = '#2E1B70'
simb = (f'<defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AZ}"/><stop offset="1" stop-color="{VM}"/></linearGradient></defs>'
        f'<g transform="translate(66 66) scale(.86) translate(-6.22 0.79)">'
        f'<g class="fade" style="animation-delay:1.1s;animation-duration:.05s"><path class="draw" style="animation-delay:1.1s" pathLength="1" d="{M._BULBO}" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></g>'
        f'<g class="fade" style="animation-delay:2.0s;animation-duration:.05s"><path class="draw" style="animation-delay:2.0s;animation-duration:.6s" pathLength="1" d="{M._ARCO}" fill="none" stroke="url(#ga)" stroke-width="8" stroke-linecap="round"/></g>'
        f'<rect class="fade" style="animation-delay:1.9s" x="-12" y="37" width="24" height="7" rx="3.5" fill="#fff"/></g>')
logo = (f'<svg width="560" height="560" viewBox="0 0 140 140" style="overflow:visible">'
        f'<g class="pop" style="animation-delay:.7s;transform-origin:70px 70px"><circle cx="74" cy="74" r="58" fill="{AM}"/>'
        f'<circle cx="66" cy="66" r="58" fill="{ROXO}" stroke="{AM}" stroke-width="6"/></g>{simb}</svg>')
def cena(ini, fim, html, extra=''):
    return (f'<div class="sc" style="animation:show 0s {ini}s both,hide 0s {fim}s forwards;{extra}">{html}</div>')
def card(rot, txt, d, cor=AM):
    return (f'<div class="up" style="animation-delay:{d}s;background:{FI};border-top:10px solid {cor};border-radius:28px;padding:32px 36px;display:flex;flex-direction:column;gap:12px">'
            f'<div style="font-size:32px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:{cor}">{rot}</div>'
            f'<div style="font-size:48px;line-height:1.3;color:#F2F2F4">{txt}</div></div>')
c1 = (f'<div class="up" style="animation-delay:.2s;font-size:44px;font-weight:900;letter-spacing:.1em;color:{AM}">NOVO NOME · NOVO LOGO</div>'
      f'<div class="up" style="animation-delay:.35s;font-family:\'Source Serif 4\';font-weight:800;font-size:96px;line-height:1.05;color:#fff">A Verita agora é</div>'
      f'<div style="display:grid;place-items:center;margin:30px 0 10px">{logo}</div>'
      f'<div class="up" style="animation-delay:2.6s;text-align:center;font-family:\'Source Serif 4\';font-weight:900;font-size:170px;letter-spacing:-.03em;line-height:1;color:#fff">Clareia</div>'
      f'<div class="up" style="animation-delay:2.9s;text-align:center;font-weight:900;font-size:62px;letter-spacing:.2em;color:{AM};margin-top:10px">ELEIÇÕES</div>')
c2 = (f'<div class="up" style="animation-delay:5.1s;font-size:40px;font-weight:900;letter-spacing:.1em;color:{AM}">O QUE MUDOU</div>'
      f'<div class="up" style="animation-delay:5.25s;font-family:\'Source Serif 4\';font-weight:800;font-size:104px;line-height:1.04;color:#fff">Novo nome,<br><span style="color:{AM}">nova cara.</span></div>'
      + card('O nome', 'Clareia Eleições: a gente quer ajudar a clarear o 2º turno.', 6.1)
      + card('O visual', 'Uma lâmpada que acende, com as duas cores da disputa.', 6.9)
      + card('O perfil', 'Agora é @clareiaeleicoes. Quem já segue não precisa fazer nada.', 7.7))
c3 = (f'<div class="up" style="animation-delay:9.6s;font-size:40px;font-weight:900;letter-spacing:.1em;color:{AM}">O QUE NÃO MUDA</div>'
      f'<div class="up" style="animation-delay:9.75s;font-family:\'Source Serif 4\';font-weight:800;font-size:104px;line-height:1.04;color:#fff">O jeito<br><span style="color:{AM}">de sempre.</span></div>'
      + card('Sempre com fonte', 'Cada informação com o link de onde veio.', 10.5, '#7EA6FF')
      + card('Mesmo critério', 'Os dois lados tratados do mesmo jeito.', 11.3, VM))
c4 = (f'<div style="display:grid;place-items:center" class="pop" style="animation-delay:14s"><div>{M.icone(380)}</div></div>'
      f'<div class="up" style="animation-delay:14.5s;text-align:center;font-family:\'Source Serif 4\';font-weight:800;font-size:104px;line-height:1.05;color:#fff;margin-top:20px">Que ninguém vote<br><span style="color:{AM}">no escuro.</span></div>'
      f'<div class="up" style="animation-delay:15.6s;text-align:center;font-size:46px;line-height:1.35;color:#E2D9FA">Pesquisas, checagens e boatos desmentidos do 2º turno, com a fonte de cada um.</div>'
      f'<div class="up" style="animation-delay:16.6s;display:flex;justify-content:center;margin-top:10px"><span style="background:{AM};color:{T};border:4px solid {T};box-shadow:7px 7px 0 {T};border-radius:999px;padding:22px 40px;font-weight:900;font-size:46px">Tudo no link da bio</span></div>')
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Public Sans';src:url('file://{F}/PublicSans.ttf');font-weight:100 900}}
@font-face{{font-family:'Source Serif 4';src:url('file://{F}/SourceSerif4.ttf');font-weight:200 900}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:{ROXO};font-family:'Public Sans';color:#fff}}
.sc{{position:absolute;inset:0;padding:290px 80px 260px;display:flex;flex-direction:column;justify-content:center;gap:34px;box-sizing:border-box;visibility:hidden}}
.up{{animation:up .7s cubic-bezier(.2,.8,.2,1) both}} .pop{{animation:pop .8s cubic-bezier(.2,.9,.3,1.25) both}}
.draw{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1s ease-in-out both}} .fade{{animation:fade .4s both}}
@keyframes up{{from{{transform:translateY(70px);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes pop{{0%{{transform:scale(.3);opacity:0}}70%{{transform:scale(1.06);opacity:1}}100%{{transform:scale(1)}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}} @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes show{{from{{visibility:hidden}}to{{visibility:visible}}}} @keyframes hide{{to{{visibility:hidden}}}}
@keyframes wipe{{0%{{transform:translateX(-110%)}}45%,55%{{transform:translateX(0)}}100%{{transform:translateX(110%)}}}}
</style></head><body>
<div style="position:absolute;left:0;right:0;top:0;height:22px;display:flex;z-index:5"><i style="flex:1;background:{AZ}"></i><i style="flex:1;background:{VM}"></i></div>
<div class="up" style="animation-delay:4.9s;position:absolute;left:80px;right:80px;top:120px;display:flex;justify-content:space-between;align-items:center;z-index:5">
 <div style="display:flex;align-items:center;gap:18px">{M.icone(84)}<div style="display:flex;flex-direction:column;line-height:1"><span style="font-family:'Source Serif 4';font-weight:900;font-size:52px;letter-spacing:-.03em">Clareia</span><span style="font-weight:900;font-size:21px;letter-spacing:.14em;color:{AM};margin-top:4px">ELEIÇÕES</span></div></div>
 <span style="font-size:30px;font-weight:800;color:#E2D9FA">{M.ARROBA}</span></div>
<svg style="position:absolute;right:-200px;bottom:60px;opacity:.08" width="700" height="700" viewBox="0 0 140 140">{M.simbolo()}</svg>
{cena(0, 4.6, c1)}{cena(4.6, 9.2, c2)}{cena(9.2, 13.7, c3)}{cena(13.7, 21, c4)}
<div style="position:absolute;inset:-200px;background:{AM};transform:translateX(-110%);animation:wipe .9s cubic-bezier(.7,0,.3,1) 4.15s both;z-index:9"></div>
<div style="position:absolute;inset:-200px;background:{AZ};transform:translateX(-110%);animation:wipe .9s cubic-bezier(.7,0,.3,1) 8.75s both;z-index:9"></div>
<div style="position:absolute;inset:-200px;background:{VM};transform:translateX(-110%);animation:wipe .9s cubic-bezier(.7,0,.3,1) 13.25s both;z-index:9"></div>
<div style="position:absolute;left:80px;bottom:120px;font-size:28px;color:#C9BFEA;z-index:5">Clareia Eleições, antes Verita Eleições</div>
</body></html>'''
async def main(saida, fps=30, dur=20):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True); tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, 'v.html'), 'w').write(html)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        await pg.goto('file://' + os.path.join(tmp, 'v.html')); await pg.wait_for_timeout(600)
        for i in range(fps * dur):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i*1000/fps}}})")
            await pg.screenshot(path=os.path.join(tmp, f'f{i:04d}.jpg'), type='jpeg', quality=90)
        await b.close()
    Image.open(os.path.join(tmp, 'f0105.jpg')).save(os.path.join(saida, 'capa.jpg'), quality=92)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',os.path.join(tmp,'f%04d.jpg'),'-i',TRILHA,
                    '-c:a','aac','-b:a','192k','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',
                    os.path.join(saida,'reels.mp4')], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
asyncio.run(main(sys.argv[1]))
