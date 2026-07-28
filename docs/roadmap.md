# Roadmap de Desenvolvimento

## Estratégia

O projeto deve ser desenvolvido incrementalmente.

Cada fase deve resultar em um estado executável e validado.

O LLM não deve avançar automaticamente para a próxima fase.

---

# Fase 0 — Documentação e decisões

- [ ] Revisar `prd.md`.
- [ ] Revisar `game-rules.md`.
- [ ] Revisar `glossary.md`.
- [ ] Revisar `architecture.md`.
- [ ] Revisar `llm-instructions.md`.
- [ ] Definir decisões pendentes.
- [ ] Registrar decisões arquiteturais relevantes em `docs/decisions/`.

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
- [ ] Criar `GameState`.
- [ ] Criar `GameStatus`.
- [ ] Criar representação de rodada.
- [ ] Definir valores oficiais das 26 maletas.
- [ ] Criar regras de invariantes.
- [ ] Criar testes unitários.

**Critério de saída:** domínio representa corretamente uma partida inicial.

---

# Fase 3 — Aleatoriedade

- [ ] Criar fonte de aleatoriedade.
- [ ] Permitir semente determinística.
- [ ] Embaralhar valores.
- [ ] Associar valores às maletas.
- [ ] Testar distribuição.
- [ ] Testar reprodução com seed.

**Critério de saída:** partidas podem ser aleatórias e reproduzíveis.

---

# Fase 4 — Estratégia do Banqueiro

- [ ] Criar estratégia de oferta.
- [ ] Calcular média dos valores restantes.
- [ ] Aplicar percentual por estágio.
- [ ] Arredondar oferta para centavos.
- [ ] Garantir que a maleta do jogador permaneça no conjunto de valores restantes.
- [ ] Testar ofertas em diferentes rodadas.
- [ ] Testar estratégia com valores conhecidos.

**Critério de saída:** oferta do Banqueiro é determinística para um estado conhecido.

---

# Fase 5 — Casos de uso

- [ ] `StartGame`.
- [ ] `SelectInitialBriefcase`.
- [ ] `OpenBriefcase`.
- [ ] `ProcessBankerOffer`.
- [ ] `DecideOffer`.
- [ ] `SwapBriefcase`.
- [ ] `RevealFinalBriefcase`.

**Critério de saída:** fluxo completo pode ser executado sem CLI.

---

# Fase 6 — Testes de integração

Criar cenários completos:

- [ ] partida iniciada;
- [ ] escolha da maleta;
- [ ] rodada 1;
- [ ] oferta;
- [ ] recusa;
- [ ] rodada seguinte;
- [ ] múltiplas ofertas;
- [ ] aceitação da oferta;
- [ ] final sem aceitar;
- [ ] troca de maleta;
- [ ] tentativa inválida de abertura;
- [ ] tentativa de abrir maleta do jogador;
- [ ] tentativa de continuar jogo encerrado.

**Critério de saída:** fluxo principal protegido por testes.

---

# Fase 7 — Interface CLI

- [ ] Criar controller.
- [ ] Criar views.
- [ ] Criar presenters.
- [ ] Exibir maleta do jogador.
- [ ] Exibir valores restantes.
- [ ] Exibir valores eliminados.
- [ ] Exibir rodada atual.
- [ ] Exibir oferta.
- [ ] Receber Topa/Não Topa.
- [ ] Implementar tratamento de entradas inválidas.
- [ ] Implementar game loop.

**Critério de saída:** partida completa jogável pelo terminal.

---

# Fase 8 — Refinamento

- [ ] Melhorar experiência visual da CLI.
- [ ] Melhorar mensagens.
- [ ] Revisar tratamento de erros.
- [ ] Revisar testes.
- [ ] Revisar documentação.
- [ ] Criar testes de regressão.
- [ ] Atualizar README.

---

# Fase 9 — Preparação para evolução

Somente após a CLI estar estável:

- [ ] avaliar persistência;
- [ ] avaliar GUI;
- [ ] avaliar arquitetura de múltiplas interfaces;
- [ ] avaliar histórico de partidas;
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
