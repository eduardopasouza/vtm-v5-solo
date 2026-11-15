# Plano revisado do plugin — VtM V5 Solo

> Redigido em **2026-11-14**. Só documento, nada implementado.
> Substitui como plano de trabalho o design de `docs/2026-03-07-vtm-plugin-design.md` e a `_retomada/PROPOSTA-DEV-2026-10-31.md` (que ficam como histórico).
> Escopo confirmado pelo Eduardo em 2026-11-14: o plugin, não a campanha. Dez frentes.
> Cada afirmação cita `arquivo:linha` ou fonte. O que não foi conferido está marcado **[a verificar]**.

---

## 0. Restrições que valem para todo o plano

### 0.1 A trava G1 do IUS bloqueia o desenvolvimento e o jogo nesta pasta

Lido em `C:\Users\eduar\.claude\plugins\marketplaces\local-desktop-app-uploads\ius\hooks\`:

- O hook `PreToolUse` do IUS intercepta `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, `Bash`, `PowerShell`, as ferramentas de escrita e processo do Desktop Commander e ferramentas de envio (`hooks.json:12`).
- A G1 só libera três janelas: `C:\Cowork` (ou `CLAUDE_PLUGIN_OPTION_COWORK_ROOT`), `C:\dev\ius-nucleo` (fixo no código) e a pasta temporária do sistema, além da auto-memória do Claude (`pretooluse.py:25`, `:38-40`, `:138-149`).
- Efeito em `C:\dev\vtm-v5-solo`: não dá para escrever arquivo nem rodar terminal. **Uma sessão de jogo não conseguiria rolar dados** pelo `vtm_dice.py`, porque a rolagem passa pelo Bash.
- Ferramentas MCP que não estão na lista do `matcher` passam (`hooks.json:12`). Leitura (`Read`, `Grep`, `Glob`) passa.

- O narrador também grava os arquivos da campanha a cada cena. Tirar só as rolagens do Bash não resolve: a escrita continuaria bloqueada.
- O hook `SessionStart` do IUS injeta prazos, valores e nomes de clientes em toda sessão, inclusive numa sessão de jogo.
- O IUS não aparece em `enabledPlugins` de `~/.claude/settings.json` (`:535-540`); a mensagem do hook o identifica como `ius@inline`. A forma de desativá-lo só neste projeto **[a verificar no teste]**.

**Passo 0 (decisão do Eduardo, não mexo no IUS):** liberar esta pasta. Opções na decisão P2 (seção 3).

### 0.2 Acervo localizado

`D:\Downloads-ES101026\BibliotecaElfica\` — **175 PDFs** (inventário por Glob em 2026-11-14):

| Pasta | Conteúdo relevante |
|-------|--------------------|
| `Vampiro a Máscara/` (~76) | **V5 em inglês:** Core (`Vampire the Masquerade.pdf`), Camarilla, Anarch, Chicago by Night, The Fall of London, Cults of the Blood Gods, V5 Companion, fichas de mecânica básica. **Edições anteriores em PT-BR:** Módulo Básico 1ª/2ª e 3ª ed., V20, Guia dos Jogadores, Guia da Camarilla, Guia do Sabá, Livro de Nod, Revelações da Mãe Sombria, Gehenna, ~20 Livros de Clã, Carniçais, Tempo do Sangue Fraco, Vampiros do Oriente etc. Três clanbooks Revised em inglês. |
| `Vampiro a Idade das Trevas/` | Idade das Trevas (PT-BR) |
| `Lobisomem o Apocalipse/` (~47) | Módulo Básico 2ª ed. e Revised, 17 Livros de Tribo, 6 Raças Metamórficas, Umbra, Livros da Wyrm/Weaver/Wyld etc. (PT-BR). Fichas de mecânica básica. **Sem W5.** |
| `Mago a Ascensão/` (~26) | Módulo Básico 2ª e 3ª ed., 9 Tradições, Tecnocracia, Iteração X etc. (PT-BR). **Sem M20.** |
| `Hunter_ The Reckoning/` | Só as fichas de mecânica básica do H5. **Sem o livro de regras.** |
| `Vampiro o Réquiem/`, `Mago o Despertar/`, `Lobisomem os Destituídos/` | Crônicas das Trevas (CofD) — outro universo, não o WoD clássico. |

Lacunas para "todos os elementos do WoD": **Wraith, Changeling, Demon, Mummy, Hunter (livro), Kindred of the East** não estão no acervo, salvo `Vampiros do Oriente` (VtM Revised). Ver decisão P9.

Alguns PDFs pedem OCR (o nome do arquivo diz "passar OCR", ex.: `Livro de Clã - Tremere (passar OCR)`).

Teste em 2026-11-14: o leitor de PDF do Claude falhou (falta o `pdftoppm`). **Atualização 2026-11-15:** o PyMuPDF (`fitz`) já está instalado no Python global e extrai o texto do V5 Core inteiro (431 páginas; página impressa = PDF − 2). Os livros marcados "passar OCR" ainda não foram testados.

### 0.3 O repositório é público

- `github.com/eduardopasouza/vtm-v5-solo` é público. Texto extraído dos PDFs é conteúdo de terceiros: o índice do acervo mora em `${CLAUDE_PLUGIN_DATA}` ou na pasta do acervo, **nunca no repositório**.
- Os 126 resumos de `12_Resumos_dos_Livros/` já estão públicos e derivam de livros comerciais e de traduções de fã. Decisão P3.

### 0.4 O que a documentação do Claude Code confirma (lida em 2026-11-14)

Fonte: subagente `claude-code-guide`, páginas de manifesto, skills, subagentes, hooks e instalação em `code.claude.com/docs`.

- `${CLAUDE_PLUGIN_ROOT}` e `${CLAUDE_SKILL_DIR}` são substituídos no corpo de skills, comandos e agentes. Também em hooks e no `.mcp.json`. O Bash **não** recebe essas variáveis no ambiente: a skill escreve o caminho no texto.
- `userConfig` no manifesto: tipos `string`, `number`, `boolean`, `directory`, `file`. As skills leem por `${user_config.CHAVE}`. Isso **substitui o `.local.md`** criado na D6 da Onda 0.
- `${CLAUDE_PLUGIN_DATA}`: pasta persistente entre atualizações do plugin. Lugar do índice, do cache e de logs.
- Agentes de plugin aceitam `tools`, `disallowedTools`, `model`, `skills`, `maxTurns`, entre outros.
- Skills de plugin aparecem como `/plugin:skill`. **Não há documentação** sobre como o disparo automático se resolve entre plugins (confiança baixa).
- Hook `SessionStart` pode injetar texto no contexto.
- Instalação pessoal: `claude --plugin-dir <pasta>` para testar; persistente por `marketplace.json` local ou repositório GitHub.
- **[a verificar no teste da Onda 1]:** links relativos dentro da skill, Python no PATH para MCP no Windows, colisão de disparo.

### 0.5 Três sistemas de memória já rodam

- O **IUS** injeta contexto jurídico no início de toda sessão (hook `SessionStart`).
- O **ai-memory** captura observações de sessão.
- A **auto-memória** do Claude fica em `~/.claude/projects/C--dev-vtm-v5-solo/memory/`.
- Regra do plano: **os arquivos da campanha são a única fonte de verdade do jogo.** O plugin não grava estado de jogo no ai-memory nem na auto-memória. O hook do plugin injeta só um resumo curto da campanha ativa.

---

## 1. Arquitetura-alvo

Três camadas:

| Camada | O que é | Onde mora | Vai pro git público? |
|--------|---------|-----------|----------------------|
| **Motor** | Skills, agentes, hooks, scripts Python, referência V5 própria, templates | Pasta do plugin (`${CLAUDE_PLUGIN_ROOT}`) | Sim |
| **Campanha** | Uma pasta por jogo (`Edward Bello/` etc.) | `${user_config.pasta_campanhas}` | Decisão P3/P8 |
| **Acervo** | PDFs + índice com texto por página | `${user_config.pasta_acervo}` + índice em `${CLAUDE_PLUGIN_DATA}` | Nunca |

Layout proposto do plugin:

```
vtm-v5/
├── .claude-plugin/
│   ├── plugin.json          # nome, versão, userConfig
│   └── marketplace.json     # instalação pessoal ("source": "./")
├── skills/
│   ├── narrar/      SKILL.md + references/{combate,alimentacao,cacada,frenesi,politica,disciplinas}.md
│   ├── criar/       SKILL.md + references/
│   ├── personagem/  SKILL.md
│   ├── npcs/        SKILL.md
│   ├── gerenciar/   SKILL.md
│   └── pesquisar/   SKILL.md            # nova (frente 7)
├── agents/
│   ├── guardiao-regras.md
│   ├── arquivista.md
│   ├── continuidade.md
│   ├── pesquisador-historico.md
│   ├── agenda-npcs.md
│   └── cronista-wod.md
├── hooks/hooks.json          # SessionStart: resumo da campanha ativa
├── scripts/
│   ├── vtm_dice.py           # motor de rolagens (frente 6)
│   ├── efemerides.py         # sol e lua por data e cidade (frente 7)
│   ├── acervo_indexar.py     # PDF → texto por página → SQLite FTS5 (frente 8)
│   ├── acervo_buscar.py
│   └── campanha_auditar.py   # consistência (frente 3)
├── tests/
├── reference/                # hoje 01_Sistema … 05_Cenario, 10_Ferramentas
└── templates/                # hoje 08_Templates
```

`userConfig` proposto:

| Chave | Tipo | Uso |
|-------|------|-----|
| `pasta_campanhas` | directory | Onde ficam as pastas de jogo |
| `campanha_ativa` | string | Nome da pasta da campanha em jogo |
| `pasta_acervo` | directory | `D:\Downloads-ES101026\BibliotecaElfica` |
| `mostrar_dados` | boolean | D5 da Onda 0 (padrão: true) |
| `python` | file | Caminho do Python (o IUS usa `C:/Users/eduar/AppData/Local/Python/pythoncore-3.14-64/python.exe`, `hooks.json:6`) |

---

## 2. As dez frentes

Formato fixo: estado atual · alvo · componente · dependências · aceite · esforço · decisões.

### Frente 1 — Planejamento

- **Estado:** design de 07/03 (`docs/2026-03-07-vtm-plugin-design.md`, 5 skills) e proposta de 31/10 (6 ondas, `_retomada/`). Ambos anteriores à confirmação de `userConfig` e à descoberta da G1.
- **Alvo:** este plano vira `docs/PLANO-PLUGIN.md` no repositório do plugin, com registro de decisões (`docs/decisoes.md`, uma linha por decisão: data, opção, motivo).
- **Componente:** documento.
- **Dependências:** P1 (onde fica o plugin).
- **Aceite:** Eduardo aprova o plano; cada decisão P1-P9 registrada com data.
- **Esforço:** 1 h depois das decisões.
- **Decisões:** nenhuma própria.

### Frente 2 — Estrutura de plugin

- **Estado:** 5 skills soltas em `.claude/skills/`; sem manifesto, agentes, hooks ou MCP. Settings em `.claude/vtm.local.md.example` (Onda 0, D6).
- **Alvo:** layout da seção 1, instalável por `marketplace.json`, `userConfig` no lugar do `.local.md` (um mecanismo só), descrições das skills ancoradas em "vampiro/VtM".
- **Componente:** manifesto, reorganização de pastas.
- **Dependências:** P1, P2, P4.
- **Aceite (teste com `claude --plugin-dir`):**
  1. `/vtm:narrar` e as demais aparecem;
  2. `${CLAUDE_PLUGIN_ROOT}` e `${user_config.pasta_campanhas}` chegam substituídos no corpo da skill;
  3. uma rolagem real roda pelo `vtm_dice.py`;
  4. a G1 não bloqueia (depois do passo 0);
  5. numa sessão em `C:\Cowork`, "continuar a sessão" não dispara a skill de narrar.
- **Esforço:** 4-6 h.
- **Decisões:** P1, P2, P4, P5.

### Frente 3 — Memória da campanha

- **Estado:** arquivos `.md` em `07_Jogos/Edward Bello/`. Defasagens reais:
  - `timeline.md` para na Sessão 7 (`timeline.md:139-165`, rodapé "Sessão 7"); sessões 8-15 não estão lá;
  - `objetivos.md` e `personagem.md` param na Sessão 14 (`objetivos.md:187`, `personagem.md:417`), enquanto `contexto.md` está na 15 (`contexto.md:11`);
  - `09_Preferencias.md` ainda cita `objetivos_ativos.md` e `direcao_narrador_SEGREDOS.md` (`:58`, `:122`) e caminhos do OneDrive que não existem (`:171-172`).
  - Nada audita essas diferenças.
- **Alvo:**
  - `estado.json` por campanha com o que é número (Fome, FdV, Saúde, Humanidade, Manchas, XP, BP, data ficcional, local, hora da noite). Os `.md` ficam para narrativa.
  - `campanha_auditar.py`: aponta NPC citado sem ficha, sessão fora da linha do tempo, número divergente entre `estado.json` e `personagem.md`, rodapé de "atualizado em" defasado.
  - Hook `SessionStart`: se a sessão estiver na pasta de campanhas, injeta 10-15 linhas de `contexto.md` + `estado.json`. Só leitura.
  - Agente `arquivista` no fim da sessão propõe as atualizações; o narrador aplica.
  - `direcao.md` continua secreto por convenção (o jogador pode abrir o arquivo; o narrador não revela).
- **Componente:** script, hook, agente, template.
- **Dependências:** frente 2.
- **Aceite:** auditoria roda no Edward Bello e lista as defasagens acima; depois do conserto, volta vazia.
- **Esforço:** 4-6 h.
- **Decisões:** P8.

### Frente 4 — Agentes especializados

Regra: nenhum agente grava na campanha; propõem, o narrador decide e aplica. Modelo final escolhido no teste.

O frontmatter libera ou nega uma ferramenta inteira: não dá para dar a um agente "Bash só para um script". Por isso a busca no acervo e as rolagens viram **ferramentas MCP só de leitura** do plugin (P5), que os agentes recebem sem ganhar o terminal. Se os hooks do IUS também valem para subagentes **[a verificar]**, isso evita que a G1 trave os agentes.

| Agente | Função | Ferramentas | Modelo proposto |
|--------|--------|-------------|-----------------|
| `guardiao-regras` | Responde dúvida de regra com citação (livro, página) do índice do acervo e da `reference/`. Sem fonte, diz "não sei". | Read, Grep, MCP `vtm_acervo_buscar` | sonnet |
| `arquivista` | Lê o log da sessão e lista o que muda em cada arquivo da campanha | Read, Grep | sonnet |
| `continuidade` | Procura contradições entre sessões, fichas, linha do tempo e `direcao.md` | Read, Grep | sonnet |
| `pesquisador-historico` | Fatos reais para a data e cidade da campanha, com URL e data de acesso | WebSearch, WebFetch, Read | sonnet |
| `agenda-npcs` | Entre sessões, propõe o que cada NPC Maior fez fora de cena, conforme a ficha | Read, Grep | inherit |
| `cronista-wod` | Lore das outras criaturas (Garou, magos, caçadores…) com citação, e como interagem com vampiros | Read, Grep, MCP `vtm_acervo_buscar` | sonnet |

- **Dependências:** frente 2; `guardiao-regras` e `cronista-wod` dependem da frente 8.
- **Aceite:** cada agente roda uma tarefa de teste com saída citada; nenhum escreve arquivo.
- **Esforço:** 3-4 h.
- **Decisões:** P5 (o `Bash` restrito cai se o motor virar MCP).

### Frente 5 — Skills do narrador

- **Estado:** 5 skills com descrições genéricas ("jogar, continuar, sessão…", `.claude/skills/vtm-narrar/SKILL.md:2`). Combate, alimentação e frenesi espalhados dentro da `vtm-narrar` em poucas linhas (`:133-173`).
- **Alvo:** manter as 5, criar **uma** nova (`pesquisar`), e mover o detalhe para `references/` dentro de `narrar/`: combate, alimentação e ressonância, caçada por tipo de predador, frenesi e Rötschreck, política e favores (boons), uso de disciplinas. Cada referência aponta para a página do livro via índice. Cada skill nova é mais uma chance de colisão de disparo: só onde o fluxo é outro.
- **Componente:** skills e referências.
- **Dependências:** frente 2; o conteúdo das referências depende da frente 8.
- **Aceite:** em jogo de teste, uma cena de combate e uma de alimentação seguem as referências e citam a regra.
- **Esforço:** 4-6 h.
- **Decisões:** P4.

### Frente 6 — Motor de dados em Python

- **Estado:** `scripts/vtm_dice.py` faz `roll`, `rouse`, `remorse`, `frenzy` (`:17-143`). Lacunas:
  - Rouse sem o re-roll por Potência de Sangue (`01_Sistema/04_Fome_e_Bestia.md:73-86`);
  - sem re-rolagem por Força de Vontade (até 3 dados normais, `vtm-narrar/SKILL.md:148-149`);
  - sem teste resistido (Compelir contra resistência), Blood Surge (`04_Fome_e_Bestia.md:96-112`), cura (`:60-62`), alimentação com restrição por BP (`:143-153`) e ressonância (`01_Sistema/09_Ressonancia_Sanguinea.md`), combate e dano;
  - `frenzy` não aplica os modificadores (`04_Fome_e_Bestia.md:272-279`);
  - nenhum teste automatizado, nenhum registro das rolagens.
- **Alvo:** todas as rolagens do V5, cada função com a regra citada no código; registro de cada rolagem em `rolagens.jsonl` da campanha; testes com semente fixa conferindo as tabelas de referência.
- **Componente:** script (ou servidor MCP, decisão P5).
- **Dependências:** passo 0; P5; P6 (fonte canônica das regras).
- **Aceite:** testes verdes; os exemplos e as tabelas do V5 Core reproduzidos com citação de página (pela P6, o Core prevalece sobre `01_Sistema/04` e `05`).
- **Esforço:** 6-8 h.
- **Decisões:** P5, P6.

### Frente 7 — Busca para simetria com a realidade

- **Estado:** os 9 arquivos de `cenario/` do Edward Bello foram escritos à mão, sem fonte, misturando fato e ficção (ex.: `cenario/geografia.md`). Sem calendário, sem sol e lua. A regra "tempo narrativo rígido" (`09_Preferencias.md:97`) não tem número por trás.
- **Alvo:**
  - `efemerides.py`: pôr e nascer do sol, duração da noite e fase da lua por cidade e data, calculados localmente (algoritmo da NOAA em Python puro, sem dependência). Alimenta o relógio da noite no `estado.json`.
  - Skill `pesquisar` + agente `pesquisador-historico`: na sessão zero e antes de cada sessão, pesquisa a semana ficcional (política, economia, sociedade, cultura, religião, clima, eventos datados, figuras públicas).
  - Marcação de proveniência por bloco: `<!-- @historico fonte=URL acesso=AAAA-MM-DD -->` ou `<!-- @ficcao -->`.
  - Arquivo `calendario.md` por campanha.
- **Componente:** script, skill, agente.
- **Dependências:** frente 2; frente 3 (data ficcional no estado).
- **Aceite:** para Londres, dezembro de 1836: pôr do sol e lua das noites 77-90, e pelo menos 5 fatos datados da quinzena, cada um com URL.
- **Esforço:** 5-7 h.
- **Decisões:** nenhuma própria.

### Frente 8 — Regras e livros com citação

- **Estado:** acervo achado (0.2), nunca lido. Os 126 resumos foram gerados por IA em março e não foram conferidos contra os livros. A `reference/` própria (`01_Sistema` etc.) não cita página.
- **Alvo:**
  - `acervo_indexar.py`: extrai o texto de cada PDF por página; OCR nos que pedem; grava em SQLite FTS5 em `${CLAUDE_PLUGIN_DATA}` (livro, edição, linha, idioma, página, trecho).
  - `acervo_buscar.py`: busca por termo e devolve livro + página + trecho curto.
  - Regra do narrador: regra só com citação; sem citação, "não sei".
  - Conferência dos resumos e da `reference/` contra o índice, marcando divergências.
- **Componente:** scripts, agente `guardiao-regras`.
- **Dependências:** passo 0; P6; verificado em 2026-11-15: `pymupdf` e `pypdf` instalados, FTS5 disponível no `sqlite3` do Python 3.14; `tesseract` (OCR) **ausente**. O `pdftoppm` deixou de ser necessário (seção 0.2).
- **Aceite:** busca por "Blood Surge", "Rouse Check" e "Ventrue bane" devolve a página certa do V5 Core; PDFs com OCR legíveis.
- **Esforço:** 6-10 h (OCR pesa).
- **Decisões:** P3, P6.

### Frente 9 — Nuances de Vampiro

- **Estado:** 16 clãs, 12 disciplinas, 5 seitas, 6 textos de cenário, 12 de sistema. Cobertura de linhagens, Tradições, prestação de favores (boons), domínio e coterie, diablerie, Golconda, torpor, Laço de Sangue e rituais **[a verificar no inventário]**.
- **Alvo:** inventário de temas cruzado com o índice do acervo; para cada tema, uma ficha em `reference/` com a regra resumida e a citação; lista de lacunas.
- **Componente:** referência + agente `guardiao-regras`.
- **Dependências:** frente 8.
- **Aceite:** checklist de temas com fonte para cada item; lacunas listadas.
- **Esforço:** 8-12 h, incremental.
- **Decisões:** P6.

### Frente 10 — Integração com o resto do WoD

- **Estado:** um texto geral (`05_Cenario/04_Seres_Sobrenaturais.md`, Garou e outros). Acervo com Lobisomem e Mago em edições antigas (PT-BR), fichas do Hunter 5, CofD (outro universo). Sem Wraith, Changeling, Demon, Mummy.
- **Alvo:**
  - `reference/wod/<linha>/`: sociedade, poderes, como cada criatura vê e trata vampiros, onde aparece em Londres vitoriana e em outras eras;
  - fichas de NPC das outras criaturas em termos do V5 (para o narrador rolar contra);
  - agente `cronista-wod`.
- **Componente:** referência, agente, template de NPC por criatura.
- **Dependências:** frente 8; P7; P9.
- **Aceite:** um Garou e um mago Hermético prontos como NPC de Londres 1836, com citação do livro da linha.
- **Esforço:** 10-15 h para Lobisomem e Mago; mais por linha.
- **Decisões:** P7, P9.

---

## 3. Decisões pendentes, em ordem de dependência

| # | Decisão | Opções | Destrava |
|---|---------|--------|----------|
| **P2** | Passo 0: liberar esta pasta da G1 | (a) desativar o IUS só nas sessões deste projeto (forma exata **[a verificar]**, o plugin carrega como `ius@inline`) · (b) alterar o código do IUS para incluir a pasta nas janelas (`pretooluse.py:25`, mudança versionada no projeto do IUS) | Qualquer implementação, até copiar este plano para o repositório |
| **P1** | Onde fica o plugin | (a) neste repositório, reorganizado · (b) repositório novo `vtm-v5`, e este vira só a campanha. Um repositório novo também fica em `C:\dev` e depende da P2 | Frente 2, Onda 1 |
| **P3** | Repositório público e resumos | (a) tornar o repositório privado · (b) manter público e tirar os resumos para a camada do acervo · (c) manter como está | Frentes 2, 8 |
| **P4** | Disparo das skills | (a) automático, com descrições ancoradas · (b) só por comando `/vtm:...` (`disable-model-invocation`) | Frentes 2, 5 |
| **P5** | Motor de dados | (a) script chamado pelo Bash · (b) servidor MCP em Python | Frentes 4, 6 |
| **P6** | Fonte canônica de regra | (a) V5 em inglês (Core e suplementos) prevalece, PT-BR só para termos · (b) outra | Frentes 6, 8, 9 |
| **P7** | Cruzamento com outras linhas | (a) só ambientação, NPCs com estatísticas V5 · (b) converter regras de cada linha | Frente 10 |
| **P8** | Estado da campanha | (a) `.md` + `estado.json` · (b) só `.md` | Frente 3 |
| **P9** | Linhas do WoD e edições | Quais linhas entram (Lobisomem, Mago, Caçador, Wraith, Changeling, Demon, Múmia, Kindred of the East), se CofD entra, e o que precisa ser adquirido | Frente 10 |

---

## 4. Ondas revisadas

| Onda | Escopo | Pré-requisito | Esforço |
|------|--------|---------------|---------|
| 0 | Consolidação — **feita** (`c200210`, 2026-10-31) | — | — |
| 1 | Esqueleto do plugin + teste `--plugin-dir` (aceite da frente 2) + migrar `.local.md` → `userConfig` | P2, P1, P4, P5 | 4-6 h |
| 2 | Motor de dados completo e testado (frente 6) | Onda 1, P6 | 6-8 h |
| 3 | Memória da campanha: `estado.json`, auditoria, hook, arquivista, continuidade; consertar as defasagens do Edward Bello (frente 3) | Onda 1, P8 | 4-6 h |
| 4 | Acervo indexado + guardião de regras (frente 8) | Onda 1, P3, P6 | 6-10 h |
| 5 | Realidade: efemérides, skill `pesquisar`, pesquisador, proveniência (frente 7) | Onda 3 | 5-7 h |
| 6 | Skills e referências do narrador; nuances de Vampiro (frentes 5 e 9) | Onda 4 | 12-18 h |
| 7 | Integração com o WoD (frente 10) | Onda 4, P7, P9 | 10-15 h |
| 8 | Validação: sessão zero de uma campanha nova, de ponta a ponta | Ondas 1-6 | 1 sessão |

Total: **~50-75 h**, em 12-18 sessões. As estimativas são de ordem de grandeza.

---

*Plano redigido na pasta temporária da sessão por causa da trava G1; copiado para o repositório em 2026-11-14, depois do passo 0.*

---

## 5. Registro de decisões

| Data | Decisão | Opção | Motivo |
|------|---------|-------|--------|
| 2026-11-14 | P2 | (a) IUS desligado só neste projeto (`.claude/settings.local.json`) | Confirmado: terminal e escrita rodam sem "[IUS G1]" |
| 2026-11-14 | P1 | (a) plugin neste repositório | Histórico e referências juntos, nada a migrar |
| 2026-11-14 | P4 | (a) disparo automático, descrições ancoradas em VtM/vampiro/campanha | Mantém a linguagem natural; colisão conferida em teste |
| 2026-11-14 | P5 | Núcleo Python + servidor MCP do plugin + `vtm_dice.py` como CLI | Agentes rolam sem ganhar o Bash; um servidor para motor e acervo |
| 2026-11-14 | P6 | Hierarquia: regras da casa aprovadas por escrito pelo Eduardo > V5 Core (inglês) > suplementos V5 > `01_Sistema` e resumos > edições antigas (só lore). PT-BR só para termos | Regra verificável por página; adaptação registrada em vez de disfarçada de regra oficial. Exige um arquivo de regras da casa (a criar) |
| 2026-11-14 | P8 | (a) `.md` + `estado.json`: números só no JSON, `.md` só narrativa e sem repetir números | Uma fonte para os números; o motor lê e grava com a biblioteca padrão. Exige migrar os números do `personagem.md` na Onda 3 |
| 2026-11-14 | P3 | (b) repositório continua público; os 126 resumos de `12_Resumos_dos_Livros/` saem para a camada do acervo, fora do repositório | Mantém o plugin público. Em aberto: reescrever ou não o histórico do git (os resumos seguem nele sem isso) e se a campanha Edward Bello continua pública |
| 2026-11-15 | P3 — histórico | Reescrever o histórico na retirada dos resumos (frente 8): `git filter-repo` apaga `12_Resumos_dos_Livros/` de todos os commits, seguido de force push com OK explícito | Histórico limpo; 0 forks, então custo baixo. Todos os SHAs mudam; pedir ao suporte do GitHub a limpeza dos commits antigos em cache |
| 2026-11-15 | P3 — campanha | A campanha Edward Bello vai para um repositório privado separado (nome provisório `vtm-campanhas`) e sai do histórico público no mesmo `filter-repo` dos resumos | Separa motor e campanha (camadas da seção 1) e fecha os segredos do narrador. Exige: criar o repo, apontar `pasta_campanhas`, desligar o IUS lá |
| 2026-11-15 | P7 | (a) lore dos livros de cada linha, com citação; em cena, as outras criaturas são NPCs com estatísticas V5, e cada poder marcante convertido vira regra da casa registrada (P6) | Um sistema só na mesa; esforço dentro das 10-15 h. Os poderes são aproximações, não a regra original da linha |
| 2026-11-15 | P9 | Entram todas as linhas do WoD clássico: Lobisomem, Mago, Caçador, Wraith, Changeling, Demon, Múmia, Kindred of the East. CofD fica fora do índice e do `cronista-wod` | Cobertura completa sem misturar universos. Lobisomem e Mago têm livros no acervo; para as outras linhas é preciso adquirir: livro do H5 (o acervo só tem as fichas), Wraith, Changeling, Demon, Múmia, KotE (só há Vampiros do Oriente, Revised). Sem livro, a linha fica sem citação e o `cronista-wod` diz "não sei" |
| 2026-11-15 | Exceção à frente 4 | O servidor MCP `dados` grava cada rolagem em `rolagens.jsonl` da campanha (só acréscimo), embora as ferramentas MCP sejam "só leitura" | É um log de rolagens, não estado de jogo; nenhum arquivo da campanha é editado. O log fica fora do git (`.gitignore`) até a campanha sair do repositório público |
| 2026-11-14 | Escopo da Onda 1 | Pastas `01_Sistema`…`10_Ferramentas` ficam onde estão; `reference/` e `templates/` numa onda futura | Evita quebrar 49+ referências internas; nenhum aceite da Onda 1 depende disso |

## 6. Andamento da Onda 1 (2026-11-14)

- Feito: `.claude-plugin/plugin.json` (nome `vtm`, `userConfig` com `pasta_campanhas`, `campanha_ativa`, `pasta_acervo`, `mostrar_dados`, `python`) e `marketplace.json` (`vtm-local`, `"source": "."`); `claude plugin validate` passa. Skills movidas de `.claude/skills/vtm-*` para `skills/*`, descrições ancoradas, caminhos por `${CLAUDE_PLUGIN_ROOT}` e `${user_config.*}`, com regra de reserva para valor não preenchido. `vtm.local.md.example` removido. A chave `atributo_composure` do `.local.md` não foi migrada (nenhuma skill a lia).
- Documentação (2026-11-14): marketplace local de tipo `directory` carrega o plugin no lugar, sem cópia em cache; valores de `userConfig` ficam em `pluginConfigs` do settings do usuário; o comportamento de `${user_config.X}` sem valor **não é documentado**.
- Aceite 1 ✓ (as 5 skills aparecem como `/vtm:*` com `--plugin-dir`). Aceite 3 parcial (o script roda pelo caminho absoluto, de fora do repositório).
- Ativação (2026-11-14): só escrever `extraKnownMarketplaces` + `enabledPlugins` no `.claude/settings.local.json` **não instala**; o CLI não enxergou o marketplace. Funcionou com `claude plugin marketplace add C:/dev/vtm-v5-solo --scope local` e depois `claude plugin install vtm@vtm-local --scope local --config pasta_campanhas=... --config campanha_ativa=...`. O status ficou `enabled` (escopo local), e os valores foram para `pluginConfigs."vtm@vtm-local".options` em `~/.claude/settings.json`. `pasta_acervo` ficou vazia até a frente 8.
- Pendente: aceites 2 e 3 numa sessão nova aberta nesta pasta; aceite 5 com o Claude aninhado (precisa renovar o login do `claude` no terminal).

## 7. Andamento da Onda 2 — motor de dados (2026-11-15)

- **Fonte:** V5 Core lido localmente com PyMuPDF (`fitz` já instalado; o `pdftoppm` não é necessário). Texto extraído só na pasta temporária, fora do repositório. Página impressa = página do PDF − 2. Código e testes parafraseiam e citam "Core p. N".
- **Feito:**
  - `scripts/vtm_motor.py`: núcleo puro (recebe `random.Random` ou dados prontos) com avaliação de parada (sucesso, crítico, crítico confuso, falha bestial, falha total, vitória com custo), Fome substituindo dados, re-rolagem por FdV, testes de tracker, Rouse com 2 dados pela Potência, despertar, Blood Surge, cura Superficial e Agravada, frenesi, Remorso, conflito e dano, alimentação com penalidades da Potência, tabela de Potência (p. 216) e registro em `rolagens.jsonl`.
  - `scripts/vtm_dice.py`: CLI reescrito sobre o núcleo (mesma saída humana + `---JSON---`; `--campanha` ou `VTM_CAMPANHA` para registrar).
  - `scripts/vtm_mcp.py` + `.mcp.json` (em 2026-11-15 passou para `mcpServers` do `plugin.json`, ver seção 9) (servidor `dados`, FastMCP do pacote `mcp` 1.26.0 do Python global): ferramentas `mcp__plugin_vtm_dados__*`. O caminho da campanha chega por `env` com `${user_config.*}` (único uso documentado com exemplo).
  - `tests/`: 39 testes verdes (`python -m pytest tests`): núcleo com dados escolhidos, CLI por subprocesso com semente, servidor MCP real por stdio.
  - `skills/narrar` e `CLAUDE.md` atualizados para a nova semântica.
- **Mudança de semântica (quebra o uso antigo):** `roll <parada_total> <fome> <dif>` — antes os dois números eram somados. `remorse <humanidade> <manchas>` e `frenzy <fdv_intacta> <humanidade> <dif>` mudaram de argumentos.
- **Divergências encontradas (o Core prevalece, P6; alimentam a frente 8):**
  - Script antigo: somava a Fome ao pool (Core p. 205: substitui); Remorso com 0 dados virava degeneração automática (p. 239: mínimo 1 dado); frenesi sem o bônus de Humanidade ÷ 3 e sem a diferença do crítico (p. 219); Rouse sem 2 dados pela Potência (p. 211, 216).
  - `CLAUDE.md`: fórmula do Remorso era `humanidade − manchas` (correto: `10 − humanidade − manchas`). Corrigido.
  - `skills/narrar`: "drenar até matar → Fome 1" (Core p. 211-212: matar é o único jeito de chegar a 0). Corrigido.
  - `01_Sistema/03_Combate.md:374,473` e `04_Fome_e_Bestia.md:262,455`: frenesi sem o bônus de Humanidade ÷ 3. **Não corrigido** (frente 8).
  - `01_Sistema/08_Potencia_de_Sangue.md:126-133`: trata o bônus de poder como dados extras de re-rolagem; no Core (p. 216) são dados somados à parada da Disciplina. **Não corrigido** (frente 8).
- **Resolvido em 2026-11-15:** na imagem da p. 216, a célula de alimentação vale para as linhas 6-7 e para as linhas 8-9. BP 7 = 2 a menos, piso 2 (o motor já tinha); BP 9 = **2** a menos, piso 3 (o motor tinha 3; corrigido, com asserção no teste). "Sangue animal sacia metade" (BP 2) arredonda para baixo.
- **Fora desta onda:** combate avançado (p. 295-305), Disciplinas e poderes específicos, Ressonância e Discrasia, regras da casa (arquivo ainda não existe).
- **Pendente:** confirmar numa sessão nova que o servidor `dados` sobe pelo plugin (Python `python` = alias do WindowsApps neste computador) e que o `env` recebe o `userConfig` substituído.

## 8. Andamento da Onda 3 — memória da campanha (2026-11-15)

- **Ordem decidida (2026-11-15):** a parte do plugin vem agora, testada com uma campanha fictícia criada nos testes. O Edward Bello só foi **lido** pelo auditor. A migração dos números para o `estado.json` e os consertos ficam para depois de a campanha ir para o repositório privado (P3).
- **Feito:**
  - `scripts/vtm_campanha.py` com:
    - schema v1 do `estado.json`, validado só com a biblioteca padrão (sessão; tempo: noite, data ficcional, local, hora; personagem: Fome, BP, Humanidade, Manchas, Saúde e FdV com máximo e dano, XP);
    - auditor;
    - resumo para o início de sessão (não lê `direcao.md`).
  - `scripts/campanha.py`: CLI `auditar` / `validar` / `resumo` / `hook`.
  - `08_Templates/07_estado.json`: template.
  - `hooks/hooks.json`: SessionStart que injeta até 15 linhas, só quando o `cwd` está dentro da pasta de campanhas ou na pasta logo acima (o repositório); `C:\dev` e `C:\Cowork` não recebem o resumo. Lê `CLAUDE_PLUGIN_OPTION_*`, exportadas aos hooks.
  - Ferramenta MCP `auditar_campanha`.
  - Agentes `agents/arquivista.md` e `agents/continuidade.md` (Read, Grep, Glob + `auditar_campanha`; só propõem).
  - Skills `narrar`, `criar` e `gerenciar` e o `CLAUDE.md` passam a usar o `estado.json`.
  - 54 testes verdes.
- **Auditoria do Edward Bello (2026-11-15, só leitura): 3 erros e 13 avisos.**
  - Erro: `timeline.md` sem as sessões 8-15 (confirma o plano). Conferido à mão: a coluna numérica das tabelas finais é "Noite", não "Sessão".
  - Erro (2): `personagem.md:365` diz "Surge +4" e "Bane 3" com BP 4; a tabela do Core p. 216 dá 2 e 2. **Pergunta para a migração:** erro da ficha ou regra da casa ligada à coniunctio com Mithras? Se for regra da casa, registrá-la por escrito (P6) e ensinar o auditor a aceitá-la.
  - Aviso: rodapés de `objetivos.md` e `personagem.md` na Sessão 14 e de `timeline.md` na 7 (confirma o plano).
  - Aviso: Adelbert, Lucius, Dunstan e Henrik aparecem nas relações sem ficha.
  - Aviso: as fichas de Ilse Vogt, Kaspar Hesse, O Doktor, Robert Sedgwick e Thane estão fora do `npcs/indice.md`.
  - Aviso: `estado.json` ausente.
  - O auditor ainda não confere as referências quebradas de `09_Preferencias.md` (`:58`, `:122`, `:171-172`), que estão fora da pasta da campanha.
- **Perguntas em aberto para a migração:**
  - Máximos derivados da ficha (Saúde 7 = Vigor + Fortitude + 3, FdV 6 = Compostura + Determinação), BP e Humanidade: são estado ou ficha? Enquanto ficarem no `personagem.md`, o auditor marca `NUMERO_DUPLICADO`.
- **Pendente:**
  - mover a campanha para o repositório privado. No repositório novo também é preciso rodar `claude plugin marketplace add C:/dev/vtm-v5-solo --scope local` e `claude plugin install vtm@vtm-local --scope local --config ...`; senão as sessões lá não terão skills, hook nem MCP. E criar o `settings.local.json` que desliga o IUS;
  - criar o `estado.json` do Edward Bello e tirar os números dos `.md`;
  - consertar as defasagens até a auditoria voltar sem erros (aceite da frente 3);
  - confirmar numa sessão nova que o hook roda pelo plugin.

## 9. Andamento da Onda 4 — acervo indexado (2026-11-15)

- **Escopo (Eduardo, 2026-11-15):** o núcleo (índice, busca, MCP e agente) e mais três extras: conferir a `01_Sistema` contra o Core, OCR, e retirar a campanha e os resumos com reescrita do histórico.
- **Feito (parte 1):**
  - `scripts/vtm_acervo.py`: classifica cada PDF pela pasta e pelo nome (linha VtM/VtDA/WtA/MtA/HtR; edição core/v5/clássica; idioma). CofD fica fora (P9). Extrai texto por página com PyMuPDF e OCR opcional (Tesseract). Detecta a página impressa e grava em SQLite FTS5 (`remove_diacritics`), em `%LOCALAPPDATA%/vtm-v5/acervo.sqlite` (ou `VTM_INDICE`), fora do repositório. Reindexação incremental. A busca ordena pela P6 (Core > V5 > clássica) e devolve livro, página impressa e trecho curto.
  - `scripts/acervo.py` (CLI `indexar` / `buscar` / `status`), ferramenta MCP `buscar_acervo` e agente `agents/guardiao-regras.md` (sem fonte, "não sei").
  - As 5 skills passam a buscar no acervo e citar página.
  - Reserva da pasta de Jogos: em vez de `[Base]/07_Jogos`, pergunta ao jogador e nunca grava no repositório. Hook: a pasta logo acima só recebe o resumo se for o repositório do plugin.
  - 64 testes verdes, incluindo OCR real e `buscar_acervo` pelo servidor MCP.
- **Índice real (2026-11-15):** 161 livros, 18.604 páginas, 15.717 com texto; 14 PDFs do CofD fora. **Aceite da busca ✓:** "Blood Surge" → Core p. 218; "Rouse Check" → p. 211; "Ventrue bane" → p. 102.
- **OCR:** o Tesseract 5.4.0 **já estava instalado**, com `por` e `eng`, e nada foi baixado. Cerca de 6 s por página. A rodada nos ~2.900 páginas sem texto está em andamento.
- **Mudança da campanha e dos resumos (2026-11-15):**
  - Backup espelho em `C:\dev\_backup-vtm-v5-solo-2026-11-15\`, com cópia do `settings.local.json` e do `_retomada/`.
  - `git-filter-repo` instalado pelo pip.
  - Repositório **privado** `eduardopasouza/vtm-campanhas` (`C:\dev\vtm-campanhas`): `Edward Bello/` + `_resumos/`, histórico das sessões preservado. Os 192 arquivos foram conferidos blob a blob contra o público.
  - Plugin instalado lá (escopo local) e IUS desligado.
  - `userConfig`: `pasta_campanhas = C:/dev/vtm-campanhas`, `pasta_resumos = C:/dev/vtm-campanhas/_resumos`, `pasta_acervo = D:/Downloads-ES101026/BibliotecaElfica`. Gravado com `claude plugin configure --values-stdin` pelo `cmd` (no PowerShell o wrapper `.ps1` do `claude` estraga o stdin).
  - Histórico do público reescrito no lugar com `--invert-paths`: nenhum commit tem mais `07_Jogos` ou `12_Resumos_dos_Livros`. Todos os SHAs mudaram, e o commit só de campanha (Sessão 15) caiu. A pasta `07_Jogos/` ficou só com subpastas vazias, ignoradas.
- **MCP pelo plugin ✓ (2026-11-15):** numa sessão com o plugin recarregado, `auditar_campanha` e `buscar_acervo` responderam com o `userConfig` substituído. Achado: o `.mcp.json` na raiz era lido também como MCP **do projeto** (o repo do plugin é a pasta da sessão), sem `${CLAUDE_PLUGIN_ROOT}` substituído, e falhava. O servidor foi para `mcpServers` do `plugin.json` e o `.mcp.json` saiu.
- **Force push (2026-11-15):** o GitHub público está em `a6cffd9`, com 11 commits; `07_Jogos`, `12_Resumos_dos_Livros` e `.mcp.json` dão 404 pela API.
- **Conferência da `01_Sistema` (2026-11-15, subagente + amostragem):** há divergências com o Core em **todos os 12 arquivos**, cerca de 165 itens, umas 30 de gravidade alta. Exemplos de alta:
  - frenesi com Compostura + Determinação (o certo é FdV atual + Humanidade ÷ 3, p. 119/219);
  - Cavalgar a Onda com teste;
  - tabelas de Surge, Severidade da Perdição e alimentação por Potência erradas (p. 216);
  - Remorso contando as caixas ao contrário (p. 239);
  - penalidade social por Humanidade (p. 237-239);
  - dano somando Força (p. 126);
  - distribuição de Atributos e Habilidades na criação (p. 136);
  - Tipos de Predador dando Habilidade (p. 176-178);
  - custo de Vantagens e compra de FdV com XP.

  Conferidos à mão no índice: Atributos p. 136 ✓, tabela de DD do frenesi p. 220 ✓. O subagente apontou o `CLAUDE.md` com a fórmula antiga do Remorso, mas ela já estava corrigida desde a Onda 2. Relatório completo fora do git, em `_retomada/CONFERENCIA-01_SISTEMA-2026-11-15.md`. **Nada foi corrigido**: isso é a decisão seguinte (frente 9).
- **Gravidade ALTA corrigida (2026-11-15):** os ~35 itens da seção "Alta" em 01, 02, 03, 04, 05, 06, 07, 08, 09 e 11, cada um relido no índice (e a p. 216 também na imagem). O relatório errava no resumo da alimentação de BP 4+ (o certo: 4-5 sacia 1 a menos, 6-9 sacia 2, 10 sacia 3). Correções além do relatório: 08 dizia que chegar a Fome 5 pelo Surge dava frenesi imediato (p. 220: só Rouse falho com Fome 5); o ciclo de degeneração do 05 foi reescrito pela conta 10 − Humanidade − Manchas. Fica para a gravidade MÉDIA: DDs de frenesi no 04 e no 11, estaca e "Rötschreck automático" no 03, especialidades de Predador no 02.
- **Pendência do Edward Bello (decidir depois, na migração da campanha):** com BP 4 o Core dá Surto +2, Perdição 2, cura 3 Superficiais, Disciplina +2; animal e bolsa não saciam; humano sacia 1 a menos; sem exigência de matar (isso começa no BP 5). A campanha diverge em `personagem.md:289` (Surto +4), `personagem.md:365` (Surge +4, Bane 3, "exige drenar"), `personagem.md:296` e `contexto.md:19`. Opções: seguir o Core ou registrar regra da casa da coniunctio (P6).
- **Gravidade MÉDIA corrigida (2026-11-15):** os ~50 itens da seção "Média" em 01, 02, 03, 04, 05, 06, 07, 08, 09, 11 e 12, cada um relido no índice. Entre eles: DDs de frenesi (p. 220, de 2 a 4, sem "automático"), estaca, armas, tiro dirigido, agarrar, iniciativa e surpresa (p. 221-223, 297-304); FdV (p. 158-159); Perdições dos 7 clãs do Core (p. 67-105); Geração e Potência (p. 137, 214); Tipos de Predador (p. 176-179; Spider marcado como fora do Core); Laço de Sangue (p. 233-234); Ressonância e Discrasia (p. 227-231); Âncoras e Manchas (p. 239-240); torpor (p. 223, 241); diablerie (p. 234-235). Junto entraram as BAIXAS dos mesmos trechos (falha bestial, DD 7+, especialidade de Briga, Iron Gullet •••, Caitiff, decapitação, duração do turno, ordem do Core, fogo Agravado, empate no 12). No 12, a redução de DD no solo virou proposta pendente de aprovação.
- **Regras da casa (2026-11-15):** arquivo criado em `09_Preferencias/02_Regras_da_Casa.md`. RC-1 = XP por sessão 2-3 + bônus (substitui Core p. 130), aprovada pelo Eduardo. O agente guardião aponta para o arquivo.
- **Gravidade BAIXA corrigida (2026-11-15):** Morte Final só por fogo/sol em torpor, decapitação ou destruição do corpo (p. 223); garras sobrenaturais Agravadas (p. 126); cura de mortais por Vigor e Medicina (p. 127); compulsões dos 7 clãs do Core (p. 210-211); Blush dura a noite (p. 218); a Potência não fortalece o Laço, só limita o número de servos (p. 234); Loresheets com a lista do Core (p. 382-398): Montano, a Teia e High/Low Clan marcadas como fora do Core. Fora da 01_Sistema: frenesi corrigido em `10_Ferramentas_do_Narrador/01_Rolagens_Rapidas.md` e `04_Tabela_de_Fome.md` (Fome 5 não dá frenesi automático). A skill narrar passou a ler as regras da casa.
- **10_Ferramentas_do_Narrador conferida (2026-11-15):**
  - DDs dos guias e tabelas: 01 e 05 usavam uma escala 1 ponto acima da do Core (DD 2 = "rotineiro"). Desceram 1 ponto, mantendo os exemplos de cada nível (p. 119).
  - Caça pela tabela de território (p. 307-308).
  - Paradas de combate e estaca (p. 125, 221, 300-302).
  - "Percepção", que não é atributo do V5, virou Raciocínio + Prontidão/Intuição.
  - Rouse e alimentação pelas p. 212-219; não há Rouse por cena para manter Disciplina.
  - Discrasia e frenesi de terror em 03.
  - O 02_Gerador cabe nos limites da p. 214.
- **Pendência do Edward resolvida (2026-11-15):** o Eduardo decidiu seguir o Core. A ficha no `vtm-campanhas` passou para Surto +2, Perdição 2, humano sacia 1 a menos, sem exigência de drenar. Também foram corrigidos a Perdição Ventrue (gasta FdV, p. 102) e a parada de frenesi (8 dados, p. 219), e `contexto.md` e `direcao.md` foram alinhados.
- **Aceites 2 e 3 (2026-11-15):**
  - **Aceite 2 ok.** "quero jogar VtM" dispara `vtm:narrar`, e "continuar a sessão de ontem" não dispara.
  - **Aceite 3 ok.** Com o plugin instalado, as 6 chaves chegam substituídas na skill; `python` e `mostrar_dados` foram gravados via `claude plugin configure --values-stdin`. Com `--plugin-dir`, nenhuma chave é substituída, então esse modo não serve para o aceite 3.
  - **Cuidado:** `--allowedTools` não impede edições, porque as permissões da sessão já as liberam. O primeiro teste gravou na campanha, e as edições foram revertidas. O script `_retomada/teste_plugin.ps1` agora passa `--disallowedTools` para Edit, Write, PowerShell e Bash.
  - **Aceite 5:** coberto pelo teste negativo em pasta neutra ("continuar a sessão de ontem" não disparou a skill). O teste com cwd em `C:\Cowork` não foi rodado de propósito: o SessionStart ali injeta dados de clientes na saída do teste (LGPD).
  - Pendente: o erro TIMELINE do auditor no Edward (sessões 8-15 sem registro na linha do tempo; é tarefa da migração da campanha).
- **Loresheets (2026-11-15):** níveis de Helena (p. 391), Tyler (p. 397), Golconda 1-5 (p. 389) e Week of Nightmares (p. 395) conferidos e parafraseados.
- **Pendente:** `10_Ferramentas_do_Narrador/01_Rolagens_Rapidas.md:172-177` ainda usa a parada antiga do frenesi; conferir o resultado da segunda rodada de OCR (os processos já terminaram); aceite 2 (disparo automático por "quero jogar VtM", ainda não testado); `python` e `mostrar_dados` sem valor gravado no `userConfig` (chegam literais na skill; o fallback cobre); pedir ao suporte do GitHub a limpeza dos commits antigos em cache (cabe ao Eduardo).
