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
| `destaques.json` | Próximos eventos (debates, dia da votação) para o banner da página | `id, tipo, titulo, data, hora_inicio, hora_fim, local, como_assistir, descricao, url` |
| `aovivo.json` | Cobertura ao vivo de debates e entrevistas: programação, momentos e falas checadas na hora | `id, evento, data, hora, tipo, candidato, texto, veredito, categoria, fonte, url` |
| `erratas.json` | Correções feitas nos dados depois de publicados, com o motivo e a fonte | `id, data, conjunto, registro_id, o_que_mudou, antes, depois, motivo, url` |
| `selos.json` | Códigos de verificação de cada informação (gerado automaticamente) | `codigo, conjunto, id, registro, primeira_vez, ainda_publicado` |
| `status.json` | Hora da última atualização e horários das próximas (Brasília) | `id, ultima_atualizacao, horarios, fuso, url` |
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
- **Demais conjuntos**: pesquisas, redes, agenda, campanha e checagens selecionadas exigem ler reportagens e são atualizados por uma tarefa agendada do Claude a cada hora, das 7h às 23h (horário de Brasília), com execuções extras a cada 15 minutos durante debates, com as mesmas regras acima.
- **Ao vivo** (`aovivo.json`): durante debates e entrevistas, tarefas extras do Claude acrescentam momentos e falas checadas mais ou menos a cada meia hora. `evento` é o `id` do evento em `destaques.json`, e `tipo` é um de Programação, Momento, Fala ou Checagem. Uma linha só é Checagem quando o checador publicou o selo, que fica em `veredito`.
- **Página pública** (`index.html`): publicada pelo GitHub Pages a partir da raiz do repositório. Ela lê os arquivos de `data/` a cada visita e de novo a cada 3 minutos com a página aberta. Tem modo claro e escuro (segue o celular e tem um botão para trocar).
- **Códigos de verificação** (`selos.json`): a automação `.github/workflows/selos.yml` roda a cada mudança em `data/` e dá a cada informação um código curto (ex.: `3F9A-12C7`), tirado da impressão digital SHA-256 do conteúdo exato da linha (`scripts/selos.py`). A página mostra o código ao lado de cada informação, e na aba **Verificar** qualquer pessoa digita o código de um print e vê a informação como ela está nos dados. Se uma letra ou número mudar, o código muda. Códigos de versões corrigidas continuam no arquivo com `ainda_publicado: false`. O histórico de commits deste repositório registra, com data e hora, tudo o que foi publicado. Link direto para conferir um código: `https://aluadocoelho.github.io/Eleicoes-de-2026/#verificar=3F9A12C7`.
- **Revisão e erratas** (`erratas.json`): duas vezes por dia uma tarefa do Claude confere as checagens, boatos, pesquisas e registros do ao vivo mais recentes contra as fontes originais (selo, quem falou, números, link). Quando acha erro, corrige o dado e registra aqui o que mudou, como era antes, como ficou e por quê. As erratas aparecem na aba **Verificar** da página.
- **Validação**: toda mudança em `data/` passa por `scripts/validate.py` (`.github/workflows/validate.yml`), que confere chaves, tipos, datas, categorias, ids repetidos e links `https://`. Rode localmente com `python scripts/validate.py`.

## Aviso sobre as fontes e o uso de IA

Este projeto é um **agregador de informações**. Ele não faz pesquisas nem checagens próprias: reúne o que institutos, veículos de imprensa e agências de checagem já publicaram, sempre com o nome e o link da fonte original, onde está o conteúdo completo.

Para respeitar o direito autoral, aqui só entram resumos curtos escritos com palavras próprias e trechos breves de falas públicas dos candidatos, entre aspas. Não são copiados textos inteiros, fotos, vídeos, gráficos ou logotipos de terceiros. O projeto não tem ligação com os veículos, institutos, checadores ou campanhas citados. Se você é autor de algum conteúdo citado e quer correção ou retirada, abra uma issue.

O site e os dados são feitos com ajuda de inteligência artificial (Claude, da Anthropic): coleta, resumos, organização e código. Os dados passam por validação automática e por revisão de qualidade duas vezes por dia, e as correções ficam registradas em `data/erratas.json`. Mesmo assim pode haver erro: confira sempre na fonte.

## Licença

- **Dados** (`data/`): [CC BY 4.0](LICENSE-DADOS.md). Pode usar para qualquer fim, inclusive comercial, citando este projeto e, para cada dado, a fonte original do campo `url`.
- **Código** (`scripts/` e `.github/workflows/`): [MIT](LICENSE).

A licença cobre a compilação, os resumos e as classificações feitos aqui. Os números das pesquisas e os selos das checagens pertencem aos institutos e checadores que os publicaram; este repositório só os reúne e aponta a fonte.

## Erros e correções

Se encontrar um erro, abra uma issue com o link da fonte correta.
