# Documentação revisada — tont-game

Este diretório contém a documentação revisada para inicialização do projeto `tont-game`.

Arquivos:

- `llm-instructions.md` — regras operacionais para o LLM.
- `prd.md` — requisitos do produto.
- `game-rules.md` — regras oficiais do jogo.
- `glossary.md` — vocabulário do domínio.
- `architecture.md` — arquitetura e organização técnica.
- `roadmap.md` — fases de desenvolvimento.

## Ordem recomendada

1. Copiar `llm-instructions.md` para a raiz do projeto.
2. Criar `docs/`.
3. Copiar `prd.md`, `game-rules.md`, `glossary.md`, `architecture.md` e `roadmap.md` para `docs/`.
4. Criar `docs/decisions/`.
5. Inicializar o Git.
6. Abrir o projeto no VSCode.
7. Iniciar o LLM CLI.
8. Pedir ao LLM para ler toda a documentação.
9. Solicitar que execute somente a Fase 1 do roadmap.
10. Validar o resultado antes de avançar.

## Observação

A tabela de valores das maletas foi explicitamente definida como decisão inicial de produto em `game-rules.md`. Caso a intenção seja reproduzir uma tabela específica de uma versão televisiva, substitua essa decisão antes de iniciar a implementação.
