import sys,os,asyncio
sys.path.insert(0,'/home/claude/eleicoes-2026-dados/instagram/modelos'); import marca as M
F='/home/claude/eleicoes-2026-dados/instagram/modelos/fontes'; ROXO,AM,T=M.ROXO,M.AMARELO,'#16181D'
def pag(h, story):
    lg=420 if story else 300; fs=150 if story else 118
    url=(f'<div style="background:#fff;border:5px solid {AM};box-shadow:12px 12px 0 {AM};border-radius:36px;padding:30px 34px;display:flex;align-items:center;gap:22px;align-self:flex-start">'
         f'{M.icone(96,sombra=False)}<div style="font-weight:900;font-size:54px;color:{T}">clareiaeleicoes<span style="color:{ROXO}">.com.br</span></div></div>')
    return f'''<!doctype html><meta charset="utf-8"><style>@font-face{{font-family:'Public Sans';src:url('file://{F}/PublicSans.ttf');font-weight:100 900}}
@font-face{{font-family:'Source Serif 4';src:url('file://{F}/SourceSerif4.ttf');font-weight:200 900}}body{{margin:0}}</style>
<div id="r" style="width:1080px;height:{h}px;background:{ROXO};color:#fff;font-family:'Public Sans';position:relative;overflow:hidden;box-sizing:border-box;padding:{170 if story else 90}px 80px {200 if story else 80}px;display:flex;flex-direction:column;justify-content:space-between">
<div style="position:absolute;left:0;right:0;top:0;height:22px;display:flex"><i style="flex:1;background:#1F4FA8"></i><i style="flex:1;background:#D62B2B"></i></div>
<svg style="position:absolute;right:-220px;bottom:-80px;opacity:.08" width="700" height="700" viewBox="0 0 140 140">{M.simbolo()}</svg>
<div style="font-size:36px;font-weight:900;letter-spacing:.12em;color:{AM}">NOVO NOME E NOVO ENDEREÇO</div>
<div style="display:flex;align-items:center;gap:40px;{'flex-direction:column;align-items:flex-start' if story else ''}">
 <div style="font-family:'Source Serif 4';font-weight:800;font-size:{70 if story else 60}px;line-height:1.05;{'' if story else 'display:none'}">A Verita agora é</div>
 <div style="display:flex;align-items:center;gap:36px">{M.icone(lg if not story else 300)}<div style="display:flex;flex-direction:column;line-height:1">
 <span style="font-family:'Source Serif 4';font-weight:900;font-size:{fs}px;letter-spacing:-.03em">Clareia</span>
 <span style="font-weight:900;font-size:{fs*.38:.0f}px;letter-spacing:.18em;color:{AM};margin-top:12px">ELEIÇÕES</span></div></div></div>
<div style="font-size:{40 if story else 36}px;line-height:1.4;color:#E2D9FA">{'Mudamos de nome para não haver confusão com o Instituto Veritá, de pesquisas eleitorais, com quem nunca tivemos relação. O propósito é o mesmo: tudo com fonte, os dois lados com o mesmo critério.' if story else 'A Verita agora é Clareia: novo nome para não haver confusão com o Instituto Veritá, de pesquisas, com quem nunca tivemos relação. O propósito é o mesmo.'}</div>
<div style="display:flex;flex-direction:column;gap:22px"><div style="font-size:34px;font-weight:900;letter-spacing:.1em;color:{AM}">E AGORA TEMOS CASA PRÓPRIA</div>{url}</div>
<div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:30px;font-weight:800;color:#E2D9FA">{M.ARROBA}</span>
<span style="background:{AM};color:{T};border:4px solid {T};box-shadow:6px 6px 0 {T};border-radius:999px;padding:18px 32px;font-weight:900;font-size:40px">Link na bio</span></div></div>'''
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for nome,h,st in [('out-feed/feed.jpg',1350,False),('out-story/story.jpg',1920,True)]:
            pg=await b.new_page(viewport={'width':1080,'height':h}); await pg.set_content(pag(h,st)); await pg.wait_for_timeout(400)
            await (await pg.query_selector('#r')).screenshot(path=nome,type='jpeg',quality=92); await pg.close()
        await b.close()
asyncio.run(m())
