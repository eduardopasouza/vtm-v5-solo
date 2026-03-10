# Convencoes de Nomenclatura — VtM V5

<!-- Referencia rapida para nomear arquivos e pastas de forma consistente -->

---

## Regra Geral

- Usar **snake_case** (palavras separadas por underline) em todos os nomes de arquivo e pasta
- Sem acentos, cedilha ou caracteres especiais nos nomes de arquivo
- Prefixo numerico para ordenacao: `[NN]_` ou `[NNN]_`
- Extensao padrao: `.md` (Markdown)

---

## Nomenclatura por Tipo de Arquivo

### Ficha de NPC
```
[NN]_[nome_snake_case].md
```
- Pasta: `03_npcs\`
- Numerar na ordem de criacao
- Usar nome principal do NPC (sem titulos)
- Exemplos:
  - `01_helena_voss.md`
  - `02_padre_carlos.md`
  - `03_o_xerife.md` (alcunha se nao tiver nome revelado)

---

### Aventura
```
aventura_[NN]_[titulo_snake_case].md
```
- Pasta: `04_historia_[N]_[titulo]\`
- Numerar sequencialmente dentro de cada historia
- Titulo curto e descritivo
- Exemplos:
  - `aventura_01_a_convocacao.md`
  - `aventura_02_sombras_no_porto.md`
  - `aventura_03_o_julgamento.md`

---

### Log de Sessao
```
sessao_[NNN]_[titulo_snake_case].md
```
- Pasta: `05_gestao\logs\`
- Tres digitos para ordenacao (001, 002, ..., 999)
- Titulo curto que capture o evento principal da sessao
- Exemplos:
  - `sessao_001_noite_do_abraco.md`
  - `sessao_002_primeiro_elysium.md`
  - `sessao_015_queda_do_principe.md`

---

### Caderno de Campanha
```
caderno_[campanha_snake_case].md
```
- Pasta: `05_gestao\`
- Um por campanha
- Exemplos:
  - `caderno_beard.md`
  - `caderno_noites_de_sao_luis.md`

---

### Ficha de Personagem (PC)
```
ficha_[nome_snake_case].md
```
- Pasta: `01_personagem\`
- Usar nome do personagem, nao do jogador
- Exemplos:
  - `ficha_beard.md`
  - `ficha_marcus_wells.md`

---

### Pasta de Historia
```
04_historia_[N]_[titulo_snake_case]\
```
- Um digito para o numero da historia
- Titulo do arco narrativo
- Exemplos:
  - `04_historia_1_despertar\`
  - `04_historia_2_guerra_de_dominio\`
  - `04_historia_3_a_longa_noite\`

---

### Templates
```
[NN]_[nome].md
```
- Pasta: `08_Templates\`
- Numerados para ordenacao
- Exemplos:
  - `01_Ficha_NPC.md`
  - `02_Aventura.md`
  - `03_Log_de_Sessao.md`

---

### Documentos de Cenario
```
[NN]_[aspecto_snake_case].md
```
- Pasta: `02_cenario\`
- `00_` reservado para o hub central
- Exemplos:
  - `00_hub_central.md`
  - `01_politica_e_poder.md`
  - `02_territorios.md`
  - `03_elysiums.md`

---

### Documentos de Gestao
```
[nome_descritivo_snake_case].md
```
- Pasta: `05_gestao\`
- Sem prefixo numerico (sao poucos e fixos)
- Nomes padrao:
  - `caderno_[campanha].md`
  - `objetivos_ativos.md`
  - `enredo_arcos_narrativos.md`
  - `ramificacoes_consequencias.md`
  - `direcao_narrador_SEGREDOS.md`

---

## Hierarquia Narrativa — Terminologia

Estes termos sao usados de forma consistente em toda a documentacao:

| Nivel     | Escopo                            | Duracao Tipica        | Analogia         |
|-----------|-----------------------------------|-----------------------|------------------|
| **Jogo**      | Campanha inteira                  | Meses a anos          | Serie de TV      |
| **Partida**   | Grande arco, "temporada"          | Varias historias      | Temporada        |
| **Historia**  | Arco narrativo coeso              | Varias aventuras      | Volume / Arco    |
| **Aventura**  | Episodio jogavel                  | 1-3 sessoes           | Episodio         |
| **Cena**      | Unidade minima de jogo            | Minutos a 1 hora      | Cena             |

**Exemplo concreto:**
```
Jogo: Cronicas de Sao Luis
└── Partida 1: A Mascara Rachada
    ├── Historia 1: Despertar
    │   ├── Aventura 01: A Convocacao
    │   │   ├── Cena 1: O Telefonema
    │   │   ├── Cena 2: O Encontro no Elysium
    │   │   └── Cena 3: A Proposta
    │   ├── Aventura 02: Sombras no Porto
    │   └── Aventura 03: O Julgamento
    └── Historia 2: Guerra de Dominio
        ├── Aventura 01: Linhas no Mapa
        └── ...
```

---

## Regras Adicionais

1. **Nunca usar espacos** em nomes de arquivo ou pasta — usar underline `_`
2. **Nunca usar acentos** em nomes de arquivo — usar versao sem acento (`convocacao`, nao `convocação`)
3. **Maiusculas** apenas em nomes proprios dentro de titulos de arquivo quando necessario para clareza (`SEGREDOS` no arquivo de direcao)
4. **Datas** em nomes de arquivo, quando necessarias, usar formato `DDMMAA`: `caderno_beard_050326.md`
5. **Versoes** quando aplicavel: sufixo `_v[N]`: `aventura_01_a_convocacao_v2.md`

---

<!-- Criado com template IAra v10 — VtM V5 -->
