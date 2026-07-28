# ADR 0005 — Histórico da partida e persistência

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

Deseja-se poder reconstruir a narrativa completa de cada partida (aberturas, valores eliminados, ofertas, decisões, resultado, simulação) e analisá-la posteriormente. Ao mesmo tempo, banco de dados e persistência permanente estão fora do escopo do MVP.

## Decisão

Desde o MVP, o projeto mantém **em memória**, de forma estruturada, o histórico completo de cada partida durante seu ciclo de vida. Esse registro (`GameRecord` ou equivalente) deve conter, no mínimo:

**Configuração inicial:** identificador único da partida; data/hora de início (se aplicável); valores disponíveis; distribuição dos valores entre as maletas; seed da aleatoriedade (quando utilizada); maleta escolhida pelo jogador.

**Histórico de cada rodada:** número da rodada; maletas abertas; valores revelados; valores ainda não revelados naquele momento; oferta do Banqueiro; percentual utilizado; decisão do jogador (Topa/Não Topa).

**Resultado oficial:** motivo do encerramento; oferta aceita (quando aplicável); valor oficial recebido; valor real da maleta do jogador; decisão final de troca (quando aplicável); valor final oficial.

**Simulação pós-jogo (se realizada):** se foi executada; maletas reveladas; valor da maleta do jogador; decisão hipotética de troca (quando aplicável); resultado hipotético; comparação e diferença em relação ao oficial.

**Persistência permanente NÃO faz parte do MVP.** O histórico existe apenas em memória durante a execução; não é necessário armazenar partidas após o encerramento do programa. Persistência futura (JSON, SQLite, banco de dados) poderá ser adicionada sem acoplar o domínio a uma tecnologia específica.

### Complemento (2026-07-28) — Seed × distribuição concreta

Formalizado após a Fase 3:

- A **distribuição concreta das 26 maletas** é o registro histórico do que efetivamente ocorreu na partida e deve fazer parte do `GameRecord` como fato oficial.
- A **seed**, quando explicitamente fornecida, pode ser registrada como informação complementar para reprodutibilidade técnica e auditoria, mas **não** é a única fonte de verdade para reconstruir a partida.

Em resumo: distribuição concreta = registro histórico; seed = reprodutibilidade técnica opcional. Esta orientação será incorporada ao modelo de `GameRecord` na Fase 5 (não implementada na Fase 3).

## Justificativa

- Permite responder, hoje ou no futuro, a perguntas como: quais maletas foram abertas por rodada, quais valores eliminados, como as ofertas oscilaram, quais decisões foram tomadas, qual oferta foi aceita, qual era o valor real da maleta do jogador, qual teria sido o resultado se continuasse e se teria sido vantajoso trocar.
- Registrar desde o MVP evita retrabalho arquitetural quando a persistência for introduzida.

## Impacto arquitetural

- Distinção conceitual obrigatória entre: **estado atual** da partida; **histórico** de eventos/resultados; **resultado oficial**; **simulação pós-jogo**. Esses conceitos devem permanecer separados, ainda que os nomes exatos das classes sejam livres.
- O modelo de domínio e os casos de uso não devem impedir que um `GameRecord` completo seja persistido futuramente.
- Não criar camada de persistência complexa por antecipação. Apenas garantir o desacoplamento entre domínio e tecnologia de persistência.
