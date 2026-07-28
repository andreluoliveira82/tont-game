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

Escopo: camada Application (casos de uso do fluxo normal), histórico factual e
resultado oficial. **Não** inclui o endgame (Swap/Reveal), que fica na Fase 5.5.
Ver `docs/decisions/0006-camada-application-e-historico.md`.

- [ ] Criar a camada `application/` e `GameSession` (composição `GameState` + `GameRecord`).
- [ ] `StartGame` (cria estado embaralhado + `GameRecord`: id, `started_at`, distribuição concreta, seed).
- [ ] `SelectInitialBriefcase`.
- [ ] `OpenBriefcase`.
- [ ] `ProcessBankerOffer`.
- [ ] `DecideOffer` (Topa: `OfficialResult` imutável; Não Topa intermediário: registra e avança).
- [ ] Modelo de histórico no domínio: `GameRecord` (append-only), `RoundRecord`, `BriefcaseOpeningRecord`, `BankerOfferRecord` (com percentual), `Decision`, `OfficialResult` (write-once).
- [ ] Ports `Clock` e `GameIdGenerator` (domínio) + implementações `SystemClock` e `UuidGameIdGenerator` (infra).
- [ ] Evoluir `GameState`: oferta pendente, `accept_offer`, `reject_offer` e transições de status (`OFFER_PENDING`, `ACCEPTED`; recusa da R9 → `FINAL_SWAP_PENDING`, **sem consumir**).
- [ ] Expor `percentage_for_round` no port `BankerStrategy` (auditoria do histórico).
- [ ] Testes de domínio, aplicação, infraestrutura e integração (cenário Topa completo).

**Critério de saída:** uma partida pode ser jogada sem CLI até o **Topa**, com `GameRecord` completo e `OfficialResult` imutável; recusas intermediárias são registradas; a recusa da R9 leva o estado a `FINAL_SWAP_PENDING` (endgame não implementado nesta fase).

---

# Fase 5.5 — Endgame

Consumo do estado `FINAL_SWAP_PENDING` e conclusão da partida sem Topa,
respeitando o ADR 0003 (troca final). Não iniciar antes da conclusão da Fase 5.

- [ ] Transição/estado de endgame após recusa da oferta da Rodada 9 (duas maletas fechadas).
- [ ] Decisão de troca (opcional): realizar ou não a troca.
- [ ] `SwapBriefcase` (troca da maleta do jogador pela última maleta fechada).
- [ ] Definição da maleta final do jogador.
- [ ] `RevealFinalBriefcase` (revelação das duas últimas maletas).
- [ ] `OfficialResult` sem troca (`FINAL_REVEAL_WITHOUT_SWAP`) e com troca (`FINAL_REVEAL_WITH_SWAP`).
- [ ] Conclusão definitiva da partida (`FINISHED`).
- [ ] Testes dos dois desfechos do endgame.

**Critério de saída:** uma partida que recusa todas as ofertas conclui pelo endgame, com ou sem troca, produzindo `OfficialResult` imutável.

---

# Fase 6 — Simulação pós-jogo

- [ ] Implementar `RunPostGameSimulation`.
- [ ] Reutilizar a distribuição da partida original (sem novo embaralhamento).
- [ ] Partir do estado do momento da aceitação da oferta.
- [ ] Revelar progressivamente as maletas restantes e a maleta do jogador.
- [ ] Simular a decisão hipotética de troca quando o fluxo chegar a duas maletas.
- [ ] Produzir resultado hipotético e comparação com o resultado oficial.
- [ ] Garantir que o resultado oficial não seja alterado.
- [ ] Testes cobrindo a separação entre resultado oficial e hipotético.

**Critério de saída:** simulação pós-jogo funcional, separada da partida oficial, sem alterar o resultado oficial.

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
