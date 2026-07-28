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

Fases 0 a 4 concluídas: documentação e decisões, setup técnico, modelo de domínio, aleatoriedade/distribuição e estratégia do Banqueiro. Já existem o núcleo do domínio (maletas, estado da partida, 9 rodadas, invariantes), a distribuição aleatória reproduzível e o cálculo das ofertas do Banqueiro. Ainda **não** há casos de uso, histórico da partida (`GameRecord`) nem CLI. O desenvolvimento segue o [`roadmap.md`](docs/roadmap.md), uma fase por vez; o próximo passo é a Fase 5 (casos de uso, `GameRecord` e resultado oficial).

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
| `uv run task run` | executa o ponto de entrada (placeholder até a CLI) |

## Ferramentas

`uv`, `ruff`, `pytest` e `taskipy`.
