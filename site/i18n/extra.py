import json
EN={
"Para o 2º turno, a Justiça Eleitoral mudou o endereço de 4.352 seções, menos de 1% do total, por causa de estragos de chuva, reformas e falta de segurança ou de acessibilidade em alguns prédios. Confira o seu antes de sair de casa no app e-Título ou no site do TSE.":
"For the runoff, the Electoral Court changed the address of 4,352 polling stations, less than 1% of the total, because of rain damage, renovations and lack of safety or accessibility in some buildings. Check yours before leaving home in the e-Título app or on the TSE website.",
"Reúne checagens de falas dos dois candidatos feitas por agências como Lupa, Aos Fatos, Estadão Verifica, g1 Fato ou Fake e Ranking dos Políticos. Cada um usa selos e critérios próprios, aqui agrupados em três faixas: verdadeiro, impreciso ou sem contexto, e falso. Os placares mostram só as falas que cada checador escolheu verificar, não são comparáveis entre checadores e não medem a campanha inteira. Em alguns casos os checadores registram de forma diferente até o que foi dito. Toque no nome do checador para abrir a checagem original.":
"Brings together fact-checks of statements by both candidates made by outlets such as Lupa, Aos Fatos, Estadão Verifica, g1 Fato ou Fake and Ranking dos Políticos. Each one uses its own labels and criteria, grouped here into three bands: true, imprecise or missing context, and false. The scores only show the statements each fact-checker chose to check, cannot be compared between fact-checkers and do not measure the whole campaign. In some cases fact-checkers even record what was said differently. Tap the fact-checker's name to open the original fact-check.",
"Removido pelo TSE (sabidamente inverídico, segundo o ministro)": "Removed by the TSE (knowingly untrue, according to the justice)",
"Resultado do {n}º turno, em votos válidos: {t}": "First round result, in valid votes: {t}",
"Barra: Flávio Bolsonaro com {n}% e Lula com {n}% dos votos válidos, na média das pesquisas.": "Bar: Flávio Bolsonaro with {n}% and Lula with {n}% of valid votes, in the poll average.",
"{t}: Flávio {n}% e Lula {n}% das falas checadas classificadas como falsas": "{t}: Flávio {n}% and Lula {n}% of checked statements rated false",
"{t}: Flávio — e Lula {n}% das falas checadas classificadas como falsas": "{t}: Flávio — and Lula {n}% of checked statements rated false",
"{t}: Flávio {n}% e Lula — das falas checadas classificadas como falsas": "{t}: Flávio {n}% and Lula — of checked statements rated false",
"{t} (encomenda do Grupo Globo, registro {t}); válidos calculados": "{t} (commissioned by Grupo Globo, registration {t}); valid votes calculated",
"{t} (registro {t}, contratada pela {t}), via {t}": "{t} (registration {t}, commissioned by {t}), via {t}",
}
ES={
"Para o 2º turno, a Justiça Eleitoral mudou o endereço de 4.352 seções, menos de 1% do total, por causa de estragos de chuva, reformas e falta de segurança ou de acessibilidade em alguns prédios. Confira o seu antes de sair de casa no app e-Título ou no site do TSE.":
"Para la segunda vuelta, la Justicia Electoral cambió la dirección de 4.352 mesas de votación, menos del 1% del total, por daños de lluvia, reformas y falta de seguridad o de accesibilidad en algunos edificios. Revisa la tuya antes de salir de casa en la app e-Título o en el sitio del TSE.",
"Reúne checagens de falas dos dois candidatos feitas por agências como Lupa, Aos Fatos, Estadão Verifica, g1 Fato ou Fake e Ranking dos Políticos. Cada um usa selos e critérios próprios, aqui agrupados em três faixas: verdadeiro, impreciso ou sem contexto, e falso. Os placares mostram só as falas que cada checador escolheu verificar, não são comparáveis entre checadores e não medem a campanha inteira. Em alguns casos os checadores registram de forma diferente até o que foi dito. Toque no nome do checador para abrir a checagem original.":
"Reúne verificaciones de declaraciones de los dos candidatos hechas por agencias como Lupa, Aos Fatos, Estadão Verifica, g1 Fato ou Fake y Ranking dos Políticos. Cada una usa sellos y criterios propios, agrupados aquí en tres franjas: verdadero, impreciso o sin contexto, y falso. Los marcadores solo muestran las declaraciones que cada verificador eligió revisar, no se pueden comparar entre verificadores y no miden toda la campaña. En algunos casos los verificadores registran de forma distinta incluso lo que se dijo. Toca el nombre del verificador para abrir la verificación original.",
"Removido pelo TSE (sabidamente inverídico, segundo o ministro)": "Retirado por el TSE (falso a sabiendas, según el ministro)",
"Resultado do {n}º turno, em votos válidos: {t}": "Resultado de la primera vuelta, en votos válidos: {t}",
"Barra: Flávio Bolsonaro com {n}% e Lula com {n}% dos votos válidos, na média das pesquisas.": "Barra: Flávio Bolsonaro con {n}% y Lula con {n}% de los votos válidos, en el promedio de las encuestas.",
"{t}: Flávio {n}% e Lula {n}% das falas checadas classificadas como falsas": "{t}: Flávio {n}% y Lula {n}% de las declaraciones verificadas calificadas como falsas",
"{t}: Flávio — e Lula {n}% das falas checadas classificadas como falsas": "{t}: Flávio — y Lula {n}% de las declaraciones verificadas calificadas como falsas",
"{t}: Flávio {n}% e Lula — das falas checadas classificadas como falsas": "{t}: Flávio {n}% y Lula — de las declaraciones verificadas calificadas como falsas",
"{t} (encomenda do Grupo Globo, registro {t}); válidos calculados": "{t} (encargada por Grupo Globo, registro {t}); válidos calculados",
"{t} (registro {t}, contratada pela {t}), via {t}": "{t} (registro {t}, contratada por {t}), vía {t}",
}
for lg,d in [('en',EN),('es',ES)]:
    u=json.load(open(f'i18n/ui_{lg}.json')); u.update(d); json.dump(u,open(f'i18n/ui_{lg}.json','w'),ensure_ascii=False,indent=0)
print('ok')
