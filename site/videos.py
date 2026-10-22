#!/usr/bin/env python3
"""Prepara os vídeos do site a partir de data/videos.json: cópia leve em 720p (videos/<id>.mp4, 1 a 2 MB),
capa (videos/<id>.jpg) e miniatura redonda da bolinha (videos/<id>-b.jpg). Pula o que já existe.
Cada item: {id, titulo, curto, data, origem (pasta com reels.mp4 e capa.jpg), video, capa, bolinha, instagram}.
Uso: python3 site/videos.py   (na raiz do repositório)
A publicação do Instagram (scripts/instagram_publicar.py) chama adicionar() para cada reels publicado;
no post.json, "site": false deixa o reels fora do site, "curto" dá o nome da bolinha e "titulo_site" o título no player."""
import json, os, subprocess, re
MAX_LISTA = 12   # bolinhas no site; as mais antigas saem da lista (os arquivos ficam)

def preparar(v):
    from PIL import Image
    os.makedirs('videos', exist_ok=True)
    src = os.path.join(v['origem'], 'reels.mp4')
    if not os.path.exists(v['video']):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '29',
                        '-maxrate', '900k', '-bufsize', '1800k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', v['video']], check=True)
    capa = os.path.join(v['origem'], 'capa.jpg')
    if not os.path.exists(v['capa']):
        Image.open(capa).convert('RGB').resize((432, 768), Image.LANCZOS).save(v['capa'], quality=80, optimize=True, progressive=True)
    if not os.path.exists(v['bolinha']):
        im = Image.open(capa).convert('RGB'); w, h = im.size; s = w   # quadrado do meio da tela, onde fica o título
        top = int(h * .30); im.crop((0, top, s, top + s)).resize((168, 168), Image.LANCZOS).save(v['bolinha'], quality=82, optimize=True)
    print(v['id'], os.path.getsize(v['video']) // 1024, 'KB')

def adicionar(pasta, post, link):
    """Chamado pela publicação do Instagram: põe o reels recém-publicado no começo da lista do site."""
    if post.get('tipo') != 'reels' or post.get('site') is False: return
    base = os.path.basename(pasta.rstrip('/'))
    vid = re.sub(r'-reels$', '', base); vid = re.sub(r'[^a-z0-9-]', '', vid.lower())
    lista = json.load(open('data/videos.json')) if os.path.exists('data/videos.json') else []
    if any(x['id'] == vid for x in lista): return
    tit = post.get('titulo_site') or post.get('titulo', '')
    curto = post.get('curto') or (tit.split(':')[0] if ':' in tit else ' '.join(tit.split()[:2]))[:14]
    v = {'id': vid, 'titulo': tit, 'curto': curto, 'data': f'{base[:4]}-{base[4:6]}-{base[6:8]}', 'origem': pasta,
         'video': f'videos/{vid}.mp4', 'capa': f'videos/{vid}.jpg', 'bolinha': f'videos/{vid}-b.jpg', 'instagram': link}
    try:
        preparar(v)
    except Exception as e:
        print('vídeo do site não preparado:', e); return
    lista.insert(0, v)
    json.dump(lista[:MAX_LISTA], open('data/videos.json', 'w'), ensure_ascii=False, indent=1); open('data/videos.json', 'a').write('\n')

if __name__ == '__main__':
    for v in json.load(open('data/videos.json')):
        preparar(v)
