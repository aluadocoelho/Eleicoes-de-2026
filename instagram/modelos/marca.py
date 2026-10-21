"""Marca da Clareia Eleições: a lâmpada em forma de C, com o arco de luz em degradê azul-vermelho.

icone(px, forma='circulo')  -> SVG com fundo roxo, contorno e sombra amarelos ('circulo' ou 'quadrado')
simbolo(cor='#fff')          -> só o desenho (grupo SVG centralizado em 66,66 num viewBox 0 0 140 140)
"""
import itertools
NOME, ARROBA = 'Clareia', '@clareiaeleicoes'
FORMA = 'circulo'   # troque para 'quadrado' se quiser o ícone quadrado
ROXO, AMARELO, AZUL, VERM = '#3E2492', '#FFD43B', '#2D6BE0', '#E23A3A'
_BULBO = ('M23.64 -28.47 A30 30 0 1 0 -22.98 9.28 C-15.91 17.70 -12 20 -12 28 L12 28 C12 20 15.91 17.70 22.98 9.28 '
          'A30 30 0 0 0 27.81 1.24')
_ARCO = 'M35.60 -35.86 A44 44 0 0 1 41.35 5.05'
_n = itertools.count()

def simbolo(cor='#fff', escala=1):
    gid = f'clr{next(_n)}'
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AZUL}"/>'
            f'<stop offset="1" stop-color="{VERM}"/></linearGradient></defs>'
            f'<g transform="translate(66 66) scale({escala}) translate(-6.22 0.79)">'
            f'<path d="{_BULBO}" fill="none" stroke="{cor}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{_ARCO}" fill="none" stroke="url(#{gid})" stroke-width="8" stroke-linecap="round"/>'
            f'<rect x="-12" y="37" width="24" height="7" rx="3.5" fill="{cor}"/></g>')

def icone(px, forma=None, sombra=True):
    forma = forma or FORMA
    if forma == 'quadrado':
        sh = f'<rect x="16" y="16" width="116" height="116" rx="30" fill="{AMARELO}"/>' if sombra else ''
        fr = f'<rect x="8" y="8" width="116" height="116" rx="30" fill="{ROXO}" stroke="{AMARELO}" stroke-width="6"/>'
    else:
        sh = f'<circle cx="74" cy="74" r="58" fill="{AMARELO}"/>' if sombra else ''
        fr = f'<circle cx="66" cy="66" r="58" fill="{ROXO}" stroke="{AMARELO}" stroke-width="6"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 140 140">{sh}{fr}{simbolo(escala=.86 if forma != "quadrado" else 1)}</svg>')
