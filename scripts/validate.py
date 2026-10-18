"""Valida os arquivos de data/ antes de aceitar qualquer mudança.

Confere, para cada conjunto: que o arquivo é uma lista de objetos, que toda
linha tem exatamente as chaves esperadas, que ids são únicos, que valores de
categoria estão entre os permitidos, que números são números e que todo link
começa com https://. Sai com código 1 e lista os problemas se algo falhar.

Uso: python scripts/validate.py
"""
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

SCHEMAS = {
    "pesquisas": {
        "key": "id",
        "fields": ["id", "instituto", "divulgacao", "campo", "amostra", "margem",
                   "flavio_validos", "lula_validos", "flavio_totais", "lula_totais", "fonte", "url"],
        "numbers": ["amostra", "margem", "flavio_validos", "lula_validos", "flavio_totais", "lula_totais"],
        "dates": ["divulgacao"],
        "required": ["id", "instituto", "divulgacao", "flavio_validos", "lula_validos", "url"],
    },
    "primeiro_turno": {
        "key": "candidato",
        "fields": ["candidato", "partido", "pct", "votos"],
        "numbers": ["pct", "votos"],
        "required": ["candidato", "partido", "pct"],
    },
    "transferencia": {
        "key": "id",
        "fields": ["id", "grupo", "pesquisa", "flavio", "lula", "url"],
        "numbers": ["flavio", "lula"],
        "required": ["id", "grupo", "pesquisa", "flavio", "lula", "url"],
    },
    "redes": {
        "key": "id",
        "fields": ["id", "metrica", "periodo", "lula", "flavio", "fonte", "url"],
        "numbers": ["lula", "flavio"],
        "required": ["id", "metrica", "periodo", "lula", "flavio", "fonte", "url"],
    },
    "sinais": {
        "key": "id",
        "fields": ["id", "data", "sinal", "fonte", "url"],
        "dates": ["data"],
        "required": ["id", "data", "sinal", "fonte", "url"],
    },
    "agenda": {
        "key": "data",
        "fields": ["data", "lula", "flavio", "url"],
        "dates": ["data"],
        "required": ["data", "lula", "flavio"],
    },
    "campanha": {
        "key": "id",
        "fields": ["id", "data", "tipo", "descricao", "fonte", "url"],
        "dates": ["data"],
        "enums": {"tipo": ["Resultado", "Apoio", "Justiça Eleitoral", "Debate", "Estratégia"]},
        "required": ["id", "data", "tipo", "descricao", "fonte", "url"],
    },
    "checagens_placar": {
        "key": "id",
        "fields": ["id", "candidato", "agencia", "evento", "data", "total", "verdadeiro", "impreciso", "falso", "nota", "url"],
        "numbers": ["total", "verdadeiro", "impreciso", "falso"],
        "dates": ["data"],
        "enums": {"candidato": ["Lula", "Flávio"]},
        "required": ["id", "candidato", "agencia", "evento", "data", "total", "verdadeiro", "impreciso", "falso", "url"],
    },
    "checagens": {
        "key": "id",
        "fields": ["id", "data", "candidato", "agencia", "evento", "afirmacao", "veredito", "categoria", "explicacao", "url", "direcao"],
        "dates": ["data"],
        "enums": {
            "candidato": ["Lula", "Flávio"],
            "categoria": ["Verdadeiro", "Impreciso ou sem contexto", "Falso"],
            "direcao": ["Ataque ao adversário", "Defesa de si ou do próprio governo", "Proposta ou outro tema"],
        },
        "required": ["id", "data", "candidato", "agencia", "afirmacao", "veredito", "categoria", "url", "direcao"],
    },
    "boatos": {
        "key": "id",
        "fields": ["id", "data", "alvo", "boato", "veredito", "agencia", "explicacao", "url",
                   "beneficiado", "origem_campo", "origem_detalhe", "tema"],
        "dates": ["data"],
        "enums": {
            "alvo": ["Lula", "Flávio"],
            "beneficiado": ["Lula", "Flávio"],
            "origem_campo": ["Campo de Flávio", "Campo de Lula", "Não identificada"],
        },
        "required": ["id", "data", "alvo", "boato", "veredito", "agencia", "url", "beneficiado", "origem_campo"],
    },
}


def check(name, spec, rows):
    errs = []
    if not isinstance(rows, list):
        return [f"{name}: o arquivo precisa ser uma lista de objetos"]
    seen = set()
    expected = set(spec["fields"])
    for i, r in enumerate(rows):
        where = f"{name}[{i}]"
        if not isinstance(r, dict):
            errs.append(f"{where}: não é um objeto")
            continue
        keys = set(r)
        if keys != expected:
            missing, extra = expected - keys, keys - expected
            if missing:
                errs.append(f"{where}: faltam chaves {sorted(missing)}")
            if extra:
                errs.append(f"{where}: chaves a mais {sorted(extra)}")
        k = r.get(spec["key"])
        if k in seen:
            errs.append(f"{where}: {spec['key']} repetido: {k!r}")
        seen.add(k)
        for f in spec.get("required", []):
            if r.get(f) in (None, ""):
                errs.append(f"{where}: campo obrigatório vazio: {f}")
        for f in spec.get("numbers", []):
            v = r.get(f)
            if v is not None and not isinstance(v, (int, float)):
                errs.append(f"{where}: {f} deveria ser número, veio {v!r}")
        for f in spec.get("dates", []):
            v = r.get(f)
            if v is not None and not DATE.match(str(v)):
                errs.append(f"{where}: {f} deveria ser AAAA-MM-DD, veio {v!r}")
        for f, allowed in spec.get("enums", {}).items():
            v = r.get(f)
            if v is not None and v not in allowed:
                errs.append(f"{where}: {f}={v!r} fora de {allowed}")
        u = r.get("url")
        if "url" in expected and u is not None and not str(u).startswith("https://"):
            errs.append(f"{where}: url precisa começar com https://")
    if name == "checagens_placar":
        for i, r in enumerate(rows):
            try:
                if r["verdadeiro"] + r["impreciso"] + r["falso"] != r["total"]:
                    errs.append(f"{name}[{i}]: verdadeiro + impreciso + falso ≠ total")
            except (KeyError, TypeError):
                pass
    if name == "boatos":
        for i, r in enumerate(rows):
            if r.get("alvo") and r.get("beneficiado") and r["alvo"] == r["beneficiado"]:
                errs.append(f"{name}[{i}]: beneficiado não pode ser o próprio alvo")
    return errs


def main():
    errs = []
    for name, spec in SCHEMAS.items():
        path = DATA / f"{name}.json"
        if not path.exists():
            errs.append(f"{name}: arquivo data/{name}.json não encontrado")
            continue
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errs.append(f"{name}: JSON inválido ({e})")
            continue
        errs += check(name, spec, rows)
    if errs:
        print("Problemas encontrados:")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(SCHEMAS)} conjuntos válidos.")


if __name__ == "__main__":
    main()
