# tont-game

Implementação digital do jogo "Topa ou Não Topa", com interface de linha de comando (CLI) em Português do Brasil.

A CLI é a primeira interface do projeto, não o seu núcleo: as regras de negócio residem em um domínio independente da interface, preparado para futura evolução (GUI, persistência), conforme descrito na documentação.

## Documentação

A documentação oficial do projeto está em `docs/` e na raiz:

- [`llm-instructions.md`](llm-instructions.md) — regras operacionais para o desenvolvimento assistido por LLM (permanece exclusivamente na raiz).
- [`docs/prd.md`](docs/prd.md) — requisitos do produto.
- [`docs/game-rules.md`](docs/game-rules.md) — regras oficiais do jogo (fonte de verdade das regras de negócio).
- [`docs/glossary.md`](docs/glossary.md) — vocabulário do domínio.
- [`docs/architecture.md`](docs/architecture.md) — arquitetura e organização técnica.
- [`docs/roadmap.md`](docs/roadmap.md) — fases de desenvolvimento.
- [`docs/decisions/`](docs/decisions/) — registros de decisão (ADRs).

Ordem de leitura recomendada antes de qualquer desenvolvimento: `llm-instructions.md` → `prd.md` → `game-rules.md` → `glossary.md` → `architecture.md` → `roadmap.md` → `docs/decisions/`.

## Resumo do jogo

- 26 maletas, cada uma com um valor monetário.
- O jogador escolhe uma maleta inicial, que fica protegida durante as rodadas.
- 9 rodadas de abertura: `6, 5, 4, 3, 2, 1, 1, 1, 1` (24 maletas abertas).
- Ao final de cada rodada, o Banqueiro faz uma oferta; o jogador escolhe **Topa** (aceita, encerra) ou **Não Topa** (continua).
- Ao final da Rodada 9 restam duas maletas fechadas; após a última oferta, se o jogador recusar, decide opcionalmente pela **troca final**.
- Após aceitar uma oferta, o jogador pode executar uma **simulação pós-jogo** opcional, que não altera o resultado oficial.

Detalhes completos em [`docs/game-rules.md`](docs/game-rules.md) e nos ADRs.

## Estado do projeto

Fases 0 a 8 concluídas: documentação e decisões, setup técnico, modelo de domínio, aleatoriedade/distribuição, estratégia do Banqueiro, a camada de aplicação com histórico da partida, o endgame, a simulação pós-jogo, a suíte de testes de integração e a **interface CLI**. Já existem o núcleo do domínio (maletas, estado da partida, 9 rodadas, invariantes), a distribuição aleatória reproduzível, o cálculo das ofertas do Banqueiro, os casos de uso do fluxo normal (`StartGame`, `SelectInitialBriefcase`, `OpenBriefcase`, `ProcessBankerOffer`, `DecideOffer`), o histórico factual (`GameRecord`), o resultado oficial imutável (`OfficialResult`), o endgame (`DecideFinalSwap`, com e sem troca) e a simulação pós-jogo (`RunPostGameSimulation`, cenário `CONTINUE_HOLD`).

A **Fase 8** adicionou uma **interface de linha de comando** (`interface_adapters/cli`: `CliController`, `presenters`, `views`) que orquestra os casos de uso existentes, sem regra de negócio. A CLI: está em **PT-BR**; permite jogar a **partida completa** pelo terminal (seleção da maleta, rodadas, aberturas, ofertas, Topa/Não Topa); conduz o **endgame** com **troca final**; oferece a **simulação pós-jogo após um Topa** e apresenta a **comparação oficial × hipotético**; **trata entradas inválidas** com reprompt; usa formatação monetária brasileira (`R$ 1.000,00`); e aceita uma **seed opcional** para partidas reproduzíveis. O projeto tem **180 testes passando**. Ainda **não** há analytics nem persistência. O desenvolvimento segue o [`roadmap.md`](docs/roadmap.md), uma fase por vez; o próximo passo é a **Fase 9 — Refinamento** (ainda não iniciada).

## Requisitos

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/)

## Como configurar e validar

```bash
uv sync            # cria o ambiente e instala as dependências
uv run task check  # format (--check) + lint + testes
```

Comandos disponíveis via `taskipy`:

| Comando | Ação |
|---|---|
| `uv run task test` | executa os testes (`pytest`) |
| `uv run task lint` | análise estática (`ruff check`) |
| `uv run task format` | formatação (`ruff format`) |
| `uv run task check` | `format --check` + `lint` + `test` |
| `uv run task run` | inicia a CLI do jogo (`python -m tont_game`) |

## Como jogar

```bash
uv run python -m tont_game        # partida aleatória
uv run python -m tont_game 42     # partida reproduzível (seed 42)
```

A interface é em Português do Brasil: escolha a maleta inicial, abra maletas a cada rodada, decida **Topa/Não Topa** a cada oferta e, ao final, conduza a troca do endgame ou (após um Topa) a simulação pós-jogo.

## Ferramentas

`uv`, `ruff`, `pytest` e `taskipy`.
