"""Busca checagens publicadas sobre os candidatos na Google Fact Check Tools API.

Agências como Lupa e Aos Fatos marcam suas checagens no padrão ClaimReview, que
o Google reúne nessa API. O script consulta cada termo, normaliza o resultado e
grava data/factcheck_api.json (mantendo o que já estava lá e acrescentando o
que for novo). É uma fonte bruta: os selos vêm como cada agência publicou,
sem agrupamento.

Requer a variável de ambiente GOOGLE_FACTCHECK_API_KEY (chave gratuita criada
no Google Cloud com a "Fact Check Tools API" ativada). Sem ela, o script avisa
e termina sem erro, para não quebrar a automação.

Uso: GOOGLE_FACTCHECK_API_KEY=... python scripts/fact_check_api.py
"""
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "factcheck_api.json"
ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
TERMOS = ["Lula", "Flávio Bolsonaro"]
MAX_DIAS = 60
POR_PAGINA = 100
MAX_PAGINAS = 5


def buscar(termo, chave):
    itens, token = [], None
    for _ in range(MAX_PAGINAS):
        q = {"query": termo, "languageCode": "pt", "maxAgeDays": MAX_DIAS,
             "pageSize": POR_PAGINA, "key": chave}
        if token:
            q["pageToken"] = token
        url = ENDPOINT + "?" + urllib.parse.urlencode(q)
        with urllib.request.urlopen(url, timeout=30) as r:
            dados = json.load(r)
        itens += dados.get("claims", [])
        token = dados.get("nextPageToken")
        if not token:
            break
    return itens


def normalizar(claim, termo):
    linhas = []
    for rev in claim.get("claimReview", []):
        url = rev.get("url") or ""
        if not url.startswith("https://"):
            continue
        linhas.append({
            "id": url,
            "termo": termo,
            "afirmacao": claim.get("text"),
            "quem_disse": claim.get("claimant"),
            "data_afirmacao": (claim.get("claimDate") or "")[:10] or None,
            "checador": (rev.get("publisher") or {}).get("name") or (rev.get("publisher") or {}).get("site"),
            "selo": rev.get("textualRating"),
            "titulo": rev.get("title"),
            "data_checagem": (rev.get("reviewDate") or "")[:10] or None,
            "url": url,
        })
    return linhas


def main():
    chave = os.environ.get("GOOGLE_FACTCHECK_API_KEY")
    if not chave:
        print("GOOGLE_FACTCHECK_API_KEY não definida; nada a buscar.")
        return 0
    atual = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    por_id = {r["id"]: r for r in atual}
    novos = 0
    for termo in TERMOS:
        try:
            claims = buscar(termo, chave)
        except Exception as e:  # rede, cota ou chave inválida: registra e segue
            print(f"Falha ao buscar {termo!r}: {e}", file=sys.stderr)
            continue
        for c in claims:
            for linha in normalizar(c, termo):
                if linha["id"] not in por_id:
                    novos += 1
                por_id[linha["id"]] = linha
    saida = sorted(por_id.values(), key=lambda r: (r.get("data_checagem") or "", r["id"]), reverse=True)
    OUT.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(saida)} checagens no arquivo ({novos} novas).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
