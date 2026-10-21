#!/usr/bin/env python3
"""Gera favicons, ícones do app, imagem de compartilhamento (og-image) e a foto de perfil da Clareia.
Uso: python3 instagram/modelos/marca/gerar_icones.py <pasta_raiz_do_site>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(AQUI))
import marca as M
from PIL import Image
F = os.path.join(os.path.dirname(AQUI), 'fontes')
raiz = sys.argv[1]
def sem_sombra(): return M.icone(140, sombra=False).replace('width="140" height="140" ', '')
def cheio(px, escala=.86, raio='0'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 140 140">'
            f'<rect width="140" height="140" rx="{raio}" fill="{M.ROXO}"/><g transform="translate(70 70) scale({escala}) translate(-66 -66)">{M.simbolo()}</g></svg>')
og = f'''<div id="r" style="width:1200px;height:630px;background:{M.ROXO};color:#fff;position:relative;overflow:hidden;font-family:'Public Sans';display:flex;align-items:center;gap:56px;padding:0 90px;box-sizing:border-box">
<div style="position:absolute;left:0;right:0;top:0;height:16px;display:flex"><i style="flex:1;background:#1F4FA8"></i><i style="flex:1;background:#D62B2B"></i></div>
{M.icone(260)}<div><div style="font-family:'Source Serif 4';font-weight:900;font-size:112px;letter-spacing:-.03em;line-height:1">Clareia</div>
<div style="font-weight:900;font-size:40px;letter-spacing:.16em;color:{M.AMARELO};margin-top:10px">ELEIÇÕES</div>
<div style="font-size:30px;font-weight:600;color:#E2D9FA;margin-top:30px;line-height:1.35">Que ninguém vote no escuro.<br>2º turno 2026 · Flávio Bolsonaro × Lula</div></div></div>'''
paginas = {
 'favicon.svg': None,
 'favicon-32.png': (32, sem_sombra()), 'icon-192.png': (192, sem_sombra()), 'icon-512.png': (512, sem_sombra()),
 'icon-maskable-512.png': (512, cheio(512, .62)), 'apple-touch-icon.png': (180, cheio(180, .74)),
 'perfil-instagram-1080.png': (1080, cheio(1080, .80)), 'og-image.png': (None, og),
}
async def main():
    from playwright.async_api import async_playwright
    open(os.path.join(raiz, 'favicon.svg'), 'w').write(sem_sombra())
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nome, v in paginas.items():
            if not v: continue
            px, svg = v
            pg = await b.new_page(viewport={'width': px or 1200, 'height': px or 630})
            fonts = (f"<style>@font-face{{font-family:'Public Sans';src:url('file://{F}/PublicSans.ttf');font-weight:100 900}}"
                     f"@font-face{{font-family:'Source Serif 4';src:url('file://{F}/SourceSerif4.ttf');font-weight:200 900}}"
                     "body{margin:0;background:transparent}svg{display:block}</style>")
            if px: svg = svg.replace('<svg ', f'<svg style="width:{px}px;height:{px}px" ', 1)
            await pg.set_content(f'<!doctype html><meta charset="utf-8">{fonts}<div id="r" style="display:inline-block">{svg}</div>')
            await pg.wait_for_timeout(300)
            await (await pg.query_selector('#r')).screenshot(path=os.path.join(raiz, nome), omit_background=nome in ('favicon-32.png','icon-192.png','icon-512.png'))
            await pg.close()
        await b.close()
    im = Image.open(os.path.join(raiz, 'icon-512.png')).convert('RGBA')
    im.save(os.path.join(raiz, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
asyncio.run(main())
