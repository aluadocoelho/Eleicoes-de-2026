"""Modelos de gráfico da família "pesquisa" (pedido do dono em 21/10: "use mais gráficos").

Na especificação, junto de "familia": "pesquisa", use "grafico" com um destes valores:
  tendencia  linhas com as rodadas de UM instituto (campo "instituto"); precisa de 2 ou mais rodadas
  rodada     todas as pesquisas recentes, uma por instituto: diferença entre os dois e a faixa da margem
  media      média das pesquisas recentes, com cada pesquisa como um ponto e a faixa do menor ao maior
  totais     votos totais x votos válidos de UMA pesquisa (mostra brancos, nulos e indecisos)
  margem     a margem de erro de UMA pesquisa: as duas faixas lado a lado, para explicar empate técnico
Campos opcionais: "ate" (data ISO do último dia considerado, padrão: a mais recente), "dias" (janela de
rodada/media, padrão 4), "titulo" e "nota" (substituem os automáticos).
Os números saem de data/pesquisas.json. Para totais e margem, o par instituto + divulgação (ISO ou "21/10")
escolhe a pesquisa; sem divulgação, vale a mais recente daquele instituto.
Cores: azul e vermelho só para os dados dos candidatos; textos sempre em tinta escura.
"""
import os, json, html, datetime as dt
E = html.escape
AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.abspath(os.path.join(AQUI, '..', '..', 'data', 'pesquisas.json'))
ROXO, AM, T, AZ, VM = '#3E2492', '#FFD43B', '#16181D', '#1F4FA8', '#D62B2B'
CINZA, GRADE, SUB = '#8C8799', '#E4DFEE', '#4A4458'
SANS = "'Public Sans',system-ui,sans-serif"; SERIF = "'Source Serif 4',Georgia,serif"
W = 830   # largura útil do cartão branco
num = lambda v, c=1: (f'{float(v):.{c}f}'.rstrip('0').rstrip('.') if round(float(v), c) != int(float(v)) else str(int(float(v)))).replace('.', ',')
MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
dbr = lambda d: f'{d.day:02d}/{d.month:02d}'

def carregar():
    out = []
    for p in json.load(open(DADOS)):
        if p.get('flavio_validos') is None or p.get('lula_validos') is None: continue
        q = dict(p); q['d'] = dt.date.fromisoformat(p['divulgacao']); out.append(q)
    return sorted(out, key=lambda p: (p['d'], p['instituto']))

def data_spec(v, ano):
    if not v: return None
    if '-' in v: return dt.date.fromisoformat(v)
    d, m = v.split('/')[:2]; return dt.date(ano, int(m), int(d))

def recentes(ps, ate, dias):
    """A pesquisa mais recente de cada instituto dentro da janela."""
    ini = ate - dt.timedelta(days=dias - 1); ult = {}
    for p in ps:
        if ini <= p['d'] <= ate: ult[p['instituto']] = p
    return list(ult.values())

def uma(s, ps):
    inst = s['instituto']; ate = data_spec(s.get('ate'), ps[-1]['d'].year) or ps[-1]['d']
    alvo = data_spec(s.get('divulgacao'), ate.year)
    cands = [p for p in ps if p['instituto'].lower() == inst.lower() and p['d'] <= ate]
    if alvo: cands = [p for p in cands if p['d'] == alvo] or cands
    if not cands: raise ValueError(f'sem pesquisa de {inst} em data/pesquisas.json')
    return cands[-1]

# ---------- peças de SVG ----------
def txt(x, y, t, fs=26, peso=700, cor=T, anc='start', fam=SANS, extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{fs}" font-weight="{peso}" fill="{cor}" text-anchor="{anc}" {extra}>{E(t)}</text>'
def ponto(x, y, cor, r=11, oco=False):
    # anel branco de 3px separa o ponto da linha ou de outro ponto
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 3}" fill="#fff"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{"#fff" if oco else cor}" stroke="{cor}" stroke-width="{4 if oco else 0}"/>')
def svg(h, corpo):
    return f'<svg width="{W}" height="{h}" viewBox="0 0 {W} {h}" style="display:block;overflow:visible">{corpo}</svg>'
def legenda(itens):
    return ('<div style="display:flex;gap:34px;flex-wrap:wrap;margin-bottom:22px">' + ''.join(
        f'<span style="display:inline-flex;align-items:center;gap:12px;font:800 28px {SANS};color:{T}">'
        f'<i style="width:22px;height:22px;border-radius:50%;background:{c};display:inline-block"></i>{E(n)}</span>' for n, c in itens) + '</div>')
LEG2 = [('Flávio Bolsonaro', AZ), ('Lula', VM)]

def faixa_y(vals, passo=2, folga=1.0):
    lo, hi = min(vals) - folga, max(vals) + folga
    lo = min(lo, 50 - passo); hi = max(hi, 50 + passo)
    lo = passo * int(lo // passo); hi = passo * -int(-hi // passo)
    return lo, hi

# ---------- 1. tendência de um instituto ----------
def g_tendencia(s, ps):
    inst = s['instituto']; ate = data_spec(s.get('ate'), ps[-1]['d'].year) or ps[-1]['d']
    rs = [p for p in ps if p['instituto'].lower() == inst.lower() and p['d'] <= ate][-6:]
    if len(rs) < 2: raise ValueError(f'{inst} tem só {len(rs)} rodada; use outro gráfico')
    H, L, R, TOP, BOT = 560, 70, 110, 24, 64
    vals = [p['flavio_validos'] for p in rs] + [p['lula_validos'] for p in rs]
    lo, hi = faixa_y(vals)
    y = lambda v: TOP + (hi - v) / (hi - lo) * (H - TOP - BOT)
    x = lambda i: L + 56 + i * (W - L - 56 - R) / (len(rs) - 1)
    g = ''
    for v in range(int(lo), int(hi) + 1, 2):
        forte = v == 50
        g += f'<line x1="{L}" x2="{W - R + 30}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{"#9A93AC" if forte else GRADE}" stroke-width="{3 if forte else 2}" {"" if forte else "stroke-dasharray=\"2 8\" stroke-linecap=\"round\""}/>'
        g += txt(L - 16, y(v) + 9, f'{v}%', 24, 600, SUB, 'end')
    for i, p in enumerate(rs):
        g += txt(x(i), H - 18, dbr(p['d']), 25, 700, SUB, 'middle')
    for chave, cor in (('flavio_validos', AZ), ('lula_validos', VM)):
        pts = ' '.join(f'{x(i):.1f},{y(p[chave]):.1f}' for i, p in enumerate(rs))
        g += f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
    for chave, cor in (('flavio_validos', AZ), ('lula_validos', VM)):
        for i, p in enumerate(rs): g += ponto(x(i), y(p[chave]), cor, 10)
    # rótulo direto só no primeiro e no último ponto
    for chave, sinal in (('flavio_validos', -1), ('lula_validos', 1)):
        a, b = rs[0][chave], rs[-1][chave]
        outro = 'lula_validos' if chave == 'flavio_validos' else 'flavio_validos'
        sa = -1 if a >= rs[0][outro] else 1; sb = -1 if b >= rs[-1][outro] else 1
        g += txt(x(0), y(a) + (sa * 26 if sa < 0 else 44), f'{num(a)}%', 28, 800, T, 'middle')
        g += txt(x(len(rs) - 1) + 24, y(b) + 10, f'{num(b)}%', 34, 900, T, 'start')
    a, b = rs[0], rs[-1]
    d0 = a['flavio_validos'] - a['lula_validos']; d1 = b['flavio_validos'] - b['lula_validos']
    titulo = s.get('titulo') or f'As {len(rs)} rodadas da {inst}'
    nota = s.get('nota') or (f'De {dbr(a["d"])} a {dbr(b["d"])}, a diferença foi de {num(abs(d0))} para {num(abs(d1))} ponto{"s" if round(abs(d1), 1) != 1 else ""}'
                             + (f', a favor de {"Flávio" if d1 > 0 else "Lula"}.' if d1 else ', empate numérico.'))
    meta = f'Votos válidos · {len(rs)} pesquisas de {dbr(a["d"])} a {dbr(b["d"])}'
    return titulo, meta, legenda(LEG2) + svg(H, g), nota, fontes(rs)

# ---------- 2. todas as pesquisas recentes ----------
def g_rodada(s, ps):
    ate = data_spec(s.get('ate'), ps[-1]['d'].year) or ps[-1]['d']; dias = int(s.get('dias', 4))
    rs = sorted(recentes(ps, ate, dias), key=lambda p: p['flavio_validos'] - p['lula_validos'], reverse=True)[:10]
    LW, RW, TOP = 260, 160, 20
    lim = max(6, max(abs(p['flavio_validos'] - p['lula_validos']) + 2 * (p.get('margem') or 0) for p in rs))
    lim = 2 * -int(-lim // 2)
    rh = 52 if len(rs) > 8 else 64; H = TOP + rh * len(rs) + 20
    x = lambda d: LW + (d + lim) / (2 * lim) * (W - LW - RW)
    g = (f'<rect x="{x(-lim):.1f}" y="{TOP - 10}" width="{x(0) - x(-lim):.1f}" height="{H - TOP - 10}" fill="{VM}" opacity=".05"/>'
         f'<rect x="{x(0):.1f}" y="{TOP - 10}" width="{x(lim) - x(0):.1f}" height="{H - TOP - 10}" fill="{AZ}" opacity=".05"/>')
    g += txt(x(-lim), H + 66, '◀ Lula', 25, 800, T) + txt(x(lim), H + 66, 'Flávio ▶', 25, 800, T, 'end')
    for v in range(-lim, lim + 1, 2):
        if v: g += txt(x(v), H + 26, f'{abs(v)}', 22, 600, SUB, 'middle')
    g += txt(x(0), H + 26, '0', 22, 800, T, 'middle')
    g += f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="{TOP - 10}" y2="{H}" stroke="{T}" stroke-width="3"/>'
    sem = False
    for i, p in enumerate(rs):
        cy = TOP + rh * i + rh / 2; d = p['flavio_validos'] - p['lula_validos']; mg = p.get('margem')
        cor = AZ if d > 0 else (VM if d < 0 else CINZA)
        if i: g += f'<line x1="0" x2="{W}" y1="{cy - rh / 2:.1f}" y2="{cy - rh / 2:.1f}" stroke="{GRADE}" stroke-width="2"/>'
        g += txt(0, cy + 9, p['instituto'] + ('' if mg else '*'), 27, 800, T)
        if mg:
            g += f'<line x1="{x(d - 2 * mg):.1f}" x2="{x(d + 2 * mg):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="{cor}" stroke-opacity=".35" stroke-width="14" stroke-linecap="round"/>'
        else: sem = True
        g += ponto(x(d), cy, cor, 11)
        lado = 'Empate' if d == 0 else ('Flávio' if d > 0 else 'Lula') + f' +{num(abs(d))}'
        g += txt(W, cy + 9, lado, 26, 800, T, 'end')
    leg = (f'<div style="display:flex;gap:28px;flex-wrap:wrap;margin-bottom:18px;font:700 24px/1.3 {SANS};color:{SUB}">'
           f'<span style="display:inline-flex;align-items:center;gap:10px"><i style="width:22px;height:22px;border-radius:50%;background:{AZ}"></i><i style="width:22px;height:22px;border-radius:50%;background:{VM};margin-left:-4px"></i>diferença, em pontos</span>'
           f'<span style="display:inline-flex;align-items:center;gap:10px"><i style="width:56px;height:14px;border-radius:7px;background:{CINZA};opacity:.45"></i>margem de erro da diferença</span></div>')
    cruza = sum(1 for p in rs if p.get('margem') and abs(p['flavio_validos'] - p['lula_validos']) <= 2 * p['margem'])
    com = sum(1 for p in rs if p.get('margem'))
    nota = s.get('nota') or (f'Em {cruza} de {com} pesquisas com margem informada, a faixa passa pelo zero: empate técnico.' if com else 'Diferença entre os dois em cada pesquisa.')
    if sem: nota += ' * Sem margem de erro informada.'
    titulo = s.get('titulo') or 'Todas as pesquisas da semana'
    meta = f'Votos válidos · a mais recente de cada instituto, {dbr(ate - dt.timedelta(days=dias - 1))} a {dbr(ate)}'
    return titulo, meta, leg + svg(H + 76, g), nota, fontes(rs)

# ---------- 3. média ----------
def g_media(s, ps):
    ate = data_spec(s.get('ate'), ps[-1]['d'].year) or ps[-1]['d']; dias = int(s.get('dias', 4))
    rs = recentes(ps, ate, dias)
    mf = sum(p['flavio_validos'] for p in rs) / len(rs); ml = sum(p['lula_validos'] for p in rs) / len(rs)
    vals = [p['flavio_validos'] for p in rs] + [p['lula_validos'] for p in rs]
    lo, hi = faixa_y(vals, 2, .6)
    L, R = 20, 20; x = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)
    H = 470; trilhas = (('Flávio Bolsonaro', 'flavio_validos', AZ, mf, 130), ('Lula', 'lula_validos', VM, ml, 330))
    g = ''
    for v in range(int(lo), int(hi) + 1, 1):
        forte = v == 50
        if v % 2 == 0 or forte:
            g += f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="90" y2="{H - 46}" stroke="{"#9A93AC" if forte else GRADE}" stroke-width="{3 if forte else 2}"/>'
            g += txt(x(v), H - 12, f'{v}%', 24, 700 if forte else 600, T if forte else SUB, 'middle')
    for nome, k, cor, m, cy in trilhas:
        a, b = min(p[k] for p in rs), max(p[k] for p in rs)
        g += txt(L, cy - 62, nome, 28, 800, T, extra='paint-order="stroke" stroke="#fff" stroke-width="10"')
        g += f'<rect x="{x(a) - 16:.1f}" y="{cy - 46}" width="{x(b) - x(a) + 32:.1f}" height="92" rx="30" fill="{cor}" opacity=".12"/>'
        usados = []
        for v in sorted(p[k] for p in rs):
            for dy in (0, -22, 22, -44, 44):
                if all(abs(x(v) - ux) > 22 or dy != uy for ux, uy in usados): break
            usados.append((x(v), dy))
            g += f'<circle cx="{x(v):.1f}" cy="{cy + dy}" r="9" fill="#fff" stroke="{cor}" stroke-width="4"/>'
        g += f'<line x1="{x(m):.1f}" x2="{x(m):.1f}" y1="{cy - 38}" y2="{cy + 38}" stroke="{T}" stroke-width="5" stroke-linecap="round"/>'
        g += ponto(x(m), cy, cor, 15)
        g += txt(x(m), cy - 58, f'média {num(m)}%', 30, 900, T, 'middle', extra='paint-order="stroke" stroke="#fff" stroke-width="10"')
    leg = (f'<div style="display:flex;gap:30px;flex-wrap:wrap;margin-bottom:6px;font:700 24px {SANS};color:{SUB}">'
           f'<span style="display:inline-flex;align-items:center;gap:10px"><i style="width:18px;height:18px;border-radius:50%;border:4px solid {SUB}"></i>cada pesquisa</span>'
           f'<span style="display:inline-flex;align-items:center;gap:10px"><i style="width:26px;height:26px;border-radius:50%;background:{SUB}"></i>média simples</span>'
           f'<span style="display:inline-flex;align-items:center;gap:10px"><i style="width:48px;height:20px;border-radius:10px;background:{SUB};opacity:.25"></i>do menor ao maior</span></div>')
    titulo = s.get('titulo') or f'A média de {len(rs)} pesquisas'
    d = mf - ml
    nota = s.get('nota') or (f'Na média, {"Flávio" if d > 0 else "Lula"} tem {num(abs(d))} ponto{"s" if round(abs(d), 1) != 1 else ""} a mais. '
                             f'Média simples, sem peso por tamanho de amostra; não é uma pesquisa nova.')
    meta = f'Votos válidos · a mais recente de cada instituto, {dbr(ate - dt.timedelta(days=dias - 1))} a {dbr(ate)}'
    return titulo, meta, leg + svg(H, g), nota, fontes(rs)

# ---------- 4. votos totais x válidos ----------
def barra100(y, h, partes, rot):
    g = txt(0, y - 16, rot, 28, 800, T); x0 = 0
    for i, (v, cor, lab, hach) in enumerate(partes):
        w = v / 100 * W
        gap = 3 if i < len(partes) - 1 else 0
        fill = f'url(#hach)' if hach else cor
        g += f'<rect x="{x0:.1f}" y="{y}" width="{max(w - gap, 0):.1f}" height="{h}" rx="6" fill="{fill}"/>'
        if lab and w > 110:
            g += txt(x0 + w / 2, y + h / 2 + 13, lab, 36, 900, '#fff' if not hach else T, 'middle', SERIF)
        x0 += w
    return g

def g_totais(s, ps):
    p = uma(s, ps)
    if p.get('flavio_totais') is None: raise ValueError(f'{p["instituto"]} de {dbr(p["d"])} não traz votos totais')
    f, l = p['flavio_totais'], p['lula_totais']; o = round(100 - f - l, 1)
    fv, lv = p['flavio_validos'], p['lula_validos']
    defs = (f'<defs><pattern id="hach" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="14" height="14" fill="#E9E5F0"/><rect width="5" height="14" fill="#C9C2D6"/></pattern></defs>')
    g = defs + barra100(56, 96, [(f, AZ, f'{num(f)}%', 0), (l, VM, f'{num(l)}%', 0), (o, '', f'{num(o)}%', 1)], 'Votos totais: todos os entrevistados')
    g += barra100(260, 96, [(fv, AZ, f'{num(fv)}%', 0), (lv, VM, f'{num(lv)}%', 0)], 'Votos válidos: só quem escolheu um dos dois')
    # guias ligando o fim de cada parte
    xf, xl = f / 100 * W, (f + l) / 100 * W
    g += f'<path d="M{xf:.1f} 154 L{fv / 100 * W:.1f} 258" stroke="{CINZA}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>'
    g += f'<path d="M{xl:.1f} 154 L{W:.1f} 258" stroke="{CINZA}" stroke-width="2" stroke-dasharray="6 6" fill="none"/>'
    g += f'<line x1="{W / 2}" x2="{W / 2}" y1="262" y2="366" stroke="{T}" stroke-width="4"/>' + txt(W / 2, 392, 'metade', 22, 700, SUB, 'middle')
    leg = legenda(LEG2 + [('Brancos, nulos e indecisos', '#C9C2D6')])
    titulo = s.get('titulo') or 'Votos totais e votos válidos'
    nota = s.get('nota') or f'Os válidos tiram brancos, nulos e indecisos ({num(o)}% nesta pesquisa). É a conta que o TSE usa para saber quem ganha.'
    meta = f'{p["instituto"]} · divulgada em {dbr(p["d"])}' + (f' · {int(p["amostra"]):,} entrevistas'.replace(',', '.') if p.get('amostra') else '')
    return titulo, meta, leg + svg(400, g), nota, fontes([p])

# ---------- 5. margem de erro ----------
def g_margem(s, ps):
    p = uma(s, ps); mg = p.get('margem')
    if not mg: raise ValueError(f'{p["instituto"]} de {dbr(p["d"])} não informa margem')
    f, l = p['flavio_validos'], p['lula_validos']
    lo, hi = faixa_y([f - mg, f + mg, l - mg, l + mg], 2, .5)
    H, TOP, BOT, L = 560, 20, 20, 90
    y = lambda v: TOP + (hi - v) / (hi - lo) * (H - TOP - BOT)
    cols = (('Flávio Bolsonaro', f, AZ, L + 110), ('Lula', l, VM, L + 390))
    g = ''
    for v in range(int(lo), int(hi) + 1, 2):
        g += f'<line x1="{L}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{GRADE}" stroke-width="2"/>' + txt(L - 16, y(v) + 9, f'{v}%', 24, 600, SUB, 'end')
    a, b = max(f - mg, l - mg), min(f + mg, l + mg)
    if a <= b:
        g += f'<rect x="{L}" y="{y(b):.1f}" width="{W - L}" height="{y(a) - y(b):.1f}" fill="{AM}" opacity=".55"/>'
        mid = (y(a) + y(b)) / 2
        g += txt(W - 14, mid - 6, 'as faixas', 28, 900, T, 'end') + txt(W - 14, mid + 28, 'se cruzam', 28, 900, T, 'end')
    for nome, v, cor, cx in cols:
        g += f'<rect x="{cx - 34}" y="{y(v + mg):.1f}" width="68" height="{y(v - mg) - y(v + mg):.1f}" rx="34" fill="#fff"/>'
        g += f'<rect x="{cx - 34}" y="{y(v + mg):.1f}" width="68" height="{y(v - mg) - y(v + mg):.1f}" rx="34" fill="{cor}" opacity=".3"/>'
        g += f'<line x1="{cx - 52}" x2="{cx + 52}" y1="{y(v + mg):.1f}" y2="{y(v + mg):.1f}" stroke="{cor}" stroke-width="5" stroke-linecap="round"/>'
        g += f'<line x1="{cx - 52}" x2="{cx + 52}" y1="{y(v - mg):.1f}" y2="{y(v - mg):.1f}" stroke="{cor}" stroke-width="5" stroke-linecap="round"/>'
        g += ponto(cx, y(v), cor, 16)
        g += txt(cx + 70, y(v) + 12, f'{num(v)}%', 38, 900, T, 'start', SERIF)
        g += txt(cx + 70, y(v + mg) + 8, f'até {num(v + mg)}', 22, 700, SUB) + txt(cx + 70, y(v - mg) + 8, f'até {num(v - mg)}', 22, 700, SUB)
    leg = legenda(LEG2) + f'<div style="font:700 24px/1.3 {SANS};color:{SUB};margin:-8px 0 14px">Faixa colorida: o resultado pode estar em qualquer ponto dela (±{num(mg)} pontos).</div>'
    titulo = s.get('titulo') or 'O que é empate técnico'
    nota = s.get('nota') or (f'Na {p["instituto"]}, a diferença é de {num(abs(f - l))} ponto{"s" if round(abs(f - l), 1) != 1 else ""} e as faixas se cruzam. '
                             f'Pela margem, não dá para dizer quem está na frente.' if a <= b else
                             f'Na {p["instituto"]}, as faixas não se cruzam: a diferença de {num(abs(f - l))} pontos é maior que a margem.')
    meta = f'{p["instituto"]} · votos válidos · divulgada em {dbr(p["d"])}'
    return titulo, meta, leg + svg(H, g), nota, fontes([p])

def fontes(rs):
    import re
    ni = len({p['instituto'] for p in rs})
    if ni > 2:
        return f'Fontes: {ni} institutos, como divulgado pela imprensa. Lista com links em clareiaeleicoes.com.br'
    fs = []
    for p in rs[-3:]:
        for f in (p.get('fonte') or '').split(' / '):
            f = re.sub(r'\s*\([^)]*\)', '', f).split(';')[0].strip()
            if f and f not in fs: fs.append(f)
    reg = [m for p in rs for m in re.findall(r'BR-\d{5}/\d{4}', p.get('fonte') or '')]
    return ('Fontes: ' if len(fs) > 1 else 'Fonte: ') + ', '.join(fs[:3]) + (f'. Registro {reg[0]}' if reg else '') + '. Dados: clareiaeleicoes.com.br'

GRAFICOS = {'tendencia': g_tendencia, 'rodada': g_rodada, 'media': g_media, 'totais': g_totais, 'margem': g_margem}

def corpo(s, P, story, chip):
    titulo, meta, grafico, nota, fonte = GRAFICOS[s['grafico']](s, carregar())
    tfs = 92 if len(titulo) <= 24 else 78
    html_ = (f'<div>{chip("pesquisa")}<div style="font:900 {tfs}px/1.02 {SERIF};margin-top:28px;letter-spacing:-.02em">{E(titulo)}</div>'
             f'<div style="font:600 30px/1.35 {SANS};color:{P["sub"]};margin-top:14px">{E(meta)}</div></div>'
             f'<div style="background:#fff;border:5px solid {T};border-radius:36px;box-shadow:12px 12px 0 {ROXO};padding:36px 44px 30px">{grafico}</div>'
             f'<div style="background:{AM};border:4px solid {T};border-radius:24px;padding:22px 28px;font:800 33px/1.3 {SANS}">{E(nota)}</div>')
    return html_, s.get('fonte') or fonte
