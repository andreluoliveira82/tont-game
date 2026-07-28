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
│       │   ├── entities/
│       │   │   ├── briefcase.py
│       │   │   └── game_state.py
│       │   ├── services/
│       │   │   ├── distribution.py   # create_shuffled_game
│       │   │   └── banker.py         # (Fase 4)
│       │   └── value_objects/
│       │       ├── money.py
│       │       ├── game_status.py
│       │       └── round_schedule.py
│       │
│       ├── application/              # (Fase 5)
│       │   └── use_cases/
│       │       ├── start_game.py
│       │       ├── select_initial_briefcase.py
│       │       ├── open_briefcase.py
│       │       ├── process_banker_offer.py
│       │       ├── decide_offer.py
│       │       ├── swap_briefcase.py
│       │       ├── reveal_final_briefcase.py
│       │       └── run_post_game_simulation.py
│       │
│       ├── interface_adapters/       # (Fase 8)
│       │   └── cli/
│       │       ├── controller.py
│       │       ├── presenters.py
│       │       └── views.py
│       │
│       └── infrastructure/
│           └── randomness/
│               └── random_source.py  # DefaultRandomSource
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

Os casos de uso orquestram o domínio.

Exemplos:

- `StartGame`;
- `SelectInitialBriefcase`;
- `OpenBriefcase`;
- `ProcessBankerOffer`;
- `DecideOffer`;
- `SwapBriefcase` (troca final do endgame);
- `RevealFinalBriefcase`;
- `RunPostGameSimulation`.

Casos de uso não devem conter lógica de apresentação.

---

## 8. Interface Adapters

Responsável por converter:

- entrada da CLI em comandos compreensíveis pela aplicação;
- resultados da aplicação em dados apropriados para apresentação.

A CLI não deve conter regras de negócio. O Apresentador conduz o fluxo de interação (ofertas, decisões, oferta de simulação pós-jogo), mas as regras permanecem no domínio/aplicação.

---

## 9. Infrastructure

Contém detalhes externos ao domínio.

Exemplo:

- fonte de aleatoriedade;
- integração futura com persistência;
- integração futura com GUI ou outros adaptadores.

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

### Resultado oficial (`OfficialResult`)

Registrado imediatamente no encerramento e imutável: motivo do encerramento, oferta aceita (quando aplicável), valor oficial recebido, valor real da maleta do jogador, decisão final de troca (quando aplicável) e valor final oficial.

### Simulação pós-jogo (`SimulationResult`)

Resultado hipotético produzido após a aceitação de uma oferta, sem alterar o estado nem o resultado oficial. Ver `docs/decisions/0004-simulacao-pos-jogo.md`.

Objetivos da separação:

- o histórico não deve ser confundido com o estado atual;
- a simulação não deve ser confundida com a continuação oficial da partida;
- o resultado hipotético nunca substitui o resultado oficial.

---

## 13. Estratégia do Banqueiro

A política do Banqueiro deve ser isolada e substituível.

A implementação inicial utiliza uma estratégia baseada em:

- média dos valores restantes (`remaining_values`);
- percentual por rodada.

A estratégia inicial depende apenas do estado atual e da rodada, não do histórico de ofertas. O componente deve permitir evolução futura para estratégias mais sofisticadas sem alterar as entidades centrais. Ver `docs/decisions/0002-estrategia-inicial-do-banqueiro.md`.

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
