# Glossário do Domínio

## Briefcase

Uma das 26 maletas disponíveis na partida.

## Player Briefcase

A maleta escolhida inicialmente pelo jogador (`player_briefcase`). Permanece fechada durante as rodadas normais. Não pertence a `available_briefcases`, mas seu **valor** pertence a `remaining_values`.

## Available Briefcase

Maleta que ainda está fechada e pode ser escolhida para abertura em uma rodada normal. O conjunto dessas maletas é `available_briefcases` e **não** inclui a maleta do jogador.

## Opened Briefcase

Maleta que já foi aberta e cujo valor foi revelado.

## Remaining Value

Valor associado a uma maleta que ainda permanece fechada.

## Remaining Values

Conjunto de **valores** ainda não revelados. Inclui o valor da maleta do jogador **e** os valores das maletas que ainda permanecem fechadas. É a base de cálculo da oferta do Banqueiro. Difere de `available_briefcases`, que se refere a maletas abríveis.

## Available Briefcases

Conjunto de **maletas** fechadas que podem ser abertas em uma rodada normal. Não inclui a maleta do jogador.

## Known Value

Valor que já foi revelado ao jogador por meio da abertura de uma maleta.

## Round

Etapa do jogo durante a qual uma quantidade definida de maletas deve ser aberta. O jogo possui 9 rodadas, com a sequência de abertura `6, 5, 4, 3, 2, 1, 1, 1, 1`.

## Banker

Componente responsável pela política de cálculo das ofertas. É realizado diretamente por uma `Banker Strategy` (não há uma classe `Banker` separada).

## Banker Offer

Valor monetário (`Money`) oferecido ao jogador pelo Banqueiro ao final de cada rodada. É calculado sobre `remaining_values` — todos os valores que ainda permanecem matematicamente em jogo, **incluindo** o valor da maleta protegida do jogador e **excluindo** os valores das maletas já abertas.

## Offer Percentage

Percentual aplicado à média dos valores restantes para calcular uma oferta. Definido por rodada na política inicial da estratégia (`DEFAULT_BANKER_PERCENTAGES`: 0.35–0.95 ao longo das 9 rodadas), representado como `Decimal` e injetável.

## Banker Strategy

Política que determina o valor da oferta do Banqueiro. É um **port** do domínio (`BankerStrategy`, `Protocol` com o método `offer(remaining_values, round_number)`); isolada e substituível. A implementação inicial é `DefaultBankerStrategy` — `média(remaining_values) × percentual_da_rodada`, arredondada a centavos apenas no final, **stateless** e sem depender do histórico de ofertas. A oferta pode subir ou cair entre rodadas conforme a composição dos valores restantes (sem monotonicidade artificial).

## Topa

Decisão do jogador de aceitar a oferta do Banqueiro. Encerra a partida oficial.

## Não Topa

Decisão do jogador de recusar a oferta e continuar a partida.

## Swap (Troca Final)

Troca opcional da maleta do jogador pela última maleta fechada, disponível apenas no endgame, após a recusa da oferta da Rodada 9. A última maleta fechada é a única elegível.

## Endgame

Fase final da partida, após a Rodada 9, quando restam exatamente duas maletas fechadas: a do jogador e a última maleta disponível. Inclui a oferta da Rodada 9 e a decisão de troca final.

## Game State

Estado atual (corrente) da partida em determinado momento. Representa informações como:

- maletas;
- maleta do jogador;
- rodada atual;
- maletas abertas;
- valores revelados;
- oferta atual;
- estado do ciclo de vida da partida.

Distingue-se do histórico: o estado atual descreve a situação corrente; o histórico registra a sequência de eventos e resultados.

## Game Status

Estado do ciclo de vida da partida, por exemplo:

- `NOT_STARTED`;
- `IN_PROGRESS`;
- `OFFER_PENDING`;
- `ACCEPTED`;
- `FINAL_SWAP_PENDING`;
- `FINAL_REVEAL`;
- `FINISHED`.

## Official Result (Resultado Oficial)

Resultado registrado imediatamente no encerramento oficial da partida. Contém o motivo do encerramento, o valor oficial recebido, o valor real da maleta do jogador e a decisão de troca quando aplicável. Nunca é alterado por simulações posteriores.

## Post-Game Simulation (Simulação Pós-Jogo)

Experiência opcional, executada após a aceitação de uma oferta, que revela o que teria acontecido se o jogador tivesse continuado. Usa a mesma distribuição de valores e o estado do momento da aceitação, sem gerar nova partida nem alterar o resultado oficial. Produz um resultado hipotético comparado ao oficial.

## Game Record (Histórico da Partida)

Registro estruturado, mantido em memória, que permite reconstruir a narrativa completa da partida: configuração inicial (id, `started_at`, distribuição concreta, seed, maleta escolhida), histórico por rodada, resultado oficial e simulação pós-jogo (quando houver). É **append-only** (só cresce; fatos passados não são sobrescritos) e concebido para poder ser persistido futuramente sem acoplar o domínio a uma tecnologia específica.

## Game Session

Composição operacional da partida na camada de aplicação: agrupa o `GameState` (estado atual) e o `GameRecord` (histórico). Os casos de uso operam sobre ela. O `GameRecord` nunca referencia o `GameState` mutável.

## Round Record

Registro **imutável** (`frozen`) dos fatos de uma rodada: maletas abertas (`BriefcaseOpeningRecord`), oferta do Banqueiro (`BankerOfferRecord`) e decisão do jogador (`Decision`). Evolui por operações `with_*` que retornam nova instância; o `GameRecord` é a única autoridade que o acumula.

## Briefcase Opening Record

Fato imutável de uma abertura: número da maleta e valor revelado.

## Banker Offer Record

Fato imutável de uma oferta: número da rodada, valor da oferta, **percentual utilizado** e valores restantes (`remaining_values`) considerados. Preserva o percentual por auditoria, independentemente de recalcular com a implementação atual.

## Decision

Decisão do jogador diante de uma oferta: `ACCEPT` (Topa) ou `REJECT` (Não Topa). Registrada no `RoundRecord` correspondente.

## Ending Type

Tipo de encerramento oficial da partida, registrado no `OfficialResult`: `OFFER_ACCEPTED` (Topa), `FINAL_REVEAL_WITH_SWAP` e `FINAL_REVEAL_WITHOUT_SWAP` (endgame — Fase 5.5). Na Fase 5 apenas `OFFER_ACCEPTED` é produzido; os demais estão definidos, mas ainda não são gerados.

## Append-only

Propriedade de um registro que apenas cresce: novos fatos são acrescentados e os fatos passados nunca são sobrescritos nem removidos. É a propriedade do `GameRecord`.

## Write-once

Fato singular que pode ser gravado uma única vez (ex.: a oferta e a decisão de uma rodada, o `OfficialResult`); uma segunda tentativa é rejeitada com erro de domínio.

## FINAL_SWAP_PENDING

Estado do ciclo de vida atingido quando o jogador recusa a oferta da Rodada 9 (restam a maleta do jogador e a última maleta fechada). Na Fase 5 a transição ocorre mas **não é consumida**; a decisão de troca, a revelação e o encerramento pertencem à Fase 5.5.

## Clock

Port do domínio que fornece o instante atual (`datetime` timezone-aware, em UTC). Implementação concreta na infraestrutura (`SystemClock`); substituível por um relógio determinístico em testes.

## Game Id Generator

Port do domínio que gera o identificador único da partida (UUID). Implementação concreta na infraestrutura (`UuidGameIdGenerator`); substituível em testes.

## Domain Rule

Regra de negócio que deve ser protegida pelo núcleo do sistema.

## Use Case

Operação da aplicação que representa uma ação relevante do usuário ou do fluxo do jogo.

## CLI

Interface de linha de comando utilizada como primeira interface do projeto.

## Presenter / Apresentador

Na CLI, o Apresentador conduz o fluxo de interação com o jogador (ofertas, decisões, oferta de simulação pós-jogo). É responsabilidade de apresentação, não do domínio.

## Random Source

Fonte de aleatoriedade utilizada para embaralhar os valores das maletas. É um **port** do domínio (`RandomSource`, `Protocol` com o método `shuffle`); pode ser substituída por uma fonte determinística em testes. A implementação concreta padrão é `DefaultRandomSource` (infraestrutura), backed por `random.Random` com seed opcional. A simulação pós-jogo não realiza novo embaralhamento.

## Value Distribution

Serviço de domínio (`create_shuffled_game`) que embaralha os valores oficiais por meio de um `RandomSource` e monta um `GameState` válido, numerando as maletas na ordem embaralhada.

## Distribuição concreta

Associação efetiva entre cada maleta e seu valor em uma partida específica, resultante da distribuição. Representa o fato histórico daquela execução e reside no próprio `GameState`. É a base sobre a qual a futura simulação pós-jogo opera (sem re-sortear). Difere da `seed`, que é apenas informação complementar de reprodutibilidade técnica.
