# Convenções de Nomenclatura — VtM V5

<!-- Referência canônica para nomear arquivos e pastas de forma consistente -->
<!-- Decisão D2 — 2026-10-31: híbrido legalizado -->

---

## Regra Geral: híbrido

| Tipo | Convenção | Permite |
|------|-----------|---------|
| **Pastas narrativas** (Jogo, Partida, História, Aventura) | Legível | Espaços, acentos, maiúsculas em cada palavra |
| **Arquivos técnicos** (`.md` de documentação) | snake_case | Minúsculas, underline, sem acentos |

A razão: pastas narrativas aparecem em caminhos lidos por humanos ("A Queda do Príncipe" é parte do nome do arco, não só do caminho). Arquivos técnicos entram em comandos, scripts e grep — simples e previsíveis.

---

## Pastas Narrativas (legíveis)

### Jogo

```
[Campanhas]/[Nome do PC]/
```

Nome legível do PC. Exemplos:
- `[Campanhas]/Helena Prado/`
- `[Campanhas]/Marcus Wells/`
- `[Campanhas]/Dona Rita de Cássia/`

### Partida

```
[Campanhas]/[Nome do PC]/partidas/[Nome da Partida]/
```

Exemplos:
- `A Queda do Príncipe`
- `Noites de São Luís`
- `A Grande Jyhad de 1888`

### História

```
.../partidas/[Nome da Partida]/[Nome da História]/
```

Exemplos:
- `Os Corpos do Cais`
- `A Dívida de Sangue`
- `O Retorno do Ancião`

### Aventura

```
.../[Nome da História]/[Nome da Aventura]/
```

Exemplos:
- `O Armazém do Cais`
- `O Julgamento do Xerife`
- `A Visita do Arconte`

---

## Arquivos Técnicos (snake_case)

### Arquivos de Jogo (fixos)

| Arquivo | Pasta | Propósito |
|---------|-------|-----------|
| `contexto.md` | `[Campanhas]/[Nome do PC]/` | Estado atual global |
| `personagem.md` | `[Campanhas]/[Nome do PC]/` | Ficha do PC |
| `direcao.md` | `[Campanhas]/[Nome do PC]/` | Segredos do narrador (NUNCA mostrar) |
| `timeline.md` | `[Campanhas]/[Nome do PC]/` | Cronologia |
| `objetivos.md` | `[Campanhas]/[Nome do PC]/` | Tracker 4 níveis |
| `partida.md` | `.../partidas/[Nome]/` | Resumo da partida |
| `ramificacoes.md` | `.../partidas/[Nome]/` | Consequências de longo prazo |
| `historia.md` | `.../[Nome da História]/` | Arco da história |
| `aventura.md` | `.../[Nome da Aventura]/` | Resumo da aventura |

### Logs de Sessão

```
sessao_NN.md
```

- Numeração sempre com **dois dígitos**: `sessao_01.md`, `sessao_15.md`, `sessao_99.md`
- Para campanhas longas (>99 sessões), passar a 3 dígitos: `sessao_100.md` em diante
- Fica dentro da pasta da **Aventura** que contém a sessão

### Fichas de NPC

```
[Campanhas]/[Nome do PC]/npcs/[nome_npc].md
```

- `[nome_npc]` em snake_case, nome principal sem título
- Exemplos: `iris_kell.md`, `xerife_duarte.md`, `o_boticario.md`, `conde_varga.md`
- Alcunhas (quando o nome real é desconhecido) também em snake_case: `o_boticario.md`, `a_fera.md`

### Índice e Relações

| Arquivo | Caminho |
|---------|---------|
| `indice.md` | `[Campanhas]/[Nome do PC]/npcs/` |
| `relacoes.md` | `[Campanhas]/[Nome do PC]/npcs/` |

### Cenário (snake_case fixo)

| Arquivo | Conteúdo |
|---------|----------|
| `cenario.md` | Hub central |
| `geografia.md` | Mapa, bairros, territórios |
| `historia.md` | Contexto histórico |
| `sociedade.md` | Mortais |
| `politica.md` | Política vampírica |
| `economia.md` | Recursos |
| `cultura.md` | Arte, religião |
| `arquitetura.md` | Edifícios, refúgios |
| `clima.md` | Noites, estações |

### Templates

Em `08_Templates/`:
- `[NN]_[Nome_Legível].md` — permite nome legível porque templates são referências de leitura, não lidos por script.
- Exemplos existentes: `01_Ficha_NPC.md`, `04_Caderno_de_Campanha.md`.

---

## Hierarquia de Nomenclatura

Resumo visual:

```
[Campanhas]/                            ← técnico
└── Helena Prado/                    ← LEGÍVEL (nome do PC)
    ├── contexto.md                  ← técnico
    ├── personagem.md                ← técnico
    ├── npcs/
    │   └── xerife_duarte.md         ← técnico (snake_case)
    └── partidas/
        └── A Queda do Príncipe/       ← LEGÍVEL (partida)
            └── A Dívida de Sangue/  ← LEGÍVEL (história)
                └── O Armazém do Cais/ ← LEGÍVEL (aventura)
                    ├── aventura.md  ← técnico
                    └── sessao_03.md ← técnico
```

---

## Regras Adicionais

1. **Pastas narrativas** podem ter espaços, acentos e cedilha — são para leitura humana.
2. **Arquivos técnicos** não podem ter espaços nem acentos — entram em comandos e scripts.
3. **Datas** em nomes de arquivo, quando necessárias, usar formato `AAAA-MM-DD`: `handoff_2026-10-31.md`.
4. **Versões** quando aplicável: sufixo `_v[N]`: `aventura_v2.md`.
5. **Caracteres proibidos** em qualquer nome: `< > : " / \ | ? *` (restrições do sistema de arquivos Windows).

---

*Convenções canonizadas em 2026-10-31 — decisão D2 da Onda 0 de consolidação. Casa com a skill `/vtm:criar`.*
