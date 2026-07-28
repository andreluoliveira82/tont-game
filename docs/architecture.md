# Arquitetura

## 1. Objetivo

A arquitetura do `tont-game` deve manter as regras de negócio independentes da interface CLI e de detalhes externos.

A primeira interface será CLI, mas o domínio deve permitir futura criação de GUI ou persistência sem reescrever as regras do jogo.

---

## 2. Princípios

### Clean Architecture

As dependências devem apontar para dentro.

O domínio não deve depender de:

- CLI;
- terminal;
- bibliotecas de apresentação;
- persistência;
- frameworks externos.

### SOLID

Aplicar SOLID de maneira pragmática.

Dar atenção especial a:

- Single Responsibility Principle;
- Dependency Inversion Principle.

Não criar interfaces ou abstrações sem necessidade real.

### DDD

Utilizar conceitos de DDD onde agreguem clareza ao domínio.

O foco é modelar corretamente o jogo, não aplicar DDD de maneira burocrática.

---

## 3. Stack

- Python 3.13+
- `uv`
- `pytest`
- `ruff`
- `taskipy`

Dependências adicionais só devem ser introduzidas quando houver necessidade clara.

---

## 4. Estrutura recomendada

```text
tont-game/
├── docs/
│   ├── architecture.md
│   ├── game-rules.md
│   ├── glossary.md
│   ├── prd.md
│   ├── roadmap.md
│   └── decisions/
│       ├── README.md
│       ├── 0001-estrutura-rodadas-e-endgame.md
│       ├── 0002-estrategia-inicial-do-banqueiro.md
│       ├── 0003-troca-final.md
│       ├── 0004-simulacao-pos-jogo.md
│       └── 0005-historico-da-partida-e-persistencia.md
│
├── src/
│   └── tont_game/
│       ├── __init__.py
│       ├── __main__.py               # ponto de entrada (placeholder até a CLI)
│       ├── domain/
│       │   ├── errors.py
│       │   ├── official_values.py
│       │   ├── randomness.py         # port RandomSource
│       │   ├── clock.py              # port Clock (Fase 5)
│       │   ├── identifiers.py        # port GameIdGenerator (Fase 5)
│       │   ├── entities/
│       │   │   ├── briefcase.py
│       │   │   └── game_state.py
│       │   ├── services/
│       │   │   ├── distribution.py   # create_shuffled_game
│       │   │   └── banker.py         # BankerStrategy + DefaultBankerStrategy
│       │   ├── history/              # (Fase 5)
│       │   │   ├── records.py        # BriefcaseOpeningRecord, BankerOfferRecord,
│       │   │   │                     # OfficialResult, Decision, EndingType
│       │   │   ├── round_record.py   # RoundRecord (imutável/frozen)
│       │   │   └── game_record.py    # GameRecord (append-only)
│       │   └── value_objects/
│       │       ├── money.py
│       │       ├── game_status.py
│       │       └── round_schedule.py
│       │
│       ├── application/              # (Fase 5)
│       │   ├── game_session.py       # GameSession (GameState + GameRecord)
│       │   └── use_cases/
│       │       ├── start_game.py
│       │       ├── select_initial_briefcase.py
│       │       ├── open_briefcase.py
│       │       ├── process_banker_offer.py
│       │       ├── decide_offer.py
│       │       ├── decide_final_swap.py         # (Fase 5.5)
│       │       └── run_post_game_simulation.py  # (Fase 6)
│       │
│       ├── interface_adapters/       # (Fase 8)
│       │   └── cli/
│       │       ├── controller.py
│       │       ├── presenters.py
│       │       └── views.py
│       │
│       └── infrastructure/
│           ├── randomness/
│           │   └── random_source.py  # DefaultRandomSource
│           ├── clock.py              # SystemClock (Fase 5)
│           └── identifiers.py        # UuidGameIdGenerator (Fase 5)
│
├── tests/
│   ├── test_smoke.py
│   ├── unit/
│   │   ├── domain/
│   │   └── infrastructure/
│   └── integration/                 # (Fase 7)
│
├── .gitignore
├── llm-instructions.md
├── pyproject.toml
└── README.md
```

Notas:

- `llm-instructions.md` reside **exclusivamente na raiz** do projeto. Não deve ser duplicado em `docs/`.
- A estrutura pode evoluir conforme o projeto amadurecer. Os nomes de arquivos de casos de uso e de módulos de histórico/simulação são indicativos, não obrigatórios.

---

## 5. Convenção de nomenclatura

### Python

Usar `snake_case`.

Exemplos:

- `game_state.py`;
- `open_briefcase.py`;
- `banker.py`.

### Classes

Usar `PascalCase`.

Exemplos:

- `Briefcase`;
- `GameState`;
- `Banker`.

### Funções e métodos

Usar `snake_case`.

### Documentação

Usar `kebab-case`.

Exemplos:

- `game-rules.md`;
- `llm-instructions.md`.

Esta distinção é obrigatória para evitar conflito com as regras de importação de módulos Python.

---

## 6. Camada de domínio

Responsável por:

- entidades;
- value objects;
- invariantes;
- regras centrais;
- serviços de domínio.

Não deve:

- imprimir;
- receber `input`;
- conhecer CLI;
- depender de infraestrutura ou de tecnologia de persistência.

Possíveis elementos:

### `Briefcase`

Representa uma maleta.

### `GameState`

Representa o estado **atual** (corrente) da partida.

### `Banker`

Representa a estratégia de cálculo de oferta.

### `Money`

Pode ser um value object ou abstração equivalente, desde que preserve precisão decimal.

### `GameStatus`

Representa o estado do ciclo de vida da partida.

### `GameRecord`

Representa o histórico estruturado da partida (ver seção 12). Nome indicativo.

### `OfficialResult` e `SimulationResult`

Representam, respectivamente, o resultado oficial e o resultado hipotético da simulação pós-jogo (ver seção 12). Nomes indicativos.

---

## 7. Camada de aplicação

Os casos de uso orquestram o domínio e coordenam `GameState` (estado) com
`GameRecord` (histórico) por meio de uma composição `GameSession`
(`{ game_state, game_record }`).

Casos de uso por fase:

- **Fase 5:** `StartGame`, `SelectInitialBriefcase`, `OpenBriefcase`, `ProcessBankerOffer`, `DecideOffer`.
- **Fase 5.5:** `DecideFinalSwap` (endgame) — orquestra as primitivas de domínio `apply_final_swap` e `reveal_final_and_finish`; transição direta `FINAL_SWAP_PENDING → FINISHED`.
- **Fase 6:** `RunPostGameSimulation`.

### Consistência entre estado e histórico

Regra obrigatória dos casos de uso: **primeiro** a ação é validada/executada com
sucesso no domínio (`GameState`, que é a autoridade sobre regras e invariantes);
**só então** o fato correspondente é registrado no `GameRecord`. O `GameRecord`
não valida operações nem duplica regras de negócio, e uma operação inválida
(exceção do domínio) não deve gerar registro parcial ou "fato fantasma". Não há
transação técnica/rollback no MVP; a consistência é responsabilidade explícita do
desenho dos casos de uso. Ver `docs/decisions/0006-camada-application-e-historico.md`.

Casos de uso não devem conter lógica de apresentação.

---

## 8. Interface Adapters

Responsável por converter:

- entrada da CLI em comandos compreensíveis pela aplicação;
- resultados da aplicação em dados apropriados para apresentação.

A CLI não deve conter regras de negócio. O Apresentador conduz o fluxo de interação (ofertas, decisões, oferta de simulação pós-jogo), mas as regras permanecem no domínio/aplicação.

---

## 9. Infrastructure

Contém detalhes externos ao domínio, implementando **ports** definidos no domínio.

Exemplo:

- fonte de aleatoriedade (`DefaultRandomSource` → port `RandomSource`);
- relógio do sistema (`SystemClock` → port `Clock`, `datetime` UTC);
- geração de identificadores (`UuidGameIdGenerator` → port `GameIdGenerator`, UUID);
- integração futura com persistência;
- integração futura com GUI ou outros adaptadores.

Formatação e localização de datas/valores ficam nas camadas superiores
(Interface Adapters/CLI), não na Infrastructure nem no domínio.

---

## 10. Aleatoriedade

A lógica de domínio não deve depender diretamente de chamadas globais de aleatoriedade quando isso prejudicar testes.

Preferir injeção de uma fonte de aleatoriedade ou mecanismo equivalente.

A simulação pós-jogo não realiza novo embaralhamento: reutiliza a distribuição da partida original.

### Implementação (Fase 3)

- **Port `RandomSource`** (`domain/randomness.py`): `Protocol` com o método `shuffle`. O domínio depende apenas dessa abstração e nunca importa `random`.
- **Serviço de distribuição** (`domain/services/distribution.py`): `create_shuffled_game(random_source, values, schedule)` embaralha os valores oficiais via port e monta um `GameState` válido (maletas `1..26` na ordem embaralhada).
- **Implementação concreta `DefaultRandomSource`** (`infrastructure/randomness/random_source.py`): backed por `random.Random`, com seed opcional. O nome é neutro para não sugerir `random.SystemRandom` (que não é semeável).

Reprodutibilidade: mesma seed → mesma distribuição; sem seed → distribuição não determinística válida. A **distribuição concreta** produzida já reside no `GameState` (cada maleta com seu valor) — é o fato histórico daquela partida e a base sobre a qual a futura simulação pós-jogo opera, sem re-sortear. Ver ADR 0005.

---

## 11. Dinheiro

Utilizar `Decimal`.

Nunca utilizar `float` para representar valores monetários.

A formatação:

```text
R$ 1.000,00
```

é responsabilidade da apresentação.

---

## 12. Estado, histórico, resultado oficial e simulação

A arquitetura deve manter quatro conceitos claramente separados. Os nomes exatos das classes são livres, mas a separação é obrigatória.

### Estado atual da partida

Situação corrente: maletas, rodada atual, oferta pendente, status do ciclo de vida. Muda a cada ação. É consumido para calcular ofertas e validar invariantes.

### Histórico da partida (`GameRecord`)

Registro estruturado, em memória, da narrativa completa: configuração inicial (id, data/hora, valores, distribuição, seed, maleta escolhida), histórico por rodada (maletas abertas, valores revelados, valores restantes no momento, oferta, percentual, decisão) e resultado. Ver `docs/decisions/0005-historico-da-partida-e-persistencia.md`.

No endgame (Fase 5.5), a revelação das duas últimas maletas marca-as como `opened` no `GameState`, mas **não** as registra como aberturas de rodada em `GameRecord`; os fatos do encerramento ficam no `OfficialResult` (a outra maleta é derivável de `initial_distribution`). Ver `docs/decisions/0006-camada-application-e-historico.md`.

### Resultado oficial (`OfficialResult`)

Registrado imediatamente no encerramento e imutável: motivo do encerramento, oferta aceita (quando aplicável), valor oficial recebido, valor real da maleta do jogador, decisão final de troca (quando aplicável) e valor final oficial.

### Simulação pós-jogo (`SimulationResult`)

Resultado hipotético produzido após a aceitação de uma oferta, sem alterar o estado nem o resultado oficial. Ver `docs/decisions/0004-simulacao-pos-jogo.md`.

Objetivos da separação:

- o histórico não deve ser confundido com o estado atual;
- a simulação não deve ser confundida com a continuação oficial da partida;
- o resultado hipotético nunca substitui o resultado oficial.

### Analytics / visão administrativa (intenção futura — fora de escopo)

Há a intenção futura de uma camada administrativa para os donos/operadores do
jogo, capaz de analisar o histórico acumulado de várias partidas (comportamento
das ofertas por rodada, taxas de aceitação, relação entre valor recebido e valor
real da maleta, distribuição de resultados, padrões de decisão, etc.). **Nada
disso faz parte do escopo atual** e não é implementado agora (sem analytics,
métricas, relatórios ou dashboard). A única obrigação hoje é que o `GameRecord`
preserve fatos ricos e bem estruturados, de modo que essa análise seja possível
no futuro sem reconstruir nem alterar o histórico das partidas. Ver
`docs/decisions/0006-camada-application-e-historico.md`.

---

## 13. Estratégia do Banqueiro

A política do Banqueiro deve ser isolada e substituível.

A implementação inicial utiliza uma estratégia baseada em:

- média dos valores restantes (`remaining_values`);
- percentual por rodada.

A estratégia inicial depende apenas do estado atual e da rodada, não do histórico de ofertas. O componente deve permitir evolução futura para estratégias mais sofisticadas sem alterar as entidades centrais. Ver `docs/decisions/0002-estrategia-inicial-do-banqueiro.md`.

### Implementação (Fase 4)

- **Port `BankerStrategy`** (`domain/services/banker.py`): `Protocol` com o método `offer(remaining_values, round_number) -> Money`. Qualquer estratégia substituível o satisfaz.
- **`DefaultBankerStrategy`** (mesmo módulo): política inicial `média(remaining_values) × percentual_da_rodada`, arredondada a centavos **apenas no final** (cálculo em `Decimal`, sem `float`). É **stateless** e **não** recebe/consulta o histórico de ofertas.
- **Percentuais** em `DEFAULT_BANKER_PERCENTAGES: tuple[Decimal, ...]` (9 valores: 0.35–0.95), imutáveis e injetáveis no construtor (validados: quantidade, tipo `Decimal`, faixa `[0, 1]`); sem configuração externa nem persistência.
- A estratégia recebe apenas `Sequence[Money]` + `round_number`; **não** conhece `GameState`, CLI nem infraestrutura. `remaining_values` inclui sempre o valor da maleta do jogador e exclui as maletas já abertas.
- **Oscilação preservada:** nenhum piso crescente, mínimo baseado na oferta anterior ou correção de monotonicidade — a oferta pode subir ou cair conforme a composição dos valores restantes. Ver ADR 0002 e `game-rules.md` §7.
- A validação de **estado da partida** para gerar uma oferta (rodada concluída, partida encerrada) é responsabilidade do futuro caso de uso `ProcessBankerOffer` (Fase 5), não da estratégia.

---

## 14. Persistência

A persistência permanente **não** faz parte do MVP. O histórico é mantido apenas em memória durante a execução.

O domínio e os casos de uso não devem se acoplar a nenhuma tecnologia de persistência. Deve ser possível, no futuro, persistir um `GameRecord` completo (por exemplo em JSON, SQLite ou banco de dados) sem alterar as regras centrais.

Não criar camada de persistência complexa por antecipação. Ver `docs/decisions/0005-historico-da-partida-e-persistencia.md`.

---

## 15. Testabilidade

O domínio deve ser executável e testável sem CLI.

A aplicação deve permitir testes de fluxo como:

1. iniciar partida;
2. escolher maleta;
3. abrir maletas ao longo das 9 rodadas;
4. calcular oferta ao final de cada rodada;
5. recusar;
6. avançar rodada;
7. aceitar oferta (com posterior simulação pós-jogo opcional), ou
8. chegar ao endgame, decidir a troca final e finalizar.

---

## 16. Dependências

Regra de direção:

```text
Infrastructure
      ↓
Interface Adapters
      ↓
Application
      ↓
Domain
```

O domínio não deve depender das camadas externas.

---

## 17. Evitar overengineering

Não criar:

- múltiplas fábricas sem necessidade;
- interfaces para cada classe;
- abstrações sem comportamento substituível;
- camada de persistência antecipada;
- padrões apenas por convenção.

A arquitetura deve servir ao jogo, não o contrário.
