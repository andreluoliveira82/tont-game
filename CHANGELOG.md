# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.1.0] - 2026-07-29

Primeira fase do Roadmap 2.0: persistência de partidas concluídas e histórico
entre execuções, como capacidade **opcional e aditiva** (o jogo continua
totalmente jogável sem ela).

### Adicionado

- Port de saída `GameHistoryRepository` (domínio), VO `GameHistorySummary` e os
  casos de uso `SaveFinishedGame` e `ListGameHistory`.
- Adaptador `FileGameHistoryRepository` (um JSON por partida) e um locator que
  encapsula o diretório de dados na infraestrutura.
- Schema JSON público e versionado (`schema_version`), desacoplado da estrutura
  interna do `GameRecord`.
- Salvamento automático da partida ao encerrar, com aviso discreto e
  **degradação graciosa** em caso de falha de I/O.
- Comando `tont-game history` para rever partidas anteriores, com despacho
  preparado para futuros subcomandos.
- ADR 0007 (estratégia concreta de persistência).

## [1.0.0] - 2026-07-29

Primeira versão estável — encerramento do Ciclo 1 (Fases 0–10.5). Uma partida
completa de "Topa ou Não Topa" é jogável do início ao fim pela CLI, em PT-BR,
com regras corretas e reprodutibilidade por seed.

### Adicionado

- Modelo de domínio: `Money` (precisão decimal), `Briefcase`, `GameState`,
  `GameStatus`, `RoundSchedule`, valores oficiais e invariantes das 9 rodadas.
- Distribuição aleatória reproduzível via porta `RandomSource` (com seed opcional).
- Estratégia do Banqueiro (`BankerStrategy`/`DefaultBankerStrategy`): média dos
  valores restantes × percentual da rodada, sem monotonicidade artificial.
- Camada de aplicação e casos de uso do fluxo: `StartGame`,
  `SelectInitialBriefcase`, `OpenBriefcase`, `ProcessBankerOffer`, `DecideOffer`.
- Endgame com troca final opcional (`DecideFinalSwap`, com e sem troca).
- Histórico factual da partida em memória (`GameRecord`) e resultado oficial
  imutável (`OfficialResult`).
- Simulação pós-jogo `CONTINUE_HOLD` (`RunPostGameSimulation`), derivação pura e
  não interativa, separada do resultado oficial.
- Suíte de testes de unidade e integração.
- Interface de linha de comando (`interface_adapters/cli`): seleção de maleta,
  rodadas, ofertas, decisões Topa/Não Topa, endgame e simulação pós-jogo.
- Refinamento de UX da CLI: maletas disponíveis, status compacto, bloco de
  decisão com a lista completa de valores, revelação das duas maletas no
  endgame, aliases de entrada, eco da seed e encerramento gracioso em EOF/Ctrl-C.
- Narração de encerramento (`interface_adapters/cli/narration.py`): mensagem
  emocional opcional após a linha factual, escolhida de forma determinística.
- Documentação do projeto (PRD, regras do jogo, arquitetura, glossário, roadmap
  e ADRs 0001–0006) e licença MIT.

### Notas

- Não há persistência permanente nem analytics nesta versão; o histórico é
  mantido apenas em memória durante a execução.
- As evoluções futuras estão organizadas no "Roadmap 2.0" (Fases 11+), ainda
  não aprovadas para implementação.

[1.1.0]: https://github.com/andreluoliveira82/tont-game/releases/tag/v1.1.0
[1.0.0]: https://github.com/andreluoliveira82/tont-game/releases/tag/v1.0.0
