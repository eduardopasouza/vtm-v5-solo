# Design: Plugin VtM — 5 Skills para RPG Solo

**Data:** 07/03/2026
**Status:** Aprovado
**Decisões-chave:**
- Plugin com 5 skills independentes (máximo modular)
- Jogos em `07_Jogos/[Nome do PC]/`
- Estrutura aninhada refletindo hierarquia narrativa
- Script de dados compartilhado em Python
- Consulta sob demanda aos 126 resumos + PDFs integrais quando necessário
- Autoridade do jogador: warn + obey
- Zero relação com IAra
- Prós/contras em TEXTO detalhado; widgets com labels sucintos (5-7 palavras)

## Skills

| Skill | Trigger | Responsabilidade |
|-------|---------|-----------------|
| `vtm-criar` | criar jogo, novo jogo, nova partida, nova história, nova aventura, sessão zero | Arquitetar jogo completo: cenário, sociedade, objetivos, arcos narrativos |
| `vtm-narrar` | jogar, continuar, sessão, próxima cena | Loop de jogo: narrar, resolver, documentar |
| `vtm-personagem` | criar personagem, ficha, evoluir, gastar XP | Criação e evolução do PC seguindo V5 |
| `vtm-npcs` | criar NPC, editar NPC, atualizar NPCs | Criar/manter NPCs com profundidade (3 níveis) |
| `vtm-gerenciar` | revisar campanha, entre sessões, planejar, objetivos | Gestão macro: objetivos, agendas de NPCs, arcos |

## Estrutura de Jogos

Hierarquia aninhada espelhando a hierarquia narrativa (Jogo > Partida > História > Aventura > Cena):

```
07_Jogos/[Nome do PC]/
├── contexto.md              # Estado atual global do jogo
├── personagem.md            # Ficha do PC
├── direcao.md               # Segredos do narrador (NUNCA mostrar ao jogador)
├── timeline.md              # Linha do tempo cronológica
├── objetivos.md             # Tracker de objetivos ativos (todos os níveis)
├── npcs/
│   ├── indice.md            # Lista resumida de todos os NPCs
│   ├── relacoes.md          # Mapa de relações entre NPCs e PC
│   └── [nome].md            # Fichas individuais de NPCs
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
    └── [Nome da Partida]/
        ├── partida.md           # Resumo, arco, objetivos da partida
        ├── ramificacoes.md      # Consequências de longo prazo
        └── [Nome da História]/
            ├── historia.md      # Quest, objetivos, status, pistas
            └── [Nome da Aventura]/
                ├── aventura.md  # Resumo, cenas planejadas, status
                └── sessao_XX_[titulo].md  # Log de cenas/sessão
```

**Cada nível narrativo = uma pasta.** Jogos nomeados pelo PC. Dentro de cada nível, arquivos descritivos (.md) + subpastas do nível seguinte.

## Regras Transversais

1. **Autoridade do jogador:** warn + obey (XP, dados, retcon, poderes)
2. **Anti-alucinação:** NPCs conforme fichas, fatos conforme livros, contradição = PARAR
3. **Fidelidade oficial:** consultar 126 resumos sob demanda
4. **Dados reais:** script Python, nunca simulado
5. **Documentação silenciosa:** atualizar docs a cada cena, sem pedir permissão
6. **Formato de opções:** prós e contras em TEXTO detalhado; labels de widget sucintos (5-7 palavras max)
7. **Consulta a livros integrais:** em situações-chave, consultar PDFs completos (não apenas resumos)
