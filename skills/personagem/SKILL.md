---
description: "Cria e evolui o personagem jogador de Vampiro: A Máscara V5 (VtM): ficha do vampiro, clã, atributos, habilidades, disciplinas, vantagens e defeitos, gastar XP. Usar só quando o pedido mencionar VtM, vampiro ou a campanha de RPG; 'ficha' ou 'personagem' sozinhos não bastam."
model: opus
---

# VtM Personagem — Criação e Evolução do PC

Skill de criação e evolução de personagens para VtM V5 solo em Português BR.

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `${CLAUDE_PLUGIN_ROOT}` (só leitura: referências, templates, scripts) |
| Jogos | `${user_config.pasta_campanhas}` |
| Campanha ativa | `${user_config.campanha_ativa}` (o jogo que o jogador nomear vale por cima; vazio e várias campanhas = perguntar qual e passar o nome em `campanha` nas ferramentas de dados) |
| Resumos | `${user_config.pasta_resumos}` (opcional; visão geral, não fonte final) |
| PDFs integrais | `${user_config.pasta_acervo}` (opcional) |
| Livros (busca) | Ferramenta MCP `buscar_acervo` ou agente `guardiao-regras`: índice local dos PDFs com livro + página. CLI: `python "${CLAUDE_PLUGIN_ROOT}/scripts/acervo.py" buscar "termo"`. Regra citada só com página. Sem acervo indexado, valem os arquivos `01_Sistema/` do plugin (ver "Configuração não preenchida"); sem fonte nenhuma, "não sei". Hierarquia P6: regras da casa > V5 Core > suplementos V5 > `01_Sistema`/resumos > edições antigas (só lore) |
| Referências V5 | `[Base]/01_Sistema/` |

**Configuração não preenchida.** Se um valor acima aparecer vazio ou ainda como `${user_config...}` literal: Resumos = não usar; Jogos = perguntar ao jogador onde ficam as campanhas e sugerir configurar `pasta_campanhas` (comando `/plugin`, plugin `vtm`, configurar opções); **nunca gravar campanha dentro de `[Base]`**, que é a pasta de instalação do plugin e é substituída a cada atualização; Campanha ativa = perguntar se houver mais de uma; PDFs e acervo = opcionais; sem eles (ou se `buscar_acervo` disser que não há índice), a fonte de regra são os arquivos `[Base]/01_Sistema/`, `[Base]/03_Disciplinas/` (poderes, Rituais e Cerimônias) e `[Base]/10_Ferramentas_do_Narrador/`, conferidos com o V5 Core e os suplementos V5 e com a página ao lado, mais o motor de dados. Em `[Base]/02_Clas/`, `[Base]/04_Seitas_e_Politica/` e `[Base]/05_Cenario/`, cada arquivo termina com a seção "Conferência do Lore", que diz ponto a ponto o que é **V5** (com página), o que é **Antigo** (edições anteriores), o que é **Sem fonte** (texto de fã) e o que é **História real**. Tratar como fato do jogo só o que está marcado V5; o resto serve de ambientação, com aviso ao jogador quando uma decisão depender dele. O que não estiver lá: dizer "não sei" ou propor ao jogador como regra da casa, sem inventar.

## Criação de Personagem — Fluxo V5

Construir colaborativamente com o jogador. Usar AskUserQuestion em cada etapa.

**Fonte das regras de criação:** `[Base]/01_Sistema/02_Criacao_de_Personagem.md` (conferido com o V5 Core, cita a página). Os números abaixo são só um lembrete; em caso de diferença, vale o arquivo. Se houver acervo indexado, conferir no Core (`buscar_acervo`, p. 136-151). Regras da casa do jogador valem por cima.

### Etapa 1 — Conceito

Perguntar ao jogador:
- Conceito em uma frase (ex: "Detetive Nosferatu obcecado com a verdade")
- Ambição (objetivo de longo prazo)
- Desejo (objetivo de curto prazo)
- Clã (ou deixar aberto para o narrador sugerir)

Consultar `01_Sistema/02_Criacao_de_Personagem.md` (passo 2) para a tabela resumo de clãs, Perdição e Disciplinas; `02_Clas/<cla>.md` para a ficha completa de cada clã.

### Etapa 2 — Atributos

Sem prioridade por categoria. Os 9 Atributos recebem: **um 4, três 3, quatro 2 e um 1** (Core p. 136; passo 3 do arquivo).

| Físicos | Sociais | Mentais |
|---------|---------|---------|
| Força | Carisma | Inteligência |
| Destreza | Manipulação | Raciocínio |
| Vigor | Compostura | Determinação |

Apresentar opções com prós/contras em texto. Widget com labels curtos.

### Etapa 3 — Habilidades

O jogador escolhe **uma** das três distribuições (Core p. 136; passo 4 do arquivo):
- **Valete:** uma Habilidade em 3, oito em 2, dez em 1
- **Equilibrado:** três em 3, cinco em 2, sete em 1
- **Especialista:** uma em 4, três em 3, três em 2, três em 1

Especialidades gratuitas: uma em cada uma de Acadêmicos, Ofício, Atuação e Ciência (se tiver ponto nelas), mais uma livre, mais a do Tipo de Predador.

### Etapa 4 — Tipo de Predador

Consultar `01_Sistema/07_Tipos_de_Predador.md` (e o passo 5 de `02_Criacao_de_Personagem.md`):
- Define como o vampiro caça
- Dá uma especialidade, 1 ponto em uma das Disciplinas listadas e as Vantagens/Defeitos do tipo; alguns alteram a Humanidade. Nunca dá pontos de Habilidade
- Conferir as restrições por clã e Potência de Sangue

### Etapa 5 — Disciplinas

Duas Disciplinas do clã: **2 pontos em uma e 1 ponto na outra** (Core p. 136; passo 6 do arquivo), mais o ponto do Tipo de Predador. Caitiff e Sangue Ralo têm regras próprias (ver o arquivo). Poderes de cada nível: `03_Disciplinas/<disciplina>.md`.

### Etapa 6 — Geração e Potência de Sangue

Definir com o jogador a idade do vampiro (cria, neonato ou ancilla). A Geração, a Potência de Sangue inicial e os ajustes (XP inicial, Vantagens, Humanidade) saem do passo 7 do arquivo e de `01_Sistema/08_Potencia_de_Sangue.md`.

### Etapa 7 — Vantagens, Defeitos e Derivados

- **7 pontos** em Vantagens e **2 pontos** obrigatórios em Defeitos (passo 8 do arquivo), além dos que vêm do Tipo de Predador
- Loresheets opcionais (`01_Sistema/10_Loresheets.md`)
- Convicções (1-3) e uma Âncora (Touchstone) por Convicção (passo 9)
- **Saúde** = Vigor + 3
- **Força de Vontade** = Compostura + Determinação
- **Humanidade** = 7, ajustada pelo Tipo de Predador e pela idade
- **Fome** inicial = 1

### Etapa 8 — História e Conexões

Definir com o jogador:
- História mortal (quem era antes do Abraço)
- Circunstâncias do Abraço
- Senhor (quem o abraçou) — criar ficha NPC básica
- Convicções (1-3 crenças que guiam a Humanidade)
- Touchstones (humanos ligados às Convicções)
- Relações iniciais com NPCs do cenário

### Etapa 9 — Documentação

Criar `[Jogos]/[PC]/estado.json` a partir de `[Base]/08_Templates/07_estado.json` com os números iniciais (Fome, Potência de Sangue, Humanidade, máximos de Saúde e Força de Vontade, XP) e salvar a ficha em `[Jogos]/[PC]/personagem.md` com o formato:

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
- **Saúde máxima:** Vigor + 3
- **Força de Vontade máxima:** Compostura + Determinação
- Os valores atuais (Fome, dano, Humanidade, Manchas, Potência de Sangue, XP) ficam só em `estado.json`

## XP gasto
| Sessão | Melhoria | Custo |
|--------|----------|-------|

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

**Fonte dos custos:** `[Base]/01_Sistema/06_Experiencia_e_Avanco.md` (§3 e tabela resumo do §5). O ganho de XP por sessão segue as regras da casa em vigor (ver a skill de narração). Lembrete dos custos mais comuns:

| Melhoria | Custo XP |
|----------|----------|
| Atributo | Novo nível × 5 |
| Habilidade | Novo nível × 3 |
| Nova Especialidade | 3 |
| Disciplina do clã | Novo nível × 5 |
| Disciplina fora do clã | Novo nível × 7 |
| Disciplina (Caitiff) | Novo nível × 6 |
| Ritual ou Fórmula | Nível × 3 |
| Potência de Sangue | Novo nível × 10 |
| Vantagem | 3 por ponto |

Fluxo de evolução:
1. Jogador indica o que quer melhorar
2. Verificar o XP disponível em `estado.json` (`personagem.xp.disponivel`); em campanha sem `estado.json`, na ficha
3. Conferir os requisitos (ex.: Ressonância e sangue para Disciplinas, teto de Potência por Geração)
4. Mostrar custo e consequências (em texto, label curto no widget)
5. Se aprovado → atualizar a ficha em `personagem.md` e descontar o XP em `estado.json`
6. Recalcular paradas comuns afetadas
7. Registrar o gasto (o quê, custo, sessão) na seção de XP de `personagem.md`

## Regras Universais

1. **Autoridade do jogador (warn + obey):** se pedir XP grátis, stats impossíveis, etc. → alertar UMA VEZ. Se confirmar → obedecer.
2. **Fidelidade V5:** seguir as regras oficiais de criação e evolução (arquivos de `01_Sistema/`; acervo, se houver).
3. **Anti-alucinação:** stats conforme livros. Disciplinas conforme clã oficial.
4. **Documentação imediata:** toda mudança na ficha → atualizar `personagem.md` na hora; números de estado → `estado.json`.
