# ADR 0002 — Estratégia inicial do Banqueiro

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

O Banqueiro faz uma oferta ao final de cada rodada. A política inicial precisava ser definida de forma determinística, configurável e isolada, cobrindo todas as 9 rodadas ([ADR 0001](0001-estrutura-rodadas-e-endgame.md)) — a tabela anterior cobria apenas 7 rodadas.

## Decisão

O Banqueiro faz uma oferta ao final de **cada uma das 9 rodadas**, inclusive uma última oferta após a Rodada 9.

A fórmula inicial:

```
oferta = média(remaining_values) × percentual_da_rodada
```

A oferta é arredondada para centavos.

`remaining_values` = valores ainda não revelados, incluindo o valor da maleta do jogador e os valores das maletas que permanecem fechadas. Não confundir com `available_briefcases` (apenas as maletas abríveis; não inclui a do jogador).

Percentuais por rodada:

| Rodada | Percentual |
|---:|---:|
| 1 | 35% |
| 2 | 40% |
| 3 | 50% |
| 4 | 60% |
| 5 | 70% |
| 6 | 80% |
| 7 | 85% |
| 8 | 90% |
| 9 | 95% |

A estratégia inicial:

- baseia-se **apenas** no estado atual da partida e na rodada atual;
- **não** depende do histórico de ofertas anteriores;
- **não** impõe monotonicidade — a oferta pode subir, cair ou permanecer próxima da anterior, conforme a composição dos valores restantes.

Para o MVP existe apenas esta estratégia matemática.

## Justificativa

- Determinística e testável para um estado conhecido.
- A não-monotonicidade é intencional: reflete a dinâmica real do jogo, em que eliminar valores altos derruba a média e eliminar valores baixos a eleva, enquanto o percentual crescente compensa parcial, total ou insuficientemente essa variação.
- Percentuais como configuração (não regra fixa espalhada pelo código) permitem ajuste sem alterar o domínio.

## Impacto arquitetural

- A política do Banqueiro deve ser um componente de domínio isolado e substituível (por exemplo, uma interface de estratégia), permitindo futuras estratégias (conservadora, agressiva, baseada em outros fatores) sem alterar entidades centrais.
- Os percentuais devem residir em configuração da estratégia inicial, não dispersos no código.
- O cálculo não deve ler o histórico de ofertas; recebe o estado atual e a rodada.
