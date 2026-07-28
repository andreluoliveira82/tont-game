# Roadmap de Desenvolvimento

## Estratégia

O projeto deve ser desenvolvido incrementalmente.

Cada fase deve resultar em um estado executável e validado.

O LLM não deve avançar automaticamente para a próxima fase.

---

# Fase 0 — Documentação e decisões

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

- [ ] Executar `uv init`.
- [ ] Configurar Python 3.13+.
- [ ] Configurar estrutura `src/`.
- [ ] Configurar `pytest`.
- [ ] Configurar `ruff`.
- [ ] Configurar `taskipy`.
- [ ] Criar `pyproject.toml`.
- [ ] Criar `.gitignore`.
- [ ] Criar `README.md`.
- [ ] Configurar comandos:
  - [ ] `task test`
  - [ ] `task lint`
  - [ ] `task format`
  - [ ] `task run`
  - [ ] `task check`

**Critério de saída:** projeto instala, testa e valida sem funcionalidades do jogo.

---

# Fase 2 — Modelo de domínio

- [ ] Criar representação de dinheiro com precisão decimal.
- [ ] Criar `Briefcase`.
- [ ] Criar `GameState` (estado atual).
- [ ] Criar `GameStatus` (incluindo estados de endgame e aceitação).
- [ ] Criar representação das 9 rodadas e da sequência de aberturas.
- [ ] Definir valores oficiais das 26 maletas.
- [ ] Criar regras de invariantes (incluindo: duas maletas fechadas ao final da Rodada 9).
- [ ] Criar testes unitários.

**Critério de saída:** domínio representa corretamente uma partida inicial e a estrutura das 9 rodadas.

---

# Fase 3 — Aleatoriedade

- [ ] Criar fonte de aleatoriedade.
- [ ] Permitir semente determinística.
- [ ] Embaralhar valores.
- [ ] Associar valores às maletas.
- [ ] Registrar a seed na configuração inicial da partida quando utilizada.
- [ ] Testar distribuição.
- [ ] Testar reprodução com seed.

**Critério de saída:** partidas podem ser aleatórias e reproduzíveis.

---

# Fase 4 — Estratégia do Banqueiro

- [ ] Criar estratégia de oferta isolada e substituível.
- [ ] Calcular média dos valores restantes (`remaining_values`, incluindo a maleta do jogador).
- [ ] Aplicar percentual por rodada (35, 40, 50, 60, 70, 80, 85, 90, 95).
- [ ] Arredondar oferta para centavos.
- [ ] Garantir que a estratégia dependa apenas do estado atual e da rodada (não do histórico de ofertas).
- [ ] Testar ofertas nas 9 rodadas.
- [ ] Testar oscilação (oferta pode subir ou cair) com valores conhecidos.
- [ ] Testar estratégia com valores conhecidos (determinismo).

**Critério de saída:** oferta do Banqueiro é determinística para um estado conhecido.

---

# Fase 5 — Casos de uso

- [ ] `StartGame`.
- [ ] `SelectInitialBriefcase`.
- [ ] `OpenBriefcase`.
- [ ] `ProcessBankerOffer`.
- [ ] `DecideOffer`.
- [ ] `SwapBriefcase` (troca final do endgame).
- [ ] `RevealFinalBriefcase`.
- [ ] Registro do histórico da partida (`GameRecord`) ao longo do fluxo.
- [ ] Registro do resultado oficial imutável no encerramento.

**Critério de saída:** fluxo completo (9 rodadas + endgame) pode ser executado sem CLI, com histórico e resultado oficial registrados.

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
