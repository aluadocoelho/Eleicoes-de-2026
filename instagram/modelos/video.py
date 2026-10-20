#!/usr/bin/env python3
"""Gera o reels da Verita (20 s, 1080x1920, com a trilha lo-fi) a partir de um JSON.

Uso:  python3 instagram/modelos/video.py especificacao.json pasta_de_saida/

Especificação (todos os textos curtos; cada item de "itens" tem rotulo, texto e lado):
{
 "tema": "plantao" | "verita",          # plantao = preto/amarelo/vermelho; verita = roxo
 "selo": "URGENTE" | "PLANTÃO" | "NOVA PESQUISA" | "CHECAGEM" ...,
 "abertura": {"chip": "Plantão Verita · Eleições 2026", "titulo": "Quebra de", "destaque": "sigilo.", "sub": "O que pode acontecer nesta terça, 20/10."},
 "cena2": {"chip": "Terça, 20/10 · TSE", "titulo": "Lula diz que entrega...", "destaque": "quebrar seus sigilos.", "itens": [{"rotulo": "O que entra", "texto": "...", "lado": "lula"}]},
 "cena3": {"chip": "E o outro lado?", "itens": [{"rotulo": "Flávio Bolsonaro", "texto": "...", "lado": "flavio"}], "chamada": "Acompanhe", "chamada_destaque": "ao longo do dia."},
 "rodape": "Fontes: Poder360 e CNN Brasil (19/10)"
}
"lado": "lula" (vermelho), "flavio" (azul) ou "neutro" (amarelo). Gera reels.mp4 e capa.jpg.
Precisa de Playwright + Chromium, Pillow e ffmpeg. Cortes em 0,7 s, 5,6 s e 12,6 s, no ritmo da trilha.
"""
import sys, os, json, asyncio, tempfile, shutil, subprocess, html
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import pecas as P
from pecas import AMARELO, AZUL, VERM, TINTA, SERIF, SANS
E = html.escape
TRILHA = os.path.join(AQUI, 'trilhas', 'verita-lofi-20s.wav')
COR = {'lula': VERM, 'flavio': AZUL, 'neutro': AMARELO}

def item(it, d, fundo_item, txt_cor):
    cor = COR.get(it.get('lado', 'neutro'), AMARELO)
    rot = cor if cor != AZUL else '#7EA6FF'
    return (f'<div class="up" style="animation-delay:{d}s;background:{fundo_item};border:3px solid #3A3E48;border-top:10px solid {cor};border-radius:26px;padding:26px 30px;display:flex;flex-direction:column;gap:10px">'
            f'<div style="font-size:30px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:{rot}">{E(it["rotulo"])}</div>'
            f'<div style="font-size:40px;line-height:1.36;color:{txt_cor}">{E(it["texto"])}</div></div>')

def pagina(s):
    plantao = s.get('tema', 'plantao') == 'plantao'
    BG = TINTA if plantao else P.ROXO
    FI = '#22252C' if plantao else '#2E1B70'
    SUB = '#C9CBD2' if plantao else '#E2D9FA'
    TAPE = f'repeating-linear-gradient(-45deg,{AMARELO} 0 46px,{BG} 46px 92px)'
    a, c2, c3 = s['abertura'], s['cena2'], s['cena3']
    tit = lambda t, d, fs: f'{E(t)}<br><span style="color:{AMARELO}">{E(d)}</span>' if d else E(t)
    itens2 = ''.join(item(it, 7.2 + 1.4 * i, FI, '#F2F2F4') for i, it in enumerate(c2.get('itens', [])[:2]))
    itens3 = ''.join(item(it, 12.9 + 1.2 * i, FI, '#F2F2F4') for i, it in enumerate(c3.get('itens', [])[:2]))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Public Sans';src:url('file://{P.FONTES}/PublicSans.ttf');font-weight:100 900}}
@font-face{{font-family:'Source Serif 4';src:url('file://{P.FONTES}/SourceSerif4.ttf');font-weight:200 900}}
body{{margin:0}}
.f{{width:1080px;height:1920px;background:{BG};color:#fff;font-family:{SANS};position:relative;overflow:hidden}}
.sc{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 72px 120px;box-sizing:border-box}}
@keyframes up{{from{{transform:translateY(70px);opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes pop{{0%{{transform:scale(.3) rotate(-10deg);opacity:0}}60%{{transform:scale(1.12) rotate(-3deg);opacity:1}}100%{{transform:scale(1) rotate(-3deg)}}}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.15}}}}
@keyframes flash{{0%{{opacity:.9}}100%{{opacity:0}}}}
@keyframes tapeL{{from{{transform:translateX(-120%) rotate(-4deg)}}to{{transform:translateX(0) rotate(-4deg)}}}}
@keyframes tapeR{{from{{transform:translateX(120%) rotate(5deg)}}to{{transform:translateX(0) rotate(5deg)}}}}
@keyframes wipe{{0%{{transform:translateX(-110%)}}45%,55%{{transform:translateX(0)}}100%{{transform:translateX(110%)}}}}
@keyframes hide{{to{{visibility:hidden}}}}
@keyframes show{{from{{visibility:hidden}}to{{visibility:visible}}}}
@keyframes zoom{{from{{transform:scale(1)}}to{{transform:scale(1.06)}}}}
.up{{animation:up .55s cubic-bezier(.2,.8,.3,1) both}}
</style></head><body><div class="f">
<div style="position:absolute;left:0;right:0;top:0;display:flex;height:22px;z-index:5"><div style="flex:1;background:{AZUL}"></div><div style="flex:1;background:{VERM}"></div></div>
<div class="sc" style="animation:hide 0s linear 5.6s forwards;align-items:flex-start">
  <div style="position:absolute;left:-80px;right:-80px;top:300px;height:130px;background:{TAPE};animation:tapeL .6s cubic-bezier(.2,.8,.3,1) .1s both"></div>
  <div style="position:absolute;left:-80px;right:-80px;bottom:330px;height:130px;background:{TAPE};animation:tapeR .6s cubic-bezier(.2,.8,.3,1) .35s both"></div>
  <div style="position:relative;animation:zoom 5s linear both;display:flex;flex-direction:column;gap:36px;width:100%">
    <div style="animation:pop .6s cubic-bezier(.2,.9,.3,1.3) .7s both;align-self:flex-start;display:inline-flex;align-items:center;gap:22px;background:{VERM};color:#fff;border:4px solid #000;box-shadow:12px 12px 0 {AMARELO};border-radius:999px;padding:22px 46px;font-size:{96 if len(s.get('selo','')) <= 9 else 70}px;font-weight:900;letter-spacing:.06em">
      <i style="width:40px;height:40px;border-radius:50%;background:#fff;display:block;animation:blink 1s steps(2) 1.3s infinite"></i>{E(s.get('selo', 'PLANTÃO'))}</div>
    <div class="up" style="animation-delay:1.5s;font-size:40px;font-weight:900;letter-spacing:.08em;color:{AMARELO};text-transform:uppercase">{E(a.get('chip', 'Plantão Verita · Eleições 2026'))}</div>
    <h1 class="up" style="animation-delay:1.9s;margin:0;font-family:{SERIF};font-weight:800;font-size:120px;line-height:.98;letter-spacing:-.03em">{tit(a['titulo'], a.get('destaque'), 120)}</h1>
    <div class="up" style="animation-delay:2.6s;font-size:44px;line-height:1.35;color:{SUB}">{E(a.get('sub', ''))}</div>
  </div>
  <div style="position:absolute;inset:0;background:#fff;opacity:0;animation:flash .35s ease-out .7s forwards;pointer-events:none"></div>
</div>
<div class="sc" style="visibility:hidden;animation:show 0s linear 5.6s forwards,hide 0s linear 12.6s forwards">
  <div class="up" style="animation-delay:5.7s;font-size:34px;font-weight:900;letter-spacing:.08em;color:{AMARELO};text-transform:uppercase;margin-bottom:24px">{E(c2.get('chip', ''))}</div>
  <h2 class="up" style="animation-delay:5.9s;margin:0 0 40px;font-family:{SERIF};font-weight:800;font-size:92px;line-height:1;letter-spacing:-.025em">{tit(c2['titulo'], c2.get('destaque'), 92)}</h2>
  <div style="display:flex;flex-direction:column;gap:22px">{itens2}</div>
</div>
<div class="sc" style="visibility:hidden;animation:show 0s linear 12.6s forwards">
  <div class="up" style="animation-delay:12.7s;font-size:34px;font-weight:900;letter-spacing:.08em;color:{AMARELO};text-transform:uppercase;margin-bottom:24px">{E(c3.get('chip', ''))}</div>
  <div style="display:flex;flex-direction:column;gap:22px;margin-bottom:56px">{itens3}</div>
  <div class="up" style="animation-delay:14.6s;font-family:{SERIF};font-weight:800;font-size:80px;line-height:1.02;letter-spacing:-.025em;margin-bottom:40px">{tit(c3.get('chamada', 'Acompanhe no site'), c3.get('chamada_destaque'), 80)}</div>
  <div class="up" style="animation-delay:15.6s;display:flex;align-items:center;justify-content:space-between;gap:24px">
    <div style="display:flex;flex-direction:column;gap:12px">{P.assinatura(44)}<div style="font-size:24px;color:#9DA1AB;max-width:560px;line-height:1.35">{E(s.get('rodape', ''))}</div></div>
    <div style="background:{AMARELO};color:#1A1500;border:3px solid #000;box-shadow:8px 8px 0 {VERM};border-radius:24px;padding:22px 32px;font-size:44px;font-weight:900;white-space:nowrap">Link na bio</div>
  </div>
</div>
<div style="position:absolute;inset:-200px;background:{TAPE};transform:translateX(-110%);animation:wipe 1s cubic-bezier(.7,0,.3,1) 5.1s both;z-index:9"></div>
<div style="position:absolute;inset:-200px;background:{VERM};transform:translateX(-110%);animation:wipe 1s cubic-bezier(.7,0,.3,1) 12.1s both;z-index:9;display:flex;align-items:center;justify-content:center">
  <span style="font-size:110px;font-weight:900;letter-spacing:.08em;color:#fff">{E(s.get('selo', 'PLANTÃO'))}</span></div>
</div></body></html>'''

async def gerar(spec, saida, fps=30, dur=20):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True)
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, 'v.html'), 'w') as f: f.write(pagina(spec))
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        await pg.goto('file://' + os.path.join(tmp, 'v.html')); await pg.wait_for_timeout(500)
        for i in range(fps * dur):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / fps}}})")
            await pg.screenshot(path=os.path.join(tmp, f'f{i:04d}.jpg'), type='jpeg', quality=90)
        await b.close()
    Image.open(os.path.join(tmp, 'f0090.jpg')).convert('RGB').save(os.path.join(saida, 'capa.jpg'), quality=92)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, 'f%04d.jpg')]
    if os.path.exists(TRILHA): cmd += ['-i', TRILHA, '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(saida, 'reels.mp4')]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return ['reels.mp4', 'capa.jpg']

if __name__ == '__main__':
    print(asyncio.run(gerar(json.load(open(sys.argv[1])), sys.argv[2])))
