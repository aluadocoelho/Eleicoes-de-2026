"""Família "contexto" (ENTENDA): peças explicativas, em carrossel, sobre um assunto que se arrasta por dias
(pedido do dono em 21/10: peças mais informativas, com a origem das disputas e dados).
Fundo de papel claro, tinta escura, roxo e amarelo; azul e vermelho só para marcar o lado de cada candidato.

Cada imagem do carrossel é uma especificação com "familia": "contexto" e "tela":
  capa     faltam?, titulo, destaque?, sub?          (faltam = dias até a votação; aparece num selo grande)
  linha    titulo, eventos:[{data, texto, lado}]      (linha do tempo, até 5; lado = lula | flavio | neutro)
  lados    titulo, lula:{rotulo, itens:[...]}, flavio:{rotulo, itens:[...]}   (o que cada um disse ou propôs, lado a lado)
  numeros  titulo, barras:[{rotulo, valor, lado}], unidade?, nota, criterio  (barras horizontais com o critério da contagem)
  proximos titulo, itens:[{quando, texto}]           (o que vem agora; até 3)
Todos aceitam "pagina" ("2/5"), "fonte" e "formatos". Textos curtos: a peça tem que caber sem encolher muito.
"""
import html
E = html.escape
ROXO, AM, T, AZ, VM = '#3E2492', '#FFD43B', '#16181D', '#1F4FA8', '#D62B2B'
SERIF, SANS = "'Source Serif 4',Georgia,serif", "'Public Sans',system-ui,sans-serif"
COR = {'lula': VM, 'flavio': AZ, 'neutro': ROXO}
NOME = {'lula': 'Lula', 'flavio': 'Flávio'}

def cab(s, chip, P):
    pg = f'<span style="font:800 28px {SANS};color:{P["sub"]};letter-spacing:.08em">{E(s["pagina"])}</span>' if s.get('pagina') else ''
    return f'<div style="display:flex;justify-content:space-between;align-items:center">{chip("contexto")}{pg}</div>'

def tit(s, fs=96):
    t = s['titulo']; d = s.get('destaque')
    fs = fs if len(t + (d or '')) < 44 else int(fs * .82)
    return (f'<div style="font:900 {fs}px/1.03 {SERIF};letter-spacing:-.02em">{E(t)}'
            + (f'<br><span style="background:linear-gradient(transparent 58%,{AM} 58%,{AM} 92%,transparent 92%);padding:0 6px;margin:0 -6px">{E(d)}</span>' if d else '') + '</div>')

def capa(s, P, story, chip):
    selo = ''
    if s.get('faltam') is not None:
        n = int(s['faltam'])
        selo = (f'<div style="display:flex;align-items:center;gap:34px">'
                f'<div style="flex:none;width:250px;height:250px;border-radius:50%;background:{AM};border:6px solid {T};box-shadow:12px 12px 0 {ROXO};display:grid;place-items:center">'
                f'<div style="text-align:center"><div style="font:900 150px/.9 {SERIF};letter-spacing:-.04em">{n}</div>'
                f'<div style="font:900 28px/1 {SANS};letter-spacing:.14em;margin-top:6px">{"DIA" if n == 1 else "DIAS"}</div></div></div>'
                f'<div style="font:800 40px/1.25 {SANS}">{"falta" if n == 1 else "faltam"} para a votação<br><span style="color:{P["sub"]};font-weight:600;font-size:32px">domingo, 25/10</span></div></div>')
    sub = f'<div style="font:600 38px/1.4 {SANS};color:{P["sub"]}">{E(s["sub"])}</div>' if s.get('sub') else ''
    return cab(s, chip, P) + selo + tit(s, 112) + sub

def linha(s, P, story, chip):
    evs = s.get('eventos', [])[:5]
    itens = ''
    for k, e in enumerate(evs):
        c = COR.get(e.get('lado', 'neutro'), ROXO); ult = k == len(evs) - 1
        quem = (f'<span style="display:inline-block;background:{c};color:#fff;border-radius:999px;padding:4px 14px;font:900 22px {SANS};letter-spacing:.06em;margin-left:12px;vertical-align:3px">{NOME[e["lado"]].upper()}</span>'
                if e.get('lado') in NOME else '')
        itens += (f'<div style="display:flex;gap:26px">'
                  f'<div style="flex:none;width:44px;display:flex;flex-direction:column;align-items:center">'
                  f'<i style="width:36px;height:36px;border-radius:50%;background:{c};border:5px solid {P["bg"]};box-shadow:0 0 0 4px {c};margin-top:4px"></i>'
                  + ('' if ult else f'<i style="flex:1;width:5px;background:#CFC6B4;margin:6px 0 -6px"></i>') + '</div>'
                  f'<div style="padding-bottom:{0 if ult else 30}px"><div style="font:900 30px {SANS};letter-spacing:.06em">{E(e["data"])}{quem}</div>'
                  f'<div style="font:500 34px/1.36 {SANS};margin-top:8px">{E(e["texto"])}</div></div></div>')
    return cab(s, chip, P) + tit(s, 88) + f'<div>{itens}</div>'

def lados(s, P, story, chip):
    def col(k):
        d = s[k]; c = COR[k]
        li = ''.join(f'<li style="margin:0 0 16px">{E(x)}</li>' for x in d.get('itens', [])[:4])
        return (f'<div style="flex:1;background:#fff;border:5px solid {T};border-radius:30px;padding:30px 30px 14px;box-shadow:10px 10px 0 {ROXO}">'
                f'<div style="display:flex;align-items:center;gap:14px;font:900 30px/1.2 {SANS};letter-spacing:.06em;text-transform:uppercase"><i style="flex:none;width:26px;height:26px;border-radius:50%;background:{c}"></i>{E(d["rotulo"])}</div>'
                f'<ul style="margin:20px 0 0;padding-left:30px;font:500 31px/1.34 {SANS}">{li}</ul></div>')
    return cab(s, chip, P) + tit(s, 88) + f'<div style="display:flex;gap:30px;align-items:stretch">{col("lula")}{col("flavio")}</div>'

def numeros(s, P, story, chip):
    bs = s.get('barras', [])[:4]; mx = max(b['valor'] for b in bs) or 1
    barras = ''.join(
        f'<div><div style="display:flex;justify-content:space-between;align-items:baseline;font:800 32px {SANS}"><span>{E(b["rotulo"])}</span>'
        f'<span style="font:900 64px/1 {SERIF}">{b["valor"]}</span></div>'
        f'<div style="height:46px;background:#EDE6D6;border-radius:12px;margin-top:10px;overflow:hidden">'
        f'<i style="display:block;height:100%;width:{b["valor"] / mx * 100:.1f}%;background:{COR.get(b.get("lado", "neutro"), ROXO)};border-radius:12px"></i></div></div>' for b in bs)
    card = (f'<div style="background:#fff;border:5px solid {T};border-radius:34px;box-shadow:12px 12px 0 {ROXO};padding:36px 40px;display:flex;flex-direction:column;gap:30px">'
            + (f'<div style="font:800 28px {SANS};color:{P["sub"]};letter-spacing:.06em;text-transform:uppercase">{E(s["unidade"])}</div>' if s.get('unidade') else '')
            + barras + (f'<div style="font:500 25px/1.4 {SANS};color:{P["sub"]};border-top:3px solid #EDE6D6;padding-top:20px">{E(s["criterio"])}</div>' if s.get('criterio') else '') + '</div>')
    nota = f'<div style="background:{AM};border:4px solid {T};border-radius:24px;padding:22px 28px;font:800 33px/1.3 {SANS}">{E(s["nota"])}</div>' if s.get('nota') else ''
    return cab(s, chip, P) + tit(s, 84) + card + nota

def proximos(s, P, story, chip):
    its = ''.join(f'<div style="display:flex;gap:30px;align-items:flex-start;padding:28px 0;border-top:4px solid {T}">'
                  f'<b style="flex:none;width:230px;font:900 40px/1.1 {SERIF}">{E(i["quando"])}</b>'
                  f'<span style="font:500 34px/1.38 {SANS}">{E(i["texto"])}</span></div>' for i in s.get('itens', [])[:3])
    return cab(s, chip, P) + tit(s, 96) + f'<div>{its}</div>'

TELAS = {'capa': capa, 'linha': linha, 'lados': lados, 'numeros': numeros, 'proximos': proximos}

def corpo(s, P, story, chip):
    return TELAS[s.get('tela', 'capa')](s, P, story, chip), s.get('fonte', '')
