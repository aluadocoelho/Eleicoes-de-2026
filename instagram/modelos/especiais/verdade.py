#!/usr/bin/env python3
"""Especial "Agora, é hora de falar a verdade" (campanha contra fake news, pedido do dono em 27/10/2026).
Visual próprio, fora dos blocos retangulares: fundo amarelo com retícula, megafone, balões de conversa,
carimbo FALSO redondo, lupa, bolhas e pontinhos para números. Azul e vermelho só para dados dos candidatos.

Uso:
  python3 verdade.py roteiro.json pasta/            -> feed (1-xxx.jpg, um por item de "feed") e reels.mp4 + capa.jpg
  python3 verdade.py roteiro.json pasta/ --so-feed  -> só as imagens
roteiro.json: {"peca": "1/7", "fonte": "...", "feed": [cena, ...], "reels": [cena, ...]}
cena: {"tipo": "capa" | "bolhas" | "sinais" | "rosca" | "pontos" | "conversa" | "caminho" | "final", ...campos}
  capa:     titulo, destaque, sub
  bolhas:   titulo, itens:[{rotulo, valor, lado}], nota
  sinais:   titulo, destaque?, itens:[{icone: relogio|pergunta|raio|olho, titulo, texto}] (até 4)
  rosca:    titulo, itens:[{rotulo, valor}], nota
  pontos:   titulo, total, itens:[{rotulo, valor, lado}], nota
  conversa: chip, onde, boato, verdade, checador, data, lado
  caminho:  titulo, destaque?, passos:[{titulo, texto}], selos?:[...]
  final:    titulo, destaque
"""
import os, sys, json, html, asyncio, tempfile, shutil, subprocess, math
AQUI = os.path.dirname(os.path.abspath(__file__)); MOD = os.path.dirname(AQUI); sys.path.insert(0, MOD)
import marca as M
E = html.escape
FONTES = os.path.join(MOD, 'fontes'); MARCA = os.path.abspath(os.path.join(MOD, '..', '..', 'marca'))
TRILHA = os.path.join(MOD, 'trilhas', 'clareia-manchete-30s.wav')
ROXO, AM, T, AZ, VM, BR = '#3E2492', '#FFD43B', '#16181D', '#1F4FA8', '#D62B2B', '#FFFFFF'
CINZA = '#E9E6EF'
SERIF, SANS = "'Source Serif 4',Georgia,serif", "'Public Sans',system-ui,sans-serif"
COR = {'lula': VM, 'flavio': AZ, 'neutro': ROXO, 'cinza': '#B9B4C4'}
ROXOS = ['#3E2492', '#6A45D9', '#9C82F0', '#C9BAF7', '#E6DEFC']
ABRE, FINAL = 3.0, 3.0

# ---------- animação ----------
class A:
    """gera o estilo de animação; sem t0 (imagem parada) não anima"""
    def __init__(self, t0=None): self.t0 = t0
    def __call__(self, nome, atraso=0, dur=.7, curva='cubic-bezier(.2,.9,.3,1.25)'):
        if self.t0 is None: return ''
        return f'animation:{nome} {dur}s {curva} {self.t0 + atraso:.2f}s both;'

CSS = """
@keyframes show{from{visibility:hidden}to{visibility:visible}}
@keyframes hide{to{visibility:hidden}}
@keyframes sair{to{opacity:0;filter:blur(14px);transform:scale(1.03)}}
@keyframes foco{from{opacity:0;filter:blur(18px);transform:translateY(30px)}to{opacity:1;filter:none;transform:none}}
@keyframes pop{0%{opacity:0;transform:scale(.2) rotate(-10deg)}60%{opacity:1;transform:scale(1.12) rotate(3deg)}80%{transform:scale(.96)}100%{transform:none}}
@keyframes bolha{0%{opacity:0;transform:translateY(40px) scale(.6)}70%{opacity:1;transform:translateY(-6px) scale(1.03)}100%{transform:none}}
@keyframes carimbo{0%{opacity:0;transform:scale(3.2) rotate(-30deg)}55%{opacity:1;transform:scale(.88) rotate(-12deg)}75%{transform:scale(1.06) rotate(-15deg)}100%{transform:scale(1) rotate(-14deg)}}
@keyframes digita{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes some{to{opacity:0;height:0;margin:0;padding:0}}
@keyframes cresce{from{transform:scale(0)}}
@keyframes ponto{from{opacity:0;transform:scale(0)}to{opacity:1;transform:none}}
@keyframes traco{from{stroke-dashoffset:var(--L)}}
@keyframes flutua{0%,100%{translate:0 0}50%{translate:0 -18px}}
@keyframes grita{0%,100%{transform:rotate(-8deg) scale(1)}50%{transform:rotate(-4deg) scale(1.05)}}
@keyframes onda{0%{opacity:0;transform:scale(.6)}30%{opacity:1}100%{opacity:0;transform:scale(1.5)}}
@keyframes lupa{0%{opacity:0;transform:translate(-180px,120px) rotate(-30deg)}70%{opacity:1;transform:translate(10px,-6px) rotate(4deg)}100%{transform:none}}
@keyframes logo{0%{transform:scale(.4);opacity:0}70%{transform:scale(1.08);opacity:1}100%{transform:scale(1)}}
"""

# ---------- desenhos ----------
def megafone(px):
    return (f'<svg width="{px}" height="{px}" viewBox="0 0 200 200">'
            f'<path d="M40 82 L120 42 L120 158 L40 118 Z" fill="{ROXO}" stroke="{T}" stroke-width="8" stroke-linejoin="round"/>'
            f'<rect x="18" y="80" width="30" height="40" rx="8" fill="{BR}" stroke="{T}" stroke-width="8"/>'
            f'<path d="M58 118 L70 160 Q74 172 86 168 L96 165 Q106 160 102 148 L92 122" fill="{BR}" stroke="{T}" stroke-width="8" stroke-linejoin="round"/>'
            f'<ellipse cx="124" cy="100" rx="14" ry="60" fill="{AM}" stroke="{T}" stroke-width="8"/>'
            f'<path d="M156 66 Q172 100 156 134" fill="none" stroke="{T}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M172 48 Q198 100 172 152" fill="none" stroke="{T}" stroke-width="8" stroke-linecap="round"/></svg>')

def lupa_svg(px, cor=ROXO):
    return (f'<svg width="{px}" height="{px}" viewBox="0 0 200 200"><circle cx="82" cy="82" r="58" fill="rgba(255,255,255,.55)" stroke="{T}" stroke-width="14"/>'
            f'<circle cx="82" cy="82" r="58" fill="none" stroke="{cor}" stroke-width="6"/>'
            f'<path d="M126 126 L182 182" stroke="{T}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M126 126 L182 182" stroke="{cor}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M50 62 Q58 44 80 40" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/></svg>')

ICONES = {
    'relogio': '<circle cx="50" cy="52" r="34" fill="#fff" stroke="#16181D" stroke-width="7"/><path d="M50 32 V52 L64 62" fill="none" stroke="#16181D" stroke-width="7" stroke-linecap="round"/><path d="M30 14 L18 26 M70 14 L82 26" stroke="#16181D" stroke-width="7" stroke-linecap="round"/>',
    'pergunta': '<path d="M34 36 Q34 18 52 18 Q70 18 70 34 Q70 46 56 52 Q50 56 50 66" fill="none" stroke="#16181D" stroke-width="9" stroke-linecap="round"/><circle cx="50" cy="82" r="6" fill="#16181D"/>',
    'raio': '<path d="M56 8 L24 56 H48 L40 92 L76 40 H52 Z" fill="#fff" stroke="#16181D" stroke-width="7" stroke-linejoin="round"/>',
    'olho': '<path d="M8 50 Q50 10 92 50 Q50 90 8 50 Z" fill="#fff" stroke="#16181D" stroke-width="7" stroke-linejoin="round"/><circle cx="50" cy="50" r="14" fill="#16181D"/><path d="M14 20 L86 82" stroke="#D62B2B" stroke-width="7" stroke-linecap="round" opacity="0"/>',
}

def balao(txt, lado='esq', cor=BR, fg=T, fs=40, larg=760, extra='', rotulo='', pr=38):
    """balão de conversa com rabinho (o rabinho fica atrás do balão)"""
    esq = lado == 'esq'
    cauda = (f'<svg style="position:absolute;{"left:-22px" if esq else "right:-22px"};bottom:-4px;z-index:0" width="70" height="56" viewBox="0 0 70 56">'
             f'<path d="{"M60 0 L60 50 L4 52 Q34 36 30 0 Z" if esq else "M10 0 L10 50 L66 52 Q36 36 40 0 Z"}" fill="{cor}" stroke="{T}" stroke-width="5" stroke-linejoin="round"/></svg>')
    rot = f'<div style="font:900 24px {SANS};letter-spacing:.1em;text-transform:uppercase;opacity:.75;margin-bottom:10px">{E(rotulo)}</div>' if rotulo else ''
    return (f'<div style="position:relative;max-width:{larg}px;{extra}">{cauda}'
            f'<div style="position:relative;z-index:1;background:{cor};color:{fg};border:5px solid {T};'
            f'border-radius:{"44px 44px 44px 14px" if esq else "44px 44px 14px 44px"};padding:30px {pr}px 30px 38px;'
            f'box-shadow:8px 8px 0 {T};font:600 {fs}px/1.32 {SANS}">{rot}{txt}</div>'
            f'<div style="position:absolute;{"left:6px" if esq else "right:6px"};bottom:5px;width:44px;height:30px;background:{cor};z-index:2"></div></div>')

def carimbo(px, txt='FALSO'):
    return (f'<svg width="{px}" height="{px}" viewBox="0 0 200 200"><circle cx="100" cy="100" r="92" fill="rgba(214,43,43,.08)" stroke="{VM}" stroke-width="10"/>'
            f'<circle cx="100" cy="100" r="74" fill="none" stroke="{VM}" stroke-width="4" stroke-dasharray="6 8"/>'
            f'<text x="100" y="116" text-anchor="middle" font-family="Public Sans" font-weight="900" font-size="40" letter-spacing="2" fill="{VM}">{txt}</text>'
            f'<path d="M40 60 L56 64 M150 140 L164 146" stroke="{VM}" stroke-width="6" stroke-linecap="round"/></svg>')

def selo_link(a):
    return (f'<div style="{a("pop", .5)}flex:none;transform:rotate(-4deg);background:{ROXO};color:#fff;border:5px solid {T};box-shadow:7px 7px 0 {T};'
            f'border-radius:999px;padding:20px 38px;font:900 40px {SANS};white-space:nowrap">Link na bio</div>')

def titulo(t, d=None, fs=96, cor=T, dcor=ROXO, a=None, atraso=.15, centro=False):
    a = a or A()
    fs = fs if len(t + (d or '')) < 34 else int(fs * .82)
    return (f'<div style="{a("foco", atraso)}font:900 {fs}px/1.02 {SERIF};letter-spacing:-.02em;color:{cor};{"text-align:center;" if centro else ""}">{E(t)}'
            + (f'<br><span style="color:{dcor}">{E(d)}</span>' if d else '') + '</div>')

def chip(txt, a, atraso=0):
    return (f'<div style="{a("pop", atraso)}align-self:flex-start;transform:rotate(-2deg);background:{T};color:{AM};border-radius:999px;'
            f'padding:10px 26px;font:900 28px {SANS};letter-spacing:.1em;text-transform:uppercase">{E(txt)}</div>')

# ---------- cenas ----------
def c_capa(d, a, h):
    bal = [('vi no grupo!', 90, 70, -6, .5), ('compartilha!!', 640, 30, 5, .75), ('é verdade?', 560, 250, -3, 1.0)]
    bs = ''.join(f'<div style="position:absolute;left:{x}px;top:{y}px;transform:rotate({r}deg)"><div style="{a("bolha", t)}">'
                 f'<div style="animation:flutua 3s ease-in-out infinite {k*.6:.1f}s">{balao(E(s), "esq" if k % 2 == 0 else "dir", BR, T, 36, 460)}</div></div></div>'
                 for k, (s, x, y, r, t) in enumerate(bal))
    alto = 380 if h > 1500 else 330
    return (f'<div style="position:relative;height:{alto}px">{bs}</div>'
            f'<div style="display:flex;align-items:center;gap:28px;margin-top:10px"><div style="{a("pop", .2)}flex:none"><div style="animation:grita 1.2s ease-in-out infinite">{megafone(230 if h > 1500 else 200)}</div></div>'
            f'<div style="{a("pop", .1)}transform:rotate(-2deg);background:{T};color:{AM};border-radius:999px;padding:10px 26px;font:900 30px {SANS};letter-spacing:.1em">CAMPANHA CLAREIA</div></div>'
            + titulo(d['titulo'], d.get('destaque'), 124 if h > 1500 else 112, a=a, atraso=.35)
            + (f'<div style="{a("foco", .8)}font:600 40px/1.38 {SANS};color:#3A3000;margin-top:26px;max-width:900px">{E(d["sub"])}</div>' if d.get('sub') else ''))

def c_bolhas(d, a, h):
    its = d['itens']; mx = max(i['valor'] for i in its)
    base = 430 if h > 1500 else 380
    circ = ''
    for k, i in enumerate(its):
        r = base * math.sqrt(i['valor'] / mx)
        circ += (f'<div style="display:flex;flex-direction:column;align-items:center;gap:18px">'
                 f'<div style="{a("pop", .5 + .35 * k, .9)}width:{r:.0f}px;height:{r:.0f}px;border-radius:50%;background:{COR[i["lado"]]};border:6px solid {T};box-shadow:10px 10px 0 {T};'
                 f'display:grid;place-items:center;color:#fff;font:900 {r * .38:.0f}px/1 {SERIF}">{i["valor"]}</div>'
                 f'<div style="{a("foco", .8 + .35 * k)}font:900 40px {SANS}">{E(i["rotulo"])}</div></div>')
    return (chip(d.get('chip', 'Na eleição'), a) + f'<div style="height:26px"></div>' + titulo(d['titulo'], d.get('destaque'), 88, a=a)
            + f'<div style="display:flex;justify-content:center;align-items:flex-end;gap:60px;margin-top:50px">{circ}</div>'
            + (f'<div style="{a("foco", 1.4)}margin-top:44px;font:800 40px/1.35 {SANS};text-align:center"><span style="background:{BR};border:4px solid {T};border-radius:999px;padding:10px 28px;box-shadow:5px 5px 0 {T};display:inline-block">{E(d["nota"])}</span></div>' if d.get('nota') else '')
            + (f'<div style="{a("foco", 1.6)}margin-top:24px;font:500 28px/1.4 {SANS};color:#3A3000;text-align:center">{E(d["criterio"])}</div>' if d.get('criterio') else ''))

def c_sinais(d, a, h):
    its = d['itens']; out = ''
    apertado = len(its) > 2 and h < 1500
    ic, tf, xf, gap = (124, 42, 28, 22) if apertado else (170, 50, 34, 34)
    for k, i in enumerate(its):
        dir_ = k % 2 == 1
        out += (f'<div style="display:flex;align-items:center;gap:28px;{"flex-direction:row-reverse;text-align:right;" if dir_ else ""}margin-top:{0 if k == 0 else gap}px">'
                f'<div style="{a("pop", .45 + .35 * k)}flex:none;position:relative;width:{ic}px;height:{ic}px;border-radius:50%;background:{BR};border:6px solid {T};box-shadow:7px 7px 0 {T};display:grid;place-items:center">'
                f'<svg width="{ic * .56:.0f}" height="{ic * .56:.0f}" viewBox="0 0 100 100">{ICONES[i["icone"]]}</svg>'
                f'<b style="position:absolute;{"right" if dir_ else "left"}:-12px;top:-12px;width:50px;height:50px;border-radius:50%;background:{ROXO};color:#fff;border:4px solid {T};display:grid;place-items:center;font:900 26px {SANS}">{i.get("n", k + 1)}</b></div>'
                f'<div style="{a("foco", .6 + .35 * k)}"><div style="font:900 {tf}px/1.08 {SERIF}">{E(i["titulo"])}</div>'
                f'<div style="font:600 {xf}px/1.35 {SANS};color:#3A3000;margin-top:6px">{E(i["texto"])}</div></div></div>')
    return titulo(d['titulo'], d.get('destaque'), 84 if apertado else 96, a=a) + f'<div style="margin-top:{30 if apertado else 46}px">{out}</div>'

def c_rosca(d, a, h):
    its = d['itens']; tot = sum(i['valor'] for i in its); R, C = 190, 2 * math.pi * 190; acc = 0; arcs = ''; leg = ''
    for k, i in enumerate(its):
        L = C * i['valor'] / tot; cor = ROXOS[k % len(ROXOS)]
        arcs += (f'<circle cx="250" cy="250" r="{R}" fill="none" stroke="{cor}" stroke-width="90" stroke-dasharray="{L - 4:.1f} {C:.1f}" stroke-dashoffset="{-acc:.1f}" '
                 f'transform="rotate(-90 250 250)" style="--L:{L:.1f};{a("traco", .5 + .25 * k, .8, "ease-out").replace("animation:traco", "animation:traco") if a.t0 is not None else ""}"/>')
        acc += L
        leg += (f'<div style="{a("foco", .6 + .25 * k)}display:flex;align-items:center;gap:16px;margin-top:16px"><i style="flex:none;width:40px;height:40px;border-radius:50%;background:{cor};border:4px solid {T}"></i>'
                f'<span style="font:800 36px {SANS};flex:1">{E(i["rotulo"])}</span><b style="font:900 52px {SERIF}">{i["valor"]}</b></div>')
    svg = (f'<svg width="430" height="430" viewBox="0 0 500 500" style="{a("pop", .3)}"><circle cx="250" cy="250" r="{R + 50}" fill="{T}"/><circle cx="256" cy="256" r="{R + 50}" fill="none"/>'
           f'<circle cx="250" cy="250" r="{R}" fill="none" stroke="#FFF6CC" stroke-width="90"/>{arcs}'
           f'<circle cx="250" cy="250" r="{R - 50}" fill="{AM}" stroke="{T}" stroke-width="8"/>'
           f'<text x="250" y="262" text-anchor="middle" font-family="Source Serif 4" font-weight="900" font-size="104" fill="{T}">{tot}</text>'
           f'<text x="250" y="314" text-anchor="middle" font-family="Public Sans" font-weight="800" font-size="30" fill="{T}">boatos</text></svg>')
    return (chip(d.get('chip', 'Quem desmentiu'), a) + '<div style="height:26px"></div>' + titulo(d['titulo'], d.get('destaque'), 84, a=a)
            + f'<div style="display:flex;align-items:center;gap:40px;margin-top:40px"><div style="flex:none">{svg}</div><div style="flex:1">{leg}</div></div>'
            + (f'<div style="{a("foco", 1.6)}margin-top:34px;font:500 30px/1.4 {SANS};color:#3A3000">{E(d["nota"])}</div>' if d.get('nota') else ''))

def c_pontos(d, a, h):
    its = d['itens']; seq = []
    for i in its: seq += [COR[i['lado']]] * i['valor']
    col = 17; tam = 50
    pts = ''.join(f'<i style="width:{tam - 10}px;height:{tam - 10}px;border-radius:50%;background:{c};border:3px solid {T};{a("ponto", .4 + n * .012, .25, "ease-out")}"></i>' for n, c in enumerate(seq))
    leg = ''.join(f'<div style="{a("foco", 1.2 + .25 * k)}display:flex;align-items:center;gap:16px"><i style="flex:none;width:40px;height:40px;border-radius:50%;background:{COR[i["lado"]]};border:3px solid {T}"></i>'
                  f'<b style="font:900 52px {SERIF}">{i["valor"]}</b><span style="font:700 34px/1.2 {SANS}">{E(i["rotulo"])}</span></div>' for k, i in enumerate(its))
    return (chip(d.get('chip', 'E quem espalhou?'), a) + '<div style="height:26px"></div>' + titulo(d['titulo'], d.get('destaque'), 84, a=a)
            + f'<div style="display:grid;grid-template-columns:repeat({col},{tam - 10}px);gap:10px;margin-top:36px;justify-content:center">{pts}</div>'
            + f'<div style="display:flex;flex-direction:column;gap:12px;margin-top:34px">{leg}</div>'
            + (f'<div style="{a("foco", 1.8)}margin-top:24px;font:500 28px/1.4 {SANS};color:#3A3000">{E(d["nota"])}</div>' if d.get('nota') else ''))

def c_conversa(d, a, h):
    cor = COR.get(d.get('lado', 'neutro'), ROXO)
    quem = {'lula': 'Contra Lula', 'flavio': 'Contra Flávio'}.get(d.get('lado'), '')
    tag = (f'<span style="display:inline-flex;align-items:center;gap:12px;background:{BR};border:4px solid {T};border-radius:999px;padding:8px 22px;font:900 26px {SANS};letter-spacing:.08em;text-transform:uppercase">'
           f'<i style="width:22px;height:22px;border-radius:50%;background:{cor};border:3px solid {T}"></i>{quem}</span>') if quem else ''
    digit = (f'<div style="{"" if a.t0 is None else f"animation:some .01s linear {a.t0 + 1.0:.2f}s forwards;"}display:{"none" if a.t0 is None else "inline-flex"};gap:12px;background:{BR};border:5px solid {T};border-radius:44px 44px 44px 10px;padding:26px 34px;box-shadow:6px 6px 0 {T};width:max-content">'
             + ''.join(f'<i style="width:20px;height:20px;border-radius:50%;background:#9A94A8;animation:digita .9s ease-in-out {k * .2:.1f}s infinite"></i>' for k in range(3)) + '</div>')
    boato = (f'<div style="position:relative;{a("bolha", 1.0)}">'
             + balao(f'<div style="font:700 28px {SANS};color:#6A6478;margin-bottom:12px">{E(d["onde"])}</div>“{E(d["boato"])}”', 'esq', BR, T, 52, 900, pr=60)
             + f'<div style="position:absolute;right:-40px;bottom:-150px;z-index:3;{a("carimbo", 1.7, .6)}">{carimbo(240)}</div></div>')
    verdade = (f'<div style="display:flex;justify-content:flex-end;align-items:flex-end;gap:16px;margin-top:190px"><div style="flex:none;align-self:center;{a("lupa", 2.2, .9)}">{lupa_svg(170)}</div><div style="{a("bolha", 2.4)}">'
               + balao(E(d['verdade']) + f'<div style="font:700 28px {SANS};margin-top:16px;opacity:.85">Checagem: {E(d["checador"])} ({E(d["data"])})</div>', 'dir', ROXO, '#fff', 48, 860, rotulo='O que é verdade')
               + f'</div></div>')
    lupa = f'<div style="position:absolute;right:40px;top:-40px;{a("lupa", 2.2, .9)}opacity:.95">{lupa_svg(150, AM)}</div>' if False else ''
    return (f'<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">{chip(d.get("chip", "Boato desmentido"), a)}<div style="{a("pop", .2)}">{tag}</div></div>'
            + (f'<div style="height:24px"></div>' + titulo(d['titulo'], d.get('destaque'), 76, a=a) if d.get('titulo') else '')
            + f'<div style="position:relative;margin-top:44px">{digit}{boato}{verdade}{lupa}</div>')

def c_caminho(d, a, h):
    ps = d['passos']; out = ''
    for k, p in enumerate(ps):
        out += (f'<div style="display:flex;gap:30px;align-items:flex-start;position:relative;padding-bottom:{0 if k == len(ps) - 1 else 40}px">'
                + (f'<i style="position:absolute;left:52px;top:110px;bottom:0;border-left:8px dotted {T}"></i>' if k < len(ps) - 1 else '')
                + f'<div style="{a("pop", .45 + .4 * k)}flex:none;width:112px;height:112px;border-radius:50%;background:{ROXO if k < len(ps) - 1 else T};color:{AM};border:6px solid {T};box-shadow:6px 6px 0 {T};display:grid;place-items:center;font:900 56px {SERIF}">{k + 1}</div>'
                f'<div style="{a("foco", .6 + .4 * k)}padding-top:8px"><div style="font:900 48px/1.1 {SERIF}">{E(p["titulo"])}</div><div style="font:600 33px/1.35 {SANS};color:#3A3000;margin-top:8px">{E(p["texto"])}</div></div></div>')
    selos = ''
    if d.get('selos'):
        rot = [-5, 3, -2, 6, -4, 2, -6, 4]
        selos = (f'<div style="display:flex;flex-wrap:wrap;gap:16px 14px;margin-top:40px">'
                 + ''.join(f'<span style="{a("pop", 1.4 + .12 * k)}display:inline-block;transform:rotate({rot[k % 8]}deg);background:{BR};border:4px solid {T};border-radius:999px;padding:12px 26px;font:800 32px {SANS};box-shadow:5px 5px 0 {T}">{E(s)}</span>'
                           for k, s in enumerate(d['selos'])) + '</div>')
    lupa = f'<div style="position:absolute;right:20px;top:-10px;{a("lupa", .2, 1.0)}">{lupa_svg(220)}</div>'
    return (f'<div style="position:relative">{lupa}<div style="max-width:760px">{titulo(d["titulo"], d.get("destaque"), 96, a=a)}</div></div>'
            + f'<div style="margin-top:46px">{out}</div>{selos}')

def c_final(d, a, h):
    return (f'<div style="display:flex;justify-content:center;{a("pop", .1)}"><div style="animation:grita 1.2s ease-in-out infinite">{megafone(280)}</div></div>'
            + titulo(d['titulo'], d.get('destaque'), 110, a=a, atraso=.35, centro=True))

CENAS = {'capa': c_capa, 'bolhas': c_bolhas, 'sinais': c_sinais, 'rosca': c_rosca, 'pontos': c_pontos, 'conversa': c_conversa, 'caminho': c_caminho, 'final': c_final}

def fundo(h):
    return (f'<div style="position:absolute;inset:0;background:{AM}"></div>'
            f'<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(22,24,29,.13) 2.2px,transparent 2.8px);background-size:26px 26px;'
            f'-webkit-mask-image:linear-gradient(160deg,#000 0%,transparent 55%,#000 100%)"></div>'
            f'<svg style="position:absolute;right:-180px;bottom:{-120 if h < 1500 else 80}px;opacity:.10" width="700" height="700" viewBox="0 0 140 140">{M.simbolo(T)}</svg>'
            f'<div style="position:absolute;left:0;right:0;top:0;display:flex;height:18px;z-index:7"><i style="flex:1;background:{AZ}"></i><i style="flex:1;background:{VM}"></i></div>')

def topo(a, h):
    y = 110 if h > 1500 else 64
    return (f'<div style="position:absolute;left:70px;right:70px;top:{y}px;display:flex;align-items:center;justify-content:space-between;z-index:7">'
            f'<img src="file://{MARCA}/clareia-eleicoes-claro.svg" style="height:{100 if h > 1500 else 84}px;{a("logo", 0, .6)}transform-origin:left center">'
            f'<span style="font:800 30px {SANS};color:{T}">{M.ARROBA}</span></div>')

def rodape(txt, a, h, link=True):
    b = 120 if h > 1500 else 56
    return (f'<div style="position:absolute;left:70px;right:70px;bottom:{b}px;display:flex;align-items:center;justify-content:space-between;gap:24px;z-index:7">'
            f'<div style="{a("foco", .5)}font:600 26px/1.4 {SANS};color:#3A3000;max-width:600px">{E(txt)}</div>' + (selo_link(a) if link else '') + '</div>')

def doc(corpo, h):
    css = (f"@font-face{{font-family:'Public Sans';src:url('file://{FONTES}/PublicSans.ttf');font-weight:100 900}}"
           f"@font-face{{font-family:'Source Serif 4';src:url('file://{FONTES}/SourceSerif4.ttf');font-weight:200 900}}"
           f"body{{margin:0}}.f{{width:1080px;height:{h}px;position:relative;overflow:hidden;font-family:{SANS};color:{T}}}" + CSS)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="f">{corpo}</div></body></html>'

def area(h):
    return (f'position:absolute;left:{62 if h > 1500 else 70}px;right:{62 if h > 1500 else 70}px;top:{220 if h > 1500 else 180}px;bottom:{270 if h > 1500 else 170}px;'
            f'display:flex;flex-direction:column;justify-content:center;z-index:4;{"zoom:1.12;" if h > 1500 else ""}')

def feed_html(c, r):
    h = 1350; a = A()
    return doc(fundo(h) + topo(a, h) + f'<div style="{area(h)}">{CENAS[c["tipo"]](c, a, h)}</div>' + rodape(c.get('fonte', r['fonte']), a, h), h)

def dur(c):
    if c['tipo'] in ('capa',): return ABRE
    if c['tipo'] == 'final': return FINAL
    if c['tipo'] == 'conversa': return 5.5
    txt = json.dumps(c, ensure_ascii=False)
    return 5.0 if len(txt) > 260 else 4.0

def reels_html(r):
    h = 1920; blocos = []; t0 = 0.0
    for k, c in enumerate(r['reels']):
        dd = dur(c); ult = k == len(r['reels']) - 1
        anim = [f'show 0s linear {t0:.2f}s both']
        if c['tipo'] not in ('capa', 'final') and not ult: anim.append(f'sair .4s ease-in {t0 + dd - .4:.2f}s forwards')
        if not ult: anim.append(f'hide 0s linear {t0 + dd:.2f}s forwards')
        a = A(t0)
        corpo = CENAS[c['tipo']](c, a, h)
        extra = rodape(r.get('rodape', r['fonte']), a, h) if ult else ''
        blocos.append(f'<div style="position:absolute;inset:0;visibility:hidden;animation:{",".join(anim)};z-index:4"><div style="{area(h)}">{corpo}</div>{extra}</div>')
        t0 += dd
    return doc(fundo(h) + topo(A(0), h) + ''.join(blocos), h), t0

async def gerar(r, saida, so_feed=False, fps=30):
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True); tmp = tempfile.mkdtemp()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350})
        for k, c in enumerate(r['feed']):
            open(os.path.join(tmp, f'f{k}.html'), 'w').write(feed_html(c, r))
            await pg.goto('file://' + os.path.join(tmp, f'f{k}.html')); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(saida, f'{k + 1}-feed.jpg'), type='jpeg', quality=92)
        if r.get('story'):
            ps = await b.new_page(viewport={'width': 1080, 'height': 1920})
            for k, c in enumerate(r['story']):
                h = 1920; a = A()
                open(os.path.join(tmp, f's{k}.html'), 'w').write(doc(fundo(h) + topo(a, h) + f'<div style="{area(h)}">{CENAS[c["tipo"]](c, a, h)}</div>' + rodape(c.get('fonte', r['fonte']), a, h), h))
                await ps.goto('file://' + os.path.join(tmp, f's{k}.html')); await ps.wait_for_timeout(300)
                await ps.screenshot(path=os.path.join(saida, f'{k + 1}-story.jpg'), type='jpeg', quality=92)
        if not so_feed:
            html_, total = reels_html(r); open(os.path.join(tmp, 'v.html'), 'w').write(html_)
            pv = await b.new_page(viewport={'width': 1080, 'height': 1920})
            await pv.goto('file://' + os.path.join(tmp, 'v.html')); await pv.wait_for_timeout(500)
            os.makedirs(os.path.join(tmp, 'q'), exist_ok=True)
            for i in range(int(round(fps * total))):
                await pv.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / fps}}})")
                await pv.screenshot(path=os.path.join(tmp, 'q', f'f{i:04d}.jpg'), type='jpeg', quality=88)
        await b.close()
    if not so_feed:
        Image.open(os.path.join(tmp, 'q', f'f{int(fps * 2.4):04d}.jpg')).convert('RGB').save(os.path.join(saida, 'capa.jpg'), quality=92)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, 'q', 'f%04d.jpg'), '-i', TRILHA,
                        '-af', f'afade=t=out:st={total - 1.2:.2f}:d=1.2', '-c:a', 'aac', '-b:a', '192k', '-t', f'{total:.2f}',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(saida, 'reels.mp4')], check=True)
        print('duração', total)
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    asyncio.run(gerar(json.load(open(sys.argv[1])), sys.argv[2], '--so-feed' in sys.argv))
