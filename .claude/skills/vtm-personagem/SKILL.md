---
description: "vtm personagem, criar personagem, ficha, evoluir, gastar XP, atributos, habilidades, disciplinas, vantagens, defeitos, clã, vampiro ficha rpg"
model: opus
---

# VtM Personagem — Criação e Evolução do PC

Skill de criação e evolução de personagens para VtM V5 solo em Português BR.
**ZERO relação com IAra.**

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `./` |
| Jogos | `[Base]/07_Jogos/` |
| Resumos | `[Base]/12_Resumos_dos_Livros/` |
| PDFs integrais | `[Base]/06_Livros_e_Suplementos/` |
| Referências V5 | `[Base]/01_Sistema/` |

## Criação de Personagem — Fluxo V5

Construir colaborativamente com o jogador. Usar AskUserQuestion em cada etapa.
**CONSULTAR PDFs INTEGRAIS** do Core Rulebook (e suplementos relevantes) durante a criação.

### Etapa 1 — Conceito

Perguntar ao jogador:
- Conceito em uma frase (ex: "Detetive Nosferatu obcecado com a verdade")
- Ambição (objetivo de longo prazo)
- Desejo (objetivo de curto prazo)
- Clã (ou deixar aberto para o narrador sugerir)

Consultar `01_Sistema/02_Clas.md` e PDFs dos clãs para detalhes oficiais.

### Etapa 2 — Atributos (7/5/3)

Distribuir pontos em 3 categorias (Físicos, Sociais, Mentais):
- Categoria primária: 4 pontos (um atributo a 4, resto a 3, ou distribuir)
- Categoria secundária: 3 pontos
- Categoria terciária: 2 pontos
- Base: todos começam em 1

| Físicos | Sociais | Mentais |
|---------|---------|---------|
| Força | Carisma | Inteligência |
| Destreza | Manipulação | Raciocínio |
| Vigor | Compostura | Determinação |

Apresentar opções com prós/contras em texto. Widget com labels curtos.

### Etapa 3 — Habilidades (11/7/4)

Distribuir pontos em 3 categorias:
- Categoria primária: 11 pontos (nenhum acima de 4 na criação)
- Categoria secundária: 7 pontos
- Categoria terciária: 4 pontos

Consultar `01_Sistema/03_Habilidades.md` para lista completa e especialidades.

### Etapa 4 — Disciplinas

Conforme o clã (consultar `01_Sistema/04_Disciplinas.md`):
- 2 pontos em Disciplinas do clã
- Distribuir: 2 em uma ou 1+1

Consultar PDF integral para poderes específicos de cada nível.

### Etapa 5 — Vantagens e Defeitos

Consultar `01_Sistema/05_Vantagens_e_Defeitos.md`:
- 7 pontos em Vantagens
- Até 2 pontos em Defeitos (cada Defeito dá +1 ponto para Vantagens)
- Incluir Touchstone (humano que ancora a Humanidade)
- Loresheets opcionais (consultar `01_Sistema/10_Loresheets.md`)

### Etapa 6 — Tipo de Predador

Consultar `01_Sistema/07_Tipos_de_Predador.md`:
- Define como o vampiro caça
- Bônus mecânicos específicos (+1 Disciplina, +1 Especialidade, etc.)

### Etapa 7 — Derivados

Calcular automaticamente:
- **Saúde** = Vigor + 3
- **Força de Vontade** = Compostura + Determinação
- **Humanidade** = 7 (padrão)
- **Fome** = 1 (início)
- **Potência de Sangue** = 1 (neonato) — consultar `01_Sistema/08_Potencia_de_Sangue.md`

### Etapa 8 — História e Conexões

Definir com o jogador:
- História mortal (quem era antes do Abraço)
- Circunstâncias do Abraço
- Senhor (quem o abraçou) — criar ficha NPC básica
- Convicções (1-3 crenças que guiam a Humanidade)
- Touchstones (humanos ligados às Convicções)
- Relações iniciais com NPCs do cenário

### Etapa 9 — Documentação

Salvar ficha completa em `07_Jogos/[PC]/personagem.md` com formato:

```markdown
# [Nome do PC]

## Conceito
- **Conceito:** [frase]
- **Clã:** [clã]
- **Geração:** [geração]
- **Senhor:** [nome]
- **Ambição:** [objetivo longo prazo]
- **Desejo:** [objetivo curto prazo]

## Atributos

| Físicos | • | Sociais | • | Mentais | • |
|---------|---|---------|---|---------|---|
| Força | X | Carisma | X | Inteligência | X |
| Destreza | X | Manipulação | X | Raciocínio | X |
| Vigor | X | Compostura | X | Determinação | X |

## Habilidades
[Lista com valores e especialidades]

## Disciplinas
[Disciplinas com nível e poderes]

## Vantagens e Defeitos
[Lista completa]

## Derivados
- **Saúde:** ○○○○○○ (Vigor+3)
- **Força de Vontade:** ○○○○○ (Compostura+Determinação)
- **Humanidade:** ○○○○○○○ (7)
- **Fome:** ● (1)
- **Potência de Sangue:** 1
- **XP Total:** 0 | **XP Disponível:** 0

## Tipo de Predador
[Tipo + bônus mecânicos]

## Convicções e Touchstones
[Convicções com Touchstones associados]

## História
[Resumo da vida mortal, Abraço, não-vida]

## Paradas Comuns
[Pré-calcular paradas frequentes para agilizar o jogo]
| Parada | Atrib + Hab | Total |
|--------|-------------|-------|
| Persuasão | Carisma + Persuasão | X |
| Percepção | Raciocínio + Percepção | X |
| Furtividade | Destreza + Furtividade | X |
| Combate (briga) | Força + Briga | X |
| ... | ... | ... |
```

## Evolução — Gastar XP

Consultar tabela de custos V5:

| Melhoria | Custo XP |
|----------|----------|
| Atributo | Novo nível × 5 |
| Habilidade (nova) | 3 |
| Habilidade (existente) | Novo nível × 3 |
| Nova Especialidade | 3 |
| Disciplina do clã | Novo nível × 5 |
| Disciplina fora do clã | Novo nível × 7 |
| Potência de Sangue | Novo nível × 10 |
| Vantagem | Novo nível × 3 |
| Humanidade (recuperar) | Novo nível × 2 |

Fluxo de evolução:
1. Jogador indica o que quer melhorar
2. Verificar XP disponível em `personagem.md`
3. Mostrar custo e consequências (em texto, label curto no widget)
4. Se aprovado → atualizar ficha
5. Recalcular paradas comuns afetadas
6. Registrar gasto em `personagem.md` (seção XP)

## Regras Universais

1. **Autoridade do jogador (warn + obey):** se pedir XP grátis, stats impossíveis, etc. → alertar UMA VEZ. Se confirmar → obedecer.
2. **Fidelidade V5:** seguir regras oficiais de criação e evolução. Consultar PDFs integrais.
3. **Anti-alucinação:** stats conforme livros. Disciplinas conforme clã oficial.
4. **Documentação imediata:** toda mudança na ficha → atualizar `personagem.md` na hora.
5. **ZERO relação com IAra.**
