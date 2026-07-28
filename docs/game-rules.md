# Regras do Jogo

## 1. Objetivo

Este documento é a fonte oficial das regras de negócio da versão digital do `tont-game`.

Quando houver conflito entre este documento e uma implementação, a regra documentada deve prevalecer.

---

## 2. Maletas

A partida possui exatamente 26 maletas.

Cada maleta contém um valor monetário.

Os valores oficiais da primeira versão são:

| Nº | Valor |
|---:|---:|
| 1 | R$ 0,50 |
| 2 | R$ 1,00 |
| 3 | R$ 5,00 |
| 4 | R$ 10,00 |
| 5 | R$ 25,00 |
| 6 | R$ 50,00 |
| 7 | R$ 75,00 |
| 8 | R$ 100,00 |
| 9 | R$ 250,00 |
| 10 | R$ 500,00 |
| 11 | R$ 750,00 |
| 12 | R$ 1.000,00 |
| 13 | R$ 2.500,00 |
| 14 | R$ 5.000,00 |
| 15 | R$ 7.500,00 |
| 16 | R$ 10.000,00 |
| 17 | R$ 25.000,00 |
| 18 | R$ 50.000,00 |
| 19 | R$ 75.000,00 |
| 20 | R$ 100.000,00 |
| 21 | R$ 250.000,00 |
| 22 | R$ 500.000,00 |
| 23 | R$ 750.000,00 |
| 24 | R$ 1.000.000,00 |
| 25 | R$ 1.500.000,00 |
| 26 | R$ 2.000.000,00 |

> Observação: a lista acima é uma decisão de produto para a implementação inicial e deve ser tratada como configurável. Se o projeto precisar reproduzir outra tabela oficial de valores, essa decisão deverá ser registrada em `docs/decisions/`.

---

## 3. Distribuição

Ao iniciar uma partida:

1. os 26 valores devem ser embaralhados;
2. cada valor deve ser associado a uma única maleta;
3. o jogador não deve conhecer a associação entre maleta e valor;
4. a aleatoriedade deve poder receber uma semente opcional para facilitar testes.

---

## 4. Maleta do jogador

O jogador escolhe uma maleta no início.

Essa maleta:

- passa a ser sua maleta;
- permanece fechada;
- não pode ser aberta durante as rodadas normais;
- tem valor desconhecido;
- só é revelada quando a regra do jogo determinar.

### Regra matemática

A maleta do jogador continua contendo um dos valores ainda não revelados.

Portanto, seu valor faz parte do conjunto matemático dos valores possíveis restantes.

Entretanto, sua maleta não pode ser escolhida para eliminação durante as rodadas normais.

Assim, há diferença entre:

- `remaining_values`: valores ainda associados a maletas fechadas;
- `available_briefcases`: maletas que podem ser abertas;
- `player_briefcase`: maleta protegida do jogador.

---

## 5. Rodadas

A sequência inicial de abertura é:

| Rodada | Maletas a abrir |
|---:|---:|
| 1 | 6 |
| 2 | 5 |
| 3 | 4 |
| 4 | 3 |
| 5 | 2 |
| 6 | 1 |
| 7 | 1 |

Após a sétima rodada, o jogo deve seguir para a fase final definida pelo estado atual.

A quantidade de maletas a abrir deve ser validada pelo domínio.

O jogador não pode:

- abrir uma maleta já aberta;
- abrir sua própria maleta durante uma rodada normal;
- abrir mais maletas que o permitido na rodada.

---

## 6. Valores restantes

Um valor é considerado restante enquanto a maleta que o contém estiver fechada.

Quando uma maleta é aberta:

1. seu valor é revelado;
2. ela deixa de estar disponível;
3. seu valor deixa de fazer parte dos valores restantes.

O valor da maleta do jogador permanece entre os valores restantes enquanto sua maleta estiver fechada.

---

## 7. Oferta do Banqueiro

A oferta deve ser calculada com base nos valores restantes.

A estratégia do Banqueiro deve considerar:

- média dos valores restantes;
- estágio atual da partida;
- quantidade de valores restantes;
- fator percentual associado ao estágio.

A oferta não deve ser simplesmente igual à média durante todo o jogo.

A estratégia deve ser conservadora no início e aumentar progressivamente ao longo da partida.

A implementação deve encapsular essa política em um componente de domínio substituível.

### Política inicial

Para a primeira versão, utilizar a seguinte progressão de percentual sobre a média dos valores restantes:

| Estágio | Percentual |
|---|---:|
| Rodada 1 | 35% |
| Rodada 2 | 40% |
| Rodada 3 | 50% |
| Rodada 4 | 60% |
| Rodada 5 | 70% |
| Rodada 6 | 80% |
| Rodada 7 | 90% |

Esses percentuais são parâmetros de jogo, não regras estruturais do domínio, e devem ficar configuráveis.

A oferta final deve ser arredondada para centavos.

---

## 8. Topa

Quando o jogador aceita a oferta:

- a partida termina imediatamente;
- o valor da oferta aceita é registrado;
- a maleta do jogador permanece fechada, salvo necessidade de exibição posterior;
- o resultado da partida informa que o jogador aceitou a oferta.

---

## 9. Não Topa

Quando o jogador recusa a oferta:

- a oferta é registrada como recusada;
- o jogo continua;
- a próxima rodada é iniciada, quando houver.

---

## 10. Final do jogo

Se o jogador recusar todas as ofertas e chegar ao final:

1. a maleta do jogador é aberta;
2. seu valor é revelado;
3. esse valor representa o resultado final da partida.

---

## 11. Troca de maleta

A possibilidade de troca deve ocorrer somente no estágio explicitamente definido pela configuração da partida.

A primeira versão deve suportar a regra como conceito de domínio, mesmo que a política de troca seja simples.

A implementação deve permitir:

- identificar a maleta do jogador;
- identificar a outra maleta elegível;
- solicitar decisão de troca;
- registrar se a troca foi aceita;
- atualizar a maleta do jogador quando a troca for aceita.

---

## 12. Aleatoriedade

A partida deve aceitar uma fonte de aleatoriedade injetável ou equivalente.

Isso permite:

- partidas normais aleatórias;
- testes determinísticos;
- reprodução de cenários específicos.

---

## 13. Invariantes

O domínio deve garantir:

- existem exatamente 26 maletas no início;
- cada maleta possui exatamente um valor;
- cada valor pertence a exatamente uma maleta;
- uma maleta aberta não pode voltar a ficar fechada;
- uma maleta aberta não pode ser aberta novamente;
- a maleta do jogador é válida;
- a maleta do jogador não é aberta durante rodadas normais;
- a quantidade de aberturas não excede o permitido;
- o jogo não pode continuar depois de encerrado;
- uma oferta não pode ser aceita duas vezes;
- valores monetários são tratados com precisão decimal.
