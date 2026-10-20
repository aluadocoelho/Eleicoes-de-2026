#!/usr/bin/env python3
"""Gera peças da Verita Eleições para o Instagram (JPEG) a partir de um JSON.

Uso:  python3 instagram/modelos/pecas.py especificacao.json pasta_de_saida/

Modelos ("modelo" no JSON):
  pesquisa  -> {instituto, divulgacao, flavio, lula, margem, amostra, fonte, campo?}
  lista     -> {chip, titulo, destaque?, itens:[{titulo, texto, selo?}], rodape}
  destaque  -> {chip, titulo, destaque?, texto, rodape?}
Campo "formatos": lista com "feed" (1080x1350) e/ou "story" (1080x1920). Padrão: os dois.
Gera <saida>/feed.jpg e/ou <saida>/story.jpg. Precisa de Playwright + Chromium e de Pillow.
"""
import json, os, sys, html, asyncio, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(AQUI, 'fontes')
ROXO, AMARELO, AZUL, VERM, TINTA = '#3E2492', '#FFD43B', '#1F4FA8', '#D62B2B', '#16181D'
SERIF = "'Source Serif 4', Georgia, serif"; SANS = "'Public Sans', system-ui, sans-serif"
E = html.escape

# ---------- marca ----------
FULL = '12,16 36,16 50,42.5 64,16 88,16 50,88'
def icone(px):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 140 140">'
            f'<rect x="16" y="16" width="116" height="116" rx="30" fill="{TINTA}"/>'
            f'<rect x="8" y="8" width="116" height="116" rx="30" fill="{AMARELO}" stroke="{TINTA}" stroke-width="6"/>'
            f'<g transform="translate(23 25) scale(0.84)"><polygon points="{FULL}" transform="translate(5 5)" fill="{TINTA}"/>'
            f'<polygon points="12,16 36,16 50,42.5 50,88" fill="{AZUL}"/><polygon points="50,42.5 64,16 88,16 50,88" fill="{VERM}"/>'
            f'<line x1="50" y1="42.5" x2="50" y2="88" stroke="{TINTA}" stroke-width="3"/>'
            f'<polygon points="{FULL}" fill="none" stroke="{TINTA}" stroke-width="5" stroke-linejoin="round"/></g></svg>')

def pilula(txt, fs=26, rot=-2):
    return (f'<span style="display:inline-block;background:{AMARELO};color:#1A1500;border:3px solid {TINTA};box-shadow:5px 5px 0 {TINTA};'
            f'border-radius:999px;padding:{fs*0.42:.0f}px {fs:.0f}px;font-family:{SANS};font-size:{fs}px;font-weight:900;letter-spacing:0.06em;'
            f'text-transform:uppercase;line-height:1;transform:rotate({rot}deg)">{E(txt)}</span>')

def assinatura(fs=40):
    return (f'<div style="display:flex;align-items:center;gap:14px">{icone(int(fs*1.6))}'
            f'<div style="display:flex;flex-direction:column;line-height:1"><span style="font-family:{SERIF};font-weight:900;font-size:{fs}px;letter-spacing:-0.03em">Verita</span>'
            f'<span style="font-family:{SANS};font-weight:900;font-size:{fs*0.4:.0f}px;letter-spacing:0.14em;text-transform:uppercase;color:{AMARELO};margin-top:4px">Eleições</span></div></div>')

FAIXA = f'<div style="display:flex;height:22px"><div style="flex:1;background:{AZUL}"></div><div style="flex:1;background:{VERM}"></div></div>'
ARCO = '<div style="position:absolute;right:-170px;top:80px;width:520px;height:520px;border-radius:50%;border:70px solid rgba(255,255,255,0.06)"></div>'

def titulo(t, dest, fs):
    d = f'<br><span style="color:{AMARELO}">{E(dest)}</span>' if dest else ''
    return f'<h1 style="margin:0;font-family:{SERIF};font-weight:800;font-size:{fs}px;line-height:1;letter-spacing:-0.025em">{E(t)}{d}</h1>'

def cartao(inner, pad=34):
    return (f'<div style="background:#fff;color:{TINTA};border:3px solid {TINTA};box-shadow:8px 8px 0 {TINTA};border-radius:28px;'
            f'padding:{pad}px {pad+2}px;display:flex;flex-direction:column;gap:24px">{inner}</div>')

SELO_COR = {'falso': VERM, 'verdadeiro': '#1B7F4B'}
def selo(s):
    cor = SELO_COR.get(s.strip().lower(), '#8A5A00')
    return (f'<span style="flex:none;align-self:flex-start;background:{cor};color:#fff;border-radius:999px;padding:6px 14px;'
            f'font-family:{SANS};font-size:20px;font-weight:900;letter-spacing:.05em;text-transform:uppercase">{E(s)}</span>')

# ---------- modelos ----------
def corpo_pesquisa(s, story):
    f, l = float(s['flavio']), float(s['lula'])
    mg = s.get('margem')
    dif = abs(f - l)
    nota = f'Diferença de {dif:.1f} ponto{"s" if round(dif,1)!=1 else ""}'.replace('.', ',')
    if mg:
        nota += f'. Margem de erro: {str(mg).replace(".", ",")} pontos, para mais ou para menos'
        if dif <= 2 * float(mg): nota += '. Pela margem, é empate técnico'
    nota += '.'
    def barra(nome, v, cor):
        return (f'<div style="display:flex;flex-direction:column;gap:10px"><div style="display:flex;justify-content:space-between;align-items:baseline">'
                f'<span style="font-family:{SANS};font-size:34px;font-weight:900">{E(nome)}</span>'
                f'<span style="font-family:{SERIF};font-size:72px;font-weight:800;color:{cor}">{str(v).replace(".", ",")}%</span></div>'
                f'<div style="height:34px;background:#ECE8F4;border-radius:999px;overflow:hidden;border:2px solid {TINTA}"><div style="width:{v}%;height:100%;background:{cor}"></div></div></div>')
    meta = ' · '.join(x for x in [s.get('campo') and f'Campo: {s["campo"]}', s.get('amostra') and f'{int(s["amostra"]):,} entrevistas'.replace(',', '.')] if x)
    inner = (f'<div style="font-family:{SANS};font-size:24px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;color:{ROXO}">Votos válidos</div>'
             + barra('Flávio Bolsonaro', f, AZUL) + barra('Lula', l, VERM)
             + f'<div style="font-family:{SANS};font-size:25px;line-height:1.4;color:#3A3F49">{E(nota)}</div>')
    return (pilula(f'Nova pesquisa · {s["instituto"]}'), titulo('Como está o 2º turno', f'segundo a {s["instituto"]}', 84 if not story else 100),
            f'<p style="margin:0;font-size:29px;line-height:1.4;color:#E2D9FA">Divulgada em {E(s["divulgacao"])}. {E(meta)}</p>' if meta else '', cartao(inner),
            f'Fonte: {s["fonte"]}')

def corpo_lista(s, story):
    n = len(s['itens'][:5]); k = 1.25 if n <= 2 else (1.12 if n == 3 else 1)
    itens = '<div style="height:2px;background:#E4DFEE"></div>'.join(
        f'<div style="display:flex;gap:18px;align-items:flex-start"><div style="flex:1;display:flex;flex-direction:column;gap:6px">'
        f'<div style="font-family:{SANS};font-size:{(32 if story else 30)*k:.0f}px;font-weight:900;line-height:1.15">{E(i["titulo"])}</div>'
        f'<div style="font-family:{SANS};font-size:{(26 if story else 24)*k:.0f}px;line-height:1.35;color:#3A3F49">{E(i["texto"])}</div></div>'
        f'{selo(i["selo"]) if i.get("selo") else ""}</div>' for i in s['itens'][:5])
    return (pilula(s['chip']), titulo(s['titulo'], s.get('destaque'), 84 if not story else 96), '', cartao(itens), s.get('rodape', ''))

def corpo_destaque(s, story):
    return (pilula(s['chip']), titulo(s['titulo'], s.get('destaque'), 96 if not story else 112),
            f'<p style="margin:0;font-size:{34 if story else 31}px;line-height:1.45;color:#E2D9FA">{E(s["texto"])}</p>', '', s.get('rodape', ''))

MODELOS = {'pesquisa': corpo_pesquisa, 'lista': corpo_lista, 'destaque': corpo_destaque}

def pagina(s, formato):
    story = formato == 'story'
    w, h = 1080, (1920 if story else 1350)
    chip, tit, sub, card, rodape = MODELOS[s['modelo']](s, story)
    topo = '<div style="height:120px"></div>' if story else ''
    pe = (f'<div style="padding:0 72px {150 if story else 54}px;display:flex;align-items:flex-end;justify-content:space-between;gap:24px">'
          f'<div style="display:flex;flex-direction:column;gap:14px">{assinatura(38)}'
          f'<div style="font-size:20px;opacity:.8;max-width:{560 if not story else 620}px;line-height:1.35">{E(rodape)}</div></div>'
          + (f'<div style="background:{AMARELO};color:#1A1500;border:3px solid {TINTA};box-shadow:7px 7px 0 {TINTA};border-radius:22px;padding:20px 30px;font-size:38px;font-weight:900;white-space:nowrap">Link na bio</div>')
          + '</div>')
    fonts = (f"@font-face{{font-family:'Public Sans';src:url('file://{FONTES}/PublicSans.ttf');font-weight:100 900}}"
             f"@font-face{{font-family:'Source Serif 4';src:url('file://{FONTES}/SourceSerif4.ttf');font-weight:200 900}}")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}body{{margin:0}}</style></head><body>'
            f'<div style="width:{w}px;height:{h}px;box-sizing:border-box;background:{ROXO};color:#fff;font-family:{SANS};display:flex;flex-direction:column;overflow:hidden;position:relative">'
            f'{FAIXA}{ARCO}{topo}<div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding:{40 if story else 30}px 0">'
            f'<div style="position:relative;padding:0 72px;display:flex;flex-direction:column;gap:28px">'
            f'<div>{chip}</div>{tit}{sub}</div>' + (f'<div style="position:relative;margin:44px 72px 0">{card}</div>' if card else '') + f'</div>{pe}</div></body></html>'), w, h

async def gerar(spec, saida):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True)
    feitos = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for fmt in spec.get('formatos', ['feed', 'story']):
            doc, w, h = pagina(spec, fmt)
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as t:
                t.write(doc); caminho = t.name
            pg = await b.new_page(viewport={'width': w, 'height': h})
            await pg.goto('file://' + caminho); await pg.wait_for_timeout(400)
            png = os.path.join(saida, f'{fmt}.png')
            await pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(os.path.join(saida, f'{fmt}.jpg'), quality=92)
            os.remove(png); os.remove(caminho); feitos.append(f'{fmt}.jpg')
        await b.close()
    return feitos

if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    print(asyncio.run(gerar(spec, sys.argv[2])))
