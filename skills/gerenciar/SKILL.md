---
description: "Gestão entre sessões de uma campanha solo de Vampiro: A Máscara V5 (VtM): revisar a crônica, objetivos do personagem vampiro, arcos narrativos, agenda dos NPCs da campanha. Usar só quando o pedido mencionar VtM, vampiro ou a campanha de RPG; não usar para planejamento, objetivos ou trackers de trabalho."
model: opus
---

# VtM Gerenciar — Gestão Macro da Campanha

Skill de gestão entre sessões para VtM V5 solo em Português BR.

## Responsabilidade

Gestão macro: rastrear objetivos em 4 níveis, avançar agendas de NPCs, manter arcos narrativos, revisar saúde da campanha, planejar próximos passos.

## Caminhos

| Recurso | Caminho |
|---------|---------|
| Base VtM | `${CLAUDE_PLUGIN_ROOT}` (só leitura: referências, templates, scripts) |
| Jogos | `${user_config.pasta_campanhas}` |
| Campanha ativa | `${user_config.campanha_ativa}` (o jogo que o jogador nomear vale por cima; vazio e várias campanhas = perguntar qual e passar o nome em `campanha` nas ferramentas de dados) |
| PDFs integrais | `${user_config.pasta_acervo}` (opcional) |
| Livros (busca) | Ferramenta MCP `buscar_acervo` ou agente `guardiao-regras`: índice local dos PDFs com livro + página. CLI: `python "${CLAUDE_PLUGIN_ROOT}/scripts/acervo.py" buscar "termo"`. Regra citada só com página. Sem acervo indexado, valem os arquivos `01_Sistema/` do plugin (ver "Configuração não preenchida"); sem fonte nenhuma, "não sei". Hierarquia P6: regras da casa > V5 Core > suplementos V5 > `01_Sistema`/resumos > edições antigas (só lore) |
| Resumos | `${user_config.pasta_resumos}` (opcional; visão geral, não fonte final) |

**Configuração não preenchida.** Se um valor acima aparecer vazio ou ainda como `${user_config...}` literal: Resumos = não usar; Jogos = perguntar ao jogador onde ficam as campanhas e sugerir configurar `pasta_campanhas` (comando `/plugin`, plugin `vtm`, configurar opções); **nunca gravar campanha dentro de `[Base]`**, que é a pasta de instalação do plugin e é substituída a cada atualização; Campanha ativa = perguntar se houver mais de uma; PDFs e acervo = opcionais; sem eles (ou se `buscar_acervo` disser que não há índice), a fonte de regra são os arquivos `[Base]/01_Sistema/`, `[Base]/03_Disciplinas/` (poderes, Rituais e Cerimônias) e `[Base]/10_Ferramentas_do_Narrador/`, conferidos com o V5 Core e os suplementos V5 e com a página ao lado, mais o motor de dados. Em `[Base]/02_Clas/`, `[Base]/04_Seitas_e_Politica/` e `[Base]/05_Cenario/`, cada arquivo termina com a seção "Conferência do Lore", que diz ponto a ponto o que é **V5** (com página), o que é **Antigo** (edições anteriores), o que é **Sem fonte** (texto de fã) e o que é **História real**. Tratar como fato do jogo só o que está marcado V5; o resto serve de ambientação, com aviso ao jogador quando uma decisão depender dele. O que não estiver lá: dizer "não sei" ou propor ao jogador como regra da casa, sem inventar.

## Arcos visíveis — `arcos.md`

Mapa **público** da campanha, na raiz do jogo (modelo: `[Base]/08_Templates/08_arcos.md`). Uma seção por nível ativo (Partida, História, Aventura), sempre com: **Objetivo**, **Fecha quando**, **Sessões** (previstas · jogadas) e **Ponto atual**, uma frase cada. A Aventura tem também **Falta para fechar**.

- Só entra o que o personagem sabe. Segredo e plano ficam em `direcao.md`.
- Atualizar no fim de cada sessão. Nível fechado vira uma linha em "Concluídos".
- É daqui que sai a abertura da sessão em 3 linhas (skill `narrar`). Se o jogador perguntar "onde estamos?", a resposta é este arquivo.

## Orçamento de aventura

- Toda aventura nasce com **1 a 3 sessões previstas** e um **"fecha quando"** escrito.
- Na **3ª sessão**, propor um fecho ao jogador: o clímax nesta sessão, ou um corte (a aventura termina como está e o que sobrou vira objetivo da próxima).
- Passou de 3: não seguir sem o jogador escolher entre fechar agora ou dividir em duas aventuras, cada uma com seu ponto de chegada.
- História: prever o número de aventuras (em geral 2 a 4). Partida: prever o número de histórias.

## Objetivos — `objetivos.md` enxuto

Modelo: `[Base]/08_Templates/09_objetivos.md`.

- Só objetivos **ativos**, no máximo **8** ao todo, agrupados por nível (Jogo, Partida, História, Aventura).
- Uma linha cada, com identificador em ordem dentro do nível: J1, P1, H1, A1. Secundário leva "(secundário)". Não reaproveitar número.
- Concluído ou abandonado sai do arquivo e vira uma linha em `objetivos_arquivo.md` (modelo `10_objetivos_arquivo.md`), com sessão e desfecho.
- Atualizar no fim de cada sessão, com o jogador. Passou de 8: fechar, fundir ou arquivar antes de criar outro.

## Notas secretas — `direcao.md` em tópicos

Modelo: `[Base]/08_Templates/11_direcao.md`. Quatro seções fixas, nesta ordem: **Arco**, **Próxima cena**, **Ganchos**, **Decisões em aberto**.

- Só tópicos de uma linha (até 25 palavras). Texto corrido é proibido.
- "Próxima cena" sempre declara **objetivo, obstáculo e risco**. Sem os três, não é cena: vira transição de uma linha na narração.
- Cada gancho leva a sessão em que foi plantado e o prazo para ser cobrado. O que foi revelado ou perdeu a validade é apagado.

## Revisão Entre Sessões

Quando o jogador pedir "revisar campanha" ou "entre sessões":

### 1. Status Geral

Ler e apresentar:
- Estado do PC: Fome, FdV, Saúde, Humanidade, XP
- Localização e situação atual
- Onde estamos em `arcos.md` (Partida > História > Aventura) e quantas sessões a aventura já tem
- Objetivos ativos por nível
- Ameaças pendentes

### 2. Avanço de Agendas de NPCs

Para cada NPC Maior e Médio com agenda ativa:
- O que o NPC fez "off-screen" desde a última sessão?
- Como suas ações afetam o cenário?
- Mudanças de atitude baseadas em eventos?

Regras:
- NPCs agem conforme motivações documentadas
- Ações off-screen devem ser plausíveis e proporcionais
- Registrar mudanças nas fichas de NPCs
- Apresentar ao jogador como rumores, notícias, ou consequências visíveis

### 3. Passagem de Tempo

Se tempo passou entre sessões (no jogo):
- Despertares e alimentações das noites: ferramenta `montagem`, com o plano aprovado pelo jogador
- Eventos do cenário (consultar `direcao.md`)
- Atualizar `timeline.md`

### 4. Manutenção Narrativa

Verificar:
- Arcos pendentes sem resolução
- Pistas esquecidas que precisam ser retomadas
- NPCs "abandonados" que deveriam reagir
- Consequências de decisões passadas que devem se manifestar
- Ramificações em `ramificacoes.md` que precisam de follow-up

### 5. Planejamento

Propor ao jogador:
- Próxima cena/aventura lógica baseada no estado atual
- Oportunidades narrativas baseadas nas ramificações
- Ganchos para novas histórias ou quests secundárias

Apresentar em opções com ganho e risco no texto e rótulos curtos no seletor.

## Saúde da Campanha

Checklist de saúde narrativa:

| Item | Verificação |
|------|------------|
| Ritmo | A aventura atual cabe em 1 a 3 sessões? Tem "fecha quando"? |
| Variedade | Alternando intriga, ação, horror, investigação? |
| Stakes | As decisões têm peso? As consequências são sentidas? |
| NPCs | Estão vivos? Têm agendas próprias? Reagem ao PC? |
| Objetivos | `arcos.md` em dia? No máximo 8 objetivos ativos? |
| Mundo | O cenário reage? Eventos externos ocorrem? |
| Personagem | O PC está evoluindo? Humanidade em tensão? |
| Documentação | Tudo registrado? Sem contradições? |

Se algum item está fraco → propor ações corretivas.

## Manutenção de Documentação

1. **Auditoria mecânica** (só leitura):
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/campanha.py" auditar "<pasta da campanha>"
   ```
   (ou a ferramenta MCP `auditar_campanha`, com `campanha` = nome da pasta do jogo). Aponta: `estado.json` ausente ou inválido; número divergente entre `estado.json` e os `.md` (ou entre `contexto.md` e `personagem.md` sem estado); número repetido nos `.md` (pela P8 fica só no `estado.json`); Potência declarada x tabela do Core p. 216; sessões fora da `timeline.md`; rodapés "atualizado em" defasados; NPCs nas relações sem ficha; fichas fora do `indice.md`; `arcos.md` ausente ou com campo vazio; aventura na 3ª sessão ou além dela; mais de 8 objetivos ativos ou concluídos ainda em `objetivos.md`; `direcao.md` sem os tópicos fixos ou com texto corrido; Fome divergente em `rolagens.jsonl`; português de Portugal ou latim sem tradução nos logs de sessão; decisões do narrador ainda pendentes.
2. **Continuidade narrativa:** pedir ao agente `continuidade` as contradições entre sessões, fichas, linha do tempo e `direcao.md`.
3. Conferir também:
   - `relacoes.md` reflete interações recentes?
   - `arcos.md` e `objetivos.md` batem com o que aconteceu na última sessão?

Corrigir as discrepâncias e rodar a auditoria de novo até voltar sem erros. Números do personagem vão para o `estado.json`, não para os `.md`.

## Regras Universais

1. **Autoridade do jogador (warn + obey):** se pedir mudanças drásticas na campanha → alertar. Se confirmar → executar.
2. **Anti-alucinação:** NPCs off-screen agem conforme fichas. Eventos conforme lore.
3. **Transparência narrativa:** mostrar ao jogador o que o PC saberia. Ocultar segredos do narrador.
4. **Consulta a livros:** ao planejar arcos envolvendo lore oficial, consultar PDFs integrais.
5. **Documentação completa:** toda mudança registrada nos arquivos corretos.
