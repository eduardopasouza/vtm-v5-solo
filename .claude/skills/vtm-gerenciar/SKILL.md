---
description: "vtm gerenciar, revisar campanha, entre sessões, planejar, objetivos, tracker, arco narrativo, gestão, agenda NPCs, vampiro gestão rpg"
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
| Base VtM | `./` |
| Jogos | `[Base]/07_Jogos/` |
| PDFs integrais | `[Base]/06_Livros_e_Suplementos/` |
| Resumos | `[Base]/12_Resumos_dos_Livros/` |

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

Verificar consistência entre todos os arquivos:
- Datas e eventos na `timeline.md` batem com sessões?
- Stats do PC em `personagem.md` estão corretos?
- NPCs no `indice.md` correspondem às fichas individuais?
- `relacoes.md` reflete interações recentes?
- `objetivos.md` está atualizado?
- `contexto.md` reflete o estado real?

Corrigir discrepâncias silenciosamente.

## Regras Universais

1. **Autoridade do jogador (warn + obey):** se pedir mudanças drásticas na campanha → alertar. Se confirmar → executar.
2. **Anti-alucinação:** NPCs off-screen agem conforme fichas. Eventos conforme lore.
3. **Transparência narrativa:** mostrar ao jogador o que o PC saberia. Ocultar segredos do narrador.
4. **Consulta a livros:** ao planejar arcos envolvendo lore oficial, consultar PDFs integrais.
5. **Documentação completa:** toda mudança registrada nos arquivos corretos.
6. **ZERO relação com IAra.**
