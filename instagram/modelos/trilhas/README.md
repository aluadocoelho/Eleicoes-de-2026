# Trilhas da Clareia

`verita-lofi-20s.mp3` (e `.wav`) é a trilha padrão dos vídeos da Clareia: lo-fi a 85,7 bpm, piano elétrico quente, baixo redondo e batida abafada, sem agudos e com todas as notas presas no ritmo. Usada pela primeira vez no reels do plantão da quebra de sigilo (19/10/2026).

Original, composta por código: não usa música de terceiros, então pode ir para Instagram, TikTok e YouTube sem problema de direitos.

Para gerar de novo ou mudar a duração: edite `DUR` (duração), `T0` (primeiro impacto) e `LAST` em `gerar_lofi.py` e rode `python3 gerar_lofi.py` (precisa de numpy e scipy). As batidas caem a cada 0,35 s a partir de `T0`; para alinhar um corte do vídeo, coloque-o em `T0 + n × 0,35 s`.

`verita-lofi-media-20s.mp3` (e `.wav`, gerada por `gerar_lofi_media.py`) é a variação "média": mesmo ritmo, em tom maior, com o piano no registro médio, baixo e bumbo mais leves e um chimbal macio. É mais clara e leve que a original, ainda sem agudos estridentes. Foi usada no vídeo de apresentação da Verita (20/10/2026).
