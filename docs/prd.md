# Product Requirements Document (PRD)

## Projeto: Topa ou Não Topa

## 1. Visão geral

O projeto `tont-game` é uma implementação digital do conceito do jogo televisivo "Topa ou Não Topa", desenvolvida inicialmente para execução em terminal por meio de uma interface CLI.

A primeira versão deve priorizar:

- regras de negócio claras;
- domínio independente da interface;
- testes automatizados;
- registro estruturado do histórico da partida em memória;
- arquitetura preparada para futura evolução para GUI, persistência ou outra interface.

A CLI é a primeira interface, não o núcleo do sistema.

---

## 2. Objetivo

Criar uma experiência jogável em que o participante:

1. inicia uma partida;
2. escolhe uma maleta inicial;
3. abre outras maletas ao longo de 9 rodadas;
4. observa os valores eliminados;
5. recebe uma oferta do Banqueiro ao final de cada rodada;
6. decide entre aceitar (Topa) ou recusar (Não Topa) cada oferta;
7. continua até aceitar uma oferta ou chegar ao endgame;
8. no endgame, após recusar a oferta da Rodada 9, decide opcionalmente pela troca final de maleta;
9. quando aceitar uma oferta, pode opcionalmente executar uma simulação pós-jogo do que teria acontecido.

---

## 3. Escopo da primeira versão

### Incluído

- 26 maletas;
- conjunto fixo de 26 valores monetários;
- embaralhamento das maletas;
- escolha da maleta inicial;
- controle de maletas abertas e fechadas;
- 9 rodadas com a sequência de abertura `6, 5, 4, 3, 2, 1, 1, 1, 1`;
- painel de valores ainda não revelados;
- cálculo de oferta do Banqueiro ao final de cada uma das 9 rodadas;
- decisão do jogador: Topa ou Não Topa;
- encerramento por aceitação de oferta;
- endgame com troca final opcional entre a maleta do jogador e a última maleta fechada;
- registro estruturado do histórico completo da partida em memória;
- simulação pós-jogo opcional após a aceitação de uma oferta;
- testes automatizados;
- interface CLI em PT-BR.

### Fora do escopo inicial

- interface gráfica;
- persistência permanente de partidas (banco de dados, arquivos);
- multiplayer;
- contas de usuário;
- sistema online;
- áudio;
- animações;
- integração com serviços externos;
- reprodução de conteúdo televisivo protegido.

> O histórico completo da partida é mantido em memória no MVP. A persistência permanente é explicitamente adiada — ver `docs/decisions/0005-historico-da-partida-e-persistencia.md`.

---

## 4. Requisitos funcionais

### RF01 — Iniciar partida

O sistema deve criar uma nova partida com:

- 26 maletas;
- valores distribuídos aleatoriamente;
- nenhuma maleta aberta;
- nenhuma oferta realizada;
- estado inicial definido;
- registro de histórico iniciado (configuração inicial, incluindo seed quando utilizada).

### RF02 — Escolher maleta inicial

O jogador deve selecionar uma maleta disponível.

A maleta escolhida passa a ser a `player_briefcase`.

Ela permanece fechada durante as rodadas normais.

### RF03 — Abrir maletas

O jogador deve selecionar maletas para abertura conforme a quantidade definida pela rodada atual.

Uma maleta aberta não pode ser aberta novamente.

A maleta do jogador não pode ser aberta durante as rodadas normais.

### RF04 — Controlar rodadas

O sistema deve controlar a quantidade de maletas que precisam ser abertas em cada uma das 9 rodadas, conforme a sequência:

| Rodada | Maletas a abrir |
|---:|---:|
| 1 | 6 |
| 2 | 5 |
| 3 | 4 |
| 4 | 3 |
| 5 | 2 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |
| 9 | 1 |

Ao final da Rodada 9 restam exatamente duas maletas fechadas: a do jogador e a última maleta disponível. Ver `docs/decisions/0001-estrutura-rodadas-e-endgame.md`.

### RF05 — Calcular oferta

Ao final de cada uma das 9 rodadas, o sistema deve calcular uma oferta do Banqueiro de acordo com a política definida em `game-rules.md`. A oferta pode subir, cair ou permanecer próxima da anterior (não é obrigatoriamente crescente).

### RF06 — Decisão do jogador

Após uma oferta, o jogador deve escolher:

- Topa;
- Não Topa.

Se aceitar, a partida oficial termina.

Se recusar, a partida continua (ou segue para a troca final, se a recusa ocorrer após a Rodada 9).

### RF07 — Troca final (endgame)

Após a recusa da oferta da Rodada 9, o jogador deve poder optar por trocar sua maleta pela última maleta fechada. Em seguida, as duas últimas maletas são reveladas e a partida termina. Ver `docs/decisions/0003-troca-final.md`.

### RF08 — Resultado oficial

O resultado oficial deve ser registrado imediatamente no encerramento e nunca ser alterado por simulações posteriores. Deve conter o motivo do encerramento, o valor oficial recebido, o valor real da maleta do jogador e a decisão de troca quando aplicável.

### RF09 — Simulação pós-jogo

Após o jogador aceitar uma oferta, o sistema deve poder oferecer uma simulação opcional do que teria acontecido se ele tivesse continuado, usando a mesma distribuição de valores e o estado do momento da aceitação, sem alterar o resultado oficial. Ver `docs/decisions/0004-simulacao-pos-jogo.md`.

### RF10 — Histórico da partida

O sistema deve manter em memória um histórico estruturado suficiente para reconstruir a narrativa completa da partida (configuração inicial, histórico por rodada, resultado oficial e simulação pós-jogo quando houver). Ver `docs/decisions/0005-historico-da-partida-e-persistencia.md`.

---

## 5. Requisitos não funcionais

### RNF01 — Arquitetura

A lógica do domínio deve ser independente da interface CLI e de qualquer tecnologia de persistência.

### RNF02 — Testabilidade

As regras principais devem ser testáveis sem executar a CLI.

### RNF03 — Precisão monetária

Valores monetários devem ser calculados com precisão decimal.

### RNF04 — Qualidade

O projeto deve utilizar `uv`, `ruff`, `pytest` e `taskipy`.

### RNF05 — Idioma

A interface deve ser PT-BR.

O código deve ser em Inglês.

### RNF06 — Separação de conceitos

Estado atual, histórico, resultado oficial e simulação pós-jogo devem permanecer conceitualmente separados no modelo.

---

## 6. Critérios de aceitação

- [ ] Uma partida sempre começa com exatamente 26 maletas.
- [ ] Cada valor oficial aparece exatamente uma vez.
- [ ] O jogador consegue selecionar uma maleta inicial válida.
- [ ] A maleta inicial permanece fechada durante as rodadas normais.
- [ ] Uma maleta aberta não pode ser aberta novamente.
- [ ] A maleta do jogador não pode ser selecionada para eliminação normal.
- [ ] A quantidade de aberturas respeita a sequência das 9 rodadas.
- [ ] Ao final da Rodada 9 restam exatamente duas maletas fechadas.
- [ ] O Banqueiro realiza uma oferta ao final de cada uma das 9 rodadas.
- [ ] A oferta pode subir, cair ou permanecer próxima da anterior.
- [ ] O jogador pode aceitar ou recusar a oferta.
- [ ] Ao aceitar, a partida oficial termina e o resultado oficial é registrado.
- [ ] Ao recusar, o jogo continua enquanto houver rodadas.
- [ ] Após recusar a oferta da Rodada 9, o jogador pode optar pela troca final.
- [ ] A troca final ocorre apenas entre a maleta do jogador e a última maleta fechada.
- [ ] A simulação pós-jogo, quando executada, usa a mesma distribuição e não altera o resultado oficial.
- [ ] O histórico da partida permite reconstruir a narrativa completa.
- [ ] As regras podem ser testadas sem depender da CLI.

---

## 7. Critérios de sucesso da primeira versão

A primeira versão será considerada funcional quando uma partida completa puder ser executada pela CLI do início ao fim, com:

- fluxo coerente pelas 9 rodadas e endgame;
- regras determinísticas quando uma semente aleatória for fornecida;
- valores corretamente controlados;
- ofertas calculadas ao final de cada rodada;
- decisões registradas;
- resultado oficial correto e imutável;
- simulação pós-jogo opcional funcional e claramente separada do resultado oficial;
- histórico completo disponível em memória;
- testes automatizados cobrindo o núcleo do domínio e os principais fluxos.
