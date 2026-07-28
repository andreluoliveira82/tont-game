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
- [ ] Registrar a seed na configuração inicial da partida quando utilizada. → **adiado para a Fase 5** (`GameRecord`); ver nota abaixo e ADR 0005.
- [x] Testar distribuição.
- [x] Testar reprodução com seed.

> Nota: a seed já é exposta por `DefaultRandomSource.seed`. Seu registro na
> configuração inicial da partida será feito no `GameRecord` (Fase 5). A
> distribuição concreta é o registro histórico; a seed é complementar
> (reprodutibilidade técnica). Ver ADR 0005.

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

Criar cenários completos:

- [ ] partida iniciada;
- [ ] escolha da maleta;
- [ ] rodada 1;
- [ ] oferta ao final da rodada;
- [ ] recusa;
- [ ] rodada seguinte;
- [ ] múltiplas ofertas (incluindo oscilação);
- [ ] aceitação da oferta;
- [ ] simulação pós-jogo após aceitação;
- [ ] fluxo até a Rodada 9;
- [ ] troca final aceita e recusada;
- [ ] tentativa inválida de abertura;
- [ ] tentativa de abrir maleta do jogador;
- [ ] tentativa de continuar jogo encerrado;
- [ ] verificação do histórico completo da partida.

**Critério de saída:** fluxo principal protegido por testes.

---

# Fase 8 — Interface CLI

- [ ] Criar controller.
- [ ] Criar views.
- [ ] Criar presenters (Apresentador).
- [ ] Exibir maleta do jogador.
- [ ] Exibir valores restantes.
- [ ] Exibir valores eliminados.
- [ ] Exibir rodada atual.
- [ ] Exibir oferta.
- [ ] Receber Topa/Não Topa.
- [ ] Conduzir a troca final no endgame.
- [ ] Oferecer e conduzir a simulação pós-jogo.
- [ ] Apresentar comparação entre resultado oficial e hipotético.
- [ ] Implementar tratamento de entradas inválidas.
- [ ] Implementar game loop.

**Critério de saída:** partida completa jogável pelo terminal, com endgame e simulação pós-jogo.

---

# Fase 9 — Refinamento

- [ ] Melhorar experiência visual da CLI.
- [ ] Melhorar mensagens.
- [ ] Revisar tratamento de erros.
- [ ] Revisar testes.
- [ ] Revisar documentação.
- [ ] Criar testes de regressão.
- [ ] Atualizar README.

---

# Fase 10 — Preparação para evolução

Somente após a CLI estar estável:

- [ ] avaliar persistência do `GameRecord` (JSON, SQLite, banco de dados);
- [ ] avaliar GUI;
- [ ] avaliar arquitetura de múltiplas interfaces;
- [ ] avaliar histórico de partidas entre execuções;
- [ ] avaliar configuração de regras;
- [ ] avaliar diferentes estratégias do Banqueiro.

Nenhum item desta fase deve ser implementado antecipadamente sem necessidade.

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
