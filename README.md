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

Fases 0 a 10.5 concluídas: documentação e decisões, setup técnico, modelo de domínio, aleatoriedade/distribuição, estratégia do Banqueiro, a camada de aplicação com histórico da partida, o endgame, a simulação pós-jogo, a suíte de testes de integração, a **interface CLI**, o seu **refinamento** e a **narração de encerramento**. Já existem o núcleo do domínio (maletas, estado da partida, 9 rodadas, invariantes), a distribuição aleatória reproduzível, o cálculo das ofertas do Banqueiro, os casos de uso do fluxo normal (`StartGame`, `SelectInitialBriefcase`, `OpenBriefcase`, `ProcessBankerOffer`, `DecideOffer`), o histórico factual (`GameRecord`), o resultado oficial imutável (`OfficialResult`), o endgame (`DecideFinalSwap`, com e sem troca) e a simulação pós-jogo (`RunPostGameSimulation`, cenário `CONTINUE_HOLD`).

A **Fase 8** adicionou uma **interface de linha de comando** (`interface_adapters/cli`: `CliController`, `presenters`, `views`) que orquestra os casos de uso existentes, sem regra de negócio. A CLI: está em **PT-BR**; permite jogar a **partida completa** pelo terminal (seleção da maleta, rodadas, aberturas, ofertas, Topa/Não Topa); conduz o **endgame** com **troca final**; oferece a **simulação pós-jogo após um Topa** e apresenta a **comparação oficial × hipotético**; **trata entradas inválidas** com reprompt; usa formatação monetária brasileira (`R$ 1.000,00`); e aceita uma **seed opcional** para partidas reproduzíveis.

A **Fase 9** refinou a experiência da CLI a partir de testes práticos, **sem** alterar regras de negócio nem a arquitetura (mudanças restritas a `interface_adapters/cli` e testes; texto puro, sem cores, animações, áudio ou GUI): lista as **maletas disponíveis** a cada rodada, mostra um **status compacto** da partida, apresenta um **bloco de decisão** após a oferta (com a oferta em destaque e a **lista completa** dos valores ainda em jogo no momento crítico, sem revelar a média do Banqueiro), revela **as duas maletas** no endgame, aceita **aliases de entrada**, ecoa a **seed** quando fornecida e encerra graciosamente em EOF/`Ctrl-C`.

A **Fase 10** foi uma etapa de **avaliação e decisão** (sem implementação), consolidando a baseline estável e registrando as evoluções futuras como propostas ainda não aprovadas. A **Fase 10.5** acrescentou uma **narração de encerramento** (`interface_adapters/cli/narration.py`): após a linha factual do resultado, uma frase emocional opcional, escolhida de forma determinística, **sem** tocar regras, domínio ou a simulação `CONTINUE_HOLD`.

Com a **Fase 10.5** encerrou-se o **primeiro ciclo de desenvolvimento** (release `1.0.0`): uma versão jogável e estável pelo terminal, com **toda a suíte de testes automatizados passando**.

A **Fase 11** (release `1.1.0`, primeira do **Roadmap 2.0**) adicionou **persistência de partidas concluídas e histórico entre execuções** como capacidade **opcional e aditiva**: cada partida é registrada automaticamente (um JSON por partida, em diretório resolvido pela infraestrutura). A persistência **nunca** impede o jogo de funcionar — falhas degradam graciosamente. O domínio permanece desacoplado da tecnologia de armazenamento (port `GameHistoryRepository`; ver [ADR 0007](docs/decisions/0007-persistencia-do-historico.md)).

A **Fase 12** (release `1.2.0`) completou a experiência de histórico: além de listar (`tont-game history`), o jogador pode **inspecionar uma partida** em detalhe com `tont-game history show <id>`.

A **Release 1.3.0** tornou a CLI **descobrível e instalável**: `tont-game --help`/`--version`, ajuda dos subcomandos e instalação via `pipx`/`uvx` — **sem** publicar no PyPI (adiado). Ainda **não** há analytics nem GUI. As demais evoluções seguem no **Roadmap 2.1** (Fases 14+, ainda não iniciadas) — ver [`roadmap.md`](docs/roadmap.md).

## Requisitos

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/)

## Instalação (para jogar)

A partir de um clone local do projeto, sem precisar do ambiente de desenvolvimento:

```bash
uvx --from . tont-game        # executa sem instalar (isolado)
pipx install .                # instala o comando "tont-game"
```

Depois de instalado, comece por `tont-game --help`, que lista todos os comandos.
Uma vez publicado o repositório, a instalação direta do GitHub também funcionará
(`uvx --from git+https://github.com/andreluoliveira82/tont-game tont-game`).

Quick Start:

```bash
tont-game            # jogar
tont-game --help     # ver todos os comandos
tont-game history    # rever partidas anteriores
```

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
uv run tont-game                  # equivalente, pelo console script (entry point)
uv run tont-game history          # lista suas partidas anteriores
uv run tont-game history show ID  # detalha uma partida pelo id
```

A interface é em Português do Brasil: escolha a maleta inicial, abra maletas a cada rodada, decida **Topa/Não Topa** a cada oferta e, ao final, conduza a troca do endgame ou (após um Topa) a simulação pós-jogo. A cada rodada a CLI mostra as maletas disponíveis e um status compacto; ao final da rodada, um bloco de decisão reúne a oferta e a lista completa dos valores ainda em jogo.

Aliases aceitos nas decisões:

- **Topa:** `t`, `topa`, `s` ou `sim`; **Não Topa:** `n`, `nao` ou `não`.
- **Sim/Não** (troca final e simulação pós-jogo): `s`/`sim` para sim; `n`/`nao`/`não` para não.

## Ferramentas

`uv`, `ruff`, `pytest` e `taskipy`.
