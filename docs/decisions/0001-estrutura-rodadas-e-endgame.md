# ADR 0001 — Estrutura das rodadas e endgame

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

A documentação inicial definia a sequência de abertura como `6, 5, 4, 3, 2, 1, 1` (7 rodadas), com o PRD referenciando uma "regra final documentada" que não existia em `game-rules.md`. A aritmética não fechava: com 26 maletas e 1 maleta protegida do jogador, restam 25 maletas abríveis; abrir `6+5+4+3+2+1+1 = 22` deixaria 3 maletas fechadas além da do jogador, incompatível com a regra de troca que pressupõe "a outra maleta elegível" (uma única).

## Decisão

O jogo terá **9 rodadas**. A sequência completa de aberturas é:

| Rodada | Maletas a abrir | Fechadas após a rodada (inclui a do jogador) |
|---:|---:|---:|
| 1 | 6 | 20 |
| 2 | 5 | 15 |
| 3 | 4 | 11 |
| 4 | 3 | 8 |
| 5 | 2 | 6 |
| 6 | 1 | 5 |
| 7 | 1 | 4 |
| 8 | 1 | 3 |
| 9 | 1 | 2 |

Total aberto: **24 maletas**. Ao final da Rodada 9 restam exatamente **duas** maletas fechadas:

1. a maleta protegida do jogador;
2. uma única última maleta fechada disponível.

O endgame (oferta da Rodada 9 e troca final opcional) está detalhado no [ADR 0003](0003-troca-final.md).

## Justificativa

- Reduz o jogo ao estado canônico de duas maletas, tornando a regra de troca final coerente e sem ambiguidade.
- Elimina a referência quebrada do PRD.
- A matemática do fluxo passa a ser explícita e verificável, evitando ambiguidades futuras.

## Impacto arquitetural

- A representação de rodada deve conhecer a sequência das 9 rodadas e validar a quantidade de aberturas por rodada.
- O domínio deve garantir a invariante de que, após a Rodada 9, existem exatamente duas maletas fechadas.
- A oferta do Banqueiro ocorre ao final de cada uma das 9 rodadas (ver [ADR 0002](0002-estrategia-inicial-do-banqueiro.md)).
