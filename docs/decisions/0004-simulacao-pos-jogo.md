# ADR 0004 — Simulação pós-jogo

**Status:** aprovada
**Data:** 2026-07-27

## Contexto

Quando o jogador aceita uma oferta, a partida oficial termina. Há interesse em permitir que o jogador veja o que teria acontecido se tivesse continuado, sem que isso altere o resultado oficial.

## Decisão

Após o jogador aceitar uma oferta (**Topa**):

1. o resultado oficial é encerrado e registrado imediatamente;
2. o Apresentador pergunta se o jogador deseja simular a continuação;
3. se não quiser, a experiência termina;
4. se quiser, inicia-se a simulação pós-jogo.

A simulação:

- utiliza **exatamente** a mesma distribuição de valores da partida original;
- parte do mesmo estado existente no momento em que a oferta foi aceita;
- **não** gera nova partida e **não** sorteia valores novamente;
- **não** altera o resultado oficial;
- revela progressivamente as maletas que ainda não haviam sido abertas;
- ao final, revela o valor da maleta do jogador;
- quando o fluxo chegar a duas maletas, permite simular a decisão hipotética de troca ([ADR 0003](0003-troca-final.md));
- permite comparar o resultado oficial com o resultado hipotético.

A simulação é conceitualmente separada da partida oficial; não é uma continuação de uma partida encerrada. O resultado é apresentado separadamente:

```
Resultado oficial:              R$ X
Resultado hipotético da simulação: R$ Y
Diferença:                      R$ Z
```

## Justificativa

- Entrega valor de entretenimento e análise ("e se eu tivesse continuado?") sem comprometer a integridade do resultado oficial.
- A separação explícita evita que o resultado hipotético seja confundido com o oficial ou o substitua.

## Impacto arquitetural

- O estado oficial da partida no momento da aceitação deve ser suficiente para conduzir a simulação sem recriar a partida nem re-embaralhar valores ([ADR 0005](0005-historico-da-partida-e-persistencia.md)).
- O resultado oficial e o resultado da simulação são conceitos distintos e devem ser modelados separadamente.
- A simulação registra: se foi executada, maletas reveladas, valor da maleta do jogador, decisão hipotética de troca (quando aplicável), resultado hipotético e a diferença em relação ao oficial.
- A simulação é uma responsabilidade da aplicação/apresentação sobre o estado do domínio; o domínio não deve tratá-la como continuação da partida oficial.
