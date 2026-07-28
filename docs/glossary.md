# Glossário do Domínio

## Briefcase

Uma das 26 maletas disponíveis na partida.

## Player Briefcase

A maleta escolhida inicialmente pelo jogador.

## Available Briefcase

Maleta que ainda está fechada e pode ser escolhida para abertura em uma rodada normal.

## Opened Briefcase

Maleta que já foi aberta e cujo valor foi revelado.

## Remaining Value

Valor associado a uma maleta que ainda permanece fechada.

## Known Value

Valor que já foi revelado ao jogador por meio da abertura de uma maleta.

## Round

Etapa do jogo durante a qual uma quantidade definida de maletas deve ser aberta.

## Banker

Componente responsável pela política de cálculo das ofertas.

## Banker Offer

Valor monetário oferecido ao jogador pelo Banqueiro.

## Offer Percentage

Percentual aplicado à base matemática utilizada para calcular uma oferta.

## Topa

Decisão do jogador de aceitar a oferta do Banqueiro.

## Não Topa

Decisão do jogador de recusar a oferta e continuar a partida.

## Swap

Troca da maleta do jogador por outra maleta elegível, quando a regra da partida permitir.

## Game State

Estado completo da partida em determinado momento.

Deve representar informações como:

- maletas;
- maleta do jogador;
- rodada atual;
- maletas abertas;
- valores revelados;
- oferta atual;
- estado da partida.

## Game Status

Estado do ciclo de vida da partida, por exemplo:

- `NOT_STARTED`;
- `IN_PROGRESS`;
- `OFFER_PENDING`;
- `ACCEPTED`;
- `FINAL_REVEAL`;
- `FINISHED`.

## Remaining Values

Conjunto de valores ainda associados às maletas fechadas.

## Available Briefcases

Conjunto de maletas fechadas que podem ser abertas em uma rodada normal.

## Domain Rule

Regra de negócio que deve ser protegida pelo núcleo do sistema.

## Use Case

Operação da aplicação que representa uma ação relevante do usuário ou do fluxo do jogo.

## CLI

Interface de linha de comando utilizada como primeira interface do projeto.

## Banker Strategy

Política utilizada para determinar o valor da oferta do Banqueiro.

## Random Source

Fonte de aleatoriedade utilizada para embaralhar os valores das maletas.

Pode ser substituída por uma fonte determinística em testes.
