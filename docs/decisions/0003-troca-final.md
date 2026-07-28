# ADR 0003 — Troca final de maleta

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

A regra de troca precisava de um momento e uma elegibilidade bem definidos. A estrutura de 9 rodadas ([ADR 0001](0001-estrutura-rodadas-e-endgame.md)) garante que, ao final da Rodada 9, restem exatamente duas maletas fechadas, tornando a troca inequívoca.

## Decisão

Não há troca durante as rodadas 1 a 9.

Após a oferta da Rodada 9:

- se o jogador escolher **Topa**, a partida termina com a oferta aceita;
- se escolher **Não Topa**, o jogador recebe uma decisão final **opcional** de troca:

  > "Você deseja trocar sua maleta pela última maleta?"

  - **Não** → permanece com a maleta original;
  - **Sim** → troca a maleta do jogador pela última maleta fechada.

Após a decisão de troca, as duas últimas maletas são reveladas e a partida termina. O valor final oficial é o da maleta que ficou com o jogador após a decisão.

A **última maleta fechada** é a única maleta elegível para troca.

## Justificativa

- A troca só é conceitualmente válida quando restam exatamente duas maletas; a estrutura de 9 rodadas garante esse estado.
- Torna a elegibilidade determinística ("a outra maleta" é única).

## Impacto arquitetural

- O endgame é conduzido por um caso de uso único de Application, `DecideFinalSwap(swap: bool)`, que orquestra as primitivas de domínio `apply_final_swap()` e `reveal_final_and_finish()` (implementado na Fase 5.5, commit `b26b11d`; ver [ADR 0006](0006-camada-application-e-historico.md)).
- O domínio valida que a troca/revelação só ocorre no estágio final (`FINAL_SWAP_PENDING`), com exatamente duas maletas fechadas, e após a recusa da oferta da Rodada 9; a conclusão transita direto para `FINISHED`.
- A decisão de troca e a maleta resultante fazem parte do resultado oficial (`OfficialResult.from_final_reveal`, com `decision_round = None`) e o histórico existente ([ADR 0005](0005-historico-da-partida-e-persistencia.md)); **não** há registro histórico específico do endgame (a outra maleta é derivável de `initial_distribution`).
- A simulação pós-jogo pode reproduzir uma decisão hipotética de troca sem afetar o resultado oficial ([ADR 0004](0004-simulacao-pos-jogo.md)).
