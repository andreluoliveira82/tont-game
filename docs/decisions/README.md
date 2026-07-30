# Registros de Decisão (ADRs)

Este diretório contém os registros de decisões relevantes do projeto `tont-game`.

Cada registro descreve, de forma objetiva:

- **contexto** — a situação que motivou a decisão;
- **decisão** — o que foi decidido;
- **justificativa** — por que essa opção foi escolhida;
- **impacto arquitetural** — consequências para o código e para a evolução do projeto, quando aplicável.

Quando uma decisão for revista, o registro correspondente deve ser atualizado ou substituído por um novo registro que o referencie. A documentação principal (`docs/`) sempre reflete a decisão vigente; os ADRs preservam o histórico e a justificativa.

## Índice

| Nº | Decisão |
|---:|---|
| [0001](0001-estrutura-rodadas-e-endgame.md) | Estrutura das rodadas e endgame |
| [0002](0002-estrategia-inicial-do-banqueiro.md) | Estratégia inicial do Banqueiro |
| [0003](0003-troca-final.md) | Troca final de maleta |
| [0004](0004-simulacao-pos-jogo.md) | Simulação pós-jogo |
| [0005](0005-historico-da-partida-e-persistencia.md) | Histórico da partida e persistência |
| [0006](0006-camada-application-e-historico.md) | Camada Application, histórico da partida e resultado oficial |
| [0007](0007-persistencia-do-historico.md) | Estratégia de persistência do histórico |
