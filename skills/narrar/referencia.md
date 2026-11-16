# Narrador — referência de mecânicas e de configuração

> Parte da skill `narrar`. Ler no início da sessão, depois do Contrato de resposta (em `SKILL.md`), que vale por cima deste arquivo.

## Mecânicas

Ferramenta MCP entre parênteses. Com `estado.json`, as ferramentas leem e gravam os números sozinhas (não informar Fome nem Potência). O CLI (`vtm_dice.py --help`) faz as mesmas contas, sem estado.

- **Rouse** (`rouse`; Core p. 211, 216). 1 dado; 1-5 = Fome +1. Com o nível da Disciplina dentro do limite da Potência, rola 2 e fica o maior. Com Fome 5 não se desperta o sangue de propósito; se for forçado e falhar, frenesi de fome DD 4. Fome 5: avisar o jogador e oferecer caça na cena seguinte.
- **Despertar** (`despertar`). Rouse ao acordar; falha com Fome 5 = torpor.
- **Várias noites** (`montagem`). Um despertar por noite e, depois dele, as alimentações daquela noite: `eventos` = `"noite:fonte"` (ex.: `"2:humano_seguro"`). Para sozinha em torpor ou quando a Fome chega a `parar_com_fome`. `rouse` com `quantidade` maior que 1 só vale para Rouses da mesma cena (`noites_intercaladas=false`).
- **Alimentação** (`alimentar`; Core p. 211-212, 216). Fontes: `gole_humano` (1), `humano_seguro` (2), `humano_arriscado` (1-4, dano Agravado na vítima), `humano_drenar_e_matar` (único jeito de chegar a Fome 0), `animais_pequenos`, `animal_medio`, `animal_grande`, `bolsa`. O motor aplica as penalidades da Potência e o piso de Fome sem matar. Ressonância: `01_Sistema/09_Ressonancia_Sanguinea.md`.
- **Força de Vontade** (`rerolar_fdv`; Core p. 122-123). 1 ponto rerrola até 3 dados normais e marca 1 Superficial na Força de Vontade. Nunca dados de Fome, nunca Rouse, nem testes de Força de Vontade, Humanidade ou frenesi (o motor não confere isso). A ferramenta já marca o ponto gasto no `estado.json`. Testes de Força de Vontade ou Humanidade: `teste_tracker` (sem Fome, mínimo 1 dado).
- **Surto de Sangue e cura** (`surto_de_sangue`, `curar`, `curar_agravado`; Core p. 216-219). Surto: 1 Rouse, soma dados pela Potência a uma parada com Atributo. Cura: 1 Rouse por turno cura dano Superficial pela Potência; ao anoitecer, 3 Rouses curam 1 Agravado (1 por noite).
- **Combate** (`conflito`, `aplicar_dano`; Core p. 124-126). Sem turnos táticos: intenção, teste, resultado. O vencedor causa margem + arma; em conflito de dois lados, empate = 1 de dano para cada. Dano Superficial é dividido pela metade (para cima) antes de marcar; armas comuns causam Superficial a vampiros. `conflito` só calcula: marcar o dano do personagem com `aplicar_dano` e `alvo` (`saude` ou `forca_vontade`).
- **Remorso** (`remorso`; Core p. 239). Fim da sessão, se houver Manchas. Dados = 10 − Humanidade − Manchas (mínimo 1). Com 1 sucesso a Humanidade fica; sem nenhum, cai 1. As Manchas somem nos dois casos.
- **Frenesi** (`frenesi`; Core p. 219). Parada = Força de Vontade intacta + Humanidade ÷ 3 (para baixo). Vitória: resiste, mas gasta o turno contendo a Besta; crítico: resiste sem perder o turno. Falha: a Besta assume, e o que ela faz segue a regra 7 do Contrato sempre que houver mais de um desfecho possível.

## Configuração não preenchida

Quando um valor da tabela Caminhos vier vazio ou como `${user_config...}` literal:
- Jogos: perguntar onde ficam as campanhas e sugerir configurar `pasta_campanhas` (`/plugin`, plugin `vtm`, configurar opções). **Nunca gravar campanha dentro de `[Base]`**: é a pasta do plugin, substituída a cada atualização.
- Campanha ativa: perguntar, se houver mais de uma. Python: `python`. Mostrar dados: sim. Resumos, PDFs e acervo: não usar.
- Sem acervo (ou se `buscar_acervo` disser que não há índice), a fonte de regra são `[Base]/01_Sistema/`, `[Base]/03_Disciplinas/` e `[Base]/10_Ferramentas_do_Narrador/` (conferidos com o Core e os suplementos V5, com página), mais o motor de dados.
- Lore de `[Base]/02_Clas/`, `04_Seitas_e_Politica/` e `05_Cenario/`: cada arquivo termina com a tabela "Conferência do Lore". Só o que está marcado **V5** é fato do jogo; o resto é ambientação, com aviso ao jogador quando uma decisão depender dele.
- O que não estiver em fonte nenhuma: dizer "não sei" ou propor ao jogador como regra da casa. Não inventar.
