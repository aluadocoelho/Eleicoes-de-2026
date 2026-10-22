import re
"""Gera o index.html público (GitHub Pages) a partir da página do painel."""
import sys
src_path, out_path = sys.argv[1], sys.argv[2]
src = open(src_path).read()
style = src.split("<style>")[1].split("</style>")[0].replace("#dash-root{--dash-gutter:0}\n", "")
body = src.split("</style>")[1].split("<script>")[0]
script = src.split("<script>")[1].split("</script>")[0]
tokens = """:root{
  --font-anthropic-sans:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --font-anthropic-serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --cds-font-size-caption:.8125rem; --cds-font-size-body:.9375rem; --cds-font-size-heading:1.0625rem; --cds-font-size-title:1.75rem;
  --cds-font-weight-medium:600;
  --cds-gap-xs:4px; --cds-gap-sm:8px; --cds-gap-md:16px; --cds-gap-lg:24px; --cds-gap-xl:40px;
  --cds-pad-xs:4px; --cds-pad-sm:8px; --cds-pad-md:14px; --cds-pad-lg:20px; --cds-pad-xl:32px;
  --cds-radius:10px; --cds-shadow-popover:0 6px 24px rgba(16,24,40,.12); --cds-dur-slow:.3s;
}
html,body{margin:0;padding:0;background:#F6F3FB}
:root[data-theme="dark"],:root[data-theme="dark"] body{background:#0F1117}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]),:root:not([data-theme="light"]) body{background:#0F1117}}
:root[data-theme="dark"] .dash-skeleton{background:linear-gradient(90deg,#1E222C 25%,#262B36 50%,#1E222C 75%);background-size:200% 100%}
body{-webkit-text-size-adjust:100%}
html,body{overflow-x:clip;max-width:100%}
.dash-skeleton{color:transparent!important;background:linear-gradient(90deg,#EEF0F3 25%,#F6F7F9 50%,#EEF0F3 75%);background-size:200% 100%;border-radius:6px}
span.dash-skeleton,b.dash-skeleton{display:inline-block;min-width:2.2em}
@media (prefers-reduced-motion:no-preference){.dash-skeleton{animation:el-sk 1.2s linear infinite}}
@keyframes el-sk{from{background-position:200% 0}to{background-position:-200% 0}}
.el-foot a{color:inherit}
.el-notif-open{appearance:none;background:var(--accent-soft);color:var(--accent-text);padding:8px 16px;min-height:44px;font:inherit;font-weight:700;cursor:pointer}
.el-notif-open[hidden]{display:none}
#el-notif-bg{position:fixed;inset:0;z-index:60;background:rgba(22,24,29,.6)}
#el-notif-bg[hidden]{display:none}
#el-notif{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:61;width:min(460px,calc(100vw - 32px));max-height:calc(100vh - 32px);overflow:auto;box-sizing:border-box;background:#FFFFFF;color:#16181D;border:3px solid #16181D;border-radius:24px;box-shadow:8px 8px 0 #16181D;padding:24px 22px 20px;font-family:"Inter",system-ui,sans-serif;display:flex;flex-direction:column;gap:10px}
#el-notif[hidden]{display:none}
#el-ck:focus{outline:3px solid #FFD43B;outline-offset:2px}
#el-ck{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:51;width:min(440px,calc(100vw - 24px));box-sizing:border-box;background:#FFFFFF;color:#16181D;border:2px solid #16181D;border-radius:18px;box-shadow:5px 5px 0 #16181D;padding:16px 18px 14px;font-family:"Inter",system-ui,sans-serif;display:flex;flex-direction:column;gap:8px}
#el-ck[hidden]{display:none}
#el-ck h2{margin:0;font-size:1rem;line-height:1.3}
#el-ck p{margin:0;font-size:.88rem;line-height:1.5;color:#3A3F49}
#el-ck .nt-btns{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;margin-top:4px}
#el-ck button{appearance:none;font:inherit;font-weight:700;font-size:.95rem;min-height:44px;padding:8px 16px;border-radius:12px;border:2px solid #16181D;cursor:pointer;background:#FFFFFF;color:#16181D}
#el-ck .ck-yes{background:#5B2DBF;color:#FFFFFF}
#el-ck button:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
body:has(.el[data-theme="dark"]) #el-ck{background:#171A22;color:#ECEEF3;border-color:#B9A3FF;box-shadow:5px 5px 0 #B9A3FF}
body:has(.el[data-theme="dark"]) #el-ck p{color:#A6ADBB}
body:has(.el[data-theme="dark"]) #el-ck button{background:#171A22;color:#ECEEF3;border-color:#B9A3FF}
body:has(.el[data-theme="dark"]) #el-ck .ck-yes{background:#5B2DBF;color:#FFFFFF}
.el-foot-btns{display:flex;gap:10px;flex-wrap:wrap}
#el-notif .nt-top{display:flex;flex-direction:column;gap:14px;align-items:flex-start}
#el-notif .nt-ico{flex:none;width:56px;height:56px;border-radius:16px;background:#5B2DBF;color:#FFFFFF;display:flex;align-items:center;justify-content:center}
#el-notif h2{margin:0;font-size:1.3rem;line-height:1.25}
#el-notif p{margin:6px 0 0;font-size:1rem;line-height:1.55;color:#3A3F49}
#el-notif .nt-btns{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;margin-top:8px}
#el-notif .nt-btns button{flex:1 1 140px}
#el-notif button{appearance:none;font:inherit;font-weight:700;font-size:.95rem;min-height:44px;padding:8px 16px;border-radius:12px;border:2px solid #16181D;cursor:pointer}
#el-notif .nt-yes{background:#5B2DBF;color:#FFFFFF}
#el-notif .nt-no{background:#FFFFFF;color:#16181D}
#el-notif button:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
@media (prefers-reduced-motion:no-preference){#el-notif{animation:nt-in .3s cubic-bezier(.2,.9,.3,1.2) both}#el-notif-bg{animation:nt-bg .25s ease-out both}}
@keyframes nt-in{from{transform:translate(-50%,-50%) scale(.92);opacity:0}to{transform:translate(-50%,-50%) scale(1);opacity:1}}
@keyframes nt-bg{from{opacity:0}to{opacity:1}}
body.el-nt-lock{overflow:hidden}
body:has(.el[data-theme="dark"]) #el-notif{background:#171A22;color:#ECEEF3;border-color:#B9A3FF;box-shadow:5px 5px 0 #B9A3FF}
body:has(.el[data-theme="dark"]) #el-notif p{color:#A6ADBB}
body:has(.el[data-theme="dark"]) #el-notif .nt-no{background:#171A22;color:#ECEEF3;border-color:#B9A3FF}
body:has(.el[data-theme="dark"]) #el-notif .nt-yes{border-color:#B9A3FF}
"""
_fi = body.rindex('<p class="el-foot">')
old_foot = body[_fi:body.index('</p>', _fi) + 4]
body = body.replace(old_foot, '<p class="el-foot">Dados reunidos de reportagens e checagens publicadas, com link para cada fonte, atualizados a cada hora, das 7h às 23h, e com mais frequência durante debates. Os dados são abertos e podem ser baixados em <a href="https://github.com/aluadocoelho/Eleicoes-de-2026" target="_blank" rel="noopener noreferrer">github.com/aluadocoelho/Eleicoes-de-2026</a> (dados sob CC BY 4.0; os números e selos pertencem aos institutos e checadores citados). A página conta visitas com o GoatCounter, que não usa cookies nem guarda dados pessoais. Se você aceitar, também usamos o Google Analytics, que usa cookies, para entender quais abas são mais lidas; ele fica desligado se você recusar.</p><p class="el-foot el-visits" id="gc-total" hidden></p><p class="el-foot el-foot-btns"><button type="button" class="el-btn el-notif-open" id="el-notif-open" hidden>Receber avisos de novidades</button> <button type="button" class="el-btn el-notif-open" id="el-ck-open">Preferências de cookies</button></p>')
script = script.replace('d.textContent = "Failed to load"', 'd.textContent = "Não foi possível carregar"')
# --- desempenho e contraste (só no site público) ---
_PLT_END = '<button type="button" class="el-plt-x" id="el-plt-x" aria-label="Fechar o plantão">×</button>\n  </div>\n'
assert body.count(_PLT_END) == 1
body = body.replace(_PLT_END, _PLT_END + '  <script>(function(){try{var b=document.getElementById("el-plt"),v=localStorage.getItem("el-plt-h"),h=v===null?(innerWidth<=640?57:52):+v;if(h>0){b.classList.add("el-plt-res");b.style.minHeight=h+"px";}}catch(e){}})()</script>\n')
tokens += """.el-plt.el-plt-res[hidden]{display:flex;visibility:hidden}
.el .el-vf-st{color:var(--color-fg)}
.el .el-mais{color:var(--accent-text,#5B2DBF)}
"""
# gráficos e tabelas das abas fechadas só são montados quando a aba abre (a troca de aba já redesenha)
_LAZY = 'const __fechada = n => { if (typeof n === "string") n = document.querySelector(n); return !!(n && n.closest && n.closest(".el-page[hidden]")); };\n'
for _f in ["function drawDif(box, rows) {", "function drawFalsas(box, rows) {", "function drawPT(box, rows) {", "function drawRedes(box, rows) {", "function drawRedesItens(box, rows) {", "function table(sel, rows, cols, keyFn) {"]:
    assert script.count("  " + _f) == 1, _f
    _arg = _f.split("(")[1].split(",")[0]
    script = script.replace("  " + _f, "  " + _f + " if (__fechada(" + _arg + ")) return;", 1)
script = script.replace("  function table(sel, rows, cols, keyFn) {", "  " + _LAZY + "  function table(sel, rows, cols, keyFn) {", 1)
# --- acessibilidade extra (só no site público): Ouvir, alto contraste, espaçamento, sem animações, gráficos em tabela ---
_A11Y_ICO = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4.5" r="2"/><path d="M4 8.5l8 1.5 8-1.5M12 10v5l-3.5 6M12 15l3.5 6"/></svg>'
_THEME_END = '<span class="el-theme-l" id="theme-lbl">Modo escuro</span>\n      </button>'
assert body.count(_THEME_END) == 1
body = body.replace(_THEME_END, _THEME_END + '\n      <button class="el-theme" id="a11y-btn" type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="el-a11y">' + _A11Y_ICO + '<span class="el-theme-l">Acessibilidade</span></button>')
_OPC = [
 ("ouvir", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/></svg>', "Ouvir a seção"),
 ("contraste", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>', "Alto contraste"),
 ("espaco", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/><path d="M2 9v6M22 9v6"/></svg>', "Mais espaço no texto"),
 ("parado", '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M10 9v6M14 9v6"/></svg>', "Sem animações"),
]
_tiles = ''.join(f'\n      <button type="button" class="el-drw-o" data-a11y="{k}" aria-pressed="false">{ic}<span>{t}</span></button>' for k, ic, t in _OPC)
_DRW_END = '<span id="el-drw-tema">Modo escuro</span></button>'
assert body.count(_DRW_END) == 1
body = body.replace(_DRW_END, _DRW_END + _tiles)
_painel = ('<div class="el-a11y" id="el-a11y" role="dialog" aria-label="Acessibilidade" hidden><div class="el-a11y-h">Acessibilidade</div>'
           + ''.join(f'<button type="button" class="el-a11y-o" data-a11y="{k}" aria-pressed="false">{ic}<span>{t}</span></button>' for k, ic, t in _OPC)
           + '<p class="el-a11y-n">O botão azul no canto da tela abre a tradução em Libras (VLibras).</p></div>')
body = body.replace('<div class="el-actions">', '<div class="el-actions">' + _painel, 1)
_TBL_AT = {'ch-dif': 'Diferença em cada pesquisa', 'ch-pt': 'Resultado do 1º turno', 'ch-falsas': 'Taxa de falas falsas'}
_CH = {'ch-dif': '<div class="el-chart dash-skeleton" id="ch-dif" data-source="pesquisas"><svg></svg><div class="el-tip"></div></div>',
       'ch-pt': '<div class="el-chart-sm dash-skeleton" id="ch-pt" data-source="primeiro_turno"><svg></svg></div>',
       'ch-falsas': '<div class="el-chart dash-skeleton" id="ch-falsas" data-source="taxa_falsas" style="min-height:240px"><svg></svg><div class="el-tip"></div></div>'}
for _id, _h in _CH.items():
    assert body.count(_h) == 1, _id
    body = body.replace(_h, _h + f'<details class="el-tbl-alt" data-for="{_id}"><summary>Ver os números em tabela</summary><div class="el-tbl-alt-b"></div></details>')
style += r"""
.el-actions{position:relative}
.el-a11y{position:fixed;z-index:70;width:min(320px,calc(100vw - 32px));background:var(--color-panel);color:var(--color-fg);border:3px solid var(--ink);border-radius:20px;box-shadow:6px 6px 0 var(--ink);padding:14px;display:flex;flex-direction:column;gap:8px}
.el-a11y[hidden]{display:none}
.el-a11y-h{font-weight:800;font-size:.95rem;padding:2px 4px 4px}
.el-a11y-o{appearance:none;display:flex;align-items:center;gap:12px;min-height:48px;padding:8px 12px;border:2px solid var(--color-border-line);border-radius:14px;background:var(--color-bg);color:inherit;font:inherit;font-weight:700;text-align:left;cursor:pointer}
.el-a11y-o[aria-pressed="true"],.el-drw-o[data-a11y][aria-pressed="true"]{background:#5B2DBF;color:#fff;border-color:#16181D}
.el-a11y-o:focus-visible,.el-drw-o:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
.el-a11y-n{margin:4px 4px 0;font-size:.8125rem;line-height:1.45;color:var(--color-fg-muted)}
.el-tbl-alt{margin-top:10px}
.el-tbl-alt summary{cursor:pointer;font-weight:700;font-size:.875rem;color:var(--accent-text);min-height:44px;display:flex;align-items:center}
.el-tbl-alt table{width:100%;border-collapse:collapse;font-size:.875rem;font-variant-numeric:tabular-nums}
.el-tbl-alt th,.el-tbl-alt td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--color-border-line)}
.el-tbl-alt th{font-weight:700}
/* alto contraste */
.el.el-hc{--color-fg:#000;--color-fg-muted:#1A1A1A;--color-bg:#FFF;--color-panel:#FFF;--color-border-line:#000;--accent-text:#2A0F8F}
.el.el-hc[data-theme="dark"]{--color-fg:#FFF;--color-fg-muted:#F0F0F0;--color-bg:#000;--color-panel:#000;--color-border-line:#FFF;--accent-text:#FFE36E}
.el.el-hc a{text-decoration:underline!important;text-underline-offset:3px}
.el.el-hc .el-card,.el.el-hc .el-kpi,.el.el-hc table{border-color:currentColor!important}
/* mais espaço no texto (ajuda na leitura, inclusive com dislexia) */
.el.el-sp p,.el.el-sp li,.el.el-sp td,.el.el-sp .el-q-s{line-height:1.85!important;letter-spacing:.03em;word-spacing:.12em}
/* sem animações */
.el.el-na *,.el.el-na *::before,.el.el-na *::after,body.el-na-b #el-notif,body.el-na-b #el-notif-bg{animation:none!important;transition:none!important;scroll-behavior:auto!important}
"""
script += r"""
;(function () {
  const ROOT = document.querySelector(".el"), KEY = "el-a11y";
  let st = {}; try { st = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
  const salvar = () => { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} };
  const temVoz = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  const btns = () => document.querySelectorAll("[data-a11y]");
  function aplicar() {
    ROOT.classList.toggle("el-hc", !!st.contraste); ROOT.classList.toggle("el-sp", !!st.espaco);
    ROOT.classList.toggle("el-na", !!st.parado); document.body.classList.toggle("el-na-b", !!st.parado);
    btns().forEach(b => { const k = b.dataset.a11y; if (k === "ouvir") { b.hidden = !temVoz; b.setAttribute("aria-pressed", String(falando)); b.querySelector("span").textContent = falando ? "Parar de ouvir" : "Ouvir a seção"; } else b.setAttribute("aria-pressed", String(!!st[k])); });
  }
  // Ouvir: lê em voz alta o texto da seção aberta, com a voz do próprio aparelho, em pedaços curtos
  let falando = false, fila = [];
  function voz() { const vs = speechSynthesis.getVoices(); return vs.find(v => /^pt[-_]BR/i.test(v.lang)) || vs.find(v => /^pt/i.test(v.lang)) || null; }
  function proximo() {
    if (!falando || !fila.length) { falando = false; aplicar(); return; }
    const u = new SpeechSynthesisUtterance(fila.shift()); u.lang = "pt-BR"; const v = voz(); if (v) u.voice = v; u.rate = 1;
    u.onend = proximo; u.onerror = () => { falando = false; aplicar(); };
    speechSynthesis.speak(u);
  }
  function ouvir() {
    if (falando) { falando = false; fila = []; speechSynthesis.cancel(); aplicar(); return; }
    const pg = Array.from(document.querySelectorAll(".el-page")).find(p => !p.hidden); if (!pg) return;
    const partes = [];
    pg.querySelectorAll("h2,h3,p,li,.el-q-a,.el-q-s,caption,tr").forEach(n => {
      if (n.closest("[hidden],details:not([open]),svg,.el-tip,[aria-hidden=true]")) return;
      if (n.matches("p,li") && n.closest("tr")) return;
      const t = (n.innerText || "").replace(/\s+/g, " ").trim(); if (t.length > 1) { let x = n.matches("tr") ? t.replace(/\t/g, ", ") : t; if (!/[.!?:;]$/.test(x)) x += "."; partes.push(x); }
    });
    fila = [];
    partes.forEach(t => { (t.match(/[^.!?]+[.!?]*/g) || [t]).forEach(s => { s = s.trim(); if (!s) return; if (fila.length && (fila[fila.length - 1] + " " + s).length < 220) fila[fila.length - 1] += " " + s; else fila.push(s); }); });
    if (!fila.length) return;
    falando = true; speechSynthesis.cancel(); aplicar(); proximo();
  }
  document.addEventListener("click", ev => {
    const b = ev.target.closest("[data-a11y]"); if (!b) return;
    const k = b.dataset.a11y;
    if (k === "ouvir") ouvir(); else { st[k] = !st[k]; salvar(); aplicar(); }
  });
  // para a leitura ao trocar de aba
  document.querySelectorAll(".el-tab").forEach(t => t.addEventListener("click", () => { if (falando) { falando = false; fila = []; speechSynthesis.cancel(); aplicar(); } }));
  // painel do botão Acessibilidade (computador)
  const ab = document.getElementById("a11y-btn"), pn = document.getElementById("el-a11y");
  if (ab && pn) {
    const fecha = () => { pn.hidden = true; ab.setAttribute("aria-expanded", "false"); };
    ROOT.appendChild(pn);
    const posiciona = () => { const r = ab.getBoundingClientRect(); pn.style.top = Math.round(r.bottom + 10) + "px"; pn.style.right = Math.max(16, Math.round(innerWidth - r.right)) + "px"; };
    addEventListener("resize", () => { if (!pn.hidden) posiciona(); }); addEventListener("scroll", () => { if (!pn.hidden) posiciona(); }, {passive: true});
    ab.addEventListener("click", () => { const abre = pn.hidden; if (abre) posiciona(); pn.hidden = !abre; ab.setAttribute("aria-expanded", String(abre)); if (abre) { const f = pn.querySelector("button:not([hidden])"); if (f) f.focus(); } });
    document.addEventListener("keydown", ev => { if (ev.key === "Escape" && !pn.hidden) { fecha(); ab.focus(); } });
    document.addEventListener("pointerdown", ev => { if (!pn.hidden && !pn.contains(ev.target) && !ab.contains(ev.target)) fecha(); });
  }
  if (temVoz && speechSynthesis.onvoiceschanged !== undefined) speechSynthesis.onvoiceschanged = () => {};
  aplicar();
  // gráficos também em tabela, para leitor de tela e para quem prefere números
  const n1 = v => v == null || v === "" ? "—" : (typeof v === "number" ? v.toLocaleString("pt-BR", {maximumFractionDigits: 1}) : String(v));
  const dt = s => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(s || "")); return m ? m[3] + "/" + m[2] : n1(s); };
  const TAB = {
    "ch-dif": () => { const d = dash.data("pesquisas"); return d.status !== "ok" ? null : {cab: ["Instituto", "Divulgação", "Flávio (válidos)", "Lula (válidos)", "Diferença"], linhas: (d.data || []).slice().sort((a, b) => String(b.divulgacao).localeCompare(String(a.divulgacao))).map(r => [r.instituto, dt(r.divulgacao), n1(r.flavio_validos) + "%", n1(r.lula_validos) + "%", (r.flavio_validos - r.lula_validos > 0 ? "Flávio +" : r.flavio_validos - r.lula_validos < 0 ? "Lula +" : "") + n1(Math.abs(r.flavio_validos - r.lula_validos))])}; },
    "ch-pt": () => { const d = dash.data("primeiro_turno"); return d.status !== "ok" ? null : {cab: ["Candidato", "Partido", "Votos válidos"], linhas: (d.data || []).map(r => [r.candidato, r.partido || "", n1(r.pct) + "%"])}; },
    "ch-falsas": () => { const d = dash.data("taxa_falsas"); return d.status !== "ok" ? null : {cab: ["Candidato", "Até", "Falas falsas", "Falas checadas", "Taxa"], linhas: (d.data || []).map(r => [r.candidato, dt(r.data), n1(r.falsas), n1(r.total), r.taxa == null ? "—" : Math.round(r.taxa * 100) + "%"])}; }
  };
  dash.onData(() => {
    document.querySelectorAll(".el-tbl-alt").forEach(dl => {
      const f = TAB[dl.dataset.for], t = f && f(); if (!t) return;
      const box = dl.querySelector(".el-tbl-alt-b"); box.textContent = "";
      const tb = document.createElement("table"), th = tb.createTHead().insertRow();
      t.cab.forEach(c => { const e = document.createElement("th"); e.scope = "col"; e.textContent = c; th.appendChild(e); });
      const bd = tb.createTBody(); t.linhas.forEach(l => { const tr = bd.insertRow(); l.forEach(c => { tr.insertCell().textContent = c; }); });
      box.appendChild(tb);
    });
  });
})();
"""
shim = r"""
(function () {
  var DATASETS = ["pesquisas","primeiro_turno","transferencia","redes","sinais","agenda","campanha","checagens_placar","checagens","boatos","destaques","status","aovivo","selos","erratas","plantao"];
  var store = {}, calcs = [], listeners = [];
  DATASETS.forEach(function (id) { store[id] = {status: "loading", data: []}; });
  function run() { listeners.forEach(function (fn) { try { fn(); } catch (e) { console.error(e); } }); }
  function computeCalcs() {
    calcs.forEach(function (c) {
      var ins = c.inputs.map(function (i) { return store[i] || {status: "missing"}; });
      var bad = ins.find(function (s) { return s.status !== "ok"; });
      if (bad) { store[c.id] = {status: bad.status === "loading" ? "loading" : "error", data: []}; return; }
      try { store[c.id] = {status: "ok", data: c.fn.apply(null, ins.map(function (s) { return s.data; }))}; }
      catch (e) { console.error("cálculo " + c.id, e); store[c.id] = {status: "error", data: []}; }
    });
  }
  window.dash = {
    calc: function (id, spec) { calcs.push({id: id, inputs: spec.inputs, fn: spec.fn}); store[id] = {status: "loading", data: []}; },
    data: function (id) { return store[id] || {status: "missing", data: []}; },
    onData: function (fn) { listeners.push(fn); fn(); },
    setLink: function (id) { try { history.replaceState(null, "", "#" + id); } catch (e) {} },
    loader: function () {}, refresh: function () {}
  };
  var loadedOnce = {}, domPronto = document.readyState !== "loading", espera = [];
  document.addEventListener("DOMContentLoaded", function () { domPronto = true; espera.splice(0).forEach(function (f) { f(); }); });
  function quandoPronto(f) { if (domPronto) f(); else espera.push(f); }
  function fetchOne(id) {
    return fetch("data/" + id + ".json", {cache: "no-cache"})
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (rows) { store[id] = {status: "ok", data: rows}; loadedOnce[id] = true; })
      .catch(function () { if (store[id].status !== "ok") store[id] = {status: "error", data: []}; });
  }
  // Plantão: o espaço dele fica reservado desde o carregamento (com a altura da última visita),
  // para a página não "pular" quando ele aparece. Depois da primeira leitura, a reserva sai.
  function liberaPlt() {
    var b = document.getElementById("el-plt"); if (!b) return;
    var h = b.hidden ? 0 : Math.round(b.getBoundingClientRect().height);
    try { localStorage.setItem("el-plt-h", String(h)); } catch (e) {}
    b.classList.remove("el-plt-res"); b.style.minHeight = "";
  }
  var carregandoSelos = false;
  function loadSelos() {
    if (carregandoSelos) return; carregandoSelos = true;
    fetchOne("selos").then(function () { carregandoSelos = false; computeCalcs(); run(); });
  }
  var primeira = true;
  function load() {
    var onVerify = /verificar/.test(location.hash);
    // os códigos de verificação são o maior arquivo: carregam depois do resto, quando o navegador está livre,
    // e só voltam a ser relidos com a aba Verificar aberta
    Promise.all(DATASETS.filter(function (id) { return id !== "selos"; }).map(fetchOne)).then(function () {
      quandoPronto(function () {
        computeCalcs(); run();
        if (primeira) { primeira = false; liberaPlt(); }
        if (onVerify) loadSelos();
        else if (!loadedOnce.selos) { if (window.requestIdleCallback) requestIdleCallback(loadSelos, {timeout: 4000}); else setTimeout(loadSelos, 1500); }
      });
    });
  }
  load();   // começa a buscar os dados já, sem esperar imagens, fontes e scripts de terceiros
  quandoPronto(function () {
    setInterval(load, 180000);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) load(); });
    var vf = document.getElementById("verificar");
    if (vf && window.MutationObserver) new MutationObserver(function () { if (!vf.hidden && !loadedOnce.selos) loadSelos(); }).observe(vf, {attributes: true, attributeFilter: ["hidden"]});
  });
  var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(run, 150); });
})();
"""

import json as _json
_BASE = "https://clareiaeleicoes.com.br/"
_RAW = "https://github.com/aluadocoelho/Eleicoes-de-2026/blob/main/data/"
_ORG = {"@type": "Organization", "@id": _BASE + "#org", "name": "Clareia Eleições", "alternateName": "Verita Eleições",
        "url": _BASE, "logo": {"@type": "ImageObject", "url": _BASE + "icon-512.png", "width": 512, "height": 512},
        "sameAs": ["https://www.instagram.com/clareiaeleicoes/", "https://github.com/aluadocoelho/Eleicoes-de-2026"],
        "description": "Agregador independente e apartidário de informações sobre as eleições no Brasil, feito com inteligência artificial e revisado por uma pessoa. Não tem relação com partidos, campanhas ou institutos de pesquisa."}
_DESC = ("Acompanhe o 2º turno da eleição presidencial de 2026 entre Flávio Bolsonaro (PL) e Lula (PT): pesquisas de intenção de voto, "
         "checagens de falas, boatos desmentidos, agenda dos candidatos, debates ao vivo e redes sociais, sempre com o link da fonte original.")
_conj = [("pesquisas", "Pesquisas de intenção de voto do 2º turno (votos válidos e totais, instituto, amostra e margem)"),
         ("checagens", "Falas dos candidatos checadas por agências de checagem, com o selo original"),
         ("boatos", "Boatos e conteúdos falsos sobre os candidatos desmentidos por checadores ou pelo TSE"),
         ("agenda", "Agenda pública diária de Lula e Flávio Bolsonaro"),
         ("campanha", "Apoios, decisões da Justiça Eleitoral, debates e estratégia das campanhas"),
         ("redes", "Métricas comparáveis dos dois candidatos nas redes sociais"),
         ("aovivo", "Momentos e checagens de debates e sabatinas"),
         ("destaques", "Grandes eventos do 2º turno: debates, sabatinas e o dia da votação"),
         ("erratas", "Correções públicas feitas pela revisão de qualidade")]
_GRAPH = {"@context": "https://schema.org", "@graph": [
  _ORG,
  {"@type": "WebSite", "@id": _BASE + "#site", "url": _BASE, "name": "Clareia Eleições", "alternateName": ["Verita Eleições", "Clareia"],
   "inLanguage": "pt-BR", "description": _DESC, "publisher": {"@id": _BASE + "#org"}},
  {"@type": "WebPage", "@id": _BASE + "#pagina", "url": _BASE, "name": "Clareia Eleições: acompanhe o 2º turno de 2026, Flávio Bolsonaro × Lula",
   "inLanguage": "pt-BR", "isPartOf": {"@id": _BASE + "#site"}, "about": [
     {"@type": "Event", "name": "Eleição presidencial de 2026 no Brasil, 2º turno", "startDate": "2026-10-25T08:00:00-03:00", "endDate": "2026-10-25T17:00:00-03:00",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
      "location": {"@type": "Country", "name": "Brasil"}, "organizer": {"@type": "GovernmentOrganization", "name": "Tribunal Superior Eleitoral", "url": "https://www.tse.jus.br/"}},
     {"@type": "Person", "name": "Flávio Bolsonaro", "affiliation": {"@type": "PoliticalParty", "name": "Partido Liberal (PL)"}},
     {"@type": "Person", "name": "Luiz Inácio Lula da Silva", "alternateName": "Lula", "affiliation": {"@type": "PoliticalParty", "name": "Partido dos Trabalhadores (PT)"}}],
   "description": _DESC, "primaryImageOfPage": _BASE + "og-image.png", "publisher": {"@id": _BASE + "#org"}},
  {"@type": "Dataset", "@id": _BASE + "#dados", "name": "Dados abertos do 2º turno das eleições presidenciais de 2026",
   "description": "Conjuntos em JSON, atualizados automaticamente ao longo do dia, com link para a fonte de cada linha: " + "; ".join(d for _, d in _conj) + ".",
   "url": "https://github.com/aluadocoelho/Eleicoes-de-2026", "license": "https://creativecommons.org/licenses/by/4.0/",
   "inLanguage": "pt-BR", "isAccessibleForFree": True, "creator": {"@id": _BASE + "#org"},
   "keywords": ["eleições 2026", "segundo turno", "pesquisa eleitoral", "checagem de fatos", "fake news", "Lula", "Flávio Bolsonaro", "dados abertos"],
   "spatialCoverage": {"@type": "Country", "name": "Brasil"}, "temporalCoverage": "2026-10-05/2026-10-27",
   "distribution": [{"@type": "DataDownload", "name": n + ".json", "encodingFormat": "application/json", "contentUrl": _BASE + "data/" + n + ".json"} for n, _ in _conj]}
]}
LDJSON = _json.dumps(_GRAPH, ensure_ascii=False, separators=(",", ":")).replace("</", "<\/")
NOSCRIPT = ('<noscript><div style="max-width:720px;margin:24px auto;padding:0 16px;font-family:system-ui,sans-serif;line-height:1.5">'
  '<h1>Clareia Eleições: acompanhe o 2º turno de 2026</h1>'
  '<p>' + _DESC + ' Que ninguém vote no escuro.</p>'
  '<p>Esta página precisa de JavaScript para mostrar os dados ao vivo. Os mesmos dados estão abertos, em JSON:</p><ul>'
  + "".join(f'<li><a href="data/{n}.json">{d}</a></li>' for n, d in _conj) +
  '</ul><p>A Clareia Eleições (antes Verita Eleições) é independente, sem ligação com partidos, campanhas ou institutos de pesquisa. '
  'Instagram: <a href="https://www.instagram.com/clareiaeleicoes/">@clareiaeleicoes</a>. Código e dados: '
  '<a href="https://github.com/aluadocoelho/Eleicoes-de-2026">github.com/aluadocoelho/Eleicoes-de-2026</a>.</p></div></noscript>')

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Clareia Eleições · Acompanhe o 2º turno de 2026: Flávio Bolsonaro × Lula</title>
<meta name="description" content="Clareia Eleições: acompanhe o 2º turno de 2026 entre Flávio Bolsonaro e Lula. Pesquisas, checagens, boatos desmentidos, agenda e debates, em linguagem simples e com a fonte de cada informação.">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="Clareia Eleições">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="Clareia Eleições · Acompanhe o 2º turno de 2026">
<meta property="og:site_name" content="Clareia Eleições">
<meta property="og:image" content="https://clareiaeleicoes.com.br/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Logo da Clareia Eleições: que ninguém vote no escuro. 2º turno 2026, Flávio Bolsonaro × Lula">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Clareia Eleições · Acompanhe o 2º turno de 2026">
<meta name="twitter:description" content="Pesquisas, checagens, boatos desmentidos e agenda de Flávio Bolsonaro e Lula, com a fonte de cada informação. Que ninguém vote no escuro.">
<meta name="twitter:image" content="https://clareiaeleicoes.com.br/og-image.png">
<meta property="og:description" content="Que ninguém vote no escuro. Pesquisas, checagens, boatos desmentidos e agenda do 2º turno entre Flávio Bolsonaro e Lula, com a fonte de cada informação e os dois lados com o mesmo critério.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://clareiaeleicoes.com.br/">
<link rel="canonical" href="https://clareiaeleicoes.com.br/">
<meta name="theme-color" content="#F6F3FB">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Clareia">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400&display=swap" rel="stylesheet">
<style>
{tokens}{style}</style>
<script type="application/ld+json">{LDJSON}</script>
</head>
<body>
{NOSCRIPT}
{body.strip()}
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>window.d3||document.write('<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"><\\/script>')</script>
<script>{shim}</script>
<script>{script}</script>
<div id="el-ck" role="dialog" aria-modal="false" aria-labelledby="ck-t" aria-describedby="ck-d" tabindex="-1" hidden>
  <h2 id="ck-t">Podemos usar cookies de estatística?</h2>
  <p id="ck-d">Se você aceitar, o Google Analytics usa cookies para contar visitas e ver quais abas são mais lidas. Não usamos para anúncios. Se recusar, o site funciona igual.</p>
  <div class="nt-btns">
    <button type="button" id="ck-no">Recusar</button>
    <button type="button" class="ck-yes" id="ck-yes">Aceitar</button>
  </div>
</div>
<script>
(function () {{
  var GA = "G-2NR8ZVJG0L", KEY = "el-cookies", box = document.getElementById("el-ck"), loaded = false;
  function get() {{ try {{ return localStorage.getItem(KEY); }} catch (e) {{ return null; }} }}
  function set(v) {{ try {{ localStorage.setItem(KEY, v); }} catch (e) {{}} }}
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () {{ window.dataLayer.push(arguments); }};
  gtag("consent", "default", {{analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied"}});
  function load() {{
    if (loaded) return; loaded = true;
    gtag("consent", "update", {{analytics_storage: "granted"}});
    gtag("js", new Date());
    gtag("config", GA, {{allow_google_signals: false, allow_ad_personalization_signals: false}});
    var sc = document.createElement("script"); sc.async = true; sc.src = "https://www.googletagmanager.com/gtag/js?id=" + GA; document.head.appendChild(sc);
  }}
  window.elGA = function (path, title) {{ if (!loaded) return; try {{ gtag("event", "page_view", {{page_title: title, page_location: location.origin + location.pathname + "#" + path}}); }} catch (e) {{}} }};
  function hide() {{ box.hidden = true; }}
  function show() {{ box.hidden = false; setTimeout(function () {{ box.focus({{preventScroll: true}}); }}, 50); }}
  document.getElementById("ck-yes").addEventListener("click", function () {{ set("sim"); hide(); load(); }});
  document.getElementById("ck-no").addEventListener("click", function () {{
    var had = loaded; set("nao"); hide();
    if (had) {{ gtag("consent", "update", {{analytics_storage: "denied"}}); document.cookie.split(";").forEach(function (c) {{ var n = c.split("=")[0].trim(); if (/^_ga/.test(n)) document.cookie = n + "=; Max-Age=0; path=/; domain=.github.io"; document.cookie = n + "=; Max-Age=0; path=/"; }}); location.reload(); }}
  }});
  document.addEventListener("keydown", function (ev) {{ if (ev.key === "Escape" && !box.hidden) hide(); }});
  var op = document.getElementById("el-ck-open"); if (op) op.addEventListener("click", show);
  var v = get();
  if (v === "sim") load(); else if (v !== "nao") setTimeout(show, 2500);
}})();
</script>
<div id="el-notif-bg" hidden></div>
<div id="el-notif" role="dialog" aria-modal="true" aria-labelledby="nt-t" aria-describedby="nt-d" hidden>
  <div class="nt-top">
    <span class="nt-ico" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg></span>
    <div>
      <h2 id="nt-t">Quer receber um aviso quando sair novidade?</h2>
      <p id="nt-d">A gente avisa quando sair pesquisa nova, fala checada ou boato desmentido. Funciona enquanto esta página estiver aberta, mesmo em outra aba.</p>
    </div>
  </div>
  <div class="nt-btns">
    <button type="button" class="nt-no" id="nt-no">Agora não</button>
    <button type="button" class="nt-yes" id="nt-yes">Quero receber</button>
  </div>
</div>
<script>
(function () {{
  var KEY = "el-avisos", box = document.getElementById("el-notif"), openBtn = document.getElementById("el-notif-open");
  var UA = navigator.userAgent || "";
  var inApp = /Instagram|FBAN|FBAV|FB_IAB|FBIOS|Line\/|TikTok|musical_ly|BytedanceWebview|Twitter|LinkedInApp|Snapchat|; wv\)/i.test(UA);
  var iOS = /iPhone|iPad|iPod/.test(UA) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var standalone = window.navigator.standalone === true || (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches);
  var hasAPI = ("Notification" in window);
  var supported = hasAPI && !inApp;
  var reason = supported ? null : (inApp ? "inapp" : (iOS && !standalone ? "ios" : "none"));
  var swReg = null;
  if (supported && "serviceWorker" in navigator) {{
    navigator.serviceWorker.register("sw.js").then(function (r) {{ swReg = r; }}).catch(function () {{}});
    navigator.serviceWorker.addEventListener("message", function (e) {{ if (e.data && e.data.tab) location.hash = e.data.tab; }});
  }}
  function get() {{ try {{ return JSON.parse(localStorage.getItem(KEY) || "null"); }} catch (e) {{ return null; }} }}
  function set(v) {{ try {{ localStorage.setItem(KEY, JSON.stringify(v)); }} catch (e) {{}} }}
  function perm() {{ try {{ return Notification.permission; }} catch (e) {{ return "default"; }} }}
  function on() {{ var s = get(); return supported && perm() === "granted" && s && s.ok; }}
  function notify(title, body, tab) {{
    var o = {{body: body, tag: tab ? "el-novidade" : "el-ok", icon: "icon-192.png", badge: "icon-192.png", lang: "pt-BR", data: {{tab: tab || ""}}}};
    function direct() {{ try {{ var n = new Notification(title, o); n.onclick = function () {{ window.focus(); if (tab) location.hash = tab; n.close(); }}; }} catch (e) {{}} }}
    var ready = ("serviceWorker" in navigator) ? navigator.serviceWorker.getRegistration() : Promise.resolve(null);
    ready.then(function (r) {{ r = r || swReg; if (r && r.showNotification) return r.showNotification(title, o); direct(); }}).catch(direct);
  }}
  function askPerm(cb) {{
    var done = false; function once(p) {{ if (!done) {{ done = true; cb(p); }} }}
    try {{ var r = Notification.requestPermission(once); if (r && r.then) r.then(once, function () {{ once(perm()); }}); }} catch (e) {{ once(perm()); }}
  }}
  var T = document.getElementById("nt-t"), D = document.getElementById("nt-d"), Y = document.getElementById("nt-yes"), N = document.getElementById("nt-no");
  var TXT = {{
    t: T.textContent, d: D.textContent,
    inapp: ["Abra no navegador para receber avisos", "Você está vendo o site dentro de um app, como o Instagram, e esses apps não deixam sites mandarem avisos. Toque nos três pontinhos (⋯) no canto da tela, escolha “Abrir no navegador” e toque em “Receber avisos” de novo."],
    ios: ["No iPhone, falta um passo", "A Apple só libera avisos de sites que estão na Tela de Início. Toque no botão Compartilhar (o quadrado com uma seta para cima), escolha “Adicionar à Tela de Início”, abra o site pelo ícone novo e toque em “Receber avisos” de novo. Precisa do iOS 16.4 ou mais novo."],
    none: ["Este navegador não manda avisos", "Para receber avisos, abra o site no Chrome, Edge, Firefox ou Safari atualizados."],
    denied: ["Os avisos estão bloqueados", "Você ou o navegador bloquearam os avisos deste site. Para liberar, toque no cadeado ao lado do endereço da página, procure “Notificações” e escolha “Permitir”."]
  }};
  var bg = document.getElementById("el-notif-bg"), lastFocus = null;
  function hide() {{ box.hidden = true; bg.hidden = true; document.body.classList.remove("el-nt-lock"); if (lastFocus && lastFocus.focus) {{ try {{ lastFocus.focus({{preventScroll: true}}); }} catch (e) {{}} }} }}
  bg.addEventListener("click", function () {{ if (!Y.hidden) set({{ok: false, at: Date.now()}}); hide(); refreshBtn(); }});
  function show(kind) {{
    if (kind) {{ T.textContent = TXT[kind][0]; D.textContent = TXT[kind][1]; Y.hidden = true; N.textContent = "Entendi"; }}
    else {{ T.textContent = TXT.t; D.textContent = TXT.d; Y.hidden = false; N.textContent = "Agora não"; }}
    if (box.hidden) lastFocus = document.activeElement;
    box.hidden = false; bg.hidden = false; document.body.classList.add("el-nt-lock"); setTimeout(function () {{ (kind ? N : Y).focus({{preventScroll: true}}); }}, 50);
  }}
  function refreshBtn() {{
    if (!openBtn) return;
    openBtn.hidden = false;
    openBtn.textContent = on() ? "Avisos ligados (toque para desligar)" : "Receber avisos de novidades";
  }}
  N.addEventListener("click", function () {{ if (!Y.hidden) set({{ok: false, at: Date.now()}}); hide(); refreshBtn(); }});
  Y.addEventListener("click", function () {{
    if (!supported) {{ show(reason); return; }}
    hide();
    askPerm(function (p) {{
      if (p === "granted") {{
        set({{ok: true, at: Date.now()}});
        notify("Avisos ligados", "Vamos avisar aqui quando sair novidade na Clareia Eleições.");
        hide();
      }} else if (p === "denied") {{
        set({{ok: false, at: Date.now()}});
        show("denied");
      }} else {{
        set({{ok: false, at: Date.now()}});
      }}
      refreshBtn();
    }});
  }});
  document.addEventListener("keydown", function (ev) {{
    if (box.hidden) return;
    if (ev.key === "Escape") {{ hide(); return; }}
    if (ev.key === "Tab") {{ var f = [].slice.call(box.querySelectorAll("button")).filter(function (b) {{ return !b.hidden; }}); if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (ev.shiftKey && document.activeElement === a) {{ ev.preventDefault(); z.focus(); }} else if (!ev.shiftKey && document.activeElement === z) {{ ev.preventDefault(); a.focus(); }} }}
  }});
  if (openBtn) openBtn.addEventListener("click", function () {{
    if (!supported) {{ show(reason); return; }}
    if (on()) {{ set({{ok: false, at: Date.now()}}); refreshBtn(); return; }}
    show(null);
  }});
  refreshBtn();
  var s0 = get(), SEMANA = 7 * 86400000;
  if (supported && perm() === "default" && !(s0 && (s0.ok || Date.now() - s0.at < SEMANA))) setTimeout(function wait() {{ var ck = document.getElementById("el-ck"); if (ck && !ck.hidden) {{ setTimeout(wait, 4000); return; }} show(null); }}, 12000);
  if (!supported) return;

  // Novidades: compara o que chegou em cada nova leitura dos dados (a página relê a cada 3 minutos)
  var seen = null;
  var WATCH = {{
    pesquisas: function (r) {{ return "Nova pesquisa " + r.instituto + ": Flávio " + r.flavio_validos + "% e Lula " + r.lula_validos + "% dos votos válidos."; }},
    checagens: function (r) {{ return "Fala de " + r.candidato + " checada (" + r.veredito + "): " + r.afirmacao; }},
    boatos: function (r) {{ return "Boato desmentido: " + r.boato; }},
    aovivo: function (r) {{ return r.tipo === "Programação" ? null : (r.tipo === "Checagem" ? null : "Ao vivo: " + r.texto); }}
  }};
  var TAB = {{pesquisas: "pesquisas", checagens: "checagem", boatos: "checagem", aovivo: "aovivo"}};
  dash.onData(function () {{
    var snap = {{}}, ready = true;
    Object.keys(WATCH).forEach(function (id) {{ var d = dash.data(id); if (d.status !== "ok") ready = false; else snap[id] = d.data || []; }});
    if (!ready) return;
    if (!seen) {{ seen = {{}}; Object.keys(snap).forEach(function (id) {{ seen[id] = new Set(snap[id].map(function (r) {{ return r.id; }})); }}); return; }}
    var msgs = [];
    Object.keys(snap).forEach(function (id) {{
      snap[id].forEach(function (r) {{
        if (!seen[id].has(r.id)) {{ seen[id].add(r.id); var m = WATCH[id](r); if (m) msgs.push({{m: m, tab: TAB[id]}}); }}
      }});
    }});
    if (!msgs.length || !on() || !document.hidden) return;
    var first = msgs[0];
    var body = msgs.length === 1 ? first.m : first.m + " (e mais " + (msgs.length - 1) + " novidade" + (msgs.length > 2 ? "s" : "") + ")";
    notify("Novidade na Clareia Eleições", body.slice(0, 220), first.tab);
  }});
}})();
</script>
<div vw class="enabled">
  <div vw-access-button class="active"></div>
  <div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>
</div>
<script src="https://vlibras.gov.br/app/vlibras-plugin.js" defer></script>
<script data-goatcounter="https://coelhoaluado.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
<script>
(function () {{
  function show() {{
    fetch("https://coelhoaluado.goatcounter.com/counter/TOTAL.json", {{cache: "no-store"}})
      .then(function (r) {{ return r.ok ? r.json() : null; }})
      .then(function (d) {{
        if (!d) return;
        var n = parseInt(String(d.count).replace(/[^0-9]/g, ""), 10);
        if (!n) return;
        var el = document.getElementById("gc-total");
        el.textContent = n.toLocaleString("pt-BR") + (n === 1 ? " visita" : " visitas") + " desde o lançamento.";
        el.hidden = false;
      }})
      .catch(function () {{}});
  }}
  window.addEventListener("load", function () {{ setTimeout(show, 1500); }});
}})();
</script>
<script>window.addEventListener("load", function () {{ try {{ if (window.VLibras) new window.VLibras.Widget("https://vlibras.gov.br/app"); }} catch (e) {{}} }});</script>
</body>
</html>
"""
html = html.replace("Na página pública, o botão azul do VLibras", "O botão azul do VLibras")
# --- idiomas: links entre as versões (pt, en, es) e seletor de idioma ---
_ALT = ('<link rel="alternate" hreflang="pt-BR" href="https://clareiaeleicoes.com.br/">'
        '<link rel="alternate" hreflang="en" href="https://clareiaeleicoes.com.br/en/">'
        '<link rel="alternate" hreflang="es" href="https://clareiaeleicoes.com.br/es/">'
        '<link rel="alternate" hreflang="x-default" href="https://clareiaeleicoes.com.br/">')
assert html.count('<link rel="canonical" href="https://clareiaeleicoes.com.br/">') == 1
html = html.replace('<link rel="canonical" href="https://clareiaeleicoes.com.br/">', '<link rel="canonical" href="https://clareiaeleicoes.com.br/">' + _ALT)
LANGSW = ('<nav class="el-lang" aria-label="Idioma · Language · Idioma">'
          '<a href="/" hreflang="pt-BR" lang="pt-BR" aria-current="true" title="Português">PT</a>'
          '<a href="/en/" hreflang="en" lang="en" title="English">EN</a>'
          '<a href="/es/" hreflang="es" lang="es" title="Español">ES</a></nav>')
_MARCA = '<div class="el-marca"><svg class="el-marca-svg"'
assert html.count(_MARCA) == 1
html = html.replace(_MARCA, '<div class="el-marca">' + LANGSW + '<svg class="el-marca-svg"', 1)
assert html.count('<div class="el-drw-pe">') == 1
html = html.replace('<div class="el-drw-pe">', '<div class="el-drw-lang">' + LANGSW + '</div><div class="el-drw-pe">', 1)
assert html.count('<p class="el-foot el-foot-btns">') == 1
html = html.replace('<p class="el-foot el-foot-btns">', '<div class="el-foot el-foot-lang">' + LANGSW + '</div><p class="el-foot el-foot-btns">', 1)
_LCSS = """<style>
.el-lang{display:inline-flex;gap:4px;padding:3px;border:2px solid var(--ink,#16181D);border-radius:999px;background:var(--color-panel,#fff)}
.el-lang a{min-width:40px;min-height:36px;display:inline-flex;align-items:center;justify-content:center;border-radius:999px;font-weight:800;font-size:.8125rem;letter-spacing:.06em;color:var(--color-fg,#16181D);text-decoration:none}
.el-lang a[aria-current="true"]{background:#5B2DBF;color:#fff}
.el-lang a:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
.el-marca{position:relative}
.el-marca .el-lang{position:absolute;right:0;top:50%;transform:translateY(-50%)}
.el-drw-lang{margin:14px 4px 4px;display:flex;justify-content:center}
.el-drw-lang .el-lang a{min-width:56px;min-height:44px}
.el-foot-lang{margin:14px 0 4px}
@media (max-width:640px){.el-marca .el-lang{display:none}}
</style>"""
html = html.replace('</head>', _LCSS + '</head>', 1)

# --- vídeos da Clareia: bolinhas no topo e player em tela cheia (arquivos próprios em videos/, lista em data/videos.json) ---
_VHTML = ('<section class="el-vids" id="el-vids" aria-labelledby="el-vids-t"><h2 class="el-vids-t" id="el-vids-t">Vídeos da Clareia</h2>'
          '<div class="el-vids-row" id="el-vids-row">' + ''.join('<span class="el-vb el-vb-sk" aria-hidden="true"><span class="el-vb-r"><span class="el-vb-i"></span></span><span class="el-vb-t">&nbsp;</span></span>' for _ in range(6)) + '</div></section>'
          '<div class="el-vd" id="el-vd" role="dialog" aria-modal="true" aria-labelledby="el-vd-t" hidden>'
          '<div class="el-vd-box"><div class="el-vd-seg" id="el-vd-seg" aria-hidden="true"></div>'
          '<div class="el-vd-top"><p class="el-vd-t" id="el-vd-t"></p><button type="button" class="el-vd-x" id="el-vd-x" aria-label="Fechar o vídeo">×</button></div>'
          '<video class="el-vd-v" id="el-vd-v" playsinline controls preload="none"></video>'
          '<div class="el-vd-pe"><button type="button" class="el-vd-nav" id="el-vd-ant" aria-label="Vídeo anterior">‹</button>'
          '<span class="el-vd-n" id="el-vd-n"></span><a class="el-vd-ig" id="el-vd-ig" target="_blank" rel="noopener noreferrer">Ver no Instagram</a>'
          '<button type="button" class="el-vd-nav" id="el-vd-prox" aria-label="Próximo vídeo">›</button></div></div></div>')
_AV = '<aside class="el-aviso" id="el-aviso"'
assert html.count(_AV) == 1
html = html.replace(_AV, _VHTML + _AV, 1)
_VCSS = """<style>
.el-vids{margin:14px 0 6px;min-height:118px}
.el-vids-t{margin:0 0 8px;font-size:.8125rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--color-fg-muted,#5A5F6B)}
.el-vids-row{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x proximity;padding:2px 2px 6px;scrollbar-width:none}
.el-vids-row::-webkit-scrollbar{display:none}
.el-vb{appearance:none;background:none;border:0;padding:0;margin:0;font:inherit;color:inherit;cursor:pointer;flex:none;width:76px;display:flex;flex-direction:column;align-items:center;gap:6px;scroll-snap-align:start}
.el-vb-r{display:block;width:72px;height:72px;border-radius:50%;padding:3px;box-sizing:border-box;background:linear-gradient(135deg,#FFD43B,#5B2DBF)}
.el-vb.visto .el-vb-r{background:#C9C3D6}
.el-vb-i{display:block;width:100%;height:100%;border-radius:50%;border:3px solid var(--color-panel,#fff);box-sizing:border-box;overflow:hidden;background:#3E2492}
.el-vb-i img{width:100%;height:100%;object-fit:cover;display:block}
.el-vb-t{font-size:.8125rem;font-weight:700;line-height:1.2;text-align:center;max-width:76px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.el-vb:focus-visible{outline:3px solid #FFD43B;outline-offset:3px;border-radius:12px}
.el-vb-sk .el-vb-r{background:#E4DFEE}.el-vb-sk .el-vb-i{background:#EEEAF5}
.el-vd{position:fixed;inset:0;z-index:70;background:rgba(12,9,24,.94);display:flex;align-items:center;justify-content:center}
.el-vd[hidden]{display:none}
.el-vd-box{width:min(100vw,calc((100vh - 150px) * 9 / 16 + 24px),460px);display:flex;flex-direction:column;gap:10px;padding:12px;box-sizing:border-box;color:#fff}
.el-vd-seg{display:flex;gap:4px}
.el-vd-seg i{flex:1;height:4px;border-radius:2px;background:rgba(255,255,255,.3);overflow:hidden;position:relative}
.el-vd-seg i b{position:absolute;inset:0;width:0;background:#FFD43B}
.el-vd-seg i.ok b{width:100%}
.el-vd-top{display:flex;align-items:center;gap:12px}
.el-vd-t{flex:1;margin:0;font-weight:800;font-size:.95rem;line-height:1.3}
.el-vd-x,.el-vd-nav{appearance:none;flex:none;width:44px;height:44px;border-radius:50%;border:2px solid rgba(255,255,255,.6);background:transparent;color:#fff;font-size:1.6rem;line-height:1;cursor:pointer}
.el-vd-nav:disabled{opacity:.3;cursor:default}
.el-vd-v{width:100%;aspect-ratio:9/16;max-height:calc(100vh - 150px);background:#000;border-radius:14px;display:block}
.el-vd-pe{display:flex;align-items:center;gap:10px}
.el-vd-n{font-size:.8125rem;color:#D9D2EE;min-width:48px}
.el-vd-ig{flex:1;text-align:center;color:#16181D;background:#FFD43B;border-radius:999px;padding:10px 14px;font-weight:800;font-size:.875rem;text-decoration:none}
.el-vd-ig[hidden]{visibility:hidden;display:block}
.el-vd-x:focus-visible,.el-vd-nav:focus-visible,.el-vd-ig:focus-visible{outline:3px solid #FFD43B;outline-offset:2px}
body.el-vd-lock{overflow:hidden}
</style>"""
html = html.replace('</head>', _VCSS + '</head>', 1)
_VJS = """<script>(function(){
  var B=/\\/(en|es)\\//.test(location.pathname)?"../":"", sec=document.getElementById("el-vids"), row=document.getElementById("el-vids-row");
  var dlg=document.getElementById("el-vd"), v=document.getElementById("el-vd-v"), T=document.getElementById("el-vd-t"), N=document.getElementById("el-vd-n"), IG=document.getElementById("el-vd-ig"), SEG=document.getElementById("el-vd-seg");
  var ant=document.getElementById("el-vd-ant"), prox=document.getElementById("el-vd-prox"), L=[], i=0, volta=null, visto={};
  try{visto=JSON.parse(localStorage.getItem("el-vid-visto")||"{}")||{}}catch(e){}
  function guarda(){try{localStorage.setItem("el-vid-visto",JSON.stringify(visto))}catch(e){}}
  function esc(t){return String(t==null?"":t).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function desenha(){
    row.innerHTML=L.map(function(x,k){return '<button type="button" class="el-vb'+(visto[x.id]?' visto':'')+'" data-k="'+k+'" aria-label="'+esc(x.titulo)+'"><span class="el-vb-r"><span class="el-vb-i"><img src="'+B+esc(x.bolinha)+'" alt="" width="66" height="66" loading="lazy" decoding="async"></span></span><span class="el-vb-t">'+esc(x.curto)+'</span></button>'}).join("");
  }
  function abre(k){
    i=k; var x=L[i]; T.textContent=x.titulo; N.textContent=(i+1)+" / "+L.length;
    if(x.instagram){IG.href=x.instagram;IG.hidden=false}else{IG.hidden=true}
    SEG.innerHTML=L.map(function(_,j){return '<i class="'+(j<i?'ok':'')+'"><b></b></i>'}).join("");
    ant.disabled=i===0; prox.disabled=i===L.length-1;
    v.poster=B+x.capa; v.src=B+x.video; var p=v.play(); if(p&&p.catch)p.catch(function(){});
    visto[x.id]=1; guarda(); var b=row.querySelector('[data-k="'+i+'"]'); if(b)b.classList.add("visto");
    if(dlg.hidden){volta=document.activeElement;dlg.hidden=false;document.body.classList.add("el-vd-lock");document.getElementById("el-vd-x").focus()}
    if(window.gtag)try{gtag("event","video_open",{video_id:x.id})}catch(e){}
  }
  function fecha(){v.pause();v.removeAttribute("src");v.load();dlg.hidden=true;document.body.classList.remove("el-vd-lock");if(volta&&volta.focus)volta.focus()}
  row.addEventListener("click",function(e){var b=e.target.closest(".el-vb[data-k]");if(b)abre(+b.getAttribute("data-k"))});
  document.getElementById("el-vd-x").addEventListener("click",fecha);
  ant.addEventListener("click",function(){if(i>0)abre(i-1)}); prox.addEventListener("click",function(){if(i<L.length-1)abre(i+1)});
  dlg.addEventListener("click",function(e){if(e.target===dlg)fecha()});
  v.addEventListener("ended",function(){if(i<L.length-1)abre(i+1)});
  v.addEventListener("timeupdate",function(){var s=SEG.children[i];if(s&&v.duration)s.firstChild.style.width=(v.currentTime/v.duration*100)+"%"});
  document.addEventListener("keydown",function(e){if(dlg.hidden)return;if(e.key==="Escape")fecha();else if(e.key==="ArrowRight"&&i<L.length-1)abre(i+1);else if(e.key==="ArrowLeft"&&i>0)abre(i-1);else if(e.key==="Tab"){var f=[].slice.call(dlg.querySelectorAll("button:not([disabled]),a:not([hidden]),video"));var a=f[0],z=f[f.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}});
  var x0=null;dlg.addEventListener("touchstart",function(e){x0=e.touches[0].clientX},{passive:true});
  dlg.addEventListener("touchend",function(e){if(x0==null)return;var d=e.changedTouches[0].clientX-x0;x0=null;if(Math.abs(d)>60){if(d<0&&i<L.length-1)abre(i+1);else if(d>0&&i>0)abre(i-1)}},{passive:true});
  (window.__tmP||Promise.resolve()).then(function(){return fetch(B+"data/videos.json",{cache:"no-cache"})}).then(function(r){return r.ok?r.json():[]}).then(function(rows){
    if(window.__tradRows)rows=window.__tradRows("videos",rows);
    L=(rows||[]).filter(function(x){return x&&x.video}); if(!L.length){sec.hidden=true;return} desenha();
  }).catch(function(){sec.hidden=true});
})();</script>"""
html = html.replace('</body>', _VJS + '</body>', 1)

# --- computador: página mais larga, menu inteiro à vista e topo mais justo (pedido do dono em 21/10) ---
_DCSS = """<style>
@media (min-width:900px){
 .el{padding-top:22px}
 .el-wrap{max-width:1280px}
 .el-marca-svg{height:72px}
 .el-sticky{padding-top:6px}
 .el-marca{margin-bottom:0}
 .el-tabs{justify-content:space-between;gap:2px}
 .el-tab{padding:9px 13px}
}
@media (min-width:700px) and (max-width:1339px){
 .el-tab svg{display:none}
 .el-tab{padding:9px 12px}
}
@media (min-width:700px) and (max-width:1099px){.el-tab{padding:8px 10px;font-size:.875rem}}
@media (min-width:700px) and (max-width:1139px){.el-tab{padding:8px 8px;font-size:.8125rem;gap:5px}}
@media (min-width:700px) and (max-width:1019px){.el .el-tabs{flex-wrap:wrap;justify-content:center;gap:4px 6px;border-radius:26px;overflow:visible}.el-sticky>.el-tabs .el-tab[data-tab="sobre"]{margin-left:0}}
</style>"""
html = html.replace('</head>', _DCSS + '</head>', 1)
open(out_path, "w").write(html)
print("ok", len(html))
