#!/usr/bin/env python3
"""Publica no Instagram as peças aprovadas em instagram/fila/.

Cada post é uma pasta instagram/fila/<id>/ com post.json:
  {"tipo": "feed" | "carrossel" | "story" | "reels",
   "arquivos": ["feed.jpg", ...],      # JPEG para imagem, MP4 para vídeo
   "legenda": "texto da legenda",      # não usada em story
   "capa": "capa.jpg"}                 # opcional, só reels
Story com mais de um arquivo vira vários stories, na ordem.

Usa a API do Instagram com login do Instagram (graph.instagram.com).
Variável de ambiente: IG_ACCESS_TOKEN (segredo do GitHub). Os arquivos precisam
estar no GitHub (são lidos pelo endereço raw do commit atual).
Depois de publicar, move a pasta para instagram/publicados/<id>/ com resultado.json.
"""
import json, os, sys, time, shutil, subprocess, urllib.request, urllib.parse, urllib.error

API = 'https://graph.instagram.com/v23.0'
REPO = os.environ.get('GITHUB_REPOSITORY', 'aluadocoelho/Eleicoes-de-2026')
TOKEN = os.environ.get('IG_ACCESS_TOKEN', '')
FILA, FEITOS = 'instagram/fila', 'instagram/publicados'

def chamar(metodo, caminho, **params):
    params['access_token'] = TOKEN
    dados = urllib.parse.urlencode(params).encode()
    url = f'{API}/{caminho}'
    if metodo == 'GET':
        req = urllib.request.Request(url + '?' + dados.decode())
    else:
        req = urllib.request.Request(url, data=dados, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors='replace').replace(TOKEN, '***')
        raise RuntimeError(f'{metodo} {caminho}: HTTP {e.code} {corpo}')

def esperar(cid):
    for _ in range(30):
        st = chamar('GET', cid, fields='status_code,status').get('status_code')
        if st == 'FINISHED': return
        if st in ('ERROR', 'EXPIRED'): raise RuntimeError(f'container {cid}: {st}')
        time.sleep(10)
    raise RuntimeError(f'container {cid}: demorou demais')

def url_raw(sha, pasta, nome):
    return f'https://raw.githubusercontent.com/{REPO}/{sha}/{pasta}/{urllib.parse.quote(nome)}'

def midia(sha, pasta, nome, **extra):
    if nome.lower().endswith('.mp4'):
        return dict(video_url=url_raw(sha, pasta, nome), **extra)
    if not nome.lower().endswith(('.jpg', '.jpeg')):
        raise RuntimeError(f'{nome}: a API só aceita JPEG (imagem) ou MP4 (vídeo)')
    return dict(image_url=url_raw(sha, pasta, nome), **extra)

def publicar(cid):
    esperar(cid)
    return chamar('POST', 'me/media_publish', creation_id=cid)['id']

def postar(post, sha, pasta):
    tipo, arqs, leg = post['tipo'], post['arquivos'], post.get('legenda', '')
    ids = []
    if tipo == 'feed':
        ids.append(publicar(chamar('POST', 'me/media', caption=leg, **midia(sha, pasta, arqs[0]))['id']))
    elif tipo == 'carrossel':
        filhos = []
        for a in arqs[:10]:
            extra = {'media_type': 'VIDEO'} if a.lower().endswith('.mp4') else {}
            c = chamar('POST', 'me/media', is_carousel_item='true', **midia(sha, pasta, a, **extra))['id']
            esperar(c); filhos.append(c)
        ids.append(publicar(chamar('POST', 'me/media', media_type='CAROUSEL', children=','.join(filhos), caption=leg)['id']))
    elif tipo == 'story':
        for a in arqs:
            ids.append(publicar(chamar('POST', 'me/media', media_type='STORIES', **midia(sha, pasta, a))['id']))
    elif tipo == 'reels':
        extra = {'media_type': 'REELS', 'caption': leg, 'share_to_feed': 'true'}
        if post.get('capa'): extra['cover_url'] = url_raw(sha, pasta, post['capa'])
        ids.append(publicar(chamar('POST', 'me/media', **midia(sha, pasta, arqs[0], **extra))['id']))
    else:
        raise RuntimeError(f'tipo desconhecido: {tipo}')
    links = []
    for i in ids:
        try: links.append(chamar('GET', i, fields='permalink').get('permalink'))
        except Exception: links.append(None)
    return ids, links

def main():
    if not TOKEN:
        print('IG_ACCESS_TOKEN não configurado: nada publicado.'); return 1
    if not os.path.isdir(FILA): print('Fila vazia.'); return 0
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    falhas = 0
    for pid in sorted(os.listdir(FILA)):
        pasta = f'{FILA}/{pid}'
        cfg = f'{pasta}/post.json'
        if not os.path.isfile(cfg): continue
        post = json.load(open(cfg))
        try:
            ids, links = postar(post, sha, pasta)
        except Exception as e:
            falhas += 1
            print(f'[{pid}] FALHOU: {e}')
            continue
        os.makedirs(FEITOS, exist_ok=True)
        destino = f'{FEITOS}/{pid}'
        shutil.move(pasta, destino)
        json.dump({'publicado_em': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'ids': ids, 'links': links},
                  open(f'{destino}/resultado.json', 'w'), ensure_ascii=False, indent=1)
        print(f'[{pid}] publicado: {links}')
    return 1 if falhas else 0

if __name__ == '__main__':
    sys.exit(main())
