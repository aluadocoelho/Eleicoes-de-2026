"""Gera as versões em inglês e espanhol do site (en/index.html, es/index.html) a partir do index.html em português.

Uso: python3 build_i18n.py <repo>
 - Interface: dicionário i18n/ui_<lang>.json (texto em português -> tradução; {n} = número, {c} = código de verificação).
   O HTML fixo é traduzido na hora de gerar (bom para o Google); o que o JavaScript monta é traduzido no navegador.
 - Conteúdo que muda (falas checadas, boatos, agenda, ao vivo...): memória de tradução em data/i18n/<lang>.json
   (texto em português -> tradução), mantida por uma tarefa agendada. O que ainda não tiver tradução aparece em português.
"""
import sys, os, re, json
REPO = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(REPO, 'index.html')).read()
CAMPOS = json.load(open(os.path.join(AQUI, 'i18n', 'campos.json')))
HEAD = {
 'en': dict(lang='en', locale='en_US', nome='English',
   title='Clareia Eleições · Follow Brazil\'s 2026 presidential runoff: Flávio Bolsonaro × Lula',
   desc='Clareia Eleições: follow Brazil\'s 2026 presidential runoff between Flávio Bolsonaro and Lula. Polls, fact-checks, debunked rumors, schedule and debates, in plain language and with the source of every piece of information.',
   ogt='Clareia Eleições · Follow Brazil\'s 2026 runoff', ogd='So no one votes in the dark. Polls, fact-checks, debunked rumors and the schedule of the runoff between Flávio Bolsonaro and Lula, with the source of every piece of information.',
   ogalt='Clareia Eleições logo: so no one votes in the dark. Brazil 2026 runoff, Flávio Bolsonaro × Lula',
   aviso='This is the English version. Summaries of new items may appear in Portuguese for a few hours until they are translated.'),
 'es': dict(lang='es', locale='es_LA', nome='Español',
   title='Clareia Eleições · Sigue la segunda vuelta presidencial de Brasil 2026: Flávio Bolsonaro × Lula',
   desc='Clareia Eleições: sigue la segunda vuelta presidencial de Brasil 2026 entre Flávio Bolsonaro y Lula. Encuestas, verificaciones, rumores desmentidos, agenda y debates, en lenguaje simple y con la fuente de cada información.',
   ogt='Clareia Eleições · Sigue la segunda vuelta de Brasil 2026', ogd='Que nadie vote a oscuras. Encuestas, verificaciones, rumores desmentidos y la agenda de la segunda vuelta entre Flávio Bolsonaro y Lula, con la fuente de cada información.',
   ogalt='Logo de Clareia Eleições: que nadie vote a oscuras. Segunda vuelta de Brasil 2026, Flávio Bolsonaro × Lula',
   aviso='Esta es la versión en español. Los resúmenes de las novedades pueden aparecer en portugués por algunas horas, hasta que se traduzcan.'),
}
NUM = r'(\d+(?:[.,]\d+)*)'; COD = r'([0-9A-F]{4}-[0-9A-F]{4})'; TXT = r'(.+?)'

def carregar(lang):
    ui = json.load(open(os.path.join(AQUI, 'i18n', f'ui_{lang}.json')))
    tm_p = os.path.join(REPO, 'data', 'i18n', f'{lang}.json')
    tm = json.load(open(tm_p)) if os.path.exists(tm_p) else {}
    exato, modelos = {}, []
    for k, v in ui.items():
        if not v: continue
        if '{n}' in k or '{c}' in k or '{t}' in k:
            rx = '^' + re.escape(k).replace(re.escape('{n}'), NUM).replace(re.escape('{c}'), COD).replace(re.escape('{t}'), TXT) + '$'
            modelos.append((k, v, rx))
        else: exato[k] = v
    for k, v in tm.items():   # categorias e textos curtos dos dados também servem para o texto da página
        if v and len(k) <= 60: exato.setdefault(k, v)
    return exato, modelos, tm

def num_local(n, lang):
    return n.replace('.', '§').replace(',', '.').replace('§', ',') if lang == 'en' else n

def trad(t, exato, modelos, lang):
    if t in exato: return exato[t]
    for k, v, rx in modelos:
        m = re.match(rx, t)
        if m:
            vals = list(m.groups()); out = v
            for tok in re.findall(r'\{n\}|\{c\}|\{t\}', k):
                val = vals.pop(0)
                out = out.replace(tok, num_local(val, lang) if tok == '{n}' else val, 1)
            return out
    return None

def traduzir_html(html, exato, modelos, lang):
    partes = re.split(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]+>)', html, flags=re.S)
    for i, p in enumerate(partes):
        if not p: continue
        if p.startswith('<'):
            if p.startswith(('<script', '<style', '<!--')): continue
            def attr(m):
                v = m.group(2); t = trad(re.sub(r'\s+', ' ', v).strip(), exato, modelos, lang)
                return f'{m.group(1)}="{t.replace(chr(34), "&quot;")}"' if t else m.group(0)
            partes[i] = re.sub(r'\b(aria-label|title|placeholder|alt)="([^"]*)"', attr, p)
        else:
            core = re.sub(r'\s+', ' ', p).strip()
            if not core: continue
            t = trad(core.replace('&amp;', '&'), exato, modelos, lang)
            if t:
                lead = p[:len(p) - len(p.lstrip())]; tail = p[len(p.rstrip()):]
                partes[i] = lead + t.replace('&', '&amp;').replace('<', '&lt;') + tail
    return ''.join(partes)

RUNTIME = r"""<script>
(function () {
  var L = window.__LANG, X = window.__UI_X, M = window.__UI_M.map(function (m) { return [m[0], m[1], new RegExp(m[2])]; }), TM = {}, CAMPOS = window.__CAMPOS;
  function nl(n) { return L === "en" ? n.replace(/\./g, "§").replace(/,/g, ".").replace(/§/g, ",") : n; }
  function tr(t) {
    if (X[t]) return X[t];
    if (TM[t] && t.length <= 60) return TM[t];
    for (var i = 0; i < M.length; i++) { var m = M[i][2].exec(t); if (m) { var vals = m.slice(1), out = M[i][1]; (M[i][0].match(/\{n\}|\{c\}|\{t\}/g) || []).forEach(function (tok) { var v = vals.shift(); out = out.replace(tok, tok === "{n}" ? nl(v) : v); }); return out; } }
    var u = /^([+−-]?\d+(?:[.,]\d+)?)\s?(mil|mi|bi)$/.exec(t);
    if (u) return nl(u[1]) + (L === "en" ? {mil: "K", mi: "M", bi: "B"}[u[2]] : {mil: " mil", mi: " M", bi: " mil M"}[u[2]]);
    if (L === "en" && /^[+−-]?\d{1,3}(\.\d{3})*(,\d+)?\s?(%|pt|pts|p\.p\.)?$/.test(t) && /[.,]/.test(t)) return nl(t);
    return null;
  }
  var FEITO = new WeakMap();   // o que já foi trocado: evita traduzir de novo o próprio texto traduzido
  function node(n) {
    if (n.nodeType === 3) {
      if (FEITO.get(n) === n.nodeValue) return;
      var p = n.parentElement; if (!p || p.closest("script,style,[vw],[data-sem-traducao]")) return;
      var raw = n.nodeValue, core = raw.replace(/\s+/g, " ").trim(); if (!core || core.length > 400) return;
      var t = tr(core); if (t && t !== core) n.nodeValue = raw.replace(/\S[\s\S]*\S|\S/, function () { return t; }); FEITO.set(n, n.nodeValue);
    } else if (n.nodeType === 1) {
      var fa = FEITO.get(n) || {}; ["aria-label", "title", "placeholder", "alt"].forEach(function (a) { if (n.hasAttribute && n.hasAttribute(a)) { var v = n.getAttribute(a); if (fa[a] === v) return; var t = tr(v.replace(/\s+/g, " ").trim()); if (t && t !== v) n.setAttribute(a, t); fa[a] = n.getAttribute(a); } }); FEITO.set(n, fa);
      if (n.closest && n.closest("script,style,[vw]")) return;
      for (var c = n.firstChild; c; c = c.nextSibling) node(c);
    }
  }
  // conteúdo dos dados: troca os textos em português pelos traduzidos, quando houver
  window.__tradRows = function (id, rows) {
    var fs = CAMPOS[id]; if (!fs || !Array.isArray(rows)) return rows;
    rows.forEach(function (r) { fs.forEach(function (f) { var v = r[f]; if (typeof v === "string" && TM[v]) r[f] = TM[v]; }); });
    return rows;
  };
  window.__tmP = fetch("../data/i18n/" + L + ".json", {cache: "no-cache"}).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }).then(function (j) { TM = j || {}; });
  function go() {
    node(document.body);
    new MutationObserver(function (ms) { ms.forEach(function (m) {
      if (m.type === "characterData") node(m.target);
      else if (m.type === "attributes") node(m.target);
      else m.addedNodes.forEach(node);
    }); }).observe(document.body, {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ["aria-label", "title", "placeholder", "alt"]});
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
</script>"""

def gerar(lang):
    exato, modelos, tm = carregar(lang)
    H = HEAD[lang]; html = SRC
    # cabeçalho
    html = html.replace('<html lang="pt-BR">', f'<html lang="{H["lang"]}">', 1)
    html = re.sub(r'<title>.*?</title>', f'<title>{H["title"]}</title>', html, 1, flags=re.S)
    rep = {
      r'(<meta name="description" content=")[^"]*': H['desc'], r'(<meta property="og:title" content=")[^"]*': H['ogt'],
      r'(<meta name="twitter:title" content=")[^"]*': H['ogt'], r'(<meta property="og:description" content=")[^"]*': H['ogd'],
      r'(<meta name="twitter:description" content=")[^"]*': H['ogd'], r'(<meta property="og:image:alt" content=")[^"]*': H['ogalt'],
      r'(<meta property="og:locale" content=")[^"]*': H['locale'], r'(<meta property="og:url" content=")[^"]*': f'https://clareiaeleicoes.com.br/{lang}/',
      r'(<link rel="canonical" href=")[^"]*': f'https://clareiaeleicoes.com.br/{lang}/',
    }
    for rx, v in rep.items():
        html, n = re.subn(rx, lambda m: m.group(1) + v.replace('&', '&amp;'), html, 1)
        assert n == 1, rx
    # caminhos relativos (a página fica em /en/ ou /es/)
    for a in ('manifest.webmanifest', 'icon-192.png', 'favicon.svg', 'favicon.ico', 'favicon-32.png', 'apple-touch-icon.png'):
        html = html.replace(f'href="{a}"', f'href="../{a}"')
    html = html.replace('href="data/', 'href="../data/').replace('"icon-192.png"', '"../icon-192.png"').replace('register("sw.js"', 'register("../sw.js"')
    # dados: espera a memória de tradução e troca os textos
    a = 'return fetch("data/" + id + ".json", {cache: "no-cache"})'
    assert html.count(a) == 1
    html = html.replace(a, 'return window.__tmP.then(function () { return fetch("../data/" + id + ".json", {cache: "no-cache"}); })')
    a = '.then(function (rows) { store[id] = {status: "ok", data: rows}; loadedOnce[id] = true; })'
    assert html.count(a) == 1
    html = html.replace(a, '.then(function (rows) { store[id] = {status: "ok", data: window.__tradRows(id, rows)}; loadedOnce[id] = true; })')
    # seletor de idioma
    html = html.replace('<a href="/" hreflang="pt-BR" lang="pt-BR" aria-current="true" title="Português">', '<a href="/" hreflang="pt-BR" lang="pt-BR" title="Português">')
    html = html.replace(f'<a href="/{lang}/" hreflang="{lang}" lang="{lang}" title="{H["nome"]}">', f'<a href="/{lang}/" hreflang="{lang}" lang="{lang}" aria-current="true" title="{H["nome"]}">')
    # o resumo sem JavaScript e os dados estruturados ficam em português, marcados como tal
    html = html.replace('<noscript>', '<noscript><div lang="pt-BR">', 1).replace('</noscript>', '</div></noscript>', 1)
    # texto fixo traduzido aqui; o resto no navegador
    corpo_i = html.index('<body'); html = html[:corpo_i] + traduzir_html(html[corpo_i:], exato, modelos, lang)
    boot = ('<script>window.__LANG=' + json.dumps(lang) + ';window.__UI_X=' + json.dumps(exato, ensure_ascii=False)
            + ';window.__UI_M=' + json.dumps([[k, v, rx] for k, v, rx in modelos], ensure_ascii=False)
            + ';window.__CAMPOS=' + json.dumps(CAMPOS) + ';</script>' + RUNTIME)
    i = html.index('<body'); j = html.index('>', i) + 1
    aviso = f'<div class="el-lang-aviso" role="note">{H["aviso"]}</div>'
    html = html[:j] + boot.replace('</script>', '</script>', 1) + html[j:]
    html = html.replace('<div class="el-foot el-foot-lang">', f'<div class="el-foot el-foot-lang">{aviso}', 1)
    html = html.replace('</head>', '<style>.el-lang-aviso{font-size:.8125rem;line-height:1.5;color:var(--color-fg-muted);margin-bottom:10px}</style></head>', 1)
    os.makedirs(os.path.join(REPO, lang), exist_ok=True)
    open(os.path.join(REPO, lang, 'index.html'), 'w').write(html)
    print(lang, 'ok', len(html), 'textos fixos traduzidos:', len(exato), 'modelos:', len(modelos))

for lg in ('en', 'es'):
    gerar(lg)
