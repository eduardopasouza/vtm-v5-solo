# Estrutura de Pastas — Campanha VtM V5

<!-- Referencia canônica para criar a árvore de diretórios ao iniciar uma nova campanha -->
<!-- Esta estrutura é a usada pela skill /vtm:criar -->
<!-- Decisão D1 — 2026-10-31 -->

---

## Árvore de Diretórios

```
[Campanhas]/[Nome do PC]/
├── estado.json              # Números da campanha (P8, 2026-11-15) — modelo em 08_Templates/07_estado.json
├── contexto.md              # Estado atual global do jogo (narrativa; sem números quando há estado.json)
├── personagem.md            # Ficha do PC
├── direcao.md               # Segredos do narrador (NUNCA mostrar ao jogador) — modelo 11_direcao.md
├── arcos.md                 # Mapa público dos arcos — modelo 08_arcos.md
├── objetivos_arquivo.md     # Objetivos encerrados — modelo 10_objetivos_arquivo.md
├── glossario.md             # Termos de lore em uma linha — modelo 12_glossario.md
├── mesa.json                # Cena em curso e decisão pendente (ferramenta registrar_mesa)
├── timeline.md              # Linha do tempo cronológica
├── objetivos.md             # Só objetivos ativos, até 8 — modelo 09_objetivos.md
├── npcs/
│   ├── indice.md            # Lista resumida de todos os NPCs
│   ├── relacoes.md          # Mapa de relações entre NPCs e PC
│   └── [nome_npc].md        # Fichas individuais de NPCs (snake_case)
├── cenario/
│   ├── cenario.md           # Hub central do cenário
│   ├── geografia.md
│   ├── historia.md
│   ├── sociedade.md
│   ├── politica.md
│   ├── economia.md
│   ├── cultura.md
│   ├── arquitetura.md
│   └── clima.md
└── partidas/
    └── [Nome da Partida]/            # Legível, com espaços e acentos
        ├── partida.md
        ├── ramificacoes.md
        └── [Nome da História]/       # Legível
            ├── historia.md
            └── [Nome da Aventura]/   # Legível
                ├── aventura.md
                └── sessao_NN.md      # snake_case + número de 2 dígitos
```

---

## Hierarquia Narrativa

| Nível | Escopo | Pasta | Nome |
|-------|--------|-------|------|
| **Jogo** | Campanha inteira (vida do PC) | `[Campanhas]/[Nome do PC]/` | Nome do PC, legível |
| **Partida** | Grande arco narrativo | `partidas/[Nome da Partida]/` | Legível, com espaços/acentos |
| **História** | Arco narrativo coeso | `[Nome da História]/` dentro da Partida | Legível, com espaços/acentos |
| **Aventura** | Episódio jogável (1-3 sessões) | `[Nome da Aventura]/` dentro da História | Legível, com espaços/acentos |
| **Cena** | Unidade mínima de jogo | Seção dentro de `sessao_NN.md` | — |

---

## Arquivos Técnicos (snake_case)

Arquivos **dentro** das pastas narrativas seguem snake_case sem espaços nem acentos:

- `contexto.md`, `personagem.md`, `direcao.md`, `timeline.md`, `objetivos.md`
- `partida.md`, `historia.md`, `aventura.md`, `ramificacoes.md`
- `sessao_01.md`, `sessao_02.md`, ..., `sessao_NN.md` (dois dígitos sempre)
- `cenario.md`, `geografia.md`, `historia.md` (dentro de `cenario/`)
- `indice.md`, `relacoes.md` (dentro de `npcs/`)
- Fichas de NPC: `[nome].md` em snake_case (ex.: `iris_kell.md`, `xerife_duarte.md`)

Ver `06_Convencoes_de_Nomenclatura.md` para a regra completa.

---

## Como Usar

1. **Nova campanha:** Criar `[Campanhas]/[Nome do PC]/` e popular `estado.json` (do modelo `07_estado.json`), `contexto.md`, `personagem.md`, `direcao.md`, `arcos.md`, `timeline.md`, `objetivos.md`, `objetivos_arquivo.md`, `glossario.md`, pastas `npcs/` e `cenario/`.
2. **Nova partida:** Criar pasta `partidas/[Nome da Partida]/` com `partida.md` e `ramificacoes.md`.
3. **Nova história:** Criar pasta `[Nome da História]/` dentro da partida com `historia.md`.
4. **Nova aventura:** Criar pasta `[Nome da Aventura]/` dentro da história com `aventura.md` (1 a 3 sessões previstas e "fecha quando") e atualizar `arcos.md`.
5. **Nova sessão:** Criar `sessao_NN.md` dentro da aventura e atualizar `contexto.md`, `arcos.md`, `timeline.md`, `objetivos.md`.

---

*Template canonizado em 2026-10-31 — decisão D1 da Onda 0 de consolidação. Esta é a estrutura usada pela skill `/vtm:criar`.*
