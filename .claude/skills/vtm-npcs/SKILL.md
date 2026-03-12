---
description: "vtm npcs, criar NPC, novo NPC, editar NPC, atualizar NPCs, ficha NPC, relações, vampiro NPC rpg"
model: opus
---

# VtM NPCs — Criação e Gestão de NPCs

Skill de criação e manutenção de NPCs para VtM V5 solo em Português BR.
**ZERO relação com IAra.**

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `./` |
| Jogos | `[Base]/07_Jogos/` |
| PDFs integrais | `[Base]/06_Livros_e_Suplementos/` |
| Resumos | `[Base]/12_Resumos_dos_Livros/` |
| Referências | `[Base]/01_Sistema/` |

## Três Níveis de Profundidade

### Nível MAIOR — NPCs centrais

Antagonistas, aliados próximos, mentores, rivais. Ficha completa:

```markdown
# [Nome]

## Dados Básicos
- **Nome completo:** [nome]
- **Apelido/Título:** [se houver]
- **Clã:** [clã]
- **Geração:** [geração]
- **Seita:** Camarilla / Anarquista / Autarca / Sabbat
- **Posição:** [cargo na sociedade vampírica]
- **Idade aparente:** [idade]
- **Abraçado em:** [ano]

## Aparência
[2-3 frases: físico, vestimenta, maneirismos]

## Personalidade
- **Temperamento:** [traço dominante]
- **Virtude:** [ponto forte moral/social]
- **Vício:** [fraqueza ou obsessão]
- **Voz:** [como fala — formal, gírias, sotaque, padrão de discurso]

## Motivações
- **Ambição:** [objetivo de longo prazo]
- **Desejo:** [objetivo imediato]
- **Medo:** [o que teme perder/enfrentar]
- **Segredo:** [algo que esconde]

## Atributos-Chave
| Físicos | • | Sociais | • | Mentais | • |
|---------|---|---------|---|---------|---|
| Força | X | Carisma | X | Inteligência | X |
| Destreza | X | Manipulação | X | Raciocínio | X |
| Vigor | X | Compostura | X | Determinação | X |

## Disciplinas
[Disciplinas com nível e poderes principais]

## Paradas Comuns
| Parada | Cálculo | Total |
|--------|---------|-------|
| Combate | Força + Briga | X |
| Persuasão | Carisma + Persuasão | X |
| Intimidação | Carisma + Intimidação | X |
| [etc.] | | |

## Relação com o PC
- **Atitude atual:** [amigável/neutro/hostil/desconfiado]
- **Histórico:** [como se conheceram]
- **O que quer do PC:** [interesse]
- **O que o PC pode querer dele:** [utilidade]

## Notas do Narrador
[Planos secretos, informações que o jogador NÃO sabe, gatilhos de mudança de atitude]
```

### Nível MÉDIO — NPCs recorrentes

Contatos, informantes, aliados menores, NPCs de facção. Stats essenciais:

```markdown
# [Nome]

- **Conceito:** [uma frase]
- **Clã/Tipo:** [clã ou mortal]
- **Posição:** [papel social]
- **Aparência:** [1 frase]
- **Voz:** [como fala]
- **Motivação:** [o que quer]
- **Atitude com o PC:** [relação]
- **Paradas relevantes:** [2-3 paradas com valores]
- **Disciplinas:** [se vampiro: lista simples]
- **Nota do narrador:** [1-2 linhas]
```

### Nível MENOR — NPCs pontuais

Figurantes, vítimas, guardas, bartenders. Uma linha:

```markdown
- **[Nome]:** [conceito em 1 frase] | Atitude: [X] | Parada relevante: [X]
```

NPCs Menores ficam listados no `indice.md`, não em arquivos individuais.

## Fluxo: Criar NPC

1. Determinar nível de profundidade (Maior/Médio/Menor)
2. Se vampiro → **CONSULTAR PDF INTEGRAL** do clã para lore e disciplinas
3. Perguntar ao jogador: conceito, papel na história, relação com PC
4. Apresentar proposta com opções (prós/contras em texto, labels curtos no widget)
5. Gerar ficha conforme template do nível
6. Calcular paradas coerentes com o papel narrativo (stats realistas)
7. Salvar em `07_Jogos/[PC]/npcs/[nome].md`
8. Atualizar `npcs/indice.md` e `npcs/relacoes.md`

**Stats realistas:** NPC neófito não tem Disciplinas 5. Ancião não tem Atributos 1. Mortal não tem Disciplinas. Proporção de poder coerente com geração e idade.

## Gestão de NPCs

### Atualizar Atitudes

Quando uma interação muda a relação:
1. Atualizar campo "Atitude atual" na ficha
2. Registrar motivo da mudança
3. Atualizar `relacoes.md` se relação mudou significativamente

### Promover Nível

Se NPC Menor/Médio se torna importante:
1. Criar arquivo individual com nível expandido
2. Adicionar campos faltantes (motivações, paradas, etc.)
3. Atualizar `indice.md`

### Mapa de Relações (`relacoes.md`)

Manter atualizado com:
- Relações entre NPCs (alianças, rivalidades, dívidas)
- Relações de cada NPC com o PC
- Facções e lealdades
- Mudanças recentes

Formato:
```markdown
# Mapa de Relações

## PC → NPCs
- [NPC]: [atitude] — [razão]

## Entre NPCs
- [NPC A] ↔ [NPC B]: [tipo de relação]

## Facções
- Camarilla: [membros]
- Anarquistas: [membros]
- Autarcas: [membros]
```

### Índice de NPCs (`indice.md`)

Lista resumida de TODOS os NPCs com:
```markdown
| Nome | Clã | Nível | Posição | Atitude com PC | Arquivo |
|------|-----|-------|---------|----------------|---------|
| [X]  | [X] | Maior | [X]     | [X]            | [X].md  |
```

## Regras Universais

1. **Anti-alucinação:** NPCs agem APENAS conforme motivações e stats documentados. Nenhum NPC age "fora de personagem" sem justificativa.
2. **Consistência:** verificar ficha ANTES de narrar ações de qualquer NPC.
3. **Checkpoint:** novo NPC relevante precisa aprovação do jogador antes de ser canônico.
4. **Consulta a livros:** ao criar NPCs de clãs específicos, consultar PDFs integrais para lore e disciplinas corretas.
5. **Documentação imediata:** toda mudança → atualizar ficha e índice.
6. **Autoridade do jogador (warn + obey):** se pedir NPC impossível → alertar UMA VEZ. Se confirmar → obedecer.
7. **ZERO relação com IAra.**
