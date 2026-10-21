"""Capas dos destaques do Instagram e peças de engajamento (curta, compartilhe, comente) da Clareia.

Uso: python3 destaques_e_engajamento.py pasta_de_saida/
Gera destaques/<nome>.png (1080x1080, o Instagram recorta o círculo do meio) e engajamento/feed.jpg e story.jpg.
Ícones desenhados aqui, em traço branco no estilo da lâmpada da marca.
"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(AQUI))
import marca as M
F = os.path.join(os.path.dirname(AQUI), 'fontes')
ROXO, AM, AZ, VM, T = M.ROXO, M.AMARELO, M.AZUL, M.VERM, '#16181D'
# ícones em viewBox 0 0 24 24, traço
IC = {
 'pesquisas': '<path d="M4 20h16"/><rect x="5" y="11" width="3.2" height="6.5" rx="1"/><rect x="10.4" y="6.5" width="3.2" height="11" rx="1"/><rect x="15.8" y="9" width="3.2" height="8.5" rx="1"/>',
 'checagem': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 20 20"/><path d="m7.6 10.6 2 2 3.6-3.8"/>',
 'boatos': '<path d="M12 3.6 21 19.5H3z"/><path d="M12 9.6v4.4"/><circle cx="12" cy="16.9" r=".4" fill="#fff"/>',
 'agenda': '<rect x="3.6" y="5" width="16.8" height="15" rx="2.4"/><path d="M3.6 10h16.8M8 3v4M16 3v4"/><path d="m9.2 14.6 1.9 1.9 3.8-3.9"/>',
 'debate': '<path d="M3.5 5.5h10a2 2 0 0 1 2 2v4.5a2 2 0 0 1-2 2H8.5l-3.5 3v-3h-1.5a2 2 0 0 1-2-2V7.5a2 2 0 0 1 2-2z" transform="translate(.5 0)"/><path d="M18 9.5h1.5a2 2 0 0 1 2 2V16a2 2 0 0 1-2 2H18v2.8L14.8 18H11"/>',
 'votar': '<path d="M4 13.5h16v6.5H4z"/><path d="M8.2 13.5V5.2a1 1 0 0 1 1-1h5.6a1 1 0 0 1 1 1v8.3"/><path d="m10 8.8 1.6 1.6 2.6-2.8"/>',
 'plantao': '<path d="M6 9.5a6 6 0 0 1 12 0c0 6 2.6 7.8 2.6 7.8H3.4S6 15.5 6 9.5"/><path d="M10.2 20.2a2 2 0 0 0 3.6 0"/>',
 'sobre': None,   # a própria lâmpada da Clareia
}
NOMES = {'pesquisas': 'Pesquisas', 'checagem': 'Checagens', 'boatos': 'Boatos', 'agenda': 'Agenda', 'debate': 'Debates',
         'votar': 'Como votar', 'plantao': 'Plantão', 'sobre': 'A Clareia'}
CSS = (f"@font-face{{font-family:'Public Sans';src:url('file://{F}/PublicSans.ttf');font-weight:100 900}}"
       f"@font-face{{font-family:'Source Serif 4';src:url('file://{F}/SourceSerif4.ttf');font-weight:200 900}}body{{margin:0}}")

def capa(nome):
    if IC[nome]:
        ico = (f'<svg x="300" y="300" width="480" height="480" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" '
               f'stroke-linecap="round" stroke-linejoin="round">{IC[nome]}</svg>')
    else:
        ico = f'<svg x="230" y="230" width="620" height="620" viewBox="0 0 140 140">{M.simbolo(escala=1.15)}</svg>'
    # anel amarelo com o arco de luz azul-vermelho, como no logo
    return (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div id="r" style="width:1080px;height:1080px">'
            f'<svg width="1080" height="1080" viewBox="0 0 1080 1080"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{AZ}"/><stop offset="1" stop-color="{VM}"/></linearGradient></defs>'
            f'<rect width="1080" height="1080" fill="{ROXO}"/>'
            f'<circle cx="540" cy="540" r="408" fill="none" stroke="{AM}" stroke-width="26"/>'
            f'<path d="M 834 254 A 408 408 0 0 1 946 520" fill="none" stroke="url(#g)" stroke-width="26" stroke-linecap="round" transform="rotate(-8 540 540)"/>'
            f'{ico}</svg></div>')

ACOES = [
 ('Curta', 'Assim mais gente vê informação com fonte.', '<path d="M12 20.3s-7.8-4.6-7.8-10.3A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.8 2.4c0 5.7-7.8 10.3-7.8 10.3z"/>', VM),
 ('Compartilhe', 'Mande para quem vai votar no domingo (25/10).', '<path d="M21 3.5 10.4 14.1"/><path d="M21 3.5 14.4 21l-4-6.9-6.9-4z"/>', '#7EA6FF'),
 ('Comente', 'Conte que dúvida você tem sobre o 2º turno. A gente responde com fonte.', '<path d="M4 5.5h16a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-4.5 3.5V17.5H4A1.5 1.5 0 0 1 2.5 16V7A1.5 1.5 0 0 1 4 5.5z"/>', AM),
]
def engaj(h, story):
    fs = 1.12 if story else .86
    cards = ''.join(
        f'<div style="display:flex;align-items:center;gap:34px;background:#fff;color:{T};border:5px solid {T};border-radius:34px;'
        f'box-shadow:10px 10px 0 {AM};padding:{34*fs:.0f}px {38*fs:.0f}px">'
        f'<div style="flex:none;width:{132*fs:.0f}px;height:{132*fs:.0f}px;border-radius:30px;background:{ROXO};display:grid;place-items:center">'
        f'<svg width="{80*fs:.0f}" height="{80*fs:.0f}" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ic}</svg></div>'
        f'<div><div style="font-family:\'Source Serif 4\';font-weight:900;font-size:{64*fs:.0f}px;line-height:1;color:{ROXO}">{t}</div>'
        f'<div style="font-size:{34*fs:.0f}px;line-height:1.35;margin-top:10px;color:#2A2D35">{d}</div></div></div>' for t, d, ic, c in ACOES)
    return (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>'
            f'<div id="r" style="width:1080px;height:{h}px;background:{ROXO};color:#fff;font-family:\'Public Sans\';position:relative;overflow:hidden;'
            f'box-sizing:border-box;padding:{200 if story else 70}px {80 if story else 70}px {230 if story else 64}px;display:flex;flex-direction:column;justify-content:space-between">'
            f'<div style="position:absolute;left:0;right:0;top:0;height:22px;display:flex"><i style="flex:1;background:#1F4FA8"></i><i style="flex:1;background:#D62B2B"></i></div>'
            f'<svg style="position:absolute;right:-220px;bottom:-90px;opacity:.08" width="720" height="720" viewBox="0 0 140 140">{M.simbolo()}</svg>'
            f'<div style="display:flex;align-items:center;justify-content:space-between">'
            f'<img src="file://{os.path.abspath(os.path.join(AQUI, "..", "..", "..", "marca", "clareia-eleicoes-roxo.svg"))}" style="height:{110 if story else 92}px">'
            f'<span style="font-size:30px;font-weight:800;color:#E2D9FA">{M.ARROBA}</span></div>'
            f'<div><div style="font-size:34px;font-weight:900;letter-spacing:.12em;color:{AM}">GOSTOU DO CONTEÚDO?</div>'
            f'<div style="font-family:\'Source Serif 4\';font-weight:800;font-size:{96 if story else 80}px;line-height:1.04;margin-top:16px">Ajude a clarear<br><span style="color:{AM}">o 2º turno.</span></div></div>'
            f'<div style="display:flex;flex-direction:column;gap:{34 if story else 26}px">{cards}</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-size:{34 if story else 30}px;line-height:1.35;color:#E2D9FA;max-width:620px">Tudo com fonte e os dois lados no mesmo critério.</span>'
            f'<span style="background:{AM};color:{T};border:4px solid {T};box-shadow:6px 6px 0 {T};border-radius:999px;padding:18px 34px;font-weight:900;font-size:40px">Siga</span></div></div>')

async def main(saida):
    from playwright.async_api import async_playwright
    os.makedirs(os.path.join(saida, 'destaques'), exist_ok=True); os.makedirs(os.path.join(saida, 'engajamento'), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        jobs = [(capa(n), 1080, os.path.join(saida, 'destaques', f'{n}.png')) for n in IC]
        jobs += [(engaj(1350, False), 1350, os.path.join(saida, 'engajamento', 'feed.jpg')), (engaj(1920, True), 1920, os.path.join(saida, 'engajamento', 'story.jpg'))]
        for html, h, out in jobs:
            tmp = out + '.html'; open(tmp, 'w').write(html)
            pg = await b.new_page(viewport={'width': 1080, 'height': h}); await pg.goto('file://' + os.path.abspath(tmp)); await pg.wait_for_timeout(400); os.remove(tmp)
            el = await pg.query_selector('#r')
            if out.endswith('.png'): await el.screenshot(path=out)
            else: await el.screenshot(path=out, type='jpeg', quality=92)
            await pg.close()
        await b.close()
    print('ok')
if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
