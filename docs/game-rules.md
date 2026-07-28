# Regras do Jogo

## 1. Objetivo

Este documento é a fonte oficial das regras de negócio da versão digital do `tont-game`.

Quando houver conflito entre este documento e uma implementação, a regra documentada deve prevalecer.

Decisões estruturais estão registradas em `docs/decisions/` e são referenciadas ao longo deste documento.

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

- passa a ser sua maleta (`player_briefcase`);
- permanece fechada;
- não pode ser aberta durante as rodadas normais;
- tem valor desconhecido;
- só é revelada quando a regra do jogo determinar.

### Regra matemática

A maleta do jogador continua contendo um dos valores ainda não revelados.

Portanto, seu valor faz parte do conjunto matemático dos valores possíveis restantes.

Entretanto, sua maleta não pode ser escolhida para eliminação durante as rodadas normais.

Assim, há diferença entre três conceitos, usados de forma consistente em toda a documentação:

- `remaining_values`: **valores** ainda não revelados. Inclui o valor da maleta do jogador **e** os valores das maletas que ainda permanecem fechadas.
- `available_briefcases`: **maletas** que ainda estão fechadas e podem ser abertas em uma rodada normal. **Não** inclui a maleta do jogador.
- `player_briefcase`: a maleta protegida do jogador. Não pertence a `available_briefcases`, mas seu **valor** pertence a `remaining_values`.

---

## 5. Rodadas

O jogo possui **9 rodadas**. A sequência completa de aberturas é:

| Rodada | Maletas a abrir | Maletas fechadas após a rodada (inclui a do jogador) |
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

### Matemática do fluxo (explícita)

- 26 maletas no total.
- O jogador escolhe 1 maleta protegida (`player_briefcase`).
- Restam 25 maletas abríveis.
- Ao longo das 9 rodadas são abertas `6+5+4+3+2+1+1+1+1 = 24` maletas.
- `25 − 24 = 1` maleta abrível permanece fechada ao final da Rodada 9.
- Logo, ao final da Rodada 9 restam exatamente **duas** maletas fechadas: a do jogador e a última maleta fechada disponível.

A quantidade de maletas a abrir em cada rodada deve ser validada pelo domínio.

O jogador não pode:

- abrir uma maleta já aberta;
- abrir sua própria maleta durante uma rodada normal;
- abrir mais maletas que o permitido na rodada.

Referência: `docs/decisions/0001-estrutura-rodadas-e-endgame.md`.

---

## 6. Valores restantes

Um valor é considerado restante (`remaining_values`) enquanto a maleta que o contém estiver fechada.

Quando uma maleta é aberta:

1. seu valor é revelado;
2. ela deixa de estar disponível;
3. seu valor deixa de fazer parte dos valores restantes.

O valor da maleta do jogador permanece entre os valores restantes enquanto sua maleta estiver fechada.

---

## 7. Oferta do Banqueiro

O Banqueiro faz uma oferta ao final de **cada uma das 9 rodadas**, inclusive uma última oferta após a Rodada 9.

A oferta é calculada a partir do estado atual da partida:

```
oferta = média(remaining_values) × percentual_da_rodada
```

A oferta final deve ser arredondada para centavos.

A estratégia do Banqueiro:

- baseia-se apenas no estado atual da partida e na rodada atual;
- **não** depende do histórico de ofertas anteriores;
- deve ser encapsulada em um componente de domínio isolado e substituível.

### Política inicial

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

Esses percentuais são parâmetros de configuração da estratégia inicial, não regras estruturais do domínio, e devem ficar configuráveis (não dispersos pelo código).

Para o MVP existe apenas esta estratégia matemática baseada na média dos valores restantes e no percentual da rodada.

Referência: `docs/decisions/0002-estrategia-inicial-do-banqueiro.md`.

### Oscilação das ofertas

A oferta **não** é obrigatoriamente crescente. Embora o percentual aumente ao longo das rodadas, a composição de `remaining_values` também muda conforme o jogador abre maletas. Portanto:

- se o jogador elimina valores baixos, a média dos valores restantes tende a aumentar e a oferta tende a subir;
- se o jogador elimina valores altos, a média dos valores restantes tende a cair e a oferta pode cair;
- o aumento do percentual do Banqueiro pode compensar parcial, totalmente ou insuficientemente essa variação.

Consequentemente, a oferta pode subir, cair ou permanecer próxima do valor anterior. Esse comportamento é intencional. A estratégia não deve impor artificialmente que uma oferta seja maior que a anterior.

---

## 8. Topa

Quando o jogador aceita a oferta:

- a partida oficial termina imediatamente;
- o valor da oferta aceita é registrado como resultado oficial;
- a maleta do jogador permanece fechada, salvo necessidade de exibição posterior;
- o resultado da partida informa que o jogador aceitou a oferta.

Após a aceitação, o jogador pode, opcionalmente, executar uma simulação pós-jogo (ver seção 12), que nunca altera o resultado oficial.

---

## 9. Não Topa

Quando o jogador recusa a oferta:

- a oferta é registrada como recusada;
- o jogo continua;
- a próxima rodada é iniciada, quando houver;
- se a recusa ocorrer após a oferta da Rodada 9, o jogo segue para a decisão de troca final (seção 11).

---

## 10. Resultado oficial da partida

O resultado oficial é registrado imediatamente no momento do encerramento oficial e nunca é alterado por simulações posteriores.

O encerramento oficial ocorre por um destes motivos:

1. **Aceitação de oferta (Topa):** o valor oficial recebido é o valor da oferta aceita.
2. **Final sem aceitar oferta:** após a decisão de troca final da Rodada 9, as duas últimas maletas são reveladas; o valor oficial é o da maleta que ficou com o jogador.

---

## 11. Endgame e troca final

Não há troca durante as rodadas 1 a 9.

Após a oferta da Rodada 9 restam a maleta do jogador e uma única última maleta fechada.

- Se o jogador escolher **Topa**, a partida termina com a oferta aceita.
- Se escolher **Não Topa**, o jogador recebe uma decisão final **opcional** de troca:

  > "Você deseja trocar sua maleta pela última maleta?"

  - **Não** → permanece com a maleta original;
  - **Sim** → troca a maleta do jogador pela última maleta fechada.

Após a decisão de troca, as duas últimas maletas são reveladas e a partida termina. O valor final oficial é o da maleta que ficou com o jogador.

A última maleta fechada é a única maleta elegível para troca.

Referência: `docs/decisions/0003-troca-final.md`.

---

## 12. Simulação pós-jogo

A simulação pós-jogo é opcional e só existe após o jogador aceitar uma oferta.

Fluxo:

1. o jogador aceita a oferta;
2. o resultado oficial é encerrado e registrado;
3. o Apresentador pergunta se o jogador deseja simular a continuação;
4. se não quiser, a experiência termina;
5. se quiser, inicia-se a simulação pós-jogo.

A simulação deve:

1. utilizar exatamente a mesma distribuição de valores da partida original;
2. partir do mesmo estado existente no momento em que a oferta foi aceita;
3. **não** gerar uma nova partida;
4. **não** sortear novamente os valores;
5. **não** alterar o resultado oficial;
6. revelar progressivamente as maletas que ainda não haviam sido abertas;
7. revelar, ao final, o valor da maleta do jogador;
8. quando o fluxo chegar a duas maletas, permitir simular a decisão hipotética de troca (seção 11);
9. permitir comparar o resultado oficial com o resultado hipotético.

A simulação é conceitualmente separada da partida oficial e não deve ser representada como continuação de uma partida encerrada. O resultado é apresentado separadamente, por exemplo:

```
Resultado oficial:                 R$ X
Resultado hipotético da simulação: R$ Y
Diferença:                         R$ Z
```

O resultado hipotético nunca substitui nem altera o resultado oficial.

Referências: `docs/decisions/0004-simulacao-pos-jogo.md` e `docs/decisions/0003-troca-final.md`.

---

## 13. Histórico da partida

Durante toda a execução, a partida mantém em memória um histórico estruturado que permite reconstruir sua narrativa completa (configuração inicial, histórico de cada rodada, resultado oficial e simulação pós-jogo, quando houver).

O conteúdo mínimo do histórico e a decisão de não implementar persistência permanente no MVP estão definidos em `docs/decisions/0005-historico-da-partida-e-persistencia.md`.

O histórico é distinto do estado atual da partida: o estado atual representa a situação corrente; o histórico registra a sequência de eventos e resultados.

---

## 14. Aleatoriedade

A partida deve aceitar uma fonte de aleatoriedade injetável ou equivalente.

Isso permite:

- partidas normais aleatórias;
- testes determinísticos;
- reprodução de cenários específicos.

A simulação pós-jogo utiliza exatamente a distribuição de valores da partida original: não há novo embaralhamento nem nova distribuição. Quando uma seed for utilizada, ela deve fazer parte do registro da partida.

---

## 15. Invariantes

O domínio deve garantir:

- existem exatamente 26 maletas no início;
- cada maleta possui exatamente um valor;
- cada valor pertence a exatamente uma maleta;
- uma maleta aberta não pode voltar a ficar fechada;
- uma maleta aberta não pode ser aberta novamente;
- a maleta do jogador é válida;
- a maleta do jogador não é aberta durante rodadas normais;
- a quantidade de aberturas por rodada não excede o permitido pela sequência da rodada;
- ao final da Rodada 9 restam exatamente duas maletas fechadas (a do jogador e a última maleta disponível);
- a troca só ocorre no endgame, após a recusa da oferta da Rodada 9, entre a maleta do jogador e a última maleta fechada;
- o jogo não pode continuar depois de encerrado;
- uma oferta não pode ser aceita duas vezes;
- o resultado oficial, uma vez registrado, não é alterado por simulações posteriores;
- valores monetários são tratados com precisão decimal.
