---
description: "Cria a estrutura narrativa de uma campanha solo de Vampiro: A Máscara V5 (VtM): novo jogo, partida, história ou aventura de VtM, sessão zero de vampiro, cenário da crônica. Usar só quando o pedido mencionar VtM, vampiro ou a campanha de RPG; não usar para criar projetos, documentos ou casos fora do jogo."
model: opus
---

# VtM Criar — Arquitetar Jogos e Narrativas

Skill de criação para campanhas solo de Vampire: The Masquerade V5 em Português BR.

## Responsabilidade

Criar e estruturar todos os níveis narrativos: Jogo, Partida, História, Aventura. Montar cenários, definir arcos, estabelecer objetivos e preparar a documentação completa.

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `${CLAUDE_PLUGIN_ROOT}` (só leitura: referências, templates, scripts) |
| Jogos | `${user_config.pasta_campanhas}` |
| Resumos | `${user_config.pasta_resumos}` (opcional; visão geral, não fonte final) |
| PDFs integrais | `${user_config.pasta_acervo}` (opcional) |
| Livros (busca) | Ferramenta MCP `buscar_acervo` ou agente `guardiao-regras`: índice local dos PDFs com livro + página. CLI: `python "${CLAUDE_PLUGIN_ROOT}/scripts/acervo.py" buscar "termo"`. Regra citada só com página. Sem acervo indexado, valem os arquivos `01_Sistema/` do plugin (ver "Configuração não preenchida"); sem fonte nenhuma, "não sei". Hierarquia P6: regras da casa > V5 Core > suplementos V5 > `01_Sistema`/resumos > edições antigas (só lore) |
| Templates | `[Base]/08_Templates/` |
| Preferências | `[Jogos]/preferencias.md` se existir (preferências deste jogador); senão `[Base]/09_Preferencias/01_Preferencias_de_Jogo.md` (padrão do plugin) |

**Configuração não preenchida.** Se um valor acima aparecer vazio ou ainda como `${user_config...}` literal: Resumos = não usar; Jogos = perguntar ao jogador onde ficam as campanhas e sugerir configurar `pasta_campanhas` (comando `/plugin`, plugin `vtm`, configurar opções); **nunca gravar campanha dentro de `[Base]`**, que é a pasta de instalação do plugin e é substituída a cada atualização; PDFs e acervo = opcionais; sem eles (ou se `buscar_acervo` disser que não há índice), a fonte de regra são os arquivos `[Base]/01_Sistema/`, `[Base]/03_Disciplinas/` (poderes, Rituais e Cerimônias) e `[Base]/10_Ferramentas_do_Narrador/`, conferidos com o V5 Core e os suplementos V5 e com a página ao lado, mais o motor de dados. Em `[Base]/02_Clas/`, `[Base]/04_Seitas_e_Politica/` e `[Base]/05_Cenario/`, cada arquivo termina com a seção "Conferência do Lore", que diz ponto a ponto o que é **V5** (com página), o que é **Antigo** (edições anteriores), o que é **Sem fonte** (texto de fã) e o que é **História real**. Tratar como fato do jogo só o que está marcado V5; o resto serve de ambientação, com aviso ao jogador quando uma decisão depender dele. O que não estiver lá: dizer "não sei" ou propor ao jogador como regra da casa, sem inventar. O jogo novo é criado dentro da pasta de Jogos.

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
[Jogos]/[Nome do PC]/
├── estado.json              # Números da campanha (P8) — copiar de [Base]/08_Templates/07_estado.json
├── contexto.md              # Situação atual global (sem números)
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
                └── sessao_NN.md         # dois dígitos: sessao_01.md
```

## Fluxo: Criar Jogo Novo (Sessão Zero)

Construir colaborativamente com o jogador. Usar AskUserQuestion em cada etapa.

### Etapa 1 — Conceito

Perguntar ao jogador:
1. Nome do PC (será o nome da pasta do jogo)
2. Período e cidade (ex: Londres Vitoriana 1888, São Paulo contemporânea)
3. Tom desejado (horror pessoal, intriga política, ação, investigação, misto)
4. Clã do PC ou preferência narrativa

**CONSULTAR LIVROS:** se houver acervo indexado, buscar nele os livros do cenário escolhido (ex: Victorian Age Vampire, Fall of London, capítulo de clãs do Core). Sem acervo, usar `[Base]/02_Clas/` a `[Base]/05_Cenario/` e dizer ao jogador o que ficou sem fonte.

### Etapa 2 — Cenário

Pesquisar dados reais da cidade/período (busca na web, se disponível). Popular os 9 arquivos de `cenario/`:

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

Delegar criação ao jogador via skill `/vtm:personagem` (trigger: "criar personagem de VtM").
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
- `estado.json` — números iniciais, a partir de `[Base]/08_Templates/07_estado.json` (conferir com `python "${CLAUDE_PLUGIN_ROOT}/scripts/campanha.py" validar "<pasta do jogo>"`)
- `contexto.md` — situação inicial (sem números)
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

Seguir o formato das preferências (tabela Caminhos):

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
3. **Consulta a livros:** na criação de partidas e cenários, buscar no acervo indexado quando existir (`buscar_acervo`); sem acervo, usar as referências do plugin e marcar o que ficou sem fonte.
4. **Fidelidade oficial:** máxima aderência ao cânone V5. Adaptações para solo documentadas.
5. **Checkpoint:** toda decisão estrutural (clã, cidade, período, arco) precisa aprovação do jogador.
6. **Documentação completa:** criar TODOS os arquivos da estrutura. Nada fica sem documento.
