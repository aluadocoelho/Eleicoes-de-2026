# Como o site é gerado

- `painel.html`: a página do painel (mesmo conteúdo do painel privado), fonte do site.
- `build_site.py painel.html ../index.html`: gera o site em português (domínio, compartilhamento, desempenho, acessibilidade, idiomas).
- `build_i18n.py ..`: gera `en/index.html` e `es/index.html` a partir do `index.html`. A interface vem de `i18n/ui_en.json` e `i18n/ui_es.json`
  (texto em português -> tradução; `{n}` número, `{c}` código, `{t}` trecho qualquer). O conteúdo que muda vem de `data/i18n/en.json` e `data/i18n/es.json`
  (memória de tradução), mantida pela tarefa agendada de traduções com `i18n_pendentes.py`.
Ordem: `python3 site/build_site.py site/painel.html index.html && python3 site/build_i18n.py .`
