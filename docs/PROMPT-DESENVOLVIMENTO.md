# Prompt para a sessão de desenvolvimento do plugin

Copiar o bloco abaixo numa sessão nova, com o repositório `vtm-v5-solo` (e `vtm-campanhas` só para leitura, como exemplo real).

---

```
Sessão de desenvolvimento do plugin vtm (repositório vtm-v5-solo). Não é sessão de jogo: não narre.

Contexto: depois de cerca de 12 sessões de jogo seguidas, o narrador mostrou falhas de conduta e de comunicação.
Ele decidia pelo jogador, era prolixo, largava o seletor de opções, misturava português de Portugal, usava jargão
sem explicar, dava pouca didática nas opções e perdia as premissas depois da compactação. Também errava a Fome nas
rolagens e inventava regras. Faltava planejamento visível dos arcos (partida, história, aventura, cena) e as
aventuras se esticavam, sem ritmo.

Leia primeiro:
1. docs/DIAGNOSTICO-NARRADOR.md: problemas (D1-D5, C1-C9, P1-P5) e correções (F1-F7).
2. skills/narrar/SKILL.md, skills/gerenciar/SKILL.md, skills/criar/SKILL.md.
3. 09_Preferencias/01_Preferencias_de_Jogo.md e 02_Regras_da_Casa.md.
4. scripts/vtm_mcp.py, scripts/vtm_motor.py, scripts/campanha.py, scripts/vtm_campanha.py, hooks/hooks.json, tests/.
5. Como exemplo real (só leitura, não altere): vtm-campanhas/Edward Bello/CONSOLIDACAO.md, sessao_26.md e rolagens.jsonl.

Objetivo, nesta ordem (pare ao fim de cada etapa, mostre o diff resumido e espere meu ok):
1. F2 + F3: contrato de resposta do narrador e regras de língua. Reescreva o topo de skills/narrar/SKILL.md como
   um contrato curto e numerado, com 3 pares de exemplo bom/ruim. Ajuste Preferências §9 e §10. A skill fica mais
   curta, não mais longa.
2. F1: MCP com estado (ler e gravar estado.json, recusar Fome divergente, ferramentas parada e chance, montagem com
   alimentações intercaladas). Com testes em tests/.
3. F4: hook SessionStart para compact/resume que reinjeta o contrato, o estado e a decisão pendente (mesa.json).
4. F6: arcos.md público por campanha, abertura de sessão em 3 linhas, orçamento de aventura de 1-3 sessões,
   objetivos.md enxuto, direcao.md em tópicos fixos. Templates em 08_Templates/ e regras nas skills gerenciar e criar.
5. F5 + F7: registro de "decisão do narrador" com aprovação no fim da sessão; auditoria de conduta (Fome divergente
   em rolagens.jsonl, português de Portugal nos logs); casos de avaliação da skill narrar.

Restrições:
- Nunca gravar conteúdo de campanha no vtm-v5-solo (o repositório é público). Exemplos sempre genéricos.
- PT-BR em tudo. Mensagens para mim curtas e objetivas, com prós e contras quando houver escolha.
- Rodar python -m pytest tests antes de cada commit. Commit e push na branch indicada pela sessão. Sem PR, a menos que eu peça.
- Quando a etapa mudar comportamento, mostrar uma resposta de narrador antes/depois para um mesmo caso.
```
