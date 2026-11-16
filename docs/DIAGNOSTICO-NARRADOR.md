# Diagnóstico do narrador — problemas observados em jogo e correções propostas

> Origem: cerca de 12 sessões jogadas em sequência numa campanha longa (sessões 15 a 26), em novembro de 2026.
> Escopo: o comportamento do narrador (skill `narrar` e afins), o motor de dados, o MCP e as preferências.
> Este arquivo não contém conteúdo de campanha. Os exemplos são genéricos.

---

## 1. Resumo

O motor de regras funciona. Os problemas estão em três lugares:

1. **Estado e dados.** O motor não guarda estado. Quem passa a Fome a cada rolagem é o narrador, e ele erra.
2. **Conduta e comunicação.** O formato de cena existe no papel (Preferências §10, skill `narrar`), mas não se sustenta em sessões longas. O narrador fica prolixo, decide pelo jogador, larga o seletor de opções e mistura português de Portugal.
3. **Planejamento e ritmo.** Os arcos não ficam visíveis para o jogador e as aventuras se esticam. Os objetivos viram uma lista sem hierarquia.

A causa comum é que as regras de conduta são texto solto, e nada as verifica. Depois que a conversa é compactada, elas somem.

---

## 2. Problemas observados

### 2.1 Estado e dados
| # | Problema | Causa |
|---|---|---|
| D1 | Rolagem com a Fome de antes de um Rouse que já tinha subido a Fome (várias vezes) | `rolar(parada, fome)` recebe a Fome à mão |
| D2 | Dez Rouses de despertar num lote só, partindo de Fome 0 | `rouse(quantidade=N)` não sabe da Fome real nem das alimentações entre as noites |
| D3 | `oponente` errado em testes resistidos | Não há conferência |
| D4 | Parada oferecida maior que a real (12 em vez de 10) | Paradas calculadas de cabeça, sem ler a ficha |
| D5 | Regras inventadas na hora (custo de FdV por falha, +1 dado de "técnica", custos de "vitória com custo") | Não há um lugar para registrar "decisão do narrador" nem para pedir aprovação |

### 2.2 Conduta e comunicação
| # | Problema | Regra que já existia |
|---|---|---|
| C1 | **Decidir pelo jogador:** 13 rolagens seguidas numa montagem; Falhas Bestiais narradas sem escolha | "Cada cena exige pelo menos uma decisão do jogador" |
| C2 | **Seletor de opções sumido** por várias sessões; opções só em texto, sem "Outra ação" | Preferências §10 |
| C3 | **Português de Portugal** em jogo PT-BR ("estava a falar", "pô-lo", "acção", "actual", "facto", narração em "tu") | Preferências §9 |
| C4 | **Jargão e latim** acumulados sem explicação: o jogador perde o fio | — (não existe regra) |
| C5 | **Prolixidade:** recaps longos, tabelas no meio da cena, notas de mesa misturadas à narração | "Narração 2-3 parágrafos; interações curtas" |
| C6 | **Opções sem didática:** a parada, a dificuldade e a chance nem sempre aparecem de forma simples | "Prós e contras detalhados" |
| C7 | **Ruído técnico** para o jogador (commit, verificação de segurança, nome de ferramenta) | "Documentação silenciosa" |
| C8 | **Perda de premissas** depois da compactação: foi o jogador quem notou | — |
| C9 | Notas secretas (`direcao.md`) escritas em fluxo de consciência, difíceis de usar depois | — |

### 2.3 Planejamento e ritmo
| # | Problema |
|---|---|
| P1 | O jogador não sabe em que ponto do arco está: falta um "mapa" visível de Partida > História > Aventura e do que fecha cada uma |
| P2 | Aventuras esticadas para além de 1-3 sessões, sem ponto de chegada |
| P3 | `objetivos.md` virou uma lista longa com IDs fora de ordem (H5, A10, A14…) e objetivos concluídos misturados aos ativos |
| P4 | Cenas sem objetivo, obstáculo e risco claros: falta critério para cortar a cena ou abrir uma nova |
| P5 | Sequências de gastos e rerrolagens que travam a cena (três testes em seguida sobre a mesma ação) |

---

## 3. Correções propostas

Em ordem de impacto. Cada item diz onde mexer.

### F1 — Motor com estado (resolve D1, D2, D4)
- **Onde:** `scripts/vtm_mcp.py`, `scripts/vtm_motor.py`, `tests/test_mcp.py`.
- Ler a Fome, a Potência, a FdV e a Humanidade de `estado.json` quando o parâmetro não vier. Se vier e for diferente do estado, **recusar** e dizer o valor certo.
- `rouse`, `despertar`, `alimentar`, `rerolar_fdv`, `aplicar_dano` e `remorso` **gravam** o resultado em `estado.json`.
- `rouse(quantidade>1)`: só com `noites_intercaladas=false` explícito. Para despertares em várias noites, uma ferramenta `montagem(noites, eventos)` que aplica as alimentações na ordem.
- Nova ferramenta `parada(atributo, habilidade, bonus)`: lê `personagem.md` (ou um `ficha.json`) e devolve o total, para não calcular de cabeça.
- Nova ferramenta `chance(parada, fome, dificuldade)`: probabilidade aproximada de vitória, para usar nas opções (C6).

### F2 — Contrato de resposta do narrador (resolve C1, C2, C5, C6, C7)
- **Onde:** `skills/narrar/SKILL.md` (no topo, curto e numerado) e `09_Preferencias/01_Preferencias_de_Jogo.md` §10.
- Esqueleto fixo de toda mensagem de jogo:
  1. **Resultado** (se houve rolagem): uma linha, `Parada Xd (YN+ZF) | DD | [normais] | (fome) → resultado`.
  2. **Narração:** até 120-150 palavras, 2 parágrafos.
  3. **Opções A/B/C:** título curto + até 2 linhas cada: *ganho · risco · teste (X dados, DD Y, ~Z%)*.
  4. **Seletor** com rótulos de até 7 palavras e "Outra ação (descreva)".
- Proibido na mensagem de jogo: recapitulação de mais de 3 linhas, tabela, nota técnica, nome de ferramenta.
- **Uma rolagem de risco por mensagem.** Gasto de FdV, vitória com custo e rerrolagem são decisões do jogador, oferecidas como opções.
- **Montagem:** no máximo 3 rolagens por mensagem. Crítico Confuso e Falha Bestial viram cena curta com escolha.
- Exemplos bons e ruins dentro da skill (3 pares curtos), porque o modelo imita exemplos mais do que segue regras.

### F3 — Língua e clareza (resolve C3, C4)
- **Onde:** `09_Preferencias` §9, `skills/narrar`, novo `scripts/estilo.py` + teste.
- Lista de construções de português de Portugal proibidas: "a + infinitivo" no lugar do gerúndio, "pô-lo/fê-lo", "acção/actual/facto/contacto", "tu" na narração, "rapariga", "casa de banho". Diálogo de NPC pode usar "tu" se for marca de época, mas a narração e as opções, não.
- **Orçamento de jargão:** no máximo 1 termo de lore ou frase em latim por parágrafo, sempre traduzido na mesma frase.
- Glossário da campanha (`glossario.md` na pasta da campanha) com termos explicados em uma linha. A skill o lê no início.
- `estilo.py checar <arquivo>`: aponta construções de português de Portugal e frases em latim sem tradução nos logs de sessão. Pode rodar na auditoria.

### F4 — Recuperação depois da compactação (resolve C8)
- **Onde:** `hooks/hooks.json`, `scripts/campanha.py`.
- Hook `SessionStart` com matcher `compact` (e `resume`) que injeta: o contrato de resposta (F2, em 10 linhas), o estado atual (números) e a **decisão pendente**.
- Novo arquivo na campanha: `mesa.json` (ou uma seção em `estado.json`) com a cena atual, a decisão pendente e as opções oferecidas. É gravado a cada cena.

### F5 — Regras improvisadas (resolve D5)
- **Onde:** `skills/narrar`, `09_Preferencias/02_Regras_da_Casa.md`.
- Toda regra fora do Core e das RC é marcada **"decisão do narrador"** na mensagem, explicada em uma linha, e registrada em `decisoes_narrador.md` na campanha. No fim da sessão, o jogador aprova (vira RC) ou descarta.
- Antes de improvisar, `buscar_acervo` (ou o agente `guardiao-regras`).

### F6 — Arcos visíveis e ritmo (resolve P1-P5)
- **Onde:** `skills/gerenciar`, `skills/criar`, `08_Templates/`, `scripts/campanha.py`.
- Novo arquivo **público** por campanha: `arcos.md`, com Partida > História > Aventura atual. Para cada nível: objetivo em uma frase, o que fecha o nível, número de sessões previsto e o ponto atual. O segredo continua em `direcao.md`; `arcos.md` só mostra o que o personagem sabe.
- **Abertura de sessão:** 3 linhas: onde estamos na hierarquia, o que falta para fechar a aventura, e a decisão pendente.
- **Orçamento de aventura:** 1-3 sessões. Na 3ª, a skill propõe um fecho (clímax ou corte).
- **Critério de cena:** toda cena declara (para o narrador, não para o jogador) objetivo, obstáculo e risco. Sem os três, a cena vira transição de uma linha.
- **`objetivos.md` enxuto:** só os ativos, agrupados por nível; os concluídos vão para `objetivos_arquivo.md`. A auditoria avisa quando há mais de 8 ativos.
- **Notas secretas:** `direcao.md` em tópicos fixos (Arco, Próxima cena, Ganchos, Decisões em aberto). Proibido texto corrido.

### F7 — Auditoria e testes de conduta
- **Onde:** `scripts/vtm_campanha.py`, `tests/`, e `claude plugin eval` se disponível.
- Na auditoria: rolagens em `rolagens.jsonl` cuja Fome difere da Fome do estado naquele momento; logs de sessão com construções de português de Portugal.
- Casos de avaliação da skill `narrar`: dado um estado e um pedido do jogador, a resposta tem no máximo X palavras, 3 opções, o seletor, nenhuma rolagem sem decisão e PT-BR limpo.

---

## 4. Ordem sugerida para a sessão de desenvolvimento

1. **F2 + F3** (contrato de resposta e língua). É só texto nas skills e preferências, e tem o maior efeito imediato.
2. **F1** (motor com estado), com testes.
3. **F4** (hook pós-compactação + `mesa.json`).
4. **F6** (`arcos.md`, objetivos enxutos, orçamento de aventura).
5. **F5 + F7** (decisões do narrador, auditoria de conduta, avaliações).

O prompt pronto para essa sessão está em `docs/PROMPT-DESENVOLVIMENTO.md`.
