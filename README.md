# Eleições 2026 · 2º turno — dados abertos

**Página pública:** https://aluadocoelho.github.io/Eleicoes-de-2026/ — versão em linguagem simples, feita para celular, que lê os dados deste repositório.

Dados reunidos sobre o 2º turno da eleição presidencial de 2026 (Flávio Bolsonaro, PL × Lula, PT; votação em 25 de outubro): pesquisas de intenção de voto, redes sociais, agenda e eventos das campanhas, checagens de fatos e boatos desmentidos.

Cada linha traz o link (`url`) da reportagem ou checagem de onde a informação saiu. Os textos são resumos com palavras próprias; para o conteúdo completo, siga o link.

## Como usar

Os arquivos ficam em `data/` e podem ser lidos direto, sem chave nem cadastro:

```
https://raw.githubusercontent.com/aluadocoelho/Eleicoes-de-2026/main/data/pesquisas.json
```

Troque `pesquisas.json` pelo conjunto que quiser. Exemplo em Python:

```python
import json, urllib.request
url = "https://raw.githubusercontent.com/aluadocoelho/Eleicoes-de-2026/main/data/pesquisas.json"
pesquisas = json.load(urllib.request.urlopen(url))
```

## Conjuntos

Todos são listas JSON de objetos. Campos sem informação vêm como `null`. Datas no formato `AAAA-MM-DD`.

| Arquivo | O que tem | Campos |
|---|---|---|
| `pesquisas.json` | Pesquisas nacionais de 2º turno registradas no TSE | `id, instituto, divulgacao, campo, amostra, margem, flavio_validos, lula_validos, flavio_totais, lula_totais, fonte, url` |
| `primeiro_turno.json` | Resultado do 1º turno (votos válidos) | `candidato, partido, pct, votos` |
| `transferencia.json` | Voto no 2º turno de eleitores de candidatos derrotados | `id, grupo, pesquisa, flavio, lula, url` |
| `redes.json` | Métricas dos perfis oficiais (Bites, Quaest) | `id, metrica, periodo, lula, flavio, fonte, url` |
| `sinais.json` | Leituras de inteligência digital | `id, data, sinal, fonte, url` |
| `agenda.json` | Agenda dos candidatos na reta final | `data, lula, flavio, url` |
| `campanha.json` | Apoios, decisões do TSE, debates, estratégia | `id, data, tipo, descricao, fonte, url` |
| `checagens_placar.json` | Contagem de selos por candidato, checador e evento | `id, candidato, agencia, evento, data, total, verdadeiro, impreciso, falso, nota, url` |
| `checagens.json` | Falas dos candidatos checadas, uma por linha | `id, data, candidato, agencia, evento, afirmacao, veredito, categoria, explicacao, url, direcao` |
| `boatos.json` | Conteúdos virais desmentidos ou retirados pelo TSE | `id, data, alvo, boato, veredito, agencia, explicacao, url, beneficiado, origem_campo, origem_detalhe, tema` |
| `factcheck_api.json` | Checagens brutas da Google Fact Check Tools API (aparece após a primeira busca) | `id, termo, afirmacao, quem_disse, data_afirmacao, checador, selo, titulo, data_checagem, url` |

### Critérios

- **Votos válidos** excluem brancos e nulos. Quando a reportagem só traz votos totais, os válidos são calculados e o campo `fonte` diz "válidos calculados".
- **Faixas das checagens** (`categoria` e o placar): cada checador usa selos próprios. Aqui, `verdadeiro` reúne verdadeiro/correto; `falso` reúne falso; `impreciso` reúne todo o resto (exagerado, falta contexto, impreciso, insustentável, subestimado, enganoso etc.). O selo original fica em `veredito`.
- **Placar** conta só falas do próprio candidato. Falas de aliados ficam de fora, e a `nota` diz isso.
- **Tipo de fala** (`direcao`) é uma classificação deste projeto, pelo conteúdo: ataque ao adversário, defesa de si ou do próprio governo, ou proposta e outros temas.
- **Origem dos boatos** (`origem_campo`) só é preenchida com um dos lados quando a checagem, a reportagem ou a decisão do TSE aponta quem publicou. Caso contrário, fica "Não identificada". A origem nunca é deduzida pelo conteúdo.
- **Comparações entre checadores** devem ser feitas com cuidado: cada um escolhe quais falas verificar, então as taxas descrevem as falas checadas, não a campanha inteira.

## Como os dados são atualizados

- **Checagens da Google Fact Check API**: a automação `.github/workflows/factcheck.yml` roda de hora em hora no GitHub Actions e acrescenta checagens novas em `data/factcheck_api.json`. Para ativá-la, crie uma chave gratuita no Google Cloud com a *Fact Check Tools API* habilitada e salve-a como segredo do repositório com o nome `GOOGLE_FACTCHECK_API_KEY` (Settings → Secrets and variables → Actions). Sem a chave, a automação roda e termina sem fazer nada.
- **Demais conjuntos**: pesquisas, redes, agenda, campanha e checagens selecionadas exigem ler reportagens e são atualizados por uma tarefa agendada do Claude, com as mesmas regras acima.
- **Página pública** (`index.html`): publicada pelo GitHub Pages a partir da raiz do repositório. Ela lê os arquivos de `data/` a cada visita, então mostra sempre a versão mais recente dos dados.
- **Validação**: toda mudança em `data/` passa por `scripts/validate.py` (`.github/workflows/validate.yml`), que confere chaves, tipos, datas, categorias, ids repetidos e links `https://`. Rode localmente com `python scripts/validate.py`.

## Licença

- **Dados** (`data/`): [CC BY 4.0](LICENSE-DADOS.md). Pode usar para qualquer fim, inclusive comercial, citando este projeto e, para cada dado, a fonte original do campo `url`.
- **Código** (`scripts/` e `.github/workflows/`): [MIT](LICENSE).

A licença cobre a compilação, os resumos e as classificações feitos aqui. Os números das pesquisas e os selos das checagens pertencem aos institutos e checadores que os publicaram; este repositório só os reúne e aponta a fonte.

## Erros e correções

Se encontrar um erro, abra uma issue com o link da fonte correta.
