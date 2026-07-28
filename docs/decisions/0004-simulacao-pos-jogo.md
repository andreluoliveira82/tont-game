# ADR 0004 — Simulação pós-jogo

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

Quando o jogador aceita uma oferta, a partida oficial termina. Há interesse em permitir que o jogador veja o que teria acontecido se tivesse continuado, sem que isso altere o resultado oficial.

## Decisão

Após o jogador aceitar uma oferta (**Topa**):

1. o resultado oficial é encerrado e registrado imediatamente;
2. o Apresentador pergunta se o jogador deseja simular a continuação;
3. se não quiser, a experiência termina;
4. se quiser, inicia-se a simulação pós-jogo.

A simulação:

- utiliza **exatamente** a mesma distribuição de valores da partida original;
- parte do mesmo estado existente no momento em que a oferta foi aceita;
- **não** gera nova partida e **não** sorteia valores novamente;
- **não** altera o resultado oficial;
- revela progressivamente as maletas que ainda não haviam sido abertas;
- ao final, revela o valor da maleta do jogador;
- quando o fluxo chegar a duas maletas, permite simular a decisão hipotética de troca ([ADR 0003](0003-troca-final.md));
- permite comparar o resultado oficial com o resultado hipotético.

A simulação é conceitualmente separada da partida oficial; não é uma continuação de uma partida encerrada. O resultado é apresentado separadamente:

```
Resultado oficial:              R$ X
Resultado hipotético da simulação: R$ Y
Diferença:                      R$ Z
```

## Justificativa

- Entrega valor de entretenimento e análise ("e se eu tivesse continuado?") sem comprometer a integridade do resultado oficial.
- A separação explícita evita que o resultado hipotético seja confundido com o oficial ou o substitua.

## Impacto arquitetural

- O estado oficial da partida no momento da aceitação deve ser suficiente para conduzir a simulação sem recriar a partida nem re-embaralhar valores ([ADR 0005](0005-historico-da-partida-e-persistencia.md)).
- O resultado oficial e o resultado da simulação são conceitos distintos e devem ser modelados separadamente.
- A simulação registra: se foi executada, maletas reveladas, valor da maleta do jogador, decisão hipotética de troca (quando aplicável), resultado hipotético e a diferença em relação ao oficial.
- A simulação é uma responsabilidade da aplicação/apresentação sobre o estado do domínio; o domínio não deve tratá-la como continuação da partida oficial.

## Complemento (2026-07-28) — Escopo e forma da Fase 6

Formalizado ao autorizar a Fase 6:

- A simulação é uma **derivação pura e não-histórica** sobre um `GameRecord`
  imutável já encerrado; produz um **`SimulationResult` separado**.
- O `SimulationResult` **não** faz parte do `GameRecord`, **não** é o resultado
  oficial, **não** é gravado no histórico e **não** é persistido. "A simulação
  registra…" (acima) refere-se aos campos do próprio `SimulationResult`, não a
  qualquer escrita no histórico oficial.
- **Escopo da Fase 6 (MVP):** exclusivamente o cenário **`CONTINUE_HOLD`** — a
  partir de uma partida encerrada por **Topa**, comparar o valor oficialmente
  recebido (`amount_received`) com o valor hipotético de o jogador ter recusado a
  oferta e segurado a própria maleta até o fim (`player_briefcase_value`).
- **Fora do escopo da Fase 6:** simular a decisão final oposta em encerramentos
  por endgame; aceitar hipoteticamente ofertas recusadas; troca hipotética em
  Topa intermediário; recálculo de ofertas; re-sorteio. A ordem de abertura
  hipotética **não** é inventada (o swap hipotético só seria considerado quando
  determinístico pelos dados, e não é implementado neste MVP).
- **Forma:** um serviço de domínio puro conduz a derivação; um caso de uso fino
  `RunPostGameSimulation` (Application) o invoca. Sem novos ports, sem
  infraestrutura, sem persistência. Ver [ADR 0006](0006-camada-application-e-historico.md).
- **Implementação (Fase 6, commit `f6faba0`):** serviço de domínio
  `simulate_continue_hold(game_record)` + VOs `SimulationScenario`
  (`CONTINUE_HOLD`) e `SimulationResult` (frozen); caso de uso
  `RunPostGameSimulation`. Pré-condição: `official_result` presente (senão
  `InvalidGameStateError`). Diferença/comparação são deriváveis, não
  armazenadas.
