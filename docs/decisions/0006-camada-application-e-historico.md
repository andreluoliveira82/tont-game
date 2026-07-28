# ADR 0006 — Camada Application, histórico da partida e resultado oficial

**Status:** aprovada
**Data:** 2026-07-28

## Contexto

Concluídas as Fases 2–4 (domínio, aleatoriedade, Banqueiro), a Fase 5 introduz
a **camada Application** (casos de uso que orquestram o domínio) e o **modelo de
histórico** da partida, além do **resultado oficial** imutável. É preciso definir
como o estado operacional e o histórico se relacionam sem que o histórico vire
uma segunda implementação das regras, mantendo o domínio livre de infraestrutura
e sem persistência no MVP. Complementa e refina o [ADR 0005](0005-historico-da-partida-e-persistencia.md).

## Decisão

### Separação de fases

O fluxo normal (Application, `GameRecord`, `OfficialResult` pelo caminho Topa e
recusas intermediárias) fica na **Fase 5**. O **endgame** (recusa da oferta da
Rodada 9, decisão de troca, `SwapBriefcase`, `RevealFinalBriefcase`, resultado
com/sem troca, conclusão) fica na nova **Fase 5.5**, respeitando o
[ADR 0003](0003-troca-final.md). A recusa da oferta da Rodada 9 transita o estado
para `FINAL_SWAP_PENDING` já na Fase 5, mas essa transição **não é consumida**
nem tem lógica de endgame na Fase 5.

### Camada Application

Casos de uso: `StartGame`, `SelectInitialBriefcase`, `OpenBriefcase`,
`ProcessBankerOffer`, `DecideOffer`. Uma composição operacional `GameSession`
agrupa `GameState` (estado atual) e `GameRecord` (histórico). Os casos de uso
coordenam ambos; o domínio não conhece infraestrutura.

### Modelo de histórico (domínio)

- `GameRecord` (append-only): `game_id` (UUID), `started_at`/`finished_at`
  (datetime UTC), `seed` (int | None), `initial_distribution` (26 pares nº→valor,
  **fonte histórica da verdade**), `player_briefcase_number`, `rounds` e
  `official_result` (write-once).
- `RoundRecord` (append-only): aberturas, oferta e decisão da rodada.
- Folhas imutáveis (`frozen`): `BriefcaseOpeningRecord`, `BankerOfferRecord`
  (rodada, oferta, **percentual utilizado**, `remaining_values`), `OfficialResult`.
- `Decision`: enum `ACCEPT`/`REJECT` (sem registro separado).

### Resultado oficial

`OfficialResult` é imutável (`frozen`) e write-once no `GameRecord`. No Topa
registra `ending_type=OFFER_ACCEPTED`, `amount_received` (= oferta aceita),
`player_briefcase_value` (valor real da maleta do jogador, gravado mesmo aceitando,
para auditoria/simulação/estatística — não exibido ao jogador neste momento) e a
rodada da decisão. Os desfechos de endgame (`FINAL_REVEAL_WITH_SWAP`/
`WITHOUT_SWAP`) ficam desenhados para a Fase 5.5.

### Relação GameState × GameRecord (consistência)

- `GameState` é a **autoridade** sobre o estado operacional e sobre as
  regras/invariantes.
- `GameRecord` é a **autoridade** sobre o registro histórico dos fatos ocorridos;
  **não** valida operações nem duplica regras de negócio.
- Ordem obrigatória nos casos de uso: **primeiro** validar/executar a ação no
  domínio com sucesso; **só então** registrar o fato no histórico. Uma operação
  inválida (exceção do domínio) **não** deve gerar registro parcial nem "fato
  fantasma". A consistência entre estado e histórico é uma preocupação explícita
  do desenho dos casos de uso (sem transação técnica/rollback no MVP).

### Imutabilidade

Folhas `frozen` (`BriefcaseOpeningRecord`, `BankerOfferRecord`, `OfficialResult`).
`RoundRecord` também é `frozen` (imutável): evolui por operações `with_opening`/
`with_offer`/`with_decision` que retornam uma nova instância, com `with_offer`/
`with_decision` write-once. O `GameRecord` é a **única autoridade append-only**:
mantém a lista interna de rodadas e a evolui substituindo a própria entrada;
`official_result` é write-once. Os acessores devolvem tuplas de objetos
imutáveis (cópia defensiva), de modo que uma rodada entregue por `rounds` não
pode ser alterada retroativamente. Sem event sourcing.

> Nota (implementação, Fase 5, commit `2661ef7`): na revisão final o
> `RoundRecord` foi consolidado como imutável (frozen) — antes era um contêiner
> mutável — para eliminar qualquer alteração retroativa do histórico via os
> objetos entregues por `rounds`.

### Ports de tempo e identificação

`Clock` (`now() -> datetime`, UTC) e `GameIdGenerator` (`new_id() -> UUID`) como
ports do domínio; implementações `SystemClock` e `UuidGameIdGenerator` na
infraestrutura, injetadas (mesma filosofia do `RandomSource`). Formatação/
localização de datas ficam nas camadas superiores.

### Seed e distribuição

A distribuição concreta das 26 maletas é a fonte histórica da verdade, capturada
no `StartGame` a partir do `GameState` já distribuído. A `seed` é complementar
(reprodutibilidade técnica) e nunca a única fonte para reconstruir a partida.

### Persistência

Sem persistência permanente e **sem** port de repositório nesta fase. O
`GameRecord` deve ser um registro limpo e potencialmente serializável no futuro,
sem acoplamento a banco, arquivo ou tecnologia específica.

### Analytics / visão administrativa (intenção futura — fora de escopo)

Registra-se a intenção futura de uma camada administrativa para os
donos/operadores do jogo, capaz de analisar o histórico acumulado de várias
partidas (comportamento das ofertas por rodada, taxas de aceitação, relação entre
valor recebido e valor real da maleta, distribuição de resultados, padrões de
decisão, etc.). **Nada disso é implementado agora** (sem analytics, métricas,
relatórios ou dashboard). A única obrigação atual é que o `GameRecord` preserve
fatos ricos e bem estruturados para que essa análise seja possível no futuro sem
reconstruir nem alterar o histórico das partidas.

## Justificativa

- Separar Fase 5/5.5 mantém cada entrega coesa e resolve o acoplamento do endgame
  (troca + revelação) num único incremento.
- A ordem "validar no domínio → registrar" evita registros inconsistentes sem
  exigir transações no MVP.
- Ports de tempo/id garantem testes determinísticos e domínio livre de infra.

## Impacto arquitetural

- Nova camada `application/`; novo pacote `domain/history/`; novos ports/impls.
- Evolução do `GameState` (oferta pendente, aceitar/recusar, transições de status)
  e do port `BankerStrategy` (`percentage_for_round`).
- Nenhuma alteração de regra de negócio; nenhuma persistência; endgame diferido.
