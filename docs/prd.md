# Product Requirements Document (PRD)

## Projeto: Topa ou Não Topa

## 1. Visão geral

O projeto `tont-game` é uma implementação digital do conceito do jogo televisivo "Topa ou Não Topa", desenvolvida inicialmente para execução em terminal por meio de uma interface CLI.

A primeira versão deve priorizar:

- regras de negócio claras;
- domínio independente da interface;
- testes automatizados;
- arquitetura preparada para futura evolução para GUI ou outra interface.

A CLI é a primeira interface, não o núcleo do sistema.

---

## 2. Objetivo

Criar uma experiência jogável em que o participante:

1. inicia uma partida;
2. escolhe uma maleta inicial;
3. abre outras maletas ao longo de rodadas;
4. observa os valores eliminados;
5. recebe ofertas do Banqueiro;
6. decide entre aceitar ou recusar cada oferta;
7. continua até aceitar uma oferta ou chegar ao final do jogo;
8. quando aplicável, participa da etapa final de troca definida nas regras.

---

## 3. Escopo da primeira versão

### Incluído

- 26 maletas;
- conjunto fixo de 26 valores monetários;
- embaralhamento das maletas;
- escolha da maleta inicial;
- controle de maletas abertas e fechadas;
- rodadas configuráveis;
- sequência inicial de abertura: `6, 5, 4, 3, 2, 1, 1...`;
- painel de valores ainda não revelados;
- cálculo de oferta do Banqueiro;
- decisão do jogador: Topa ou Não Topa;
- encerramento por aceitação de oferta;
- encerramento por abertura da maleta do jogador;
- etapa final de troca quando definida pelas regras;
- testes automatizados;
- interface CLI em PT-BR.

### Fora do escopo inicial

- interface gráfica;
- persistência de partidas;
- banco de dados;
- multiplayer;
- contas de usuário;
- sistema online;
- áudio;
- animações;
- integração com serviços externos;
- reprodução de conteúdo televisivo protegido.

---

## 4. Requisitos funcionais

### RF01 — Iniciar partida

O sistema deve criar uma nova partida com:

- 26 maletas;
- valores distribuídos aleatoriamente;
- nenhuma maleta aberta;
- nenhuma oferta realizada;
- estado inicial definido.

### RF02 — Escolher maleta inicial

O jogador deve selecionar uma maleta disponível.

A maleta escolhida passa a ser a `Player Briefcase`.

Ela permanece fechada durante as rodadas normais.

### RF03 — Abrir maletas

O jogador deve selecionar maletas para abertura conforme a quantidade definida pela rodada atual.

Uma maleta aberta não pode ser aberta novamente.

A maleta do jogador não pode ser aberta durante as rodadas normais.

### RF04 — Controlar rodadas

O sistema deve controlar a quantidade de maletas que precisam ser abertas em cada rodada.

A sequência inicial é:

- 6;
- 5;
- 4;
- 3;
- 2;
- 1;
- 1;
- continuar conforme a regra final documentada.

### RF05 — Calcular oferta

Ao final de cada rodada, o sistema deve calcular uma oferta do Banqueiro de acordo com a política definida em `game-rules.md`.

### RF06 — Decisão do jogador

Após uma oferta, o jogador deve escolher:

- Topa;
- Não Topa.

Se aceitar, a partida termina.

Se recusar, a partida continua.

### RF07 — Encerramento

Se o jogador recusar todas as ofertas até o final, sua maleta deve ser aberta e o valor revelado.

### RF08 — Troca final

Se a regra da partida determinar uma possibilidade de troca, ela deve ser apresentada no momento definido por `game-rules.md`.

---

## 5. Requisitos não funcionais

### RNF01 — Arquitetura

A lógica do domínio deve ser independente da interface CLI.

### RNF02 — Testabilidade

As regras principais devem ser testáveis sem executar a CLI.

### RNF03 — Precisão monetária

Valores monetários devem ser calculados com precisão decimal.

### RNF04 — Qualidade

O projeto deve utilizar `uv`, `ruff`, `pytest` e `taskipy`.

### RNF05 — Idioma

A interface deve ser PT-BR.

O código deve ser em Inglês.

---

## 6. Critérios de aceitação

- [ ] Uma partida sempre começa com exatamente 26 maletas.
- [ ] Cada valor oficial aparece exatamente uma vez.
- [ ] O jogador consegue selecionar uma maleta inicial válida.
- [ ] A maleta inicial permanece fechada durante as rodadas normais.
- [ ] Uma maleta aberta não pode ser aberta novamente.
- [ ] A maleta do jogador não pode ser selecionada para eliminação normal.
- [ ] A quantidade de aberturas respeita a sequência da rodada.
- [ ] O Banqueiro realiza uma oferta quando uma rodada termina.
- [ ] O jogador pode aceitar ou recusar a oferta.
- [ ] Ao aceitar, o jogo termina.
- [ ] Ao recusar, o jogo continua enquanto houver rodadas.
- [ ] Ao chegar ao final sem aceitar oferta, a maleta do jogador é revelada.
- [ ] A troca final, quando aplicável, segue exatamente as regras documentadas.
- [ ] As regras podem ser testadas sem depender da CLI.

---

## 7. Critérios de sucesso da primeira versão

A primeira versão será considerada funcional quando uma partida completa puder ser executada pela CLI do início ao fim, com:

- fluxo coerente;
- regras determinísticas quando uma semente aleatória for fornecida;
- valores corretamente controlados;
- ofertas calculadas;
- decisões registradas;
- encerramento correto;
- testes automatizados cobrindo o núcleo do domínio e os principais fluxos.
