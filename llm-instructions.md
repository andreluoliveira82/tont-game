# Instruções para o LLM

## 1. Propósito

Este arquivo define as regras operacionais que qualquer LLM utilizado para desenvolver o projeto `tont-game` deve seguir.

Antes de gerar ou alterar qualquer código, o LLM deve ler, nesta ordem:

1. `llm-instructions.md`
2. `docs/prd.md`
3. `docs/game-rules.md`
4. `docs/glossary.md`
5. `docs/architecture.md`
6. `docs/roadmap.md`
7. Os registros de decisão em `docs/decisions/` (ADRs 0001 a 0005 e eventuais novos).

Esses documentos formam a fonte oficial de contexto do projeto. Os ADRs em `docs/decisions/` são autoritativos para as decisões que cobrem (estrutura de rodadas e endgame, estratégia do Banqueiro, troca final, simulação pós-jogo, histórico e persistência).

Este arquivo (`llm-instructions.md`) reside exclusivamente na raiz do projeto e não deve ser duplicado em `docs/`.

---

## 2. Regra fundamental: não inventar requisitos

O LLM NÃO deve inventar, presumir ou alterar regras de negócio que não estejam documentadas.

Se uma decisão necessária para implementar uma funcionalidade não estiver definida:

1. identifique a ambiguidade;
2. explique por que ela afeta a implementação;
3. registre a dúvida;
4. solicite ao desenvolvedor uma decisão antes de implementar.

Não utilizar conhecimento externo sobre versões televisivas do jogo para substituir as regras deste projeto.

---

## 3. Ordem de execução

O desenvolvimento deve seguir o `roadmap.md`.

O LLM deve:

- trabalhar em uma fase por vez;
- implementar apenas o escopo da fase atual;
- não avançar automaticamente para fases futuras;
- executar testes após alterações relevantes;
- executar lint/format antes de concluir uma tarefa;
- atualizar a documentação quando uma decisão técnica ou de negócio for oficialmente aprovada.

---

## 4. Convenções de nomenclatura

### Python

Arquivos e módulos Python devem usar `snake_case`:

- `game_state.py`
- `open_briefcase.py`
- `banker_offer.py`

Pacotes Python também devem usar `snake_case`.

### Documentação e arquivos não-Python

Arquivos de documentação Markdown devem usar `kebab-case`:

- `game-rules.md`
- `llm-instructions.md`
- `architecture.md`

Nenhum caminho deve conter acentos, espaços ou caracteres especiais desnecessários.

---

## 5. Idioma

### Código

Em Inglês:

- classes;
- funções;
- métodos;
- variáveis;
- constantes;
- Type Hints;
- nomes de módulos;
- nomes de pacotes;
- docstrings.

Docstrings devem ser objetivas e utilizadas quando agregarem contexto.

### Interface

Em Português do Brasil:

- menus;
- mensagens;
- prompts;
- erros exibidos ao jogador;
- textos da CLI;
- logs destinados ao usuário.

### Documentação

A documentação técnica do projeto deve ser escrita em Português do Brasil.

---

## 6. Arquitetura

A lógica de negócio deve permanecer independente da CLI.

Regras:

- domínio não conhece a CLI;
- entidades de domínio não fazem `print`;
- domínio não usa `input`;
- casos de uso não devem depender diretamente de detalhes de apresentação;
- infraestrutura não deve conter regras centrais do jogo;
- dependências devem apontar para dentro das camadas.

Seguir Clean Architecture e princípios SOLID sem criar abstrações artificiais apenas para cumprir padrões.

Evitar overengineering.

---

## 7. Dinheiro

Valores monetários devem utilizar `Decimal`, nunca `float`.

A representação monetária deve respeitar o padrão brasileiro na interface:

- `R$ 0,50`
- `R$ 1.000,00`
- `R$ 1.000.000,00`

A camada de domínio deve trabalhar com valores numéricos apropriados para cálculos exatos; a formatação para PT-BR pertence à camada de apresentação.

---

## 8. Testes

Toda regra de negócio relevante deve possuir testes automatizados.

Prioridade:

1. testes unitários do domínio;
2. testes dos casos de uso;
3. testes de integração do fluxo do jogo;
4. testes da CLI quando houver comportamento relevante de interface.

Os testes devem verificar comportamento, não detalhes internos desnecessários.

---

## 9. Qualidade

Ferramentas obrigatórias:

- `uv`
- `ruff`
- `pytest`
- `taskipy`

Comandos principais devem ser disponibilizados pelo `taskipy`.

O código deve ser formatado e validado antes da conclusão de cada etapa.

---

## 10. Protocolo de trabalho do LLM

Para cada tarefa:

1. Leia a documentação relevante.
2. Inspecione o código existente.
3. Identifique a fase atual do roadmap.
4. Liste brevemente o que será alterado.
5. Implemente somente o necessário.
6. Execute testes.
7. Execute lint/format.
8. Corrija problemas encontrados.
9. Verifique se a documentação ainda está consistente.
10. Informe o que foi concluído e o próximo passo recomendado.

Não faça grandes refatorações fora do escopo da tarefa.

---

## 11. Integridade da documentação

Se uma decisão for tomada que altere uma regra ou arquitetura:

- atualize o documento correspondente;
- se for uma decisão arquitetural relevante, crie um registro em `docs/decisions/`;
- mantenha uma única fonte oficial para cada regra.

Nunca deixe o código contradizer silenciosamente a documentação.

---

## 12. Critério de conclusão

Uma tarefa só deve ser considerada concluída quando:

- implementação estiver completa;
- testes relevantes estiverem passando;
- lint estiver passando;
- formatação estiver correta;
- documentação necessária estiver atualizada;
- nenhuma regra de negócio tiver sido inventada ou alterada sem decisão explícita.

---

## 13. Documentação viva

A documentação do projeto é viva e não é congelada após a Fase 0. Código, arquitetura, decisões e documentação devem permanecer coerentes entre si durante toda a evolução do projeto.

Ao concluir cada fase:

- verifique se a implementação exige atualização de algum documento existente e atualize apenas o que estiver desatualizado, inconsistente ou incompleto;
- mantenha o `roadmap.md` sincronizado com o estado real (fases concluídas, com status e commit associado);
- registre decisões arquiteturais ou de negócio relevantes em `docs/decisions/` (ADRs); não crie ADRs para detalhes triviais;
- mantenha o glossário e a terminologia consistentes entre todos os documentos;
- não altere regras de negócio silenciosamente para "combinar" com o código — se houver divergência, identifique a causa e, se exigir nova decisão de negócio, consulte o desenvolvedor;
- revise a consistência entre código e documentação antes de considerar a fase concluída.
