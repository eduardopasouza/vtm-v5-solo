# Estrutura de Pastas — Campanha VtM V5

<!-- Referencia para criar a arvore de diretorios ao iniciar uma nova campanha -->
<!-- Substituir [Nome_Campanha] pelo nome real, em snake_case -->

---

## Arvore de Diretorios

```
[Nome_Campanha]\
├── 00_INDICE_MESTRE.md
├── 01_personagem\
│   └── ficha_[nome].md
├── 02_cenario\
│   ├── 00_hub_central.md
│   └── [NN]_[aspecto].md
├── 03_npcs\
│   └── [NN]_[nome].md
├── 04_historia_[N]_[titulo]\
│   └── aventura_[NN]_[titulo].md
├── 05_gestao\
│   ├── caderno_[campanha].md
│   ├── objetivos_ativos.md
│   ├── enredo_arcos_narrativos.md
│   ├── ramificacoes_consequencias.md
│   ├── direcao_narrador_SEGREDOS.md
│   └── logs\
│       └── sessao_[NNN]_[titulo].md
└── 06_recursos\
    └── [mapas, imagens, referencias]
```

---

## Descricao de Cada Pasta

### `00_INDICE_MESTRE.md`

Arquivo raiz da campanha. Funciona como portal de navegacao. Contem:
- Links para todos os documentos principais
- Estado atual da campanha (partida, historia, aventura, cena)
- Lista de NPCs ativos com links para fichas
- Lista de pistas ativas
- Referencia rapida para a proxima sessao

Manter atualizado a cada sessao. E o primeiro arquivo a ser lido ao retomar a campanha.

---

### `01_personagem\`

Ficha completa do personagem jogador (PC). Um arquivo por personagem.

**Contem:**
- Ficha mecanica completa (atributos, habilidades, disciplinas, vantagens, defeitos)
- Historia do personagem (mortal e Membro)
- Relacoes pessoais (Touchstones, Senhor, Coterie se houver)
- Conviccoes e Cronicas de Sangue
- Historico de XP e avancos

**Nomenclatura:** `ficha_[nome_snake_case].md`

---

### `02_cenario\`

Documentacao do cenario onde a campanha se passa. Cada aspecto relevante do cenario tem seu proprio arquivo.

**Contem:**
- `00_hub_central.md` — Visao geral da cidade/dominio: geografia, atmosfera, estrutura de poder, Elysiums, territorios
- Arquivos tematicos para aspectos especificos: `01_politica_camarilla.md`, `02_territorio_anarquista.md`, `03_locais_notaveis.md`, etc.

**Nomenclatura:** `[NN]_[aspecto_snake_case].md`

---

### `03_npcs\`

Fichas de todos os NPCs da campanha, usando o template `01_Ficha_NPC.md`.

**Contem:**
- Uma ficha por NPC
- Dados mecanicos, personalidade, motivacoes, relacao com o PC
- Secao de notas do narrador (spoilers)

**Nomenclatura:** `[NN]_[nome_snake_case].md`
- Numerar sequencialmente na ordem de criacao
- Exemplo: `01_dr_helena_voss.md`, `02_padre_carlos.md`

---

### `04_historia_[N]_[titulo]\`

Uma pasta por historia (arco narrativo). Dentro, as aventuras que compoem essa historia.

**Contem:**
- Aventuras individuais usando o template `02_Aventura.md`
- Cada aventura e um episodio jogavel dentro do arco

**Nomenclatura da pasta:** `04_historia_[N]_[titulo_snake_case]\`
**Nomenclatura dos arquivos:** `aventura_[NN]_[titulo_snake_case].md`

**Hierarquia narrativa:**
```
Jogo (campanha inteira)
└── Partida (grande arco, como uma "temporada")
    └── Historia (arco narrativo coeso, como um "volume")
        └── Aventura (episodio jogavel, 1-3 sessoes)
            └── Cena (unidade minima de jogo)
```

Pode haver multiplas pastas `04_historia_*` em uma campanha.

---

### `05_gestao\`

Documentos de gerenciamento da campanha. O "backend" do narrador.

**Contem:**

| Arquivo | Proposito |
|---------|-----------|
| `caderno_[campanha].md` | Documento vivo — estado atual da campanha, atualizado a cada sessao. Usar template `04_Caderno_de_Campanha.md` |
| `objetivos_ativos.md` | Lista consolidada de objetivos em todos os niveis (jogo, partida, historia, aventura) |
| `enredo_arcos_narrativos.md` | Visao macro dos arcos planejados — onde a historia esta indo |
| `ramificacoes_consequencias.md` | Registro de decisoes do jogador e suas consequencias futuras (referencia cruzada com logs) |
| `direcao_narrador_SEGREDOS.md` | Segredos do narrador, revelacoes planejadas, twists. **NUNCA compartilhar com o jogador** |

**Subpasta `logs\`:**
- Logs individuais de cada sessao, usando o template `03_Log_de_Sessao.md`
- **Nomenclatura:** `sessao_[NNN]_[titulo_snake_case].md`
- Numerar com tres digitos para ordenacao: `sessao_001_`, `sessao_002_`, etc.

---

### `06_recursos\`

Materiais de apoio que nao sao documentos de texto narrativo.

**Contem:**
- Mapas (cidade, locais, territorios)
- Imagens de referencia (NPCs, locais, objetos)
- Playlists ou referencias musicais
- Tabelas de consulta rapida
- Material visual para mostrar ao jogador
- PDFs de suplementos relevantes

**Nomenclatura:** livre, mas usar prefixo descritivo. Exemplo: `mapa_ponta_dareia.png`, `ref_elysium_teatro.jpg`

---

## Como Usar Esta Estrutura

1. **Nova campanha:** Criar a arvore de pastas conforme acima
2. **Nova historia:** Criar pasta `04_historia_[N]_[titulo]\` e popular com aventuras
3. **Nova sessao:** Criar log em `05_gestao\logs\` e atualizar o caderno
4. **Novo NPC:** Criar ficha em `03_npcs\` e registrar no caderno
5. **Sempre:** Manter `00_INDICE_MESTRE.md` e `caderno_[campanha].md` atualizados

---

<!-- Criado com template IAra v10 — VtM V5 -->
