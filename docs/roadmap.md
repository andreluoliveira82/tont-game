# Roadmap de Desenvolvimento

## Estratégia

O projeto deve ser desenvolvido incrementalmente.

Cada fase deve resultar em um estado executável e validado.

O LLM não deve avançar automaticamente para a próxima fase.

---

# Fase 0 — Documentação e decisões

**Status:** ✅ Concluída — commit `185ab44` (consolidação das especificações e ADRs 0001–0005).

- [x] Revisar `prd.md`.
- [x] Revisar `game-rules.md`.
- [x] Revisar `glossary.md`.
- [x] Revisar `architecture.md`.
- [x] Revisar `llm-instructions.md`.
- [x] Definir decisões pendentes (rodadas/endgame, Banqueiro, troca final, simulação pós-jogo, histórico/persistência).
- [x] Registrar decisões relevantes em `docs/decisions/` (ADRs 0001 a 0005).

**Critério de saída:** documentação consistente e sem ambiguidades críticas.

---

# Fase 1 — Setup

**Status:** ✅ Concluída — commit `0e70da6` (ambiente `uv`, pacote instalável `src/tont_game`, `pytest`/`ruff`/`taskipy` e tarefas).

- [x] Executar `uv init` (equivalente: `pyproject.toml` manual + `uv sync`).
- [x] Configurar Python 3.13+.
- [x] Configurar estrutura `src/`.
- [x] Configurar `pytest`.
- [x] Configurar `ruff`.
- [x] Configurar `taskipy`.
- [x] Criar `pyproject.toml`.
- [x] Criar `.gitignore`.
- [x] Criar `README.md`.
- [x] Configurar comandos:
  - [x] `task test`
  - [x] `task lint`
  - [x] `task format`
  - [x] `task run`
  - [x] `task check`

**Critério de saída:** projeto instala, testa e valida sem funcionalidades do jogo.

---

# Fase 2 — Modelo de domínio

**Status:** ✅ Concluída — commit `5c60f16` (`Money`, `Briefcase`, `GameState`, `GameStatus`, `RoundSchedule`, valores oficiais, invariantes; 43 testes).

- [x] Criar representação de dinheiro com precisão decimal.
- [x] Criar `Briefcase`.
- [x] Criar `GameState` (estado atual).
- [x] Criar `GameStatus` (incluindo estados de endgame e aceitação).
- [x] Criar representação das 9 rodadas e da sequência de aberturas.
- [x] Definir valores oficiais das 26 maletas.
- [x] Criar regras de invariantes (incluindo: duas maletas fechadas ao final da Rodada 9).
- [x] Criar testes unitários.

**Critério de saída:** domínio representa corretamente uma partida inicial e a estrutura das 9 rodadas.

---

# Fase 3 — Aleatoriedade

**Status:** ✅ Concluída — commit `0d5bd32` (port `RandomSource`, serviço `create_shuffled_game`, `DefaultRandomSource`; 13 testes).

- [x] Criar fonte de aleatoriedade (port `RandomSource` no domínio).
- [x] Permitir semente determinística (`DefaultRandomSource(seed=...)`).
- [x] Embaralhar valores (serviço `create_shuffled_game`).
- [x] Associar valores às maletas (via `GameState.create`).
- [x] Registrar a seed na configuração inicial da partida quando utilizada. → **adiado na Fase 3 e concluído na Fase 5** (`StartGame`/`GameRecord`); ver nota abaixo e ADR 0005.
- [x] Testar distribuição.
- [x] Testar reprodução com seed.

> Nota: a seed já é exposta por `DefaultRandomSource.seed`. Seu registro na
> configuração inicial da partida foi **adiado nesta fase e realizado na Fase 5**
> (o `StartGame` grava a seed no `GameRecord`). A distribuição concreta é o
> registro histórico; a seed é complementar (reprodutibilidade técnica). Ver ADR 0005.

**Critério de saída:** partidas podem ser aleatórias e reproduzíveis. ✅ Atendido (distribuição via `DefaultRandomSource`, reprodutível por seed, domínio desacoplado).

---

# Fase 4 — Estratégia do Banqueiro

**Status:** ✅ Concluída — commit `ecbb332` (port `BankerStrategy`, `DefaultBankerStrategy`, percentuais `DEFAULT_BANKER_PERCENTAGES`; 19 testes).

- [x] Criar estratégia de oferta isolada e substituível (port `BankerStrategy` + `DefaultBankerStrategy`).
- [x] Calcular média dos valores restantes (`remaining_values`, incluindo a maleta do jogador).
- [x] Aplicar percentual por rodada (35, 40, 50, 60, 70, 80, 85, 90, 95).
- [x] Arredondar oferta para centavos (apenas o resultado final, em `Decimal`).
- [x] Garantir que a estratégia dependa apenas do estado atual e da rodada (não do histórico de ofertas).
- [x] Testar ofertas nas 9 rodadas.
- [x] Testar oscilação (oferta pode subir ou cair) com valores conhecidos.
- [x] Testar estratégia com valores conhecidos (determinismo).

**Critério de saída:** oferta do Banqueiro é determinística para um estado conhecido. ✅ Atendido.

---

# Fase 5 — Application, GameRecord e Resultado Oficial

**Status:** ✅ Concluída — commit `2661ef7` (camada Application, histórico factual e resultado oficial; 115 testes). **Não** inclui o endgame (Swap/Reveal), que é a Fase 5.5.

Escopo: camada Application (casos de uso do fluxo normal), histórico factual e
resultado oficial. Ver `docs/decisions/0006-camada-application-e-historico.md`.

- [x] Criar a camada `application/` e `GameSession` (composição `GameState` + `GameRecord`).
- [x] `StartGame` (cria estado embaralhado + `GameRecord`: id, `started_at`, distribuição concreta, seed).
- [x] `SelectInitialBriefcase`.
- [x] `OpenBriefcase`.
- [x] `ProcessBankerOffer`.
- [x] `DecideOffer` (Topa: `OfficialResult` imutável; Não Topa intermediário: registra e avança).
- [x] Modelo de histórico no domínio: `GameRecord` (append-only), `RoundRecord` (imutável/frozen), `BriefcaseOpeningRecord`, `BankerOfferRecord` (com percentual), `Decision`, `EndingType`, `OfficialResult` (write-once).
- [x] Ports `Clock` e `GameIdGenerator` (domínio) + implementações `SystemClock` e `UuidGameIdGenerator` (infra).
- [x] Evoluir `GameState`: oferta pendente, `accept_offer`, `reject_offer` e transições de status (`OFFER_PENDING`, `ACCEPTED`; recusa da R9 → `FINAL_SWAP_PENDING`, **sem consumir**).
- [x] Expor `percentage_for_round` no port `BankerStrategy` (auditoria do histórico).
- [x] Testes de domínio, aplicação, infraestrutura e integração (cenário Topa completo).

**Critério de saída:** uma partida pode ser jogada sem CLI até o **Topa**, com `GameRecord` completo e `OfficialResult` imutável; recusas intermediárias são registradas; a recusa da R9 leva o estado a `FINAL_SWAP_PENDING` (endgame não implementado nesta fase). ✅ Atendido.

---

# Fase 5.5 — Endgame

**Status:** ✅ Concluída — commit `b26b11d` (endgame: `DecideFinalSwap`, primitivas de domínio e `OfficialResult.from_final_reveal`; 22 testes novos, 137 no total).

Consumo do estado `FINAL_SWAP_PENDING` e conclusão da partida sem Topa,
respeitando o ADR 0003 (troca final) e o ADR 0006 (Application/histórico).

- [x] Caso de uso único `DecideFinalSwap(swap: bool)` (Application), que orquestra as primitivas de domínio.
- [x] Primitiva de domínio `apply_final_swap()` (troca a maleta do jogador pela única outra maleta fechada).
- [x] Primitiva de domínio `reveal_final_and_finish()` (revela as duas últimas maletas e conclui a partida).
- [x] Transição direta `FINAL_SWAP_PENDING → FINISHED` (sem usar `GameStatus.FINAL_REVEAL`).
- [x] Revelação marca as duas maletas como `opened`, **sem** registrá-las como aberturas de rodada em `GameRecord`.
- [x] `OfficialResult.from_final_reveal(...)` — sem troca (`FINAL_REVEAL_WITHOUT_SWAP`) e com troca (`FINAL_REVEAL_WITH_SWAP`); `decision_round = None`.
- [x] **Sem** novo registro histórico (nem `FinalRevealRecord`/`SwapRecord`): os fatos do endgame ficam em `OfficialResult` + `initial_distribution` + histórico existente (a outra maleta é derivável).
- [x] Consistência estado × histórico (ADR 0006): domínio primeiro, registro depois.
- [x] Testes dos dois desfechos do endgame (com e sem troca) e de operações inválidas.

**Critério de saída:** uma partida que recusa todas as ofertas conclui pelo endgame, com ou sem troca, produzindo `OfficialResult` imutável. ✅ Atendido.

---

# Fase 6 — Simulação pós-jogo

**Status:** ✅ Concluída — commit `f6faba0` (simulação pós-jogo `CONTINUE_HOLD`: serviço de domínio puro + caso de uso fino; 12 testes novos, 149 no total).

Escopo (MVP): derivação pura sobre um `GameRecord` encerrado por **Topa**,
produzindo um `SimulationResult` **separado** (não-histórico). Único cenário:
**`CONTINUE_HOLD`**. Ver `docs/decisions/0004-simulacao-pos-jogo.md`.

- [x] Serviço de domínio puro de simulação (`simulate_continue_hold`, deriva do `GameRecord` imutável; sem ports/infra/estado mutável).
- [x] Caso de uso fino `RunPostGameSimulation` (Application) que delega ao serviço de domínio.
- [x] `SimulationScenario` (apenas `CONTINUE_HOLD`) e `SimulationResult` (frozen: `scenario`, `hypothetical_amount`, `official_amount`).
- [x] Cenário `CONTINUE_HOLD`: `hypothetical_amount = official_result.player_briefcase_value`; `official_amount = official_result.amount_received`.
- [x] Exigir `official_result` presente; caso contrário, `InvalidGameStateError`.
- [x] Garantir que a simulação **não** altera `GameRecord`/`OfficialResult`/`GameState` e **não** é persistida.
- [x] Testes: cenário Topa, determinismo, imutabilidade (oficial/histórico), pré-condição, e delegação do caso de uso.

**Não** nesta fase: decisão de endgame oposta; aceitar ofertas recusadas; troca hipotética em Topa intermediário; recálculo de ofertas; re-sorteio; persistência. (A diferença/comparação são deriváveis, não campos armazenados.)

**Critério de saída:** simulação pós-jogo `CONTINUE_HOLD` funcional, separada da partida oficial, determinística e sem alterar o resultado oficial. ✅ Atendido.

---

# Fase 7 — Testes de integração

**Status:** ✅ Concluída — commit `c7a1b67` (suíte de testes de integração via casos de uso reais; `tests/integration/conftest.py` com dublês/`GameDriver` de testes; **sem** alteração de código de produção; 159 testes no total).

Cenários completos (via casos de uso reais, sem CLI):

- [x] partida iniciada;
- [x] escolha da maleta;
- [x] rodada 1;
- [x] oferta ao final da rodada;
- [x] recusa;
- [x] rodada seguinte;
- [x] múltiplas ofertas (incluindo oscilação);
- [x] aceitação da oferta;
- [x] simulação pós-jogo após aceitação;
- [x] fluxo até a Rodada 9;
- [x] troca final aceita e recusada;
- [x] tentativa inválida de abertura;
- [x] tentativa de abrir maleta do jogador;
- [x] tentativa de continuar jogo encerrado;
- [x] verificação do histórico completo da partida.

**Critério de saída:** fluxo principal protegido por testes. ✅ Atendido.

---

# Fase 8 — Interface CLI

**Status:** ✅ Concluída — commit `a28cbd6` (camada `interface_adapters/cli`: `presenters`, `views` `Console`/`TerminalConsole`, `CliController`; `__main__` como composition root; 21 testes novos, 180 no total).

Camada `interface_adapters/cli` que orquestra os casos de uso existentes, sem
regra de negócio; interface em **PT-BR**; formatação monetária `R$ 1.000,00`.

- [x] Criar controller (`CliController`).
- [x] Criar views (`Console`/`TerminalConsole`).
- [x] Criar presenters (Apresentador).
- [x] Exibir maleta do jogador.
- [x] Exibir valores restantes.
- [x] Exibir valores eliminados. → primeira versão nesta fase (listagem agregada por rodada); **refinado na Fase 9**: a listagem agregada foi removida em favor da revelação de cada maleta no momento da abertura e da lista completa de valores restantes no bloco de decisão.
- [x] Exibir rodada atual.
- [x] Exibir oferta.
- [x] Receber Topa/Não Topa.
- [x] Conduzir a troca final no endgame.
- [x] Oferecer e conduzir a simulação pós-jogo (após Topa).
- [x] Apresentar comparação entre resultado oficial e hipotético.
- [x] Implementar tratamento de entradas inválidas (reprompt).
- [x] Implementar game loop.
- [x] Seed opcional/reprodutibilidade via `__main__` (`python -m tont_game <seed>`).

**Critério de saída:** partida completa jogável pelo terminal, com endgame e simulação pós-jogo. ✅ Atendido.

---

# Fase 9 — Refinamento da CLI

**Status:** ✅ Concluída — commit `2210639` (refinamento de UX da CLI a partir de testes práticos reais; **restrito** a `interface_adapters/cli` e testes; 15 testes novos, 195 no total).

Refinamento **exclusivo** da camada CLI e de seus testes, a partir de partidas
reais, **sem** alterar Domain/Application/Infrastructure, regras de negócio ou
casos de uso, e **sem** cores, animações, áudio ou GUI (texto puro em PT-BR).

- [x] Melhorar experiência visual da CLI (texto puro, sem cores/animações).
- [x] Melhorar mensagens (boas-vindas com orientação; textos mais claros; menos verbosidade).
- [x] Revisar tratamento de erros (encerramento gracioso em EOF/KeyboardInterrupt).
- [x] Revisar testes.
- [x] Revisar documentação (esta sincronização documental).
- [x] Criar testes de regressão (cobrindo o bloco de decisão, o endgame revelado e o encerramento gracioso).
- [x] Atualizar README.

Principais entregas:

- **Descoberta das maletas disponíveis:** exibição dos números das maletas ainda abríveis a cada rodada.
- **Status compacto da partida:** resumo em uma linha (rodada, maleta do jogador, maletas fechadas, faixa de valores).
- **Bloco de decisão após a oferta:** apresentação dedicada entre a oferta e o prompt, com a oferta em destaque (uma única vez) — **sem** revelar a média/fórmula do Banqueiro.
- **Valores completos no momento crítico:** lista **completa** e ordenada dos valores ainda em jogo, agrupada em linhas, sempre exibida no bloco de decisão.
- **Endgame e troca:** revelação das duas maletas finais capturando as identidades **antes** da troca (com e sem troca).
- **Aliases de entrada:** Topa (`t`/`topa`/`s`/`sim`), Não Topa (`n`/`nao`/`não`) e sim/não (`s`/`sim` · `n`/`nao`/`não`).
- **Encerramento gracioso:** tratamento de EOF/KeyboardInterrupt com mensagem de despedida.
- **Eco da seed:** exibição da seed quando fornecida, reforçando a reprodutibilidade.

**Critério de saída:** CLI mais clara e jogável a partir de testes práticos, com o momento da decisão bem apresentado, preservando integralmente a arquitetura e as regras de negócio. ✅ Atendido.

---

# Fase 10 — Preparação para evolução (avaliação e decisão)

**Status:** ✅ Concluída — fase de avaliação/decisão (sem implementação de produto). Nenhum código alterado; nenhum ADR criado.

> **Natureza da fase:** esta é uma fase de **avaliação, investigação e decisão
> arquitetural/produto**. Ela **não implementa funcionalidades de produto**. Seu
> propósito é decidir, com base no estado real do projeto, quais evoluções fazem
> sentido, quais devem ser adiadas ou descartadas, e quais decisões precisam ser
> registradas **antes** de qualquer implementação futura. Nenhum tema abaixo deve
> ser convertido automaticamente em requisito de implementação.

## Conclusão (registro do encerramento)

A Fase 10 foi executada como avaliação e decisão. **Conclusão central: a baseline
atual (Fases 0–9) está estável e é o estado vigente do projeto; nenhuma
implementação adicional está aprovada neste momento.** As Fases 0–9 permanecem
concluídas. A avaliação confirmou que a arquitetura mantém os pontos de extensão
abertos para evoluções futuras, mas nenhum tema tem hoje um driver real que
justifique implementação.

**Decisões por tema avaliado:**

| Tema | Decisão |
|---|---|
| Persistência de resultados concluídos | **Adiar** (sem driver imediato; `GameRecord` já é serializável). |
| Histórico entre execuções | **Adiar** — dependente de persistência (tema anterior). |
| Múltiplas interfaces | **Capacidade arquitetural já validada** pela CLI; **nenhuma ação necessária**. |
| GUI | **Não implementar agora.** |
| Configuração das regras/parâmetros | **Investigar somente quando surgir uma variante concreta** (valores/sequência/percentuais já são injetáveis no código). |
| Estratégias adicionais do Banqueiro | **Não implementar agora** (o port `BankerStrategy` já é suficiente; fórmula preservada). |

**Também descartado por enquanto (sem driver):**

- **Save/resume de partida em andamento** — descartado por enquanto (custo/risco de serializar estado mutável, sem necessidade).
- **Configuração estrutural das regras** (quantidade de maletas, sequência estrutural de rodadas) — descartada por enquanto (tocaria invariantes; sem necessidade).

**Direção futura registrada apenas como proposta (não é decisão vigente):** a
persistência, quando/se ocorrer, poderia usar uma **porta de saída + arquivo JSON
(não banco de dados)**, gravando a **distribuição concreta** (não só a seed).
Isso é **direção potencial condicionada a um driver real**, **não** uma decisão
arquitetural adotada — por isso **nenhum ADR foi criado** nesta fase.

**Propostas de fases futuras — APENAS PROPOSTAS, NÃO APROVADAS:**

- **Fase 11 (proposta, não aprovada):** persistência de resultados concluídos.
- **Fase 12 (proposta, não aprovada):** histórico entre execuções (depende da 11).
- **Fase 13 (proposta, não aprovada):** superfície de configuração (expor parâmetros já injetáveis).

Estas fases **não estão autorizadas para implementação automática**. Cada uma
exige aprovação explícita futura antes de qualquer código.

**Backlog não priorizado** (sem fase associada, sem aprovação): GUI, novas
estratégias do Banqueiro, reconfiguração estrutural das regras e analytics/visão
administrativa.

> **Estado vigente do projeto:** baseline estável (Fases 0–9), com a CLI como
> interface oficial. A conclusão da Fase 10 é deliberadamente um **ponto de
> parada estável**, e **não** uma autorização para iniciar automaticamente a
> Fase 11 ou qualquer implementação.

## Objetivo

Definir, com base no estado atual do projeto (Fases 0–9 concluídas: domínio,
aplicação, histórico, endgame, simulação, testes de integração e CLI refinada),
quais evoluções futuras fazem sentido, quais devem ser descartadas ou adiadas e
quais decisões arquiteturais precisam ser tomadas antes de qualquer implementação.

## Motivação

Vários temas de evolução foram mencionados ao longo do desenvolvimento
(persistência, GUI, múltiplas interfaces, etc.) sem uma decisão consciente sobre
prioridade, valor e impacto. Esta fase existe para **evitar que um agente
posterior implemente prematuramente** uma funcionalidade apenas por ela ter sido
citada como possibilidade, e para produzir um conjunto de decisões explícitas que
guie as fases de implementação seguintes.

## Pré-requisitos

- Fases 0–9 concluídas e documentadas (✅ atendido).
- Working tree limpo e `task check` verde.
- CLI estável como primeira interface.

## Documentos e artefatos a analisar

- `docs/prd.md`, `docs/game-rules.md` (escopo e regras vigentes);
- `docs/architecture.md`, `docs/glossary.md` (arquitetura e vocabulário);
- `docs/decisions/` (ADRs 0001–0006, decisões vigentes — em especial 0005 sobre persistência);
- este `docs/roadmap.md` (histórico das fases);
- código atual de `domain/`, `application/`, `infrastructure/`, `interface_adapters/`;
- suíte de testes atual (unidade + integração) como baseline de estabilidade.

## Temas a avaliar

(Preservados do planejamento original; podem ser reorganizados, mas nenhum é, por
si só, um requisito de implementação. Todos foram **avaliados** na Fase 10 — ver
as decisões na seção "Conclusão"; avaliado **não** significa aprovado para
implementação.)

- [x] Persistência do `GameRecord` (por exemplo JSON, SQLite ou banco de dados);
- [x] Histórico de partidas entre execuções;
- [x] Arquitetura de múltiplas interfaces;
- [x] GUI;
- [x] Configuração das regras (valores oficiais, sequência de rodadas, percentuais);
- [x] Estratégias alternativas do Banqueiro.

## Para cada tema, avaliar (quando aplicável)

- problema/oportunidade que seria resolvido;
- benefício esperado;
- impacto no usuário;
- impacto arquitetural;
- impacto na separação de responsabilidades existente;
- dependências;
- complexidade aproximada;
- riscos;
- alternativas;
- relação com o estado atual do projeto;
- necessidade ou não de ADR;
- recomendação: **seguir**, **adiar** ou **descartar**.

Não é necessário inventar estimativas numéricas nem antecipar decisões ainda não tomadas.

## Entregáveis esperados

1. um relatório de avaliação consolidado dos temas analisados;
2. decisões explícitas (seguir/adiar/descartar) sobre cada tema avaliado;
3. ADRs **somente** quando uma decisão arquitetural relevante justificar (não é obrigatório criar ADR para toda conclusão);
4. atualização deste `roadmap.md` com os próximos passos aprovados;
5. eventual definição de futuras fases de implementação (11+), **caso** aprovadas.

## Critérios de saída

A Fase 10 só é considerada concluída quando:

- os temas previstos tiverem sido avaliados;
- as principais decisões estiverem documentadas;
- não houver ambiguidade sobre o que será feito a seguir;
- eventuais ADRs necessários tiverem sido criados;
- as decisões aprovadas estiverem refletidas no roadmap;
- nenhuma funcionalidade de produto tiver sido implementada antecipadamente;
- `task check` continuar verde;
- o working tree estiver limpo após o commit documental correspondente.

## O que NÃO fazer nesta fase

A Fase 10, por si só, **não** autoriza:

- implementar persistência ou banco de dados;
- implementar GUI ou criar novas interfaces;
- implementar histórico entre execuções;
- alterar regras do jogo;
- criar novas estratégias do Banqueiro;
- refatorar o domínio;
- modificar Application, Domain ou Infrastructure;
- adicionar funcionalidades apenas para "experimentar";
- iniciar qualquer implementação que pertença a uma futura fase.

A Fase 10 produz **decisões e documentação**, não código de produto. Qualquer
implementação decorrente pertence a uma fase futura, aprovada explicitamente.

---

# Fase 10.5 — Refinamento narrativo e celebração da CLI

**Status:** ✅ Concluída — implementada em quatro incrementos (testes da simulação; módulo de narração puro; fiação no Topa; fiação no endgame) e este commit documental.

Fase de refinamento **exclusivo da apresentação da CLI**, a partir de uma decisão
de Game Design/UX congelada. Acrescenta uma **narração de encerramento**: após a
linha factual do resultado, uma frase emocional opcional, escolhida de forma
determinística sob o `RandomSource` já existente. **Sem** alterar regras, domínio,
aplicação, infraestrutura ou a simulação `CONTINUE_HOLD`; **sem** cores,
animações, áudio ou GUI.

Principais entregas:

- **Módulo puro `interface_adapters/cli/narration.py`:** quatro momentos de encerramento — `PEAK` (APOGEU), `FLOOR` (FUNDO), `TRIUMPH` (VITÓRIA), `REGRET` (ARREPENDIMENTO) — classificados por `moment_for(got, gave_up, max_value, min_value)` (precedência PEAK > FLOOR > TRIUMPH > REGRET; régua "muito mais" = pelo menos o dobro; silêncio caso contrário) e um banco estático de mensagens em PT-BR.
- **Informação primeiro:** a linha factual permanece idêntica; a narração vem logo depois. Quando nenhum momento se destaca, o silêncio é intencional.
- **Fiação no fluxo Topa** e **no endgame** (com e sem troca), reutilizando um único helper de apresentação no controller; seleção de variante via `RandomSource` (determinística sob seed).
- **Testes de regressão da simulação:** cobertos os dois vereditos de `simulation_comparison` que faltavam ("Você fez bem em aceitar a oferta." e "Daria no mesmo.").

**Situação da simulação pós-Topa:** permanece **inalterada** — a simulação vigente é `CONTINUE_HOLD` (derivação pura; ADR 0004 e seu Complemento). A **simulação progressiva/retrospectiva** (reprodução das rodadas hipotéticas, revelação progressiva, troca hipotética) permanece **backlog não priorizado** — evolução futura **não aprovada** para implementação.

**Escopo estrito (o que NÃO mudou):** Domain, Application, Infrastructure, `presenters`, regras do jogo, fórmula do Banqueiro e o comportamento de `CONTINUE_HOLD`. Nenhuma dependência externa; nenhuma cor/animação/áudio/GUI.

**Critério de saída:** encerramentos da CLI mais expressivos, com a informação factual preservada, seleção determinística e testável, sem tocar regras ou arquitetura. ✅ Atendido.

---

# Fase 11 — Persistência de partidas + histórico entre execuções

**Status:** ✅ Concluída — primeira fase do Roadmap 2.0 (release `1.1.0`). Concretiza a estratégia de persistência que o ADR 0005 deixou em aberto; ver **ADR 0007**.

Persistência de partidas **concluídas** como **capacidade opcional e aditiva** —
o jogo permanece totalmente jogável sem ela. Nada nas regras, no domínio ou na
simulação `CONTINUE_HOLD` mudou.

Principais entregas:

- **Porta de saída `GameHistoryRepository`** (domínio) + VO `GameHistorySummary` e casos de uso finos `SaveFinishedGame` / `ListGameHistory`.
- **Adaptador `FileGameHistoryRepository`** (infraestrutura): um JSON por partida; diretório resolvido por um **locator** encapsulado na infraestrutura (o resto da aplicação recebe apenas um caminho).
- **Schema público e versionado** (`schema_version`), desacoplado da estrutura interna do `GameRecord` (dinheiro como string, datas ISO-8601, ids como string, enums por valor).
- **Salvamento automático** da partida ao encerrar, com aviso discreto; falha de I/O **degrada graciosamente** (o jogo continua).
- **Comando `tont-game history`** para rever partidas passadas, com despacho preparado para futuros subcomandos (`show`/`stats`/`export`).

**Critério de saída:** partidas concluídas persistidas e revisáveis entre execuções, sem acoplar o domínio a tecnologia de armazenamento e sem quebrar o jogo em caso de falha. ✅ Atendido.

---

# Roadmap 2.0 — Fases futuras (propostas, NÃO aprovadas)

As Fases 0–10.5 constituem o **Ciclo 1**; a **Fase 11** (acima) abriu o Roadmap 2.0
e está concluída. As fases a seguir são **propostas de evolução — ainda NÃO
aprovadas** para implementação; cada uma exige autorização explícita e não deve
ser iniciada automaticamente.

- **Fase 12 (proposta) — Distribuição para jogadores reais:** empacotamento/publicação do console script já existente, para uso por não-desenvolvedores.
- **Fase 13 (proposta) — Superfície de configuração:** expor valores/sequência/percentuais/estratégia (já injetáveis no código), orientada a um driver concreto.
- **Fase 14 (proposta) — Analytics / visão administrativa:** análise do histórico acumulado; depende da Fase 11 e de volume de dados reais.
- **Fase 15 (proposta) — GUI:** segunda interface gráfica reutilizando o núcleo, somente com demanda validada.

**Backlog não priorizado:** simulação progressiva/retrospectiva pós-Topa; estratégias alternativas do Banqueiro; reconfiguração estrutural das regras; internacionalização; remoção do `GameStatus.FINAL_REVEAL` (dívida cosmética).

---

## Definição de pronto

Uma fase está concluída quando:

- código implementado;
- testes passando;
- lint passando;
- formatação aplicada;
- documentação atualizada;
- critérios de saída atendidos.

O LLM deve informar explicitamente:

- fase concluída;
- arquivos criados/alterados;
- testes executados;
- comandos executados;
- problemas encontrados;
- próximo passo sugerido.
