#!/usr/bin/env python3
"""Vigia do site: abre a página como um visitante (celular e computador, em pt, en e es) e falha se algo estiver quebrado.

Confere: erros de JavaScript; cada aba abre e mostra conteúdo; nenhuma camada fixa cobrindo a tela sem ter sido aberta;
nada vazando para os lados no celular; menu inteiro no computador; selos das checagens preenchidos; bolinhas de vídeo;
dados atualizados (status com menos de 4 horas, entre 8h e 23h de Brasília).

Uso: python3 scripts/teste_site.py [URL]   (padrão: https://clareiaeleicoes.com.br)
     SITE_LOCAL=pasta para servir uma cópia local (o teste sobe um servidor em http://localhost:8799).
Grava capturas em teste-site/ e o resumo em teste-site/resultado.md. Sai com código 1 se houver falha.
"""
import asyncio, os, sys, json, datetime as dt, subprocess, time
from playwright.async_api import async_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'https://clareiaeleicoes.com.br').rstrip('/')
OUT = 'teste-site'; os.makedirs(OUT, exist_ok=True)
ABAS = ['inicio', 'aovivo', 'pesquisas', 'redes', 'campanha', 'checagem', 'verificar', 'sobre']
FALHAS, AVISOS = [], []
D3_LOCAL = os.environ.get('D3_LOCAL')   # caminho de um d3.min.js, para testar sem internet

def falha(msg): FALHAS.append(msg); print('FALHA:', msg)
def aviso(msg): AVISOS.append(msg); print('aviso:', msg)

COBERTURA = """() => {  // camadas fixas grandes e visíveis sem diálogo aberto de propósito
  const W = innerWidth, H = innerHeight, out = [];
  for (const e of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(e);
    if (cs.position !== 'fixed' || cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    const r = e.getBoundingClientRect(); const area = Math.max(0, Math.min(r.right, W) - Math.max(r.left, 0)) * Math.max(0, Math.min(r.bottom, H) - Math.max(r.top, 0));
    if (area > W * H * .4) out.push((e.id ? '#' + e.id : e.tagName) + '.' + String(e.className).split(' ')[0]);
  }
  return [...new Set(out)].slice(0, 5).concat(out.length > 5 ? [`(${out.length} elementos)`] : []);
}"""

async def rota(route):
    u = route.request.url
    if D3_LOCAL and 'd3' in u and u.endswith('.js'): return await route.fulfill(path=D3_LOCAL)
    if any(k in u for k in ('vlibras', 'goatcounter', 'zgo.at', 'googletagmanager', 'google-analytics')): return await route.abort()
    await route.continue_()

async def testar(b, lang, nome, vp):
    url = BASE + ('/' if lang == 'pt' else f'/{lang}/')
    pg = await b.new_page(viewport=vp); erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:200]))
    await pg.route('**/*', rota)
    await pg.goto(url + '?vigia=' + str(int(time.time())), wait_until='load', timeout=60000)
    await pg.wait_for_timeout(3000)
    await pg.evaluate("() => { for (const id of ['el-ck', 'el-notif', 'el-notif-bg']) { const e = document.getElementById(id); if (e) e.hidden = true; } }")
    tag = f'{lang}-{nome}'
    cob = await pg.evaluate(COBERTURA)
    if cob: falha(f'{tag}: camada fixa cobrindo a tela sem ter sido aberta: {cob}')
    larg = await pg.evaluate('() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    if larg[0] > larg[1] + 2: falha(f'{tag}: a página vaza para os lados ({larg[0]} px de conteúdo para {larg[1]} px de tela)')
    if vp['width'] >= 1000:
        nav = await pg.evaluate("() => { const n = document.querySelector('.el-tabs'); return n ? [n.scrollWidth, n.clientWidth] : null }")
        if nav and nav[0] > nav[1] + 2: falha(f'{tag}: o menu não cabe inteiro ({nav[0]} px para {nav[1]} px)')
    n_vid = await pg.evaluate("() => document.querySelectorAll('#el-vids-row .el-vb[data-k]').length")
    if n_vid == 0: aviso(f'{tag}: nenhuma bolinha de vídeo carregou')
    for aba in ABAS:
        ok = await pg.evaluate(f"""() => {{ const t = document.querySelector('.el-tabs [data-tab="{aba}"]') || document.querySelector('[data-tab="{aba}"]'); if (t) t.click(); return !!t }}""")
        await pg.wait_for_timeout(900)
        info = await pg.evaluate(f"""() => {{ const s = document.getElementById('{aba}'); if (!s) return null; const r = s.getBoundingClientRect();
            return {{h: r.height, txt: s.innerText.trim().length, oculto: s.hidden || getComputedStyle(s).display === 'none'}} }}""")
        if not info or info['oculto'] or info['h'] < 150 or info['txt'] < 150:
            falha(f'{tag}: a aba "{aba}" não abriu ou está vazia ({info})')
        cob = await pg.evaluate(COBERTURA)
        if cob: falha(f'{tag}: na aba "{aba}", camada fixa cobrindo a tela: {cob}')
        if aba == 'checagem':
            vazios = await pg.evaluate("""() => { let n = 0, t = 0; document.querySelectorAll('#checagem td').forEach(td => {
                const l = td.getAttribute('data-label') || ''; if (/Selo|Seal|Sello|Tipo de fala|Type of statement|Tipo de declaración/i.test(l)) { t++; if (!td.innerText.trim()) n++; } }); return [n, t] }""")
            if vazios[1] and vazios[0] > vazios[1] * .2: falha(f'{tag}: {vazios[0]} de {vazios[1]} selos ou tipos de fala aparecem vazios na aba Checagem')
        if nome == 'celular' and lang == 'pt':
            await pg.screenshot(path=f'{OUT}/{tag}-{aba}.png')
    if erros: falha(f'{tag}: erros de JavaScript: {erros[:3]}')
    await pg.close()

def frescor():
    import urllib.request
    try:
        st = json.load(urllib.request.urlopen(BASE + '/data/status.json?v=' + str(int(time.time())), timeout=30))
        ult = dt.datetime.fromisoformat(st[0]['ultima_atualizacao'].replace('Z', '+00:00'))
        agora = dt.datetime.now(dt.timezone.utc); h_brt = (agora - dt.timedelta(hours=3)).hour
        idade = (agora - ult).total_seconds() / 3600
        if 8 <= h_brt <= 23 and idade > 4: falha(f'os dados não são atualizados há {idade:.1f} horas (última: {st[0]["ultima_atualizacao"]})')
    except Exception as e:
        aviso(f'não consegui ler data/status.json: {e}')

async def main():
    srv = None
    global BASE
    if os.environ.get('SITE_LOCAL'):
        srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8799', '-d', os.environ['SITE_LOCAL']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5); BASE = 'http://localhost:8799'
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            for lang in ('pt', 'en', 'es'):
                for nome, vp in (('celular', {'width': 390, 'height': 844}), ('computador', {'width': 1280, 'height': 860})):
                    try: await testar(b, lang, nome, vp)
                    except Exception as e: falha(f'{lang}-{nome}: o teste não conseguiu abrir a página: {str(e)[:200]}')
            await b.close()
        if not srv: frescor()
    finally:
        if srv: srv.terminate()
    res = ['# Vigia do site', '', f'Endereço: {BASE}', f'Quando: {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC', '']
    res += ['## Falhas'] + [f'- {x}' for x in FALHAS] if FALHAS else ['Nenhuma falha.']
    if AVISOS: res += ['', '## Avisos'] + [f'- {x}' for x in AVISOS]
    open(f'{OUT}/resultado.md', 'w').write('\n'.join(res) + '\n')
    print('\n'.join(res))
    sys.exit(1 if FALHAS else 0)

if __name__ == '__main__':
    asyncio.run(main())
