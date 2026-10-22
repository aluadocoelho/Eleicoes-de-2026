#!/usr/bin/env python3
"""Gera o reels da Clareia (1080x1920, com a trilha lo-fi) a partir de um JSON.

Ritmo (pedido do dono, 20/10): abertura e tela final de 3 s, sem animação de saída; telas de conteúdo de 4 s
(pouco texto) ou 5 s (mais de 150 caracteres), com no máximo 2 itens por tela. O texto entra "em foco"
(desfoque para nítido), selos e botões com elástico, cartões em sequência; telas de conteúdo saem com desfoque.
A duração total sai disso (em geral 14 a 22 s).

Uso:  python3 instagram/modelos/video.py especificacao.json pasta_de_saida/

Especificação (todos os textos curtos; cada item de "itens" tem rotulo, texto e lado; cena2 aceita até 4 itens, cena3 até 2):
{
 "tema": "plantao" | "verita",          # plantao = preto/amarelo/vermelho; verita (ou clareia) = roxo
 "familia": "pesquisa" | "checagem" | "boato" | "agenda" | "plantao" | "servico" | "engajamento",   # opcional (preferível): cores da família visual (familias.py) e trilha que combina com o assunto
 "selo": "PLANTÃO" | "ATUALIZAÇÃO" | "NOVA PESQUISA" | "CHECAGEM" ... (evite "URGENTE": tom sóbrio passa mais confiança),
 "abertura": {"chip": "Plantão Clareia · Eleições 2026", "titulo": "Quebra de", "destaque": "sigilo.", "sub": "O que pode acontecer nesta terça, 20/10."},
 "cena2": {"chip": "Terça, 20/10 · TSE", "titulo": "Lula diz que entrega...", "destaque": "quebrar seus sigilos.", "itens": [{"rotulo": "O que entra", "texto": "...", "lado": "lula"}]},
 "cena3": {"chip": "E o outro lado?", "itens": [{"rotulo": "Flávio Bolsonaro", "texto": "...", "lado": "flavio"}], "chamada": "Acompanhe", "chamada_destaque": "ao longo do dia."},
 "rodape": "Fontes: Poder360 e CNN Brasil (19/10)",
 "grafico": {"grafico": "rodada"},   # opcional, só na família pesquisa: tela de 5 s com um gráfico de graficos.py (mesmos campos: grafico, instituto?, ate?, dias?), depois da cena2
 "trilha": "noite"   # opcional: praca, noite ou jornal (ou verita-lofi-20s.wav / verita-lofi-media-20s.wav); sem o campo, sorteia entre praca, noite e jornal
}
"lado": "lula" (vermelho), "flavio" (azul) ou "neutro" (amarelo). Gera reels.mp4 e capa.jpg.
Precisa de Playwright + Chromium, Pillow e ffmpeg. As trilhas estão a 90 bpm: telas de 3, 4 e 5 s trocam sempre numa colcheia.
"""
import sys, os, json, asyncio, tempfile, shutil, subprocess, html
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import pecas as P
from pecas import AMARELO, AZUL, VERM, TINTA, SERIF, SANS
E = html.escape
TRILHAS_DIR = os.path.join(AQUI, 'trilhas')
ROTACAO = ['praca', 'noite', 'jornal']   # trilhas aprovadas pelo dono (20/10/2026)
def escolher_trilha(spec):
    """Usa spec["trilha"] (nome curto, ex. "noite", ou arquivo); senão sorteia uma das trilhas de ROTACAO (a escolha depende do conteúdo, então cada reels tende a sair com uma diferente)."""
    import glob, hashlib, random
    nomes = [os.path.join(TRILHAS_DIR, f'clareia-lofi-{n}-30s.wav') for n in ROTACAO]
    nomes = [n for n in nomes if os.path.exists(n)]
    pedida = spec.get('trilha')
    if pedida:
        for n in sorted(glob.glob(os.path.join(TRILHAS_DIR, '*.wav'))):
            if os.path.basename(n) in (pedida, f'clareia-lofi-{pedida}-30s.wav', f'{pedida}.wav'): return n
    fam = spec.get('familia')
    if fam:
        import familias
        cands = []
        for n in familias.TRILHAS.get(fam, []):
            for f in (f'clareia-lofi-{n}-30s.wav', f'clareia-{n}-30s.wav'):
                if os.path.exists(os.path.join(TRILHAS_DIR, f)): cands.append(os.path.join(TRILHAS_DIR, f)); break
        if cands: nomes = cands
    semente = hashlib.md5(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return random.Random(semente).choice(nomes) if nomes else None
COR = {'lula': VERM, 'flavio': AZUL, 'neutro': AMARELO}

# ---------- ritmo e animações ----------
# Telas de abertura e final: 3 s, sem animação de saída. Telas de conteúdo: 4 s com pouco texto,
# 5 s com bastante (mais de LIMITE caracteres), no máximo 2 itens por tela, e saem com desfoque.
# Linguagem visual da Clareia: o texto "entra em foco" (desfoque -> nítido, como luz clareando),
# selos e botões entram com elástico, cartões sobem em sequência.
ABERTURA = FINAL = 3.0
CURTA, LONGA, LIMITE = 4.0, 5.0, 150
def item(it, d, fundo_item, txt_cor, C=None):
    C = C or {}
    cor = COR.get(it.get('lado', 'neutro'), AMARELO)
    if cor == AMARELO and C.get('acc'): cor = C['acc']
    # caixa padrão da Clareia (regra do dono, 21/10): fundo branco, borda escura e sombra dura; o lado aparece só no pontinho colorido
    sombra = C.get('sombra', AMARELO)
    ponto = f'<i style="flex:none;width:30px;height:30px;border-radius:50%;background:{cor};border:3px solid {TINTA}"></i>' if it.get('lado') in ('lula', 'flavio') else ''
    return (f'<div class="card" style="animation-delay:{d:.2f}s;background:#FFFFFF;color:{TINTA};border:5px solid {TINTA};border-radius:30px;box-shadow:12px 12px 0 {sombra};padding:32px 36px;display:flex;flex-direction:column;gap:14px">'
            f'<div style="display:flex;align-items:center;gap:14px;font-size:34px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:{P.ROXO}">{ponto}{E(it["rotulo"])}</div>'
            f'<div style="font-size:50px;line-height:1.32;color:{TINTA}">{E(it["texto"])}</div></div>')

def telas(s):
    """Divide o roteiro em telas: [(tipo, dados, duração)]."""
    out = [('abertura', s['abertura'], ABERTURA)]
    for nome in ('cena2', 'cena3'):
        c = s.get(nome) or {}
        its = (c.get('itens') or [])[:4]
        grupos = [its[i:i + 2] for i in range(0, len(its), 2)] or ([[]] if nome == 'cena2' else [])
        for k, g in enumerate(grupos):
            cab = (c.get('chip', ''), c.get('titulo', '') if k == 0 else '', c.get('destaque', '') if k == 0 else '')
            chars = sum(len(x) for x in cab) + sum(len(it.get('rotulo', '')) + len(it.get('texto', '')) for it in g)
            out.append(('conteudo', (cab, g), LONGA if chars > LIMITE else CURTA))
        if nome == 'cena2' and s.get('grafico'):
            out.append(('grafico', s['grafico'], LONGA))
    out.append(('final', s.get('cena3') or {}, FINAL))
    return out

def duracao(s):
    return sum(d for _, _, d in telas(s))

CSS = """
.f{width:1080px;height:1920px;color:#fff;position:relative;overflow:hidden}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:250px 80px 300px;box-sizing:border-box;visibility:hidden}
@keyframes show{from{visibility:hidden}to{visibility:visible}}
@keyframes hide{to{visibility:hidden}}
@keyframes foco{from{opacity:0;filter:blur(18px);transform:translateY(26px) scale(.985)}to{opacity:1;filter:blur(0);transform:none}}
@keyframes surge{from{opacity:0}to{opacity:1}}
@keyframes card{from{opacity:0;filter:blur(10px);transform:translateY(70px)}to{opacity:1;filter:blur(0);transform:none}}
@keyframes elastico{0%{opacity:0;transform:scale(.4) rotate(-6deg)}55%{opacity:1;transform:scale(1.1) rotate(-3deg)}75%{transform:scale(.96) rotate(-3deg)}100%{transform:scale(1) rotate(-3deg)}}
@keyframes sair{to{opacity:0;filter:blur(14px);transform:scale(1.015)}}
@keyframes logo{0%{transform:scale(.4);opacity:0}70%{transform:scale(1.08);opacity:1}100%{transform:scale(1)}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
@keyframes tapeL{from{transform:translateX(-120%) rotate(-4deg)}to{transform:translateX(0) rotate(-4deg)}}
@keyframes tapeR{from{transform:translateX(120%) rotate(5deg)}to{transform:translateX(0) rotate(5deg)}}
.foco{animation:foco .7s cubic-bezier(.2,.8,.3,1) both}
.surge{animation:surge .6s ease-out both}
.card{animation:card .65s cubic-bezier(.2,.8,.3,1) both}
.elastico{animation:elastico .75s cubic-bezier(.3,1.4,.5,1) both}
"""

# paletas das famílias visuais (ver familias.py): fundo, cartão, texto, texto suave, destaque, borda, selo e logo
LAV = '#EEE8FA'
FAM = {
 'pesquisa': dict(bg=LAV, fi='#FFFFFF', fg=TINTA, sub='#4A4458', acc=P.ROXO, bd=TINTA, sombra=P.ROXO, selo=(TINTA, AMARELO, P.ROXO), logo='claro', claro=True),
 'checagem': dict(bg=TINTA, fi='#22252C', fg='#FFFFFF', sub='#B5AFC4', acc=AMARELO, bd='#3A3E48', selo=(AMARELO, TINTA, '#FFFFFF'), logo='escuro'),
 'boato':    dict(bg='#FFFFFF', fi='#F4F2F8', fg=TINTA, sub='#4A4458', acc=P.ROXO, bd='#CFC8DD', sombra=P.ROXO, selo=(P.ROXO, '#FFFFFF', AMARELO), logo='claro', claro=True),
 'agenda':   dict(bg=AMARELO, fi='#FFFFFF', fg=TINTA, sub='#3A3000', acc=P.ROXO, bd=TINTA, sombra=TINTA, selo=(TINTA, AMARELO, P.ROXO), logo='claro', claro=True),
 'plantao':  dict(bg=P.ROXO, fi='#2E1B70', fg='#FFFFFF', sub='#D9CFF5', acc=AMARELO, bd='#5B45A8', selo=(AMARELO, TINTA, TINTA), logo='roxo'),
 'servico':  dict(bg='#FFFFFF', fi=LAV, fg=TINTA, sub='#3A3F49', acc=P.ROXO, bd=P.ROXO, sombra=P.ROXO, selo=(P.ROXO, '#FFFFFF', AMARELO), logo='claro', claro=True),
 'engajamento': dict(bg=P.ROXO, fi='#2E1B70', fg='#FFFFFF', sub='#E2D9FA', acc=AMARELO, bd='#5B45A8', selo=(AMARELO, TINTA, TINTA), logo='roxo'),
}
def logo_img(variante, alt=115):
    caminho = os.path.abspath(os.path.join(AQUI, '..', '..', 'marca', f'clareia-eleicoes-{variante}.svg'))
    return f'<img src="file://{caminho}" alt="Clareia Eleições" style="height:{alt}px;width:auto;display:block">'

def pagina(s):
    C = FAM.get(s.get('familia'))
    plantao = s.get('tema', 'plantao') == 'plantao' and not C
    BG = TINTA if plantao else P.ROXO
    FI = '#22252C' if plantao else '#2E1B70'
    SUB = '#C9CBD2' if plantao else '#E2D9FA'
    FG, ACC = '#FFFFFF', AMARELO
    SELO_BG, SELO_FG, SELO_SH = VERM, '#FFFFFF', AMARELO
    if C:
        BG, FI, SUB, FG, ACC = C['bg'], C['fi'], C['sub'], C['fg'], C['acc']
        SELO_BG, SELO_FG, SELO_SH = C['selo']
    TAPE = f'repeating-linear-gradient(-45deg,{AMARELO} 0 46px,{BG} 46px 92px)'
    def tit(t, dd):
        if not dd: return E(t)
        return (E(t) + '<br>' if t else '') + f'<span style="color:{ACC}">{E(dd)}</span>'
    blocos, t0 = [], 0.0
    for tipo, dados, dur in telas(s):
        anim = [f'show 0s linear {t0:.2f}s both']
        if tipo == 'conteudo': anim.append(f'sair .45s ease-in {t0 + dur - .45:.2f}s forwards')
        if tipo != 'final': anim.append(f'hide 0s linear {t0 + dur:.2f}s forwards')
        vis = 'animation:' + ','.join(anim)
        d = lambda x, t0=t0: f'{t0 + x:.2f}'
        if tipo == 'abertura':
            a = dados; selo = s.get('selo', 'PLANTÃO')
            fita = (f'<div style="position:absolute;left:-80px;right:-80px;top:300px;height:130px;background:{TAPE};animation:tapeL .6s cubic-bezier(.2,.8,.3,1) {d(.05)}s both"></div>'
                    f'<div style="position:absolute;left:-80px;right:-80px;bottom:330px;height:130px;background:{TAPE};animation:tapeR .6s cubic-bezier(.2,.8,.3,1) {d(.2)}s both"></div>') if plantao else ''
            blocos.append(
                f'<div class="sc" style="{vis};align-items:flex-start">{fita}'
                f'<div style="position:relative;display:flex;flex-direction:column;gap:36px;width:100%">'
                f'<div class="elastico" style="animation-delay:{d(.15)}s;align-self:flex-start;display:inline-flex;align-items:center;gap:22px;background:{SELO_BG};color:{SELO_FG};border:4px solid #000;box-shadow:12px 12px 0 {SELO_SH};border-radius:999px;padding:22px 46px;font-size:{96 if len(selo) <= 9 else 70}px;font-weight:900;letter-spacing:.06em">'
                f'<i style="width:40px;height:40px;border-radius:50%;background:{SELO_FG};display:block;animation:blink 1s steps(2) {d(.8)}s infinite"></i>{E(selo)}</div>'
                f'<div class="foco" style="animation-delay:{d(.55)}s;font-size:40px;font-weight:900;letter-spacing:.08em;color:{ACC};text-transform:uppercase">{E(a.get("chip", "Clareia · Eleições 2026"))}</div>'
                f'<h1 class="foco" style="animation-delay:{d(.75)}s;margin:0;font-family:{SERIF};font-weight:800;font-size:136px;line-height:.98;letter-spacing:-.03em">{tit(a["titulo"], a.get("destaque"))}</h1>'
                f'<div class="surge" style="animation-delay:{d(1.25)}s;font-size:50px;line-height:1.35;color:{SUB}">{E(a.get("sub", ""))}</div>'
                f'</div></div>')
        elif tipo == 'conteudo':
            (chip, tt, dest), g = dados
            tem_tit = bool(tt or dest)
            cards = ''.join(item(it, t0 + (.75 if tem_tit else .4) + .35 * i, FI, '#F2F2F4' if FG == '#FFFFFF' else FG, C) for i, it in enumerate(g))
            titulo = (f'<h2 class="foco" style="animation-delay:{d(.3)}s;margin:0 0 50px;font-family:{SERIF};font-weight:800;font-size:{104 if len(tt + dest) < 45 else 90}px;line-height:1.02;letter-spacing:-.025em">{tit(tt, dest)}</h2>') if tem_tit else ''
            blocos.append(
                f'<div class="sc" style="{vis}">'
                f'<div class="foco" style="animation-delay:{d(.1)}s;font-size:38px;font-weight:900;letter-spacing:.08em;color:{ACC};text-transform:uppercase;margin-bottom:30px">{E(chip)}</div>'
                f'{titulo}<div style="display:flex;flex-direction:column;gap:30px">{cards}</div></div>')
        elif tipo == 'grafico':
            import graficos
            titulo_g, meta, graf, nota, _ = graficos.GRAFICOS[dados['grafico']](dados, graficos.carregar())
            blocos.append(
                f'<div class="sc" style="{vis};padding-left:56px;padding-right:56px">'
                f'<div class="foco" style="animation-delay:{d(.1)}s;font-size:38px;font-weight:900;letter-spacing:.08em;color:{ACC};text-transform:uppercase;margin-bottom:24px">{E(dados.get("chip", "Pesquisas"))}</div>'
                f'<h2 class="foco" style="animation-delay:{d(.3)}s;margin:0 0 14px;font-family:{SERIF};font-weight:800;font-size:{92 if len(titulo_g) < 26 else 78}px;line-height:1.02;letter-spacing:-.025em">{E(dados.get("titulo") or titulo_g)}</h2>'
                f'<div class="surge" style="animation-delay:{d(.5)}s;font-size:30px;line-height:1.35;color:{SUB};margin-bottom:40px">{E(meta)}</div>'
                f'<div class="card" style="animation-delay:{d(.7)}s;background:#fff;border:5px solid {TINTA};border-radius:36px;box-shadow:12px 12px 0 {P.ROXO};padding:36px 44px 30px;color:{TINTA}">{graf}</div>'
                f'<div class="elastico" style="animation-delay:{d(1.6)}s;margin-top:44px;background:{AMARELO};color:{TINTA};border:4px solid {TINTA};border-radius:24px;padding:24px 30px;font-size:38px;font-weight:800;line-height:1.3;transform:rotate(0)">{E(dados.get("nota") or nota)}</div></div>')
        else:
            c3 = dados
            blocos.append(
                f'<div class="sc" style="{vis}">'
                f'<div class="foco" style="animation-delay:{d(.1)}s;font-family:{SERIF};font-weight:800;font-size:110px;line-height:1.02;letter-spacing:-.025em;margin-bottom:56px">{tit(c3.get("chamada", "Acompanhe no site"), c3.get("chamada_destaque"))}</div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;gap:24px">'
                f'<div class="surge" style="animation-delay:{d(.6)}s;font-size:30px;color:{SUB};max-width:560px;line-height:1.4">{E(s.get("rodape", ""))}</div>'
                f'<div class="elastico" style="animation-delay:{d(.45)}s;background:{AMARELO if not (C and C.get("claro")) else P.ROXO};color:{"#1A1500" if not (C and C.get("claro")) else "#FFFFFF"};border:3px solid #000;box-shadow:8px 8px 0 {VERM if not C else TINTA};border-radius:24px;padding:24px 34px;font-size:46px;font-weight:900;white-space:nowrap">Link na bio</div>'
                f'</div></div>')
        t0 += dur
    fontes = (f"@font-face{{font-family:'Public Sans';src:url('file://{P.FONTES}/PublicSans.ttf');font-weight:100 900}}"
              f"@font-face{{font-family:'Source Serif 4';src:url('file://{P.FONTES}/SourceSerif4.ttf');font-weight:200 900}}")
    topo = (f'<div style="position:absolute;left:0;right:0;top:0;display:flex;height:22px;z-index:5"><div style="flex:1;background:{AZUL}"></div><div style="flex:1;background:{VERM}"></div></div>'
            f'<svg style="position:absolute;right:-200px;bottom:120px;opacity:{.08 if C and C.get("claro") else .10};z-index:0" width="700" height="700" viewBox="0 0 140 140">{P.M.simbolo(P.ROXO if C and C.get("claro") else "#fff")}</svg>'
            f'<div style="position:absolute;left:80px;right:80px;top:120px;display:flex;align-items:center;justify-content:space-between;z-index:6">'
            f'<div style="animation:logo .6s cubic-bezier(.2,.9,.3,1.3) 0s both;transform-origin:left center">{logo_img(C["logo"]) if C else P.assinatura(50)}</div>'
            f'<span class="surge" style="animation-delay:.3s;font-size:30px;font-weight:800;color:{SUB}">{P.M.ARROBA}</span></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{fontes}body{{margin:0}}{CSS}'
            f'.f{{background:{BG};color:{FG};font-family:{SANS}}}</style></head><body><div class="f">{topo}{"".join(blocos)}</div></body></html>')

async def gerar(spec, saida, fps=30, dur=None):
    dur = dur or duracao(spec)
    from playwright.async_api import async_playwright
    from PIL import Image
    os.makedirs(saida, exist_ok=True)
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, 'v.html'), 'w') as f: f.write(pagina(spec))
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        await pg.goto('file://' + os.path.join(tmp, 'v.html')); await pg.wait_for_timeout(500)
        for i in range(int(round(fps * dur))):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / fps}}})")
            await pg.screenshot(path=os.path.join(tmp, f'f{i:04d}.jpg'), type='jpeg', quality=90)
        await b.close()
    Image.open(os.path.join(tmp, f'f{int(fps * 2.6):04d}.jpg')).convert('RGB').save(os.path.join(saida, 'capa.jpg'), quality=92)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(tmp, 'f%04d.jpg')]
    TRILHA = escolher_trilha(spec); print('trilha:', os.path.basename(TRILHA) if TRILHA else None)
    if TRILHA and os.path.exists(TRILHA): cmd += ['-i', TRILHA, '-af', f'afade=t=out:st={max(0, dur - 1.2):.2f}:d=1.2', '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.2f}']
    cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-movflags', '+faststart', os.path.join(saida, 'reels.mp4')]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return ['reels.mp4', 'capa.jpg']

if __name__ == '__main__':
    print(asyncio.run(gerar(json.load(open(sys.argv[1])), sys.argv[2])))
