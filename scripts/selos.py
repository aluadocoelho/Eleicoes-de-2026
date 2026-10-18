"""Gera os códigos de verificação de cada informação publicada (data/selos.json).

Cada linha de cada conjunto recebe um código curto (ex.: "3F9A-12C7"), tirado de
uma impressão digital (SHA-256) do conteúdo exato da linha. Se qualquer letra ou
número da informação mudar, o código muda junto. A página pública mostra o código
ao lado de cada informação, e na aba "Verificar" qualquer pessoa digita o código
e vê a informação como ela está nos dados oficiais.

O arquivo guarda também os códigos antigos: quando uma linha é corrigida, o código
anterior continua no arquivo com "ainda_publicado": false, para que um print
antigo e verdadeiro possa ser conferido. "primeira_vez" é o momento em que o
código apareceu pela primeira vez nos dados (horário UTC).

Uso: python scripts/selos.py
"""
import datetime
import hashlib
import json
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT = DATA / "selos.json"

# conjunto -> campo que identifica a linha
CONJUNTOS = {
    "pesquisas": "id",
    "primeiro_turno": "candidato",
    "transferencia": "id",
    "redes": "id",
    "sinais": "id",
    "agenda": "data",
    "campanha": "id",
    "destaques": "id",
    "checagens_placar": "id",
    "checagens": "id",
    "boatos": "id",
    "aovivo": "id",
}


def codigo(conjunto, registro):
    base = json.dumps({"conjunto": conjunto, "registro": registro}, sort_keys=True,
                      ensure_ascii=False, separators=(",", ":"))
    h = hashlib.sha256(base.encode("utf-8")).hexdigest()[:8].upper()
    return h[:4] + "-" + h[4:]


def main():
    agora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    antigos = []
    if OUT.exists():
        try:
            antigos = json.loads(OUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            antigos = []
    por_codigo = {s["codigo"]: s for s in antigos}
    for s in por_codigo.values():
        s["ainda_publicado"] = False

    novos = 0
    for conjunto, chave in CONJUNTOS.items():
        path = DATA / f"{conjunto}.json"
        if not path.exists():
            continue
        for r in json.loads(path.read_text(encoding="utf-8")):
            c = codigo(conjunto, r)
            if c in por_codigo:
                por_codigo[c]["ainda_publicado"] = True
            else:
                por_codigo[c] = {
                    "codigo": c,
                    "conjunto": conjunto,
                    "id": str(r.get(chave)),
                    "registro": r,
                    "primeira_vez": agora,
                    "ainda_publicado": True,
                }
                novos += 1

    lista = sorted(por_codigo.values(), key=lambda s: (s["conjunto"], s["id"], s["primeira_vez"], s["codigo"]))
    OUT.write_text(json.dumps(lista, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    ativos = sum(1 for s in lista if s["ainda_publicado"])
    print(f"OK: {ativos} informações publicadas com código, {novos} códigos novos, {len(lista) - ativos} versões antigas guardadas.")


if __name__ == "__main__":
    main()
