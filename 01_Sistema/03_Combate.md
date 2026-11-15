# Combate - Vampire: The Masquerade 5th Edition

## Sistema Completo de Combate

---

## 1. Visao Geral

O combate no V5 e projetado para ser **rapido, letal e narrativo**. Diferente de edicoes anteriores, nao ha mapa com grid ou contagem precisa de metros. O foco esta na ficcao, com a mecanica servindo para resolver conflitos de forma tensa e cinematografica.

---

## 2. Estrutura do Turno de Combate

Cada turno de combate (chamado de **round**) representa aproximadamente **3 segundos** de acao no mundo do jogo.

### Sequencia

1. **Declaracao de Intencoes:** Todos os participantes declaram o que pretendem fazer.
2. **Iniciativa:** Determina a ordem de resolucao.
3. **Resolucao:** Cada acao e resolvida na ordem de iniciativa.
4. **Fim do Turno:** Efeitos de duracao, verificacoes de Frenesi, etc.

---

## 3. Iniciativa

O V5 utiliza um sistema simplificado de iniciativa.

### Metodo Padrao

- Todos declaram suas acoes.
- O Narrador determina a ordem com base na **situacao narrativa**.
- Em geral: ataques a distancia resolvem antes de corpo a corpo; acoes defensivas antes de ofensivas.

### Metodo Opcional (Rolagem)

- Cada participante rola **Compostura + Consciencia (Awareness)**.
- Maior resultado age primeiro.
- Empates: Destreza mais alta age primeiro; se ainda empatado, acoes sao simultaneas.

### Surpresa

- Se um lado surpreende o outro, o lado surpreso **nao age no primeiro turno**.
- Emboscadas geralmente concedem +2 dados ao ataque inicial.
- Para detectar uma emboscada: **Raciocinio + Consciencia** vs **Destreza + Furtividade** do atacante.

---

## 4. Acoes em Combate

Cada personagem tem **uma acao principal** por turno. Acoes menores (falar, sacar arma ja pronta, mover-se brevemente) sao gratuitas a criterio do Narrador.

### Acoes Principais

| Acao | Parada de Dados |
|---|---|
| Ataque corpo a corpo | Forca + Briga (desarmado) ou Destreza + Armas Brancas (armado) |
| Ataque a distancia | Compostura + Armas de Fogo |
| Esquiva | Destreza + Atletismo |
| Usar Disciplina | Varia conforme a Disciplina |
| Agarrar/Imobilizar | Forca + Briga (oposto) |
| Desarmar | Destreza + Armas Brancas ou Briga (oposto) |
| Fugir | Destreza + Atletismo (oposto pelo adversario) |
| Proteger alguem | Vigor + Briga (absorve dano destinado a outro) |

### Mover-se

- Movimento curto (poucos metros): gratuito.
- Correr ou mover-se significativamente: requer Destreza + Atletismo e geralmente consome a acao.

---

## 5. Combate Corpo a Corpo (Close Combat)

### Ataque Desarmado

- **Parada:** Forca + Briga
- **Dano:** a margem de sucesso, em dano **Superficial** (a Forca nao soma ao dano)
- **Contra:** Teste oposto vs Forca + Briga (contra-ataque) ou Destreza + Atletismo (esquiva)

### Ataque com Arma Branca

- **Parada:** Destreza + Armas Brancas (ou Forca + Armas Brancas para armas pesadas)
- **Dano:** margem de sucesso + valor da arma (Forca nao entra)
- **Tipo de dano:** Geralmente **Superficial** contra vampiros; veja excecoes

### Resolucao

1. Atacante e defensor fazem testes opostos.
2. O vencedor aplica a **margem de sucesso** como dano.
3. Dano total = **Margem de sucesso + valor da arma** (se usou arma) (Core p. 126, 304)
4. Defensor aplica dano ao tracker de Saude (Superficial dividido por 2, para cima).

### Esquiva vs Contra-ataque

- **Esquiva (Destreza + Atletismo):** Nao causa dano, mas pode ser usada contra qualquer ataque.
- **Contra-ataque (Forca + Briga ou Destreza + Armas Brancas):** Se o defensor vencer, a margem se torna dano contra o atacante.

---

## 6. Combate a Distancia (Ranged Combat)

### Ataque a Distancia

- **Parada:** Compostura + Armas de Fogo
- **Dano:** margem de sucesso + valor da arma (veja tabela)
- **Contra:** Teste contestado contra a defesa do alvo, normalmente **Destreza + Atletismo** (Core p. 125, 301). Dois atiradores trocando tiros podem resolver como conflito de dois lados.

### Distancia

Nao ha tabela de DD por distancia. Atirar alem do **alcance efetivo** da arma custa **-2 dados** (Core p. 301).

### Cobertura

A cobertura modifica a **parada de defesa** do alvo, nao a do atirador (Core p. 125, 302):

| Cobertura do alvo | Modificador na defesa |
|---|---|
| Nenhuma | -2 dados |
| So ocultacao (arbustos, arvore fina contra fuzil) | -1 dado |
| Dura (bloco do motor de um carro, quina de concreto) | 0 |
| Trincheira (sacos de areia, bunker) | +1 dado |
| Seteira | +2 dados |

Alvo parado nao tem parada de defesa: o atirador rola contra DD fixa 1 (Core p. 302).

### Mirar

Gastar um turno inteiro mirando concede **+2 dados** no proximo ataque a distancia.

---

## 7. Dano

### Tipos de Dano

O V5 possui dois tipos de dano:

| Tipo | Simbolo | Descricao |
|---|---|---|
| **Superficial** | / | Contusoes, cortes leves, dor. Vampiros dividem dano Superficial por 2 (arredondando para cima). |
| **Agravado** | X | Ferimentos graves, dano sobrenatural. Nao e reduzido. Pode matar vampiros. |

### Conversao de Dano

- Quando o tracker de Saude esta cheio de dano Superficial (/) e o personagem recebe mais dano Superficial, **cada novo ponto de dano Superficial converte um Superficial (/) existente em Agravado (X)**.
- Isso simula a deterioracao progressiva — mesmo dano "leve" acumulado se torna letal.

### Tracker de Saude

O tracker tem caixas iguais ao **Vigor + 3** do personagem.

```
Exemplo (Vigor 3 = 6 caixas de Saude):
[ ][ ][ ][ ][ ][ ]   - Intacto
[/][/][ ][ ][ ][ ]   - 2 dano Superficial
[/][/][/][X][ ][ ]   - 3 Superficial, 1 Agravado
[X][X][X][X][X][X]   - Incapacitado (todo Agravado = Morte/Torpor Final)
```

### Incapacitacao

- **Mortais:** Quando todo o tracker esta preenchido com dano Agravado, o mortal morre.
- **Vampiros:** Quando todo o tracker esta preenchido com dano Agravado, o vampiro entra em **Torpor**. Se o dano Agravado exceder o total do tracker, o vampiro sofre **Morte Final**.

---

## 8. Dano Especifico contra Vampiros

Vampiros sao resistentes a maioria das formas de dano, mas possuem vulnerabilidades unicas.

### Resistencia Vampirica

- **Dano Superficial de fontes mundanas (socos, balas, facas):** Dividido por 2 (arredondando para cima).
- Apenas o dano Superficial de fontes mundanas e reduzido. Dano Agravado nunca e reduzido.

### Tabela de Dano por Fonte

| Fonte | Tipo contra Vampiros | Notas |
|---|---|---|
| Socos e chutes | Superficial (halved) | Dividido por 2 |
| Armas brancas | Superficial (halved) | Dividido por 2 |
| Armas de fogo | Superficial (halved) | Dividido por 2 |
| Garras sobrenaturais | Superficial (full) | Nao dividido |
| Estaca no coracao | Especial | Paralisa, nao mata (veja abaixo) |
| Fogo | **Agravado** | Causa panico e possivel Frenesi de Terror |
| Luz solar | **Agravado** | Dano por turno de exposicao |
| Dentes de vampiro | **Agravado** | Mordida em combate causa Agravado |
| Disciplinas ofensivas | Varia | Conforme a descricao do poder |
| Decapitacao | **Morte Final** | Automatico se bem-sucedido |
| Garras de Lobisomem | **Agravado** | Ignoram resistencia vampirica |

### Fogo

| Intensidade | Dano por Turno |
|---|---|
| Tocha, chama pequena | 1 Agravado |
| Fogueira | 2 Agravado |
| Incendio | 3 Agravado |
| Inferno | 4+ Agravado |

- Fogo causa **Frenesi de Terror** automaticamente (DD 3-5 dependendo da intensidade).
- Vampiro em chamas sofre o dano **no inicio de cada turno** ate apagar.

### Luz Solar

| Exposicao | Dano (Core p. 221) |
|---|---|
| Direta | Agravado igual a **Severidade da Perdicao**, por turno |
| Obscurecida (cortinas, dia muito nublado) ou corpo coberto (casaco, luvas, mascara, chapeu, oculos) | O mesmo dano, mas a cada dois turnos ou menos |
| Sangue Ralo, sol direto | 1 Superficial por turno |

- Causa Frenesi de Terror automatico.
- A Humanidade nao aumenta o dano solar. So **Humanidade 10** reduz o dano a metade (Core p. 236).

### Estaca no Coracao

- Requer um ataque direcionado com DD +2 ao teste normal.
- Parada: Destreza + Armas Brancas (ou Briga se empurrando a estaca a mao).
- Se o dano penetrar (apos reducao), o vampiro fica **paralisado** — consciente mas completamente imobilizado.
- Remover a estaca liberta o vampiro instantaneamente.
- Nao causa Morte Final por si so.

---

## 9. Armas

### Armas Corpo a Corpo

| Arma | Bonus de Dano | Tipo | Ocultavel | Notas |
|---|---|---|---|---|
| Punho (desarmado) | +0 | Superficial | — | Padrao |
| Soco-ingles | +1 | Superficial | Sim | — |
| Faca / Adaga | +1 | Superficial | Sim | Pode ser arremessada |
| Espada curta / Machete | +2 | Superficial | Nao | — |
| Espada longa / Katana | +3 | Superficial | Nao | — |
| Machado / Martelo grande | +4 | Superficial | Nao | Arma pesada, usa Forca |
| Bastao | +2 | Superficial | Nao | Alcance |
| Estaca de madeira | +1 | Superficial | Sim | Efeito especial contra vampiros |
| Motosserra | +3 | Superficial/Agravado | Nao | Potencial de decapitacao |

### Armas de Fogo

| Arma | Dano | Tipo | Ocultavel | Notas |
|---|---|---|---|---|
| Pistola leve (.22, .25) | +2 | Superficial | Sim | — |
| Pistola media (9mm) | +3 | Superficial | Sim | Mais comum |
| Pistola pesada (.44, .45) | +4 | Superficial | Dificil | Alto recuo |
| Escopeta (shotgun) | +4 | Superficial | Nao | Devastadora a curta distancia |
| Submetralhadora (SMG) | +3 | Superficial | Parcial | Rajada |
| Rifle | +4 | Superficial | Nao | Longo alcance |
| Rifle de precisao (sniper) | +5 | Superficial | Nao | Requer preparacao |

> **Nota contra vampiros:** Todo dano de armas de fogo e Superficial e dividido por 2.

### Rajada (Burst Fire)

- Armas automaticas podem disparar em rajada.
- +2 dados ao ataque, mas usa mais municao.
- Rajada completa: +3 dados, mas aplica penalidade na proxima acao.

---

## 10. Armadura

| Tipo (Core p. 304) | Valor |
|---|---|
| Roupa reforcada / couro pesado | 2 (zero contra balas) |
| Tecido balistico | 2 |
| Colete Kevlar / flak jacket | 4 |
| Armadura tatica SWAT/militar | 6 (-1 dado em rolagens de Destreza) |

- Cada ponto de armadura **converte 1 ponto de dano Agravado de perfuracao ou corte em Superficial** (por rolagem de dano), que depois e dividido como sempre (Core p. 304).
- Armadura **nao reduz** dano Superficial.
- Por isso, serve quase so a mortais e Sangue Ralo: para vampiros, balas e laminas ja causam Superficial.

---

## 11. Agarrar e Imobilizar (Grappling)

### Iniciar Agarramento

- **Teste:** Forca + Briga (oposto pelo defensor com Forca + Briga ou Destreza + Atletismo).
- Se bem-sucedido, o atacante agarra o defensor.

### Acoes durante Agarramento

O personagem que controla o agarramento pode, em turnos subsequentes:

| Acao | Efeito |
|---|---|
| Manter | Mantem o alvo preso, nenhum dos dois age ofensivamente |
| Causar dano | Forca em dano Superficial por turno (esmagamento) |
| Morder | Forca + Briga para morder: dano **Agravado** + possivel alimentacao |
| Imobilizar | Testes adicionais para render completamente |
| Usar como escudo | Alvo absorve ataques de terceiros |
| Arremessar | Joga o alvo; causa dano de queda |

### Escapar

- O personagem preso usa **Forca + Briga** (oposto) como sua acao para tentar escapar.
- Se bem-sucedido, liberta-se e pode agir normalmente no proximo turno.

---

## 12. Multiplos Oponentes

### Enfrentando Varios Inimigos

- O personagem deve dividir sua parada de dados entre os alvos **ou** focar em um e ficar vulneravel aos demais.
- Cada atacante adicional alem do primeiro concede **-1 dado** a defesa do alvo contra todos os ataques.
- Se cercado por 3 oponentes: -2 dados para se defender de cada ataque.

### Limite

- A penalidade maxima por multiplos oponentes e geralmente **-5 dados** (Narrador pode ajustar).
- Disciplinas como Celeridade podem ajudar a lidar com multiplos inimigos.

---

## 13. Dano a Forca de Vontade

Alem de Saude, personagens possuem um tracker de **Forca de Vontade** (Compostura + Determinacao caixas).

### Como Funciona

- Certos efeitos (Dominacao, derrotas sociais, Falhas Bestiais) causam dano ao tracker de FdV.
- Dano Superficial a FdV: marcado com /. Recupera ao agir de acordo com Conviccoes/Ancoras.
- Dano Agravado a FdV: marcado com X. Recupera mais lentamente (1 por noite de descanso ou cena significativa).
- Se o tracker de FdV estiver **completamente preenchido**, o personagem sofre uma **quebra mental** — incapaz de agir efetivamente, vulneravel a coercao, ou entra em catatonia.

---

## 14. Cura (Mending)

### Vampiros

- Gastar um **Rouse Check** permite curar dano Superficial igual ao valor de **Mend Amount** da Potencia do Sangue.

| Potencia do Sangue | Mend Amount por Rouse Check |
|---|---|
| 0 | 1 Superficial |
| 1 | 1 Superficial |
| 2 | 2 Superficial |
| 3 | 2 Superficial |
| 4 | 3 Superficial |
| 5 | 3 Superficial |

- **Dano Agravado** cura muito mais lentamente: ao anoitecer, 3 Rouse Checks (alem do Rouse de despertar) curam 1 ponto; no maximo 1 ponto por noite (Core p. 218-219).
- **Curar em combate:** Pode gastar um Rouse Check como acao para curar dano Superficial.

### Mortais

- Mortais curam naturalmente ao longo de dias/semanas (Narrador determina).
- Primeiros socorros (Inteligencia + Medicina) podem curar 1-2 pontos de dano Superficial imediatamente.

---

## 15. Frenesi em Combate

### Gatilhos de Frenesi

| Tipo | Gatilho | Efeito |
|---|---|---|
| Frenesi de Furia | Ser provocado, humilhado, ferido gravemente | Ataca a fonte da raiva com violencia descontrolada |
| Frenesi de Fome | Sentir sangue fresco, Fome alta | Ataca a fonte de sangue mais proxima |
| Frenesi de Terror (Rotschreck) | Fogo, luz solar | Foge descontroladamente, destruindo tudo no caminho |

### Resistir ao Frenesi

- **Teste:** Forca de Vontade **atual** (caixas sem dano) + Humanidade ÷ 3 (para baixo) vs DD definida pelo Narrador (Core p. 219). Vitoria = resiste, mas gasta o turno; critico = resiste sem perder o turno.

| Situacao | DD |
|---|---|
| Provocacao leve | 2 |
| Ameaca moderada | 3 |
| Perigo grave | 4 |
| Exposicao direta a fogo/sol | 4-5 |
| Fome 5 + cheiro de sangue | 5 |

### Efeitos do Frenesi

- O personagem perde o controle — o **Narrador** controla suas acoes.
- Em Frenesi de Furia: ataca com brutalidade maxima, sem se defender, ignorando ferimentos.
- Em Frenesi de Fome: agarra a vitima mais proxima e drena sangue.
- Em Frenesi de Terror: foge em panico, usando todas as capacidades para escapar (inclusive Disciplinas).
- O Frenesi termina quando a fonte e eliminada, o perigo passa, ou o vampiro e fisicamente contido.

### Cavalgando a Onda (Riding the Wave)

Em vez de resistir, o vampiro pode **ceder de proposito** ao Frenesi, **sem teste** (Core p. 219-220).

- Valem as regras normais do Frenesi.
- O jogador conduz o proprio Frenesi (escolhe alvos, de quem se alimenta primeiro), em vez de o Narrador assumir o personagem.

---

## 16. Manobras Especiais

### Ataques Direcionados

Mirar em uma parte especifica do corpo:

| Alvo | Penalidade | Efeito Especial |
|---|---|---|
| Cabeca | +2 DD | +1 dano |
| Mao / Arma | +2 DD | Possivel desarme |
| Pernas | +1 DD | Reduz mobilidade |
| Coracao (estaca) | +2 DD | Paralisia vampirica |
| Olhos | +3 DD | Cegueira temporaria |

### Desarme

- **Teste:** Destreza + Armas Brancas ou Briga (oposto).
- Se bem-sucedido, a arma do oponente cai ou e tomada.
- Margem de 3+ permite pegar a arma para si.

### Empurrar / Derrubar

- **Teste:** Forca + Briga (oposto).
- Se bem-sucedido, alvo e empurrado ou derrubado.
- Alvo derrubado: -2 dados em defesa ate levantar (gastar acao).

### Carga

- Correr e atacar no mesmo turno.
- +1 dado ao dano, mas -2 dados na defesa ate o proximo turno.

---

## 17. Regras de Combate Social (Resumo)

O V5 tambem reconhece **conflitos sociais** como "combate":

- Disputas verbais, interrogatorios e debates seguem logica similar.
- Dano Social afeta o **tracker de Forca de Vontade** em vez de Saude.
- Disciplinas de Presenca e Dominacao podem ser usadas como "armas" sociais.
- Perder um conflito social pode resultar em humilhacao, obrigacoes ou perda de Status.

---

## 18. Resumo Rapido de Combate

```
INICIO DO TURNO:
1. Declarar intencoes
2. Determinar iniciativa
3. Resolver acoes (testes opostos)

ATAQUE:
- Corpo a corpo: Forca+Briga / Destreza+Armas Brancas vs Defesa
- Distancia: Compostura+Armas de Fogo vs Destreza+Atletismo do alvo
- Dano = Margem de Sucesso + valor da arma (Forca nao entra)
- Vampiros: Superficial mundano / 2 (arredondado para cima)

DEFESA:
- Esquiva: Destreza + Atletismo
- Contra-ataque: Forca + Briga / Destreza + Armas Brancas
- Armadura converte Agravado de corte/perfuracao em Superficial

DANO CRITICO:
- Fogo = Agravado + Frenesi Terror
- Sol = Agravado + Frenesi Terror
- Mordida vampirica = Agravado
- Estaca = Paralisia
- Tracker cheio Agravado = Torpor (vampiro) / Morte (mortal)

FRENESI:
- Resistir: FdV atual + Humanidade/3 vs DD
- Cavalgar a Onda: sem teste; o jogador conduz o frenesi
```

---

*Referencia criada para consulta rapida durante sessoes de Vampire: The Masquerade 5th Edition.*
