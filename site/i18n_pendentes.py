#!/usr/bin/env python3
"""Lista os textos dos dados que ainda não têm tradução em data/i18n/<lang>.json (inglês e espanhol).

Uso: python3 site/i18n_pendentes.py            -> grava site/i18n/pendentes.json {"en": [...], "es": [...]} e mostra quantos faltam
     python3 site/i18n_pendentes.py --juntar arquivo_en.json arquivo_es.json
                                               -> junta traduções novas ({texto em português: tradução}) na memória de tradução
Campos traduzidos por conjunto: site/i18n/campos.json. Categorias (tipo, veredito, categoria, direcao, origem_campo) também entram.
"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(AQUI)
CAMPOS = json.load(open(os.path.join(AQUI, 'i18n', 'campos.json')))
CAT = ['tipo', 'veredito', 'categoria', 'direcao', 'origem_campo']
def tm(lg):
    p = os.path.join(REPO, 'data', 'i18n', f'{lg}.json')
    return json.load(open(p)) if os.path.exists(p) else {}
def textos():
    out = set()
    for ds, fs in CAMPOS.items():
        p = os.path.join(REPO, 'data', f'{ds}.json')
        if not os.path.exists(p): continue
        for r in json.load(open(p)):
            for f in fs + CAT:
                v = r.get(f)
                if isinstance(v, str) and v.strip(): out.add(v)
    return out
if len(sys.argv) > 1 and sys.argv[1] == '--juntar':
    for lg, arq in zip(('en', 'es'), sys.argv[2:4]):
        novo = json.load(open(arq)); m = tm(lg)
        m.update({k: v for k, v in novo.items() if isinstance(v, str) and v.strip()})
        os.makedirs(os.path.join(REPO, 'data', 'i18n'), exist_ok=True)
        with open(os.path.join(REPO, 'data', 'i18n', f'{lg}.json'), 'w') as f:
            json.dump(dict(sorted(m.items())), f, ensure_ascii=False, indent=1); f.write('\n')
        print(lg, 'agora com', len(m), 'traduções')
else:
    t = textos(); pend = {lg: sorted(x for x in t if x not in tm(lg)) for lg in ('en', 'es')}
    json.dump(pend, open(os.path.join(AQUI, 'i18n', 'pendentes.json'), 'w'), ensure_ascii=False, indent=1)
    print('faltam:', {k: len(v) for k, v in pend.items()})
