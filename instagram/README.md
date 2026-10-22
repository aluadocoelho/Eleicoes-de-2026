# Instagram da Clareia Eleições (antes Verita Eleições)

Fluxo com aprovação:

1. A cada novidade, uma tarefa agendada cria as três peças (feed, story e reels) (JPEG/MP4) e a legenda e envia para um ramo `instagram/<id>`, em pastas `instagram/fila/<id>-feed/`, `instagram/fila/<id>-story/` etc.
2. A automação `instagram-revisao.yml` abre um pull request com as imagens, a legenda e as fontes.
3. **Aprovar = fazer o merge.** Descartar = fechar o pull request.
4. No merge, `instagram.yml` publica pela API oficial do Instagram e move a pasta para `instagram/publicados/<id>/`, com o link do post em `resultado.json`.

`post.json`: `{"tipo": "feed"|"carrossel"|"story"|"reels", "titulo": "...", "arquivos": ["feed.jpg"], "legenda": "...", "fontes": ["https://..."], "capa": "capa.jpg (só reels)", "alt": "texto alternativo (feed: texto; carrossel: lista, um por imagem)"}`. O `alt` descreve a imagem para leitores de tela, em uma ou duas frases com os números e o que está escrito na arte; a API do Instagram só aceita em imagens de feed e de carrossel.

As peças são geradas com `python3 instagram/modelos/pecas.py especificacao.json pasta/` (feed e story; modelos `pesquisa`, `lista`, `destaque`) e o reels de 20 s com `python3 instagram/modelos/video.py especificacao.json pasta/` (gera `reels.mp4` com a trilha lo-fi e `capa.jpg`; veja o formato no começo do arquivo). Fontes Source Serif 4 e Public Sans sob a licença SIL Open Font License (arquivos em `modelos/fontes/`).

Segredo necessário no GitHub: `IG_ACCESS_TOKEN` (token de longa duração da conta profissional do Instagram, gerado num app da Meta com a permissão `instagram_business_content_publish`; vale 60 dias).

## Famílias visuais (desde 21/10/2026)

Cada tipo de assunto tem um visual próprio, com as mesmas cores e a marca, para dar para saber do que a peça fala só de bater o olho. Use `"familia"` na especificação do feed/story (`pecas.py`) e do reels (`video.py`):

| Família | Visual | Trilha do reels |
|---|---|---|
| `pesquisa` | lavanda, placar com os dois números e a margem | estrada, pulsar |
| `checagem` | escuro, a fala e o carimbo com o selo | noite, jornal |
| `boato` | branco, o print riscado e o que é verdade | noite |
| `agenda` | amarelo, a data grande | batuque, pulsar, funk-pop |
| `plantao` | roxo com letreiro | jornal, pulso |
| `servico` | branco, passos numerados | batuque, praça |
| `contexto` | papel claro, ENTENDA: carrossel explicativo (capa com contagem, linha do tempo, lado a lado, números, próximos) | estrada, pulsar |
| `engajamento` (só reels) | roxo | funk-pop, batuque, tamborzão, praça |

**Pesquisa com gráfico** (aprovado em 21/10): na família `pesquisa`, o campo `"grafico"` troca o placar por um gráfico feito com os números de `data/pesquisas.json` (detalhes em `modelos/graficos.py`):

| `grafico` | Mostra | Quando usar |
|---|---|---|
| `rodada` | a mais recente de cada instituto: diferença e margem | peça fixa do fim do dia |
| `tendencia` | as rodadas de um instituto (`"instituto"`) em linhas | pesquisa nova de quem já tem rodada anterior |
| `media` | média simples, cada pesquisa como ponto | de vez em quando |
| `margem` | as duas faixas de uma pesquisa, explicando empate técnico | de vez em quando |
| `totais` | votos totais x válidos de uma pesquisa | quando a pesquisa traz votos totais |

Os campos de cada família estão no começo de `modelos/familias.py`. As trilhas ficam em `modelos/trilhas/` (`gerar_variacoes.py`, `gerar_estilos.py`, `gerar_dinamicas.py`, todas compostas por código, sem direitos de terceiros).

Trilha aprovada pelo dono em 21/10: funk-pop (`clareia-funkpop-30s.wav`, de `gerar_dinamicas.py`), para agenda e engajamento. As versões com batucada (pulsar com batucada, pagode-pop) ficam guardadas, fora do rodízio.
