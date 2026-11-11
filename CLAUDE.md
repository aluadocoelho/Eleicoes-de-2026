# Clareia Eleições — guia para o Claude Code

Site neutro e agregador sobre eleições (https://clareiaeleicoes.com.br), antes "Verita Eleições".
Instagram @clareiaeleicoes · TikTok @oficialclareiaeleicoes · Painel: https://claude.ai/artifact/6oknQwxSnmbV42xHkMjv76

## Estrutura
- `site/painel.html`: fonte do site (uma página com abas `.el-page`). Nunca edite `index.html`, `en/` ou `es/` à mão: são gerados.
- `data/*.json`: conjuntos de dados (plantão, checagens, boatos, mundo, entenda, manchetes, coberturas…). Esquemas em `scripts/validate.py`.
- `data/coberturas.json` + `data/coberturas/<id>.json`: hub de coberturas (aba Coberturas). Blocos: `texto`, `cadeiras`, `lista`.
- `data/manchetes.json`: "Novidades" no topo da Início (5 mais recentes).
- `data/i18n/en.json|es.json`: memória de tradução dos dados. `site/i18n/ui_en.json|ui_es.json`: textos fixos (chave = texto exato em português). Campos traduzidos por conjunto: `site/i18n/campos.json`.
- `instagram/`: modelos (`modelos/`), fila (`fila/<id>/post.json`), agendados (`agendado/<AAAAMMDDHHMM>__<id>/`), publicados.

## Comandos
- Build: `python3 site/build_site.py site/painel.html index.html && python3 site/build_i18n.py .`
- Validar: `python3 scripts/validate.py`
- Traduções pendentes: `python3 site/i18n_pendentes.py` → traduzir → `python3 site/i18n_pendentes.py --juntar en.json es.json`
- Teste local: `python3 -m http.server 8765` e `python3 scripts/teste_site.py http://localhost:8765` (depois `git checkout -- teste-site`)
- Ordem para mudar dados: editar JSON → validate → i18n_pendentes/juntar → build → testar → commit em main.

## Instagram
- Publicar = merge de PR com pastas em `instagram/fila/` (workflow `instagram.yml`). Agendados: `instagram/agendado/` + `instagram-agenda.yml`.
- **Nunca publicar nem fazer merge sem o OK explícito do dono.** Abrir PR e mostrar as peças.
- Sem story (o dono compartilha o reels nos Stories). Feed + reels.
- Legenda em bloco de código para copiar; no máximo 5 hashtags; "Link na bio"; story ≤ 120 caracteres.
- Só @ conferidos: @lulaoficial, @flaviobolsonaro, @tsejus, @infomoney, @exame, @poder360, @cnnbrasil, @sbtnews. Outros só depois de confirmar.
- Visual: logo no início, títulos grandes, respiro, sem repetir a marca. Caixas sempre com borda e **sombra dura** (nunca faixa colorida lateral/superior).
- Reels: abertura e fechamento 3 s (sem animação de saída), telas de conteúdo 4 s (pouco texto) ou 5 s (muito). Motion de verdade: mapas, símbolos, carimbos/selos, números animados, sombra dura também nos elementos; caixas de texto não podem ser o único recurso.
- Cores de candidato (Flávio #1F4FA8, Lula #D62B2B) só para dados de candidato.
- Não reproduzir personagens/obras protegidos (ex.: Wally).

## Linha editorial
- Neutro, mas **imparcial não é omisso**: mesma régua para qualquer lado, crítica baseada em fatos e fontes.
- Toda informação com fonte e link. Sites com linha partidária declarada (FONTES.md, seção H) nunca são fonte única.
- Sem travessão (—), sem adjetivos/juízo sobre candidatos, nunca escrever "não estou escolhendo lado". Promessa aparece como promessa. O que não foi confirmado é dito como não confirmado.

## Regras de segurança
- Nunca colar chaves ou tokens; segredos ficam nos GitHub Secrets.
- Mudanças de conta/configuração e exclusões só com aprovação do dono.
- Subagentes e tarefas agendadas: preferir Sonnet (economia de tokens).

## Tarefas agendadas (ficam na conta do claude.ai, não no repositório)
Plantão (:35, 7h–23h, até 31/12) · Checagens e boatos (8h27 e 19h27) · Reação do mundo (9h17 e 20h17, até 30/11) · Disparar agenda do Instagram (9h02/15h02/18h02, até 02/11) · Vigiar forks (8h52).
Datas fixas: diplomação 12/12/2026 · posse 05/01/2027 · comando de Câmara e Senado 01/02/2027.
