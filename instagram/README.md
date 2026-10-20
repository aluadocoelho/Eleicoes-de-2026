# Instagram da Verita Eleições

Fluxo com aprovação:

1. A cada novidade, uma tarefa agendada cria as três peças (feed, story e reels) (JPEG/MP4) e a legenda e envia para um ramo `instagram/<id>`, em pastas `instagram/fila/<id>-feed/`, `instagram/fila/<id>-story/` etc.
2. A automação `instagram-revisao.yml` abre um pull request com as imagens, a legenda e as fontes.
3. **Aprovar = fazer o merge.** Descartar = fechar o pull request.
4. No merge, `instagram.yml` publica pela API oficial do Instagram e move a pasta para `instagram/publicados/<id>/`, com o link do post em `resultado.json`.

`post.json`: `{"tipo": "feed"|"carrossel"|"story"|"reels", "titulo": "...", "arquivos": ["feed.jpg"], "legenda": "...", "fontes": ["https://..."], "capa": "capa.jpg (só reels)"}`

As peças são geradas com `python3 instagram/modelos/pecas.py especificacao.json pasta/` (feed e story; modelos `pesquisa`, `lista`, `destaque`) e o reels de 20 s com `python3 instagram/modelos/video.py especificacao.json pasta/` (gera `reels.mp4` com a trilha lo-fi e `capa.jpg`; veja o formato no começo do arquivo). Fontes Source Serif 4 e Public Sans sob a licença SIL Open Font License (arquivos em `modelos/fontes/`).

Segredo necessário no GitHub: `IG_ACCESS_TOKEN` (token de longa duração da conta profissional do Instagram, gerado num app da Meta com a permissão `instagram_business_content_publish`; vale 60 dias).
