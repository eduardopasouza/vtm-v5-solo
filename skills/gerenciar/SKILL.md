---
description: "Gestão entre sessões de uma campanha solo de Vampiro: A Máscara V5 (VtM): revisar a crônica, objetivos do personagem vampiro, arcos narrativos, agenda dos NPCs da campanha. Usar só quando o pedido mencionar VtM, vampiro ou a campanha de RPG; não usar para planejamento, objetivos ou trackers de trabalho."
model: opus
---

# VtM Gerenciar — Gestão Macro da Campanha

Skill de gestão entre sessões para VtM V5 solo em Português BR.
**ZERO relação com IAra.**

## Responsabilidade

Gestão macro: rastrear objetivos em 4 níveis, avançar agendas de NPCs, manter arcos narrativos, revisar saúde da campanha, planejar próximos passos.

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `${CLAUDE_PLUGIN_ROOT}` (só leitura: referências, templates, scripts) |
| Jogos | `${user_config.pasta_campanhas}` |
| Campanha ativa | `${user_config.campanha_ativa}` |
| PDFs integrais | `${user_config.pasta_acervo}` (opcional) |
| Livros (busca) | Ferramenta MCP `buscar_acervo` ou agente `guardiao-regras`: índice local dos PDFs com livro + página. CLI: `python "${CLAUDE_PLUGIN_ROOT}/scripts/acervo.py" buscar "termo"`. Regra citada só com página; sem resultado, "não sei". Hierarquia P6: regras da casa > V5 Core > suplementos V5 > `01_Sistema`/resumos > edições antigas (só lore) |
| Resumos | `${user_config.pasta_resumos}` (opcional; visão geral, não fonte final) |

**Configuração não preenchida.** Se um valor acima aparecer vazio ou ainda como `${user_config...}` literal: Resumos = não usar (buscar no acervo); Jogos = perguntar ao jogador onde ficam as campanhas e sugerir configurar `pasta_campanhas` (`/plugin configure vtm@vtm-local`); **nunca gravar campanha dentro de `[Base]`**, que é o repositório público do plugin; Campanha ativa = perguntar se houver mais de uma; PDFs = usar só os resumos.

## Sistema de Objetivos — 4 Níveis

Rastreados em `objetivos.md` na raiz do jogo:

```markdown
# Objetivos Ativos — [Nome do PC]

## Nível: Jogo
### Principais
- [ ] [Objetivo de vida do PC — ex: descobrir quem ordenou seu Abraço]
### Secundários
- [ ] [Objetivo opcional — ex: alcançar posição na Primogenitura]

## Nível: Partida — [Nome da Partida Ativa]
### Principais
- [ ] [Objetivo do arco — ex: sobreviver à Queda do Príncipe]
### Secundários
- [x] [Objetivo concluído — ex: identificar o traidor] ✓ Sessão 04

## Nível: História — [Nome da História Ativa]
### Principais
- [ ] [Quest principal — ex: encontrar o refúgio do Methuselah]
### Secundários
- [ ] [Quest secundária — ex: recrutar aliado Nosferatu]

## Nível: Aventura — [Nome da Aventura Ativa]
### Principais
- [ ] [Objetivo específico — ex: infiltrar o Elísio do Príncipe]
### Secundários
- [ ] [Opcional — ex: roubar documento do cofre]

## Histórico de Conclusões
| Objetivo | Nível | Sessão | Como |
|----------|-------|--------|------|
| [X] | História | S03 | [resultado] |
```

### Regras de Objetivos
- **Principais:** obrigatórios para avançar no nível
- **Secundários:** opcionais, enriquecem a experiência
- Objetivos completados: marcar com ✓ e registrar sessão
- Novos objetivos podem surgir durante o jogo
- Atualizar ao final de CADA sessão

## Revisão Entre Sessões

Quando o jogador pedir "revisar campanha" ou "entre sessões":

### 1. Status Geral

Ler e apresentar:
- Estado do PC: Fome, FdV, Saúde, Humanidade, XP
- Localização e situação atual
- Objetivos ativos por nível
- Ameaças pendentes

### 2. Avanço de Agendas de NPCs

Para cada NPC Maior e Médio com agenda ativa:
- O que o NPC fez "off-screen" desde a última sessão?
- Como suas ações afetam o cenário?
- Mudanças de atitude baseadas em eventos?

Regras:
- NPCs agem conforme motivações documentadas
- Ações off-screen devem ser plausíveis e proporcionais
- Registrar mudanças nas fichas de NPCs
- Apresentar ao jogador como rumores, notícias, ou consequências visíveis

### 3. Passagem de Tempo

Se tempo passou entre sessões (no jogo):
- Rouse Check de despertar para cada noite
- Alimentação rotineira (pode usar teste simplificado)
- Eventos do cenário (consultar `direcao.md`)
- Atualizar `timeline.md`

### 4. Manutenção Narrativa

Verificar:
- Arcos pendentes sem resolução
- Pistas esquecidas que precisam ser retomadas
- NPCs "abandonados" que deveriam reagir
- Consequências de decisões passadas que devem se manifestar
- Ramificações em `ramificacoes.md` que precisam de follow-up

### 5. Planejamento

Propor ao jogador:
- Próxima cena/aventura lógica baseada no estado atual
- Oportunidades narrativas baseadas nas ramificações
- Ganchos para novas histórias ou quests secundárias

Apresentar com prós/contras em texto, labels curtos no widget.

## Saúde da Campanha

Checklist de saúde narrativa:

| Item | Verificação |
|------|------------|
| Ritmo | A narrativa está avançando? Há estagnação? |
| Variedade | Alternando intriga, ação, horror, investigação? |
| Stakes | As decisões têm peso? As consequências são sentidas? |
| NPCs | Estão vivos? Têm agendas próprias? Reagem ao PC? |
| Objetivos | O jogador sabe o que perseguir? Há direção clara? |
| Mundo | O cenário reage? Eventos externos ocorrem? |
| Personagem | O PC está evoluindo? Humanidade em tensão? |
| Documentação | Tudo registrado? Sem contradições? |

Se algum item está fraco → propor ações corretivas.

## Manutenção de Documentação

1. **Auditoria mecânica** (só leitura):
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/campanha.py" auditar "<pasta da campanha>"
   ```
   (ou a ferramenta MCP `auditar_campanha`). Aponta: `estado.json` ausente ou inválido; número divergente entre `estado.json` e os `.md` (ou entre `contexto.md` e `personagem.md` sem estado); número repetido nos `.md` (pela P8 fica só no `estado.json`); Potência declarada x tabela do Core p. 216; sessões fora da `timeline.md`; rodapés "atualizado em" defasados; NPCs nas relações sem ficha; fichas fora do `indice.md`.
2. **Continuidade narrativa:** pedir ao agente `continuidade` as contradições entre sessões, fichas, linha do tempo e `direcao.md`.
3. Conferir também:
   - `relacoes.md` reflete interações recentes?
   - `objetivos.md` está atualizado?

Corrigir as discrepâncias e rodar a auditoria de novo até voltar sem erros. Números do personagem vão para o `estado.json`, não para os `.md`.

## Regras Universais

1. **Autoridade do jogador (warn + obey):** se pedir mudanças drásticas na campanha → alertar. Se confirmar → executar.
2. **Anti-alucinação:** NPCs off-screen agem conforme fichas. Eventos conforme lore.
3. **Transparência narrativa:** mostrar ao jogador o que o PC saberia. Ocultar segredos do narrador.
4. **Consulta a livros:** ao planejar arcos envolvendo lore oficial, consultar PDFs integrais.
5. **Documentação completa:** toda mudança registrada nos arquivos corretos.
6. **ZERO relação com IAra.**
