# Trilhas da Clareia

`verita-lofi-20s.mp3` (e `.wav`) é a trilha padrão dos vídeos da Clareia: lo-fi a 85,7 bpm, piano elétrico quente, baixo redondo e batida abafada, sem agudos e com todas as notas presas no ritmo. Usada pela primeira vez no reels do plantão da quebra de sigilo (19/10/2026).

Original, composta por código: não usa música de terceiros, então pode ir para Instagram, TikTok e YouTube sem problema de direitos.

Para gerar de novo ou mudar a duração: edite `DUR` (duração), `T0` (primeiro impacto) e `LAST` em `gerar_lofi.py` e rode `python3 gerar_lofi.py` (precisa de numpy e scipy). As batidas caem a cada 0,35 s a partir de `T0`; para alinhar um corte do vídeo, coloque-o em `T0 + n × 0,35 s`.

`verita-lofi-media-20s.mp3` (e `.wav`, gerada por `gerar_lofi_media.py`) é a variação "média": mesmo ritmo, em tom maior, com o piano no registro médio, baixo e bumbo mais leves e um chimbal macio. É mais clara e leve que a original, ainda sem agudos estridentes. Foi usada no vídeo de apresentação da Verita (20/10/2026).

## Variações (desde 20/10/2026)

Para os vídeos não soarem sempre iguais, `gerar_variacoes.py` gera mais cinco trilhas no mesmo ritmo e com os mesmos pontos de corte (0,7 / 5,6 / 12,6 s), todas normalizadas em cerca de -9 LUFS:

| Nome | Clima | Boa para |
|---|---|---|
| `amanhecer` | violão dedilhado em Ré maior, aro e shaker | anúncios, novidades leves |
| `praca` | kalimba e baixo saltitante em Sol maior, palmas | agenda, convites, chamadas |
| `noite` | vibrafone e pad em Lá menor, chiado de vinil | checagens, boatos, plantão à noite |
| `jornal` | piano elétrico em Mi bemol com melodia curta | pesquisas e números |
| `domingo` | violão e vibrafone em Fá maior, batida bem leve | dia da votação |

No JSON do reels, `"trilha": "noite"` escolhe uma delas (também aceita `verita-lofi-20s.wav` e `verita-lofi-media-20s.wav`). Sem o campo, o `video.py` sorteia uma das sete conforme o conteúdo.
