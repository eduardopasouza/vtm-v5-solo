# Solo Play — Adaptacoes para Jogo com IA como Narrador — VtM V5

> Regras caseiras e orientacoes para jogar VtM V5 em formato solo, com inteligencia artificial atuando como Narrador.

---

## Visao Geral

Jogar VtM V5 solo com uma IA como Narrador e uma experiencia diferente do RPG de mesa tradicional. A IA assume todos os NPCs, descreve o ambiente, arbitra regras e gera consequencias. O jogador controla um unico personagem (PC) e toma todas as decisoes.

Este documento estabelece adaptacoes e house rules para tornar essa experiencia fluida, desafiadora e narrativamente satisfatoria.

---

## Principios do Solo Play com IA

### O Que Funciona Bem
1. **Investigacao e exploracao:** A IA pode criar misterios complexos e revelar pistas gradualmente
2. **Introspeccao do personagem:** Sem outros jogadores, ha espaco para aprofundar a psicologia do PC
3. **Politica vampirica:** Intrigas, aliancas e traicoes funcionam excelentemente em solo
4. **Horror pessoal:** O foco no horror individual e a alma do V5, e solo play amplifica isso

### O Que Requer Adaptacao
1. **Combate:** Sem party, combate pode ser letal demais — precisa de ajustes
2. **Cenas sociais complexas:** Multiplos NPCs interagindo simultaneamente exige atencao do Narrador-IA
3. **Downtime:** Sem sessao fixa, o tempo entre aventuras precisa de estrutura
4. **Rolagens:** O sistema de dados precisa ser integrado de forma que nao quebre o fluxo narrativo

---

## Adaptacao de Cenas Sociais

### NPCs com Fidelidade a Fichas

Cada NPC significativo deve ter uma ficha simplificada que a IA consulta para manter consistencia:

**Ficha Rapida de NPC:**
```
Nome: [nome]
Cla: [cla] | Geracao: [geracao] | Potencia: [potencia]
Conceito: [uma frase]
Natureza: [verdadeira personalidade]
Comportamento: [como se apresenta]
Atributos-chave: [Fisico X / Social Y / Mental Z]
Disciplinas: [lista com niveis]
Forca de Vontade: [valor]
Humanidade: [valor]
Motivacao: [o que quer]
Segredo: [o que esconde]
Relacao com PC: [aliado/neutro/adversario + razao]
```

### Regras para Interacao Social com IA

1. **Consistencia:** O NPC deve reagir de acordo com sua ficha, nao de acordo com o que seria "mais divertido"
2. **Teste antes de sucesso:** Se o PC tenta persuadir, intimidar ou manipular, a IA deve pedir a rolagem ANTES de narrar o resultado
3. **NPCs podem recusar:** Nem toda tentativa social deve funcionar — NPCs tem agencia
4. **Multiplos NPCs:** Em cenas com 3+ NPCs, a IA deve declarar a posicao de cada um separadamente
5. **Reacoes em camadas:** NPCs podem concordar externamente mas plotar internamente — a IA deve rastrear ambos

### Presenca e Dominacao Usados pelo PC em NPCs

Quando o PC usa Disciplinas sociais contra NPCs:

**Presenca:**
- **Fascinio (Awe):** A IA descreve a reacao do NPC de forma gradual — interesse, fixacao, deferencia
- **Majestade (Majesty):** O NPC e completamente dominado enquanto o poder esta ativo. A IA deve narrar a submissao de forma crivel
- **Pos-efeito:** Quando Presenca termina, a IA deve narrar a reacao do NPC ao perceber que foi manipulado (raiva, confusao, medo)

**Dominacao:**
- **Comando (Compel):** A IA executa o comando literalmente — NPCs sob Dominacao nao interpretam, obedecem
- **Mesmerize:** A IA narra o NPC agindo conforme as instrucoes implantadas, mas pode inserir falhas se as instrucoes forem vagas
- **Pos-efeito:** O NPC nao lembra do comando, mas pode notar "buracos" na memoria

**Regra de ouro:** A IA nao deve tornar Disciplinas sociais "faceis demais" — resista a tentacao de fazer todo NPC ceder. Use as regras: NPCs com Forca de Vontade alta ou Disciplinas mentais proprias podem resistir. Ancioes sao quase imunes a Dominacao de neonatos.

---

## Combate Simplificado

### Problema do Combate Solo
Em grupo, combate e distribuido entre varios PCs. Solo, o PC enfrenta todos os inimigos sozinho. Isso e potencialmente letal e mecanicamente lento.

### Resolucao em Rounds Narrativos

**Substituir iniciativa complexa por:**
1. O PC declara intencao
2. A IA declara intencao dos oponentes
3. Rolagem unica por round: Pool do PC vs. Pool do oponente (teste contestado)
4. Margem de sucesso = dano infligido ou efeito alcancado
5. Empate = ambos se ferem ou ninguem avanca

### Escala de Oponentes Solo

| Categoria | Pool | Saude | Exemplo |
|-----------|------|-------|---------|
| Minion (descartavel) | 3-4 dados | 3-4 | Ladroes, guardas, transeuntes |
| Competente | 5-7 dados | 5-6 | Policial treinado, capanga profissional |
| Perigoso | 8-10 dados | 7-8 | Soldado de elite, vampiro neonato |
| Formidavel | 11-13 dados | 9-10 | Ancillae, lobisomem jovem |
| Letal | 14+ dados | 11+ | Anciao, lobisomem adulto, cacador da SI |

### Regra dos Minions Agrupados

Quando o PC enfrenta multiplos oponentes fracos, agrupe-os:
- **2-3 minions:** Tratados como um unico oponente Competente (+2 dados, +2 saude)
- **4-6 minions:** Tratados como um unico oponente Perigoso (+4 dados, +3 saude)
- **7+ minions:** Tratados como um unico oponente Formidavel (+6 dados, +4 saude)

Quando o "grupo" sofre dano suficiente, membros individuais sao eliminados narrativamente.

### Dicas de Combate Solo
- **Fuga e valida:** O PC nao precisa vencer toda luta — fugir e muitas vezes a melhor opcao
- **Ambiente como arma:** Descreva como o PC usa o ambiente (escuridao, altura, multidoes) a seu favor
- **Disciplinas sao essenciais:** Solo, o PC depende muito mais de Disciplinas do que de dados brutos
- **Limite combates:** 2-3 rounds narrativos por cena de combate. Se nao resolveu, escale ou mude a abordagem

---

## Investigacao Solo

### Problema
Sem outros jogadores para "brainstormar", o PC pode ficar preso em investigacoes.

### Sistema de Pistas Graduais

A IA deve fornecer pistas em tres camadas:

1. **Pista Obvia (DD 2-3):** Informacao que o PC obtem automaticamente ou com rolagem facil. Direciona para o proximo passo.
2. **Pista Escondida (DD 4-5):** Requer esforco — pesquisa, interrogatorio, investigacao ativa. Fornece contexto adicional.
3. **Pista Secreta (DD 6+):** Informacao crucial que muda a compreensao do misterio. Requer habilidade excepcional ou metodo criativo.

### Regra do "Nunca Trave"
Se o PC falha em encontrar a pista necessaria para avancar:
- **1a falha:** A IA oferece uma rota alternativa ("Voce nao encontrou nada aqui, mas lembra que [NPC] mencionou...")
- **2a falha:** A IA apresenta a pista de forma diferente ("Um bilhete cai de dentro de um livro quando voce o derruba acidentalmente...")
- **3a falha:** A IA fornece a pista diretamente ("Apos horas de busca, voce finalmente nota...")

**O jogo nao deve parar porque uma rolagem falhou.** Falhas devem criar complicacoes, nao becos sem saida.

### Auspicios como Ferramenta de Investigacao
- **Sentidos Aguçados (Heightened Senses):** Bonus automatico (+2 dados) em qualquer investigacao sensorial
- **Premonição (Premonition):** A IA pode oferecer "flashes" de informacao via visoes
- **Toque do Espirito (Spirit's Touch):** Psicometria — tocar objetos revela fragmentos do passado
- **Telepatia (Telepathy):** Permite "ler" NPCs suspeitos diretamente

---

## Downtime Entre Sessoes

### Atividades de Downtime

Entre sessoes/cenas principais, o PC pode realizar atividades de downtime:

| Atividade | Duracao | Rolagem | Resultado |
|-----------|---------|---------|-----------|
| Alimentacao | 1 noite | Manipulacao + Manha (DD 3-5) | Reduz Fome |
| Patrulha de Territorio | 1-3 noites | Percepcao + Manha (DD 3) | Detecta intrusos/mudancas |
| Pesquisa | 1-7 noites | Inteligencia + Academicos (DD variavel) | Obtem informacao |
| Treino | 2-4 semanas | Variavel | Justifica gasto de XP |
| Projeto Pessoal | Variavel | Variavel | Avanca objetivo do PC |
| Networking | 1-3 noites | Carisma + Etiqueta (DD 3-4) | Fortalece Contatos/Aliados |
| Vigilia | 1 noite | Percepcao + Investigacao (DD variavel) | Observa alvo sem ser detectado |
| Manutenção de Havens | 1-2 noites | Inteligencia + Tecnologia (DD 2-3) | Garante seguranca do refúgio |

### Projetos de Longo Prazo

Para objetivos maiores, use sistema de Projeto:
1. **Definir objetivo:** "Quero descobrir quem destruiu meu Sire"
2. **Definir etapas:** A IA divide em 3-5 etapas menores
3. **Cada etapa = 1 rolagem de downtime** com DD crescente
4. **Falhas:** Complicacoes, nao cancelamento. Cada falha adiciona uma etapa extra
5. **Conclusao:** Apos todas as etapas, o objetivo e alcancado com consequencias baseadas em sucessos/falhas acumulados

---

## Aliados e Retainers como "Party Members Lite"

### O Problema da Solidao Mecanica
Solo, o PC nao tem backup. Aliados e Retainers podem preencher esse vazio.

### Retainers (Servidores)

Retainers sao mortais ou ghouls a servico do PC. Em solo play, funcionam como "party members lite":

**Ficha Simplificada de Retainer:**
```
Nome: [nome]
Funcao: [guarda-costas / informante / assistente / ghoul de combate]
Pool Principal: [X dados] (para sua funcao primaria)
Pool Secundaria: [Y dados] (para tudo mais)
Saude: [3-5 caixas]
Lealdade: [1-5] (quao confiavel e)
Peculiaridade: [um traco de personalidade marcante]
```

### Regras para Retainers em Cena
1. **Acoes automaticas:** Retainers agem conforme ordens sem rolagem para tarefas simples
2. **Acoes arriscadas:** Rolagem com a Pool do Retainer, nao do PC
3. **Combate:** Retainers podem absorver 1 ataque que seria direcionado ao PC (escudo humano)
4. **Lealdade:** Em situacoes de estresse, rolar Lealdade (DD 3-5) para ver se obedecem
5. **Morte:** Retainers morrem facilmente. A IA nao deve protege-los — sua mortalidade e dramatica

### Aliados vs. Retainers
- **Aliados:** NPCs iguais ou superiores ao PC que ajudam por interesse proprio. Nao obedecem ordens — negociam
- **Retainers:** Subordinados que obedecem (geralmente). Menos poderosos, mais confiaveis

---

## Escala de Dificuldade para Solo

### DDs Ajustados

Em jogo de grupo, DDs altos sao mitigados por multiplos PCs tentando. Solo, o PC e o unico a rolar. Considere reduzir DDs em 1 para compensar:

| Situacao | DD Grupo | DD Solo |
|---------|---------|---------|
| Tarefa rotineira | 2 | 2 (sem mudanca) |
| Tarefa simples | 3 | 2-3 |
| Tarefa moderada | 4 | 3-4 |
| Tarefa desafiadora | 5 | 4-5 |
| Tarefa dificil | 6 | 5 |
| Tarefa extrema | 7+ | 6 |

**Alternativa:** Em vez de reduzir DD, permita que o PC use mais frequentemente:
- Teamwork bonus de Retainers (+1 a +2 dados)
- Surto de Sangue sem penalidade extra
- Forca de Vontade para re-rolar

---

## Regras de Alimentacao Solo

### Hunting Rolls Simplificados

Em vez de cenas completas de caca toda vez:

**Rolagem Rapida de Caca:**
- Pool: Atributo relevante + Habilidade relevante (baseado no Tipo de Predador)
- DD: Baseado no local e horario

| Local | DD | Ressonancia Provavel |
|-------|-----|---------------------|
| Area movimentada (centro, festas) | 2 | Sanguineo |
| Area residencial (casas, suburbio) | 3 | Fleumatico |
| Area perigosa (becos, docas) | 3 | Colerico |
| Area desolada (campo, floresta) | 4 | Melancolico |
| Area protegida (hospital, igreja) | 5 | Variavel |
| Territorio de outro vampiro | 5+ | Variavel + risco |

### Resultados da Caca

| Resultado | Efeito |
|-----------|--------|
| Sucesso critico | Fome reduz em 3 + Ressonancia Intensa |
| Sucesso com margem 3+ | Fome reduz em 2 + Ressonancia Fugaz |
| Sucesso simples | Fome reduz em 1 + Ressonancia Fugaz |
| Falha | Fome nao reduz, perde tempo |
| Falha critica / Bestial | Complicacao: testemunha, vitima resiste, territorio invadido, policia |

### Quando Narrar a Caca Completa
Nem toda caca precisa ser "jogada". Use rolagem rapida para alimentacao rotineira e narre apenas quando:
- O PC esta em territorio desconhecido
- Ha risco especifico (inimigos por perto, Fome 4+)
- O jogador quer explorar a cena
- A Ressonancia buscada e especifica (Dyscrasia, tipo raro)

---

## Dicas Gerais para Solo Play com IA

### Para o Jogador
1. **Escreva uma ficha detalhada** — quanto mais a IA souber sobre seu PC, melhor a narrativa
2. **Defina Touchstones claras** — a IA precisa de ancoras emocionais para gerar drama
3. **Nao tenha medo de falhar** — falhas geram historias melhores que sucessos
4. **Peca detalhes** — se a IA estiver sendo vaga, peca descricoes mais detalhadas
5. **Desafie a IA** — se algo parece facil demais, diga que quer mais desafio

### Para o Narrador-IA
1. **Mantenha fichas de NPCs** consistentes entre sessoes
2. **Nao proteja o PC** — deixe as consequencias das decisoes serem reais
3. **Use as regras** — V5 foi desenhado para gerar drama. Fome, Compulsoes, Frenesi sao ferramentas narrativas
4. **Surpreenda** — nem tudo deve ser previsivel. NPCs mudam de opiniao, traem, surpreendem
5. **Respeite o tom** — VtM e horror pessoal, nao fantasia heroica. Mantenha o peso

### Sessao Zero Solo
Antes de comecar, estabeleca com a IA:
1. Tom desejado (horror, intriga, acao, mistura)
2. Limites do jogador (temas a evitar)
3. Frequencia de combate (raro, moderado, frequente)
4. Nivel de agencia dos NPCs (submissos, independentes, antagonicos)
5. Uso de dados (rigoroso, moderado, narrativo)

---

*Referencia compilada para VtM V5 — Guerreiro Advogados Associados / Eduardo Souza*
