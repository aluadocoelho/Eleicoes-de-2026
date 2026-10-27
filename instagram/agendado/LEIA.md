# Peças agendadas

Cada pasta `<AAAAMMDDHHMM>__<id>/` (hora de Brasília) é uma peça aprovada pelo dono com dia e hora marcados.
A ação "Instagram · publicar peças agendadas" roda a cada 10 minutos: quando passa da hora, a pasta vai
para `instagram/fila/<id>/` e é publicada. Para cancelar, apague a pasta. Para mudar a hora, renomeie.
