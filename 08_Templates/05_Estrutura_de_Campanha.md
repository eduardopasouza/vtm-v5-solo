# Estrutura de Pastas — Campanha VtM V5

<!-- Referencia canônica para criar a árvore de diretórios ao iniciar uma nova campanha -->
<!-- Esta estrutura é a usada pela skill vtm-criar e pela campanha Edward Bello -->
<!-- Decisão D1 — 2026-10-31 -->

---

## Árvore de Diretórios

```
07_Jogos/[Nome do PC]/
├── contexto.md              # Estado atual global do jogo
├── personagem.md            # Ficha do PC
├── direcao.md               # Segredos do narrador (NUNCA mostrar ao jogador)
├── timeline.md              # Linha do tempo cronológica
├── objetivos.md             # Tracker de objetivos (todos os níveis)
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
| **Jogo** | Campanha inteira (vida do PC) | `07_Jogos/[Nome do PC]/` | Nome do PC, legível |
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
- Fichas de NPC: `[nome].md` em snake_case (ex.: `anne_bowesley.md`, `lord_ashworth.md`)

Ver `06_Convencoes_de_Nomenclatura.md` para a regra completa.

---

## Como Usar

1. **Nova campanha:** Criar `07_Jogos/[Nome do PC]/` e popular `contexto.md`, `personagem.md`, `direcao.md`, `timeline.md`, `objetivos.md`, pastas `npcs/` e `cenario/`.
2. **Nova partida:** Criar pasta `partidas/[Nome da Partida]/` com `partida.md` e `ramificacoes.md`.
3. **Nova história:** Criar pasta `[Nome da História]/` dentro da partida com `historia.md`.
4. **Nova aventura:** Criar pasta `[Nome da Aventura]/` dentro da história com `aventura.md`.
5. **Nova sessão:** Criar `sessao_NN.md` dentro da aventura e atualizar `contexto.md`, `timeline.md`, `objetivos.md`.

---

*Template canonizado em 2026-10-31 — decisão D1 da Onda 0 de consolidação. Esta é a estrutura usada pela skill `vtm-criar` e pela campanha Edward Bello.*
