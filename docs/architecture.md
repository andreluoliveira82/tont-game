# Arquitetura

## 1. Objetivo

A arquitetura do `tont-game` deve manter as regras de negócio independentes da interface CLI e de detalhes externos.

A primeira interface será CLI, mas o domínio deve permitir futura criação de GUI sem reescrever as regras do jogo.

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
│   ├── llm-instructions.md
│   ├── prd.md
│   ├── roadmap.md
│   └── decisions/
│
├── src/
│   └── tont_game/
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── briefcase.py
│       │   │   └── game_state.py
│       │   ├── services/
│       │   │   └── banker.py
│       │   └── value_objects/
│       │
│       ├── application/
│       │   └── use_cases/
│       │       ├── start_game.py
│       │       ├── select_initial_briefcase.py
│       │       ├── open_briefcase.py
│       │       ├── process_banker_offer.py
│       │       └── decide_offer.py
│       │
│       ├── interface_adapters/
│       │   └── cli/
│       │       ├── controller.py
│       │       ├── presenters.py
│       │       └── views.py
│       │
│       └── infrastructure/
│           └── randomness/
│               └── random_source.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .gitignore
├── llm-instructions.md
├── pyproject.toml
└── README.md
```

A estrutura pode evoluir conforme o projeto amadurecer.

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
- depender de infraestrutura.

Possíveis elementos:

### `Briefcase`

Representa uma maleta.

### `GameState`

Representa o estado completo da partida.

### `Banker`

Representa a estratégia de cálculo de oferta.

### `Money`

Pode ser um value object ou abstração equivalente, desde que preserve precisão decimal.

### `GameStatus`

Representa o estado do ciclo de vida da partida.

---

## 7. Camada de aplicação

Os casos de uso orquestram o domínio.

Exemplos:

- `StartGame`;
- `SelectInitialBriefcase`;
- `OpenBriefcase`;
- `ProcessBankerOffer`;
- `DecideOffer`;
- `SwapBriefcase`;
- `RevealFinalBriefcase`.

Casos de uso não devem conter lógica de apresentação.

---

## 8. Interface Adapters

Responsável por converter:

- entrada da CLI em comandos compreensíveis pela aplicação;
- resultados da aplicação em dados apropriados para apresentação.

A CLI não deve conter regras de negócio.

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

## 12. Estratégia do Banqueiro

A política do Banqueiro deve ser isolada e substituível.

A implementação inicial pode utilizar uma estratégia baseada em:

- média dos valores restantes;
- percentual por rodada.

O componente deve permitir evolução futura para estratégias mais sofisticadas sem alterar as entidades centrais.

---

## 13. Testabilidade

O domínio deve ser executável e testável sem CLI.

A aplicação deve permitir testes de fluxo como:

1. iniciar partida;
2. escolher maleta;
3. abrir maletas;
4. calcular oferta;
5. recusar;
6. avançar rodada;
7. aceitar ou finalizar.

---

## 14. Dependências

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

## 15. Evitar overengineering

Não criar:

- múltiplas fábricas sem necessidade;
- interfaces para cada classe;
- abstrações sem comportamento substituível;
- padrões apenas por convenção.

A arquitetura deve servir ao jogo, não o contrário.
