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

Fase 0 (documentação e decisões) concluída. O desenvolvimento segue o [`roadmap.md`](docs/roadmap.md), uma fase por vez, começando pela Fase 1 (setup).

## Ferramentas

`uv`, `ruff`, `pytest` e `taskipy`. Os comandos principais serão disponibilizados via `taskipy` a partir da Fase 1.
