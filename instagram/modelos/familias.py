#!/usr/bin/env python3
"""Famílias visuais da Clareia: um layout por tipo de assunto, com as mesmas cores e a mesma marca,
para que dê para saber do que a peça fala só de bater o olho (aprovado pelo dono em 21/10).

  pesquisa  fundo lavanda, placar com os dois números grandes e a barra com a faixa da margem de erro
  checagem  fundo escuro, a fala entre aspas e o carimbo com o selo do checador
  boato     fundo branco, o "print" do boato com o carimbo FALSO e o que é verdade
  agenda    fundo amarelo, a data grande num bloco de calendário
  plantao   fundo roxo com letreiro preto no topo, para atualizações do dia
  servico   fundo branco, passos numerados (como votar, prazos, onde ver)

Usado por pecas.py quando a especificação traz "familia" (em vez de "modelo"). Formatos: feed (1080x1350) e story (1080x1920).
Campos de cada família:
  pesquisa: instituto, divulgacao ("21/10"), flavio, lula (votos válidos), margem, amostra?, campo?, fonte, registro?, nota? (texto do quadro amarelo)
            ou grafico: tendencia | rodada | media | totais | margem (veja graficos.py; os números vêm de data/pesquisas.json)
  checagem: candidato, evento ("debate na Band (18/10)"), fala, selo ("NÃO É BEM ASSIM"), checador ("g1 Fato ou Fake"), fonte
  boato:    onde ("Circulou no X"), checado ("16/10"), boato, verdade, selo? ("FALSO"), fonte
  agenda:   dia_semana ("SEXTA"), dia ("23"), mes ("OUT"), titulo, hora?, itens:[{rotulo, texto}] (até 3), fonte
  plantao:  quando ("Quarta, 21/10 · atualizado às 11h"), titulo, destaque?, itens:[{rotulo, texto}] (até 3), fonte
  servico:  titulo, destaque?, passos:[{titulo, texto}] (até 4), fonte
"""
import os, sys, html
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import marca as M
E = html.escape
FONTES = os.path.join(AQUI, 'fontes'); MARCA_DIR = os.path.abspath(os.path.join(AQUI, '..', '..', 'marca'))
ROXO, AM, T, LAV, AZ, VM = '#3E2492', '#FFD43B', '#16181D', '#EEE8FA', '#1F4FA8', '#D62B2B'
SERIF, SANS = "'Source Serif 4',Georgia,serif", "'Public Sans',system-ui,sans-serif"
LOGO = {k: f'file://{MARCA_DIR}/clareia-eleicoes-{k}.svg' for k in ('claro', 'escuro', 'roxo')}
# cores de cada família: fundo, texto, texto suave, logo, cor do @, destaque
PALETA = {
 'pesquisa': dict(bg=LAV, fg=T, sub='#4A4458', logo='claro', arroba=ROXO, dest=ROXO),
 'checagem': dict(bg=T, fg='#fff', sub='#B5AFC4', logo='escuro', arroba='#C9C4D6', dest=AM),
 'boato':    dict(bg='#FFFFFF', fg=T, sub='#4A4458', logo='claro', arroba=ROXO, dest=ROXO),
 'agenda':   dict(bg=AM, fg=T, sub='#3A3000', logo='claro', arroba=T, dest=ROXO),
 'plantao':  dict(bg=ROXO, fg='#fff', sub='#D9CFF5', logo='roxo', arroba='#E2D9FA', dest=AM),
 'servico':  dict(bg='#FFFFFF', fg=T, sub='#3A3F49', logo='claro', arroba=ROXO, dest=ROXO),
}
TRILHAS = {   # trilhas sugeridas para o reels de cada família (video.py sorteia entre elas)
 'pesquisa': ['estrada', 'pulsar'], 'agenda': ['batuque', 'pulsar', 'funkpop'], 'servico': ['batuque', 'praca'],
 'engajamento': ['funkpop', 'batuque', 'tamborzao', 'praca'], 'plantao': ['jornal', 'pulso'], 'checagem': ['noite', 'jornal'], 'boato': ['noite'],
}
IC = {
 'pesquisa': '<path d="M4 20h16"/><rect x="5" y="11" width="3.2" height="6.5" rx="1"/><rect x="10.4" y="6.5" width="3.2" height="11" rx="1"/><rect x="15.8" y="9" width="3.2" height="8.5" rx="1"/>',
 'checagem': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3 20 20"/><path d="m7.6 10.6 2 2 3.6-3.8"/>',
 'boato': '<path d="M12 3.6 21 19.5H3z"/><path d="M12 9.6v4.4"/><circle cx="12" cy="16.9" r=".5"/>',
 'agenda': '<rect x="3.6" y="5" width="16.8" height="15" rx="2.4"/><path d="M3.6 10h16.8M8 3v4M16 3v4"/>',
 'plantao': '<path d="M6 9.5a6 6 0 0 1 12 0c0 6 2.6 7.8 2.6 7.8H3.4S6 15.5 6 9.5"/><path d="M10.2 20.2a2 2 0 0 0 3.6 0"/>',
 'servico': '<path d="M4 13.5h16v6.5H4z"/><path d="M8.2 13.5V5.2a1 1 0 0 1 1-1h5.6a1 1 0 0 1 1 1v8.3"/><path d="m10 8.8 1.6 1.6 2.6-2.8"/>',
}
NOME = {'pesquisa': 'PESQUISA', 'checagem': 'CHECAGEM', 'boato': 'BOATO DESMENTIDO', 'agenda': 'AGENDA', 'plantao': 'PLANTÃO', 'servico': 'SERVIÇO'}
CHIP = {'pesquisa': (T, AM, T), 'checagem': (AM, T, T), 'boato': (ROXO, '#fff', T), 'agenda': (T, AM, T), 'plantao': (AM, T, T), 'servico': ('#fff', ROXO, ROXO)}
PILL = {'pesquisa': (ROXO, '#fff', T), 'checagem': (AM, T, AM), 'boato': (ROXO, '#fff', T), 'agenda': (ROXO, '#fff', T), 'plantao': (AM, T, T), 'servico': (ROXO, '#fff', T)}
num = lambda v: (f'{float(v):.1f}'.rstrip('0').rstrip('.') if float(v) != int(float(v)) else str(int(float(v)))).replace('.', ',')

def ico(k, px, cor):
    return f'<svg width="{px}" height="{px}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{IC[k]}</svg>'
def chip(fam, txt=None):
    bg, fg, bd = CHIP[fam]
    return (f'<span style="display:inline-flex;align-items:center;gap:14px;background:{bg};color:{fg};border:4px solid {bd};border-radius:999px;'
            f'padding:12px 26px 12px 18px;font:900 30px/1 {SANS};letter-spacing:.12em">{ico(fam, 38, fg)}{E(txt or NOME[fam])}</span>')

def c_pesquisa(s, P, story):
    if s.get('grafico'):   # modelos com gráfico (graficos.py)
        import graficos
        return graficos.corpo(s, P, story, chip)
    f, l, mg = float(s['flavio']), float(s['lula']), float(s.get('margem') or 0)
    dif = abs(f - l)
    lado = lambda v, c, nome, al: (f'<div style="text-align:{al}"><div style="font:800 34px {SANS};color:{c}">{E(nome)}</div>'
                                   f'<div style="font:900 {136 if story else 160}px/1 {SERIF};color:{c};letter-spacing:-.04em">{num(v)}<span style="font-size:.48em">%</span></div></div>')
    faixa = (f'<i style="position:absolute;left:{50 - mg}%;width:{2 * mg}%;top:0;bottom:0;background:repeating-linear-gradient(45deg,rgba(255,255,255,.6) 0 10px,transparent 10px 20px)"></i>') if mg else ''
    barra = (f'<div style="position:relative;height:64px;border:4px solid {T};border-radius:999px;overflow:hidden;display:flex;background:#fff">'
             f'<i style="width:{f / (f + l) * 100:.2f}%;background:{AZ}"></i><i style="flex:1;background:{VM}"></i>{faixa}'
             f'<i style="position:absolute;left:50%;top:-4px;bottom:-4px;width:5px;margin-left:-2.5px;background:{T}"></i></div>'
             f'<div style="text-align:center;margin-top:14px;font:700 24px {SANS};color:#4A4458">'
             + (f'faixa listrada = margem de erro (±{num(mg)}) · linha = 50%' if mg else 'linha = 50%') + '</div>')
    meta = ' · '.join(x for x in ['Votos válidos', s.get('divulgacao') and f'divulgada em {s["divulgacao"]}', s.get('amostra') and f'{int(s["amostra"]):,} entrevistas'.replace(',', '.')] if x)
    if s.get('nota'): nota = s['nota']
    elif mg and dif <= 2 * mg: nota = f'Empate técnico: a diferença de {num(dif)} ponto{"s" if round(dif, 1) != 1 else ""} cabe na margem.'
    else: nota = f'Diferença de {num(dif)} ponto{"s" if round(dif, 1) != 1 else ""}, maior que a margem de erro.'
    corpo = (f'<div>{chip("pesquisa")}<div style="font:900 {112 if len(s["instituto"]) <= 14 else 84}px/1 {SERIF};margin-top:30px;letter-spacing:-.02em">{E(s["instituto"])}</div>'
             f'<div style="font:600 34px/1.35 {SANS};color:{P["sub"]};margin-top:14px">{E(meta)}</div></div>'
             f'<div style="background:#fff;border:5px solid {T};border-radius:36px;box-shadow:12px 12px 0 {ROXO};padding:40px 44px 34px">'
             f'<div style="display:flex;justify-content:space-between">{lado(f, AZ, "Flávio Bolsonaro", "left")}{lado(l, VM, "Lula", "right")}</div>'
             f'<div style="margin-top:26px">{barra}</div></div>'
             f'<div style="background:{AM};border:4px solid {T};border-radius:24px;padding:22px 28px;font:800 36px/1.3 {SANS}">{E(nota)}</div>')
    fonte = s.get('fonte', '') + (f' Registro {s["registro"]}.' if s.get('registro') else '')
    return corpo, fonte

def c_checagem(s, P, story):
    corpo = (f'<div>{chip("checagem")}<div style="font:700 32px {SANS};color:{P["sub"]};margin-top:30px">{E(s["candidato"])} · {E(s.get("evento", ""))}</div></div>'
             f'<div style="position:relative;padding:{90 if story else 70}px 0 0 20px">'
             f'<div style="position:absolute;left:-14px;top:-40px;font:900 260px/1 {SERIF};color:{AM}">“</div>'
             f'<div style="font:800 {80 if len(s["fala"]) < 90 else 66}px/1.14 {SERIF};color:#fff;position:relative">{E(s["fala"])}</div>'
             f'<div style="font:500 26px {SANS};color:{P["sub"]};margin-top:18px">Resumo da fala, como registrado pela checagem.</div></div>'
             f'<div style="display:flex;justify-content:flex-end;padding:30px 20px"><div style="transform:rotate(-7deg);border:9px solid {AM};border-radius:26px;padding:22px 40px 18px;text-align:center;box-shadow:0 0 0 6px {T},0 0 0 10px {AM}">'
             f'<div style="font:900 {82 if len(s["selo"]) <= 16 else 62}px/1.05 {SANS};color:{AM};letter-spacing:.02em;text-transform:uppercase">{E(s["selo"])}</div>'
             f'<div style="font:800 28px {SANS};color:#fff;margin-top:12px;letter-spacing:.1em;text-transform:uppercase">Selo do {E(s["checador"])}</div></div></div>')
    return corpo, s.get('fonte', '')

def c_boato(s, P, story):
    linhas = ''.join(f'<i style="display:block;height:18px;border-radius:9px;background:#D9D4E4;width:{w}%;margin-top:14px"></i>' for w in (92, 78, 60))
    post = (f'<div style="position:relative;background:#F4F2F8;border:3px dashed #9A93AC;border-radius:30px;padding:34px 36px 70px;margin-bottom:40px">'
            f'<div style="display:flex;align-items:center;gap:18px"><i style="width:64px;height:64px;border-radius:50%;background:#CFC8DD"></i>'
            f'<div style="flex:1"><i style="display:block;height:18px;width:46%;border-radius:9px;background:#CFC8DD"></i><i style="display:block;height:14px;width:28%;border-radius:7px;background:#E1DCEA;margin-top:10px"></i></div></div>'
            f'<div style="font:700 44px/1.28 {SANS};color:#5C566B;margin-top:26px">"{E(s["boato"])}"</div>{linhas}'
            f'<div style="position:absolute;right:-22px;bottom:-56px;transform:rotate(-9deg);background:#fff;border:10px solid {ROXO};border-radius:22px;padding:12px 36px;'
            f'box-shadow:10px 10px 0 {AM};font:900 104px/1 {SANS};color:{ROXO};letter-spacing:.04em;text-transform:uppercase">{E(s.get("selo", "Falso"))}</div></div>')
    corpo = (f'<div>{chip("boato")}<div style="font:700 32px {SANS};color:{P["sub"]};margin-top:26px">{E(s.get("onde", "Circulou nas redes"))} · checado em {E(s.get("checado", ""))}</div></div>'
             + post +
             f'<div style="border-left:12px solid {AM};padding:6px 0 6px 30px"><div style="font:900 30px {SANS};letter-spacing:.1em;color:{ROXO}">O QUE É VERDADE</div>'
             f'<div style="font:600 38px/1.35 {SANS};margin-top:10px">{E(s["verdade"])}</div></div>')
    return corpo, s.get('fonte', '')

def linha_item(k, v, P, borda):
    return (f'<div style="display:flex;gap:24px;padding:24px 0;border-top:4px solid {borda}"><b style="flex:none;width:250px;font:900 30px/1.3 {SANS};letter-spacing:.08em;text-transform:uppercase">{E(k)}</b>'
            f'<span style="font:600 36px/1.35 {SANS}">{E(v)}</span></div>')

def c_agenda(s, P, story):
    tile = (f'<div style="flex:none;width:300px;background:#fff;border:6px solid {T};border-radius:34px;box-shadow:12px 12px 0 {T};overflow:hidden;text-align:center">'
            f'<div style="background:{ROXO};color:#fff;font:900 40px/1 {SANS};letter-spacing:.14em;padding:22px 0;text-transform:uppercase">{E(s["dia_semana"])}</div>'
            f'<div style="font:900 190px/1 {SERIF};padding:18px 0 0;letter-spacing:-.04em">{E(str(s["dia"]))}</div><div style="font:900 40px/1 {SANS};letter-spacing:.14em;padding:6px 0 26px;text-transform:uppercase">{E(s["mes"])}</div></div>')
    hora = f'<div style="font:800 44px {SANS};margin-top:20px;background:{T};color:{AM};display:inline-block;padding:8px 20px;border-radius:14px">{E(s["hora"])}</div>' if s.get('hora') else ''
    corpo = (f'<div>{chip("agenda")}</div>'
             f'<div style="display:flex;gap:46px;align-items:center">{tile}<div><div style="font:900 {98 if len(s["titulo"]) < 26 else 78}px/1.02 {SERIF};letter-spacing:-.02em">{E(s["titulo"])}</div>{hora}</div></div>'
             f'<div>{"".join(linha_item(i["rotulo"], i["texto"], P, T) for i in s.get("itens", [])[:3])}</div>')
    return corpo, s.get('fonte', '')

def c_plantao(s, P, story):
    itens = ''.join(f'<div style="display:flex;gap:22px;align-items:flex-start;background:#2E1B70;border-left:12px solid {AM};border-radius:18px;padding:24px 28px">'
                    f'<b style="flex:none;font:900 30px {SANS};color:{AM};letter-spacing:.08em;width:190px;text-transform:uppercase">{E(i["rotulo"])}</b><span style="font:600 34px/1.35 {SANS}">{E(i["texto"])}</span></div>'
                    for i in s.get('itens', [])[:3])
    fs = 112 if len(s['titulo'] + s.get('destaque', '')) < 50 else 92
    corpo = (f'<div><div style="font:900 {fs}px/1.02 {SERIF};letter-spacing:-.02em">{E(s["titulo"])}</div>'
             + (f'<div style="font:900 {fs}px/1.02 {SERIF};color:{AM};letter-spacing:-.02em">{E(s["destaque"])}</div>' if s.get('destaque') else '') + '</div>'
             f'<div style="display:flex;flex-direction:column;gap:18px">{itens}</div>')
    return corpo, s.get('fonte', '')

def c_servico(s, P, story):
    passo = lambda n, p: (f'<div style="display:flex;gap:34px;align-items:flex-start"><span style="flex:none;width:104px;height:104px;border-radius:50%;background:{ROXO};color:#fff;'
                          f'display:grid;place-items:center;font:900 60px/1 {SERIF};box-shadow:6px 6px 0 {AM}">{n}</span>'
                          f'<div><div style="font:900 50px/1.1 {SERIF}">{E(p["titulo"])}</div><div style="font:500 34px/1.4 {SANS};color:#3A3F49;margin-top:8px">{E(p["texto"])}</div></div></div>')
    corpo = (f'<div>{chip("servico")}<div style="font:900 104px/1.02 {SERIF};margin-top:30px;letter-spacing:-.02em">{E(s["titulo"])}'
             + (f'<br><span style="color:{ROXO}">{E(s["destaque"])}</span>' if s.get('destaque') else '') + '</div></div>'
             f'<div style="display:flex;flex-direction:column;gap:40px">{"".join(passo(k + 1, p) for k, p in enumerate(s.get("passos", [])[:4]))}</div>')
    return corpo, s.get('fonte', '')

CORPOS = {'pesquisa': c_pesquisa, 'checagem': c_checagem, 'boato': c_boato, 'agenda': c_agenda, 'plantao': c_plantao, 'servico': c_servico}

def pagina(s, formato):
    fam = s['familia']; P = PALETA[fam]; story = formato == 'story'
    w, h = 1080, (1920 if story else 1350)
    corpo, fonte = CORPOS[fam](s, P, story)
    pt, pb = (190, 230) if story else (84, 72)
    letreiro = ''
    if fam == 'plantao':
        letreiro = (f'<div style="position:absolute;left:0;right:0;top:0;height:{170 if story else 92}px;background:{T};display:flex;align-items:flex-end;gap:26px;padding:0 40px {22 if story else 18}px">'
                    f'<span style="display:inline-flex;align-items:center;gap:12px;background:{AM};color:{T};border-radius:999px;padding:10px 22px;font:900 30px/1 {SANS};letter-spacing:.12em">'
                    f'<i style="width:16px;height:16px;border-radius:50%;background:{ROXO}"></i>PLANTÃO</span>'
                    f'<span style="font:700 28px {SANS};color:#fff;white-space:nowrap">{E(s.get("quando", ""))}</span></div>')
        pt += 100 if story else 120
    pbg, pfg, pbd = PILL[fam]
    topo = (f'<div style="display:flex;justify-content:space-between;align-items:center"><img src="{LOGO[P["logo"]]}" style="height:86px">'
            f'<span style="font:800 28px {SANS};color:{P["arroba"]}">{M.ARROBA}</span></div>')
    pe = (f'<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:30px"><span style="font:500 24px/1.4 {SANS};color:{P["sub"]};max-width:640px">{E(fonte)}</span>'
          f'<span style="flex:none;background:{pbg};color:{pfg};border:4px solid {pbd};box-shadow:6px 6px 0 {pbd};border-radius:999px;padding:16px 30px;font:900 34px {SANS}">Link na bio</span></div>')
    css = (f"@font-face{{font-family:'Public Sans';src:url('file://{FONTES}/PublicSans.ttf');font-weight:100 900}}"
           f"@font-face{{font-family:'Source Serif 4';src:url('file://{FONTES}/SourceSerif4.ttf');font-weight:200 900}}body{{margin:0}}")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
            f'<div style="width:{w}px;height:{h}px;background:{P["bg"]};color:{P["fg"]};font-family:{SANS};position:relative;overflow:hidden;box-sizing:border-box;'
            f'padding:{pt}px 76px {pb}px;display:flex;flex-direction:column">{letreiro}{topo}'
            f'<div id="miolo" style="flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;padding:30px 0"><div id="conteudo" style="display:flex;flex-direction:column;gap:{56 if story else 40}px;zoom:{1.2 if story else 1}">{corpo}</div></div>'
            f'{pe}</div></body></html>'), w, h
