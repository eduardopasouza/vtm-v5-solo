---
description: "vtm criar, criar jogo, novo jogo, nova partida, nova história, nova aventura, sessão zero, criar campanha, novo cenário, vampiro criação rpg"
model: opus
---

# VtM Criar — Arquitetar Jogos e Narrativas

Skill de criação para campanhas solo de Vampire: The Masquerade V5 em Português BR.
**ZERO relação com IAra.**

## Responsabilidade

Criar e estruturar todos os níveis narrativos: Jogo, Partida, História, Aventura. Montar cenários, definir arcos, estabelecer objetivos e preparar a documentação completa.

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `./` |
| Settings do jogador | `[Base]/.claude/vtm.local.md` (opcional; template em `vtm.local.md.example`) |
| Jogos | `[Base]/07_Jogos/` (ou `pasta_jogos` do `.local.md`) |
| Resumos | `[Base]/12_Resumos_dos_Livros/` |
| PDFs integrais | `pasta_acervo` do `.local.md` (opcional). Se vazio ou pasta não existir, usar só resumos. |
| Templates | `[Base]/08_Templates/` |
| Preferências | `[Base]/09_Preferencias/01_Preferencias_de_Jogo.md` |

Ler `.claude/vtm.local.md` antes de criar jogo novo.

## Hierarquia Narrativa

| Nível | Definição | Duração |
|-------|-----------|---------|
| **Jogo** | Vida inteira do PC como vampiro. Do Abraço ao fim. | Indefinida |
| **Partida** | Arco narrativo marcante, ligado aos eixos centrais. | Semanas/meses (tempo real) |
| **História** | Quest principal ou secundária. Arco coeso. | Várias sessões |
| **Aventura** | Parte menor com começo, meio e fim. | 1-3 sessões |
| **Cena** | Unidade mínima. Local + momento + decisão. | Minutos a dezenas |

## Estrutura de Pastas

```
07_Jogos/[Nome do PC]/
├── contexto.md              # Estado atual global
├── personagem.md            # Ficha do PC
├── direcao.md               # Segredos do narrador (NUNCA mostrar)
├── timeline.md              # Linha do tempo cronológica
├── objetivos.md             # Tracker de objetivos (todos os níveis)
├── npcs/
│   ├── indice.md
│   ├── relacoes.md
│   └── [nome].md
├── cenario/
│   ├── cenario.md           # Hub central
│   ├── geografia.md
│   ├── historia.md
│   ├── sociedade.md
│   ├── politica.md
│   ├── economia.md
│   ├── cultura.md
│   ├── arquitetura.md
│   └── clima.md
└── partidas/
    └── [Nome da Partida]/
        ├── partida.md
        ├── ramificacoes.md
        └── [Nome da História]/
            ├── historia.md
            └── [Nome da Aventura]/
                ├── aventura.md
                └── sessao_XX_[titulo].md
```

## Fluxo: Criar Jogo Novo (Sessão Zero)

Construir colaborativamente com o jogador. Usar AskUserQuestion em cada etapa.

### Etapa 1 — Conceito

Perguntar ao jogador:
1. Nome do PC (será o nome da pasta do jogo)
2. Período e cidade (ex: Londres Vitoriana 1888, São Paulo contemporânea)
3. Tom desejado (horror pessoal, intriga política, ação, investigação, misto)
4. Clã do PC ou preferência narrativa

**CONSULTAR LIVROS:** Ler PDFs integrais relevantes ao cenário escolhido (ex: Victorian Age Vampire, Fall of London, core rulebook capítulo de clãs). Não apenas resumos.

### Etapa 2 — Cenário

Pesquisar dados reais da cidade/período via web search. Popular os 9 arquivos de `cenario/`:

| Arquivo | Conteúdo |
|---------|---------|
| `cenario.md` | Hub central: nome, período, tom, resumo, links internos |
| `geografia.md` | Mapa, bairros, pontos-chave, territórios vampíricos |
| `historia.md` | Contexto histórico real + elementos sobrenaturais |
| `sociedade.md` | Mortais: classes, instituições, tensões sociais |
| `politica.md` | Política vampírica: Príncipe, Primogenitura, Barões, Autarcas |
| `economia.md` | Recursos, influências, moeda de troca entre vampiros |
| `cultura.md` | Arte, religião, entretenimento, costumes da época |
| `arquitetura.md` | Edificações, refúgios, locais de caça, Elísios |
| `clima.md` | Noites, estações, condições que afetam vampiros |

### Etapa 3 — Sociedade Vampírica Local

Definir estrutura de poder:
- Príncipe e corte
- Primogênitos por clã presente
- Barões Anarquistas (se houver)
- Autarcas relevantes
- Facções e alianças

Criar fichas mínimas dos NPCs principais em `npcs/` (usar trigger "criar NPC" para profundidade).

### Etapa 4 — Personagem

Delegar criação ao jogador via skill `vtm-personagem` (trigger: "criar personagem").
Garantir que o personagem se integra ao cenário criado.

### Etapa 5 — Primeira Partida

Definir:
- Nome da partida (arco principal)
- Eixos narrativos centrais (ex: luta pelo poder, busca pela Golconda, vingança)
- Objetivos iniciais (nível jogo + nível partida)
- Primeira história e primeira aventura
- Gancho para a primeira cena

Criar pasta `partidas/[Nome]/` com `partida.md` e `ramificacoes.md`.

### Etapa 6 — Documentação Inicial

Criar todos os arquivos base:
- `contexto.md` — estado inicial
- `timeline.md` — marco zero (Abraço ou início da história)
- `objetivos.md` — objetivos iniciais por nível
- `direcao.md` — segredos, planos do narrador, revelações futuras
- `npcs/indice.md` — lista de NPCs criados
- `npcs/relacoes.md` — mapa inicial de relações

## Fluxo: Criar Partida

1. Ler `contexto.md` e `objetivos.md` do jogo — entender estado atual
2. **CONSULTAR LIVROS** relevantes ao tema da nova partida
3. Perguntar ao jogador: tema, tom, antagonista principal, motivação do PC
4. Definir arco narrativo com 3 atos (setup, confronto, resolução)
5. Definir objetivos da partida (principais + secundários)
6. Criar pasta `partidas/[Nome]/` com:
   - `partida.md` — resumo, arco, objetivos, NPCs-chave, tom
   - `ramificacoes.md` — vazio (será preenchido durante o jogo)
7. Atualizar `objetivos.md` com novos objetivos
8. Criar primeira história da partida

## Fluxo: Criar História

1. Ler `partida.md` — entender arco e objetivos
2. Definir quest: tipo (principal ligada ao eixo, ou secundária), objetivo, stakes
3. Criar pasta `[Nome da História]/` dentro da partida
4. Criar `historia.md` — resumo, objetivos, pistas, NPCs envolvidos, status
5. Criar primeira aventura da história

## Fluxo: Criar Aventura

1. Ler `historia.md` — entender quest e objetivos
2. Definir aventura: objetivo específico, cenas planejadas (3-5), resolução
3. Criar pasta `[Nome da Aventura]/` dentro da história
4. Criar `aventura.md`:
   - Resumo e objetivo
   - Cenas planejadas (local, propósito, testes prováveis, NPCs)
   - Condições de sucesso/falha
   - Status (ativa/concluída)
5. Atualizar `objetivos.md` com objetivos da aventura

## Formato de Opções

Seguir o formato obrigatório das preferências:

```
[Descrição da situação/proposta]

**Opção A — [título]:** [detalhes com prós, contras, implicações]
**Opção B — [título]:** [detalhes com prós, contras, implicações]
**Opção C — [título]:** [detalhes com prós, contras, implicações]

→ Widget com labels sucintos (≤7 palavras). Prós/contras NO TEXTO, nunca no widget.
```

## Regras Universais

1. **Autoridade do jogador (warn + obey):** alertar consequências, se confirmar → obedecer.
2. **Anti-alucinação:** cenários conforme livros oficiais. Não inventar lore.
3. **Consulta a livros integrais:** OBRIGATÓRIA na criação de partidas e cenários. PDFs em `06_Livros_e_Suplementos/`.
4. **Fidelidade oficial:** máxima aderência ao cânone V5. Adaptações para solo documentadas.
5. **Checkpoint:** toda decisão estrutural (clã, cidade, período, arco) precisa aprovação do jogador.
6. **Documentação completa:** criar TODOS os arquivos da estrutura. Nada fica sem documento.
7. **ZERO relação com IAra.**
