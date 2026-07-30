# ADR 0007 — Estratégia de persistência do histórico

**Status:** aprovada
**Data:** 2026-07-29

## Contexto

O [ADR 0005](0005-historico-da-partida-e-persistencia.md) decidiu manter o
histórico apenas em memória no MVP e deixou **explicitamente em aberto** *qual*
estratégia de persistência adotar no futuro ("JSON, SQLite ou banco de dados…
sem acoplar o domínio"). A Fase 11 do Roadmap 2.0 materializa essa persistência,
o que exige fixar a estratégia concreta.

## Decisão

Persistir cada **partida concluída** por meio de:

- uma **porta de saída** de domínio, `GameHistoryRepository` (`save` e
  `list_summaries`), com falhas expostas como `GameHistoryError` — persistência
  é uma **capacidade opcional**, não uma dependência do domínio;
- um **adaptador de infraestrutura** `FileGameHistoryRepository`, que grava **um
  arquivo JSON por partida** (não banco de dados);
- um **schema público e versionado** (`schema_version`), desacoplado da estrutura
  interna do `GameRecord` (dinheiro como string decimal, datas ISO-8601,
  identificadores como string, enums por valor);
- um **locator na infraestrutura** que resolve o diretório de dados; o restante
  da aplicação recebe apenas um caminho e nunca o codifica;
- **gravação automática** ao encerrar a partida, com **degradação graciosa**: se
  a gravação/leitura falhar, o jogo continua normalmente.

## Justificativa

- Proporcional ao estágio: arquivo/JSON é simples, legível e auditável; um banco
  de dados seria desproporcional agora.
- Preserva a Clean Architecture: domínio e casos de uso dependem apenas da porta;
  a tecnologia de armazenamento fica confinada à infraestrutura e pode mudar
  (XDG/AppData/BD) alterando só o adaptador e o locator.
- O schema versionado torna o formato um contrato durável, independente de
  mudanças internas do código.

## Impacto arquitetural

- Nova porta de saída no domínio e um adaptador na infraestrutura; nenhuma
  mudança na direção das dependências (`Infra → Interface Adapters → Application
  → Domain`).
- Não altera regras do jogo, o resultado oficial nem a simulação `CONTINUE_HOLD`.
- Complementa o ADR 0005 (que permanece válido quanto à separação de conceitos e
  ao desacoplamento) fixando a estratégia concreta antes deixada em aberto.
