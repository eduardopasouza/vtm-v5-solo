# VtM V5 Solo — narrador de Vampiro: A Máscara para o Claude Code

Plugin `vtm` para o [Claude Code](https://claude.com/claude-code). Com ele o Claude narra uma campanha solo de **Vampiro: A Máscara 5ª Edição** em português: apresenta cenas, rola os dados com um motor de regras de verdade, guarda a memória da campanha em arquivos seus e cita a página do livro quando decide uma regra.

<img src="assets/darkpack_logo.png" alt="Dark Pack" width="140" align="right">

> **Material de fã, não oficial.** Este projeto não é material oficial do World of Darkness. É conteúdo de fã, gratuito e sem fins comerciais, publicado sob o [Dark Pack Agreement](https://www.paradoxinteractive.com/games/world-of-darkness/community/dark-pack-agreement) da Paradox Interactive.
>
> Portions of the materials are the copyrights and trademarks of Paradox Interactive AB, and are used with permission. All rights reserved. For more information please visit worldofdarkness.com.
>
> O plugin não distribui livros e não reproduz o texto deles: as referências de regra são paráfrases com indicação de página. Para jogar com as regras completas, compre os livros oficiais.

## O que vem no plugin

| Parte | Para que serve |
|---|---|
| 5 skills | `/vtm:narrar` (jogar), `/vtm:criar` (novo jogo, partida, história, aventura), `/vtm:personagem` (ficha e XP), `/vtm:npcs`, `/vtm:gerenciar` (entre sessões) |
| Motor de dados | Rolagens do V5 com Fome, Rouse Check, frenesi, remorso, conflito, dano, alimentação e Potência de Sangue. Cada regra aponta a página do Core |
| Memória da campanha | Uma pasta sua, com `estado.json` (os números) e arquivos `.md` (a narrativa). Um auditor aponta números divergentes, sessões fora da linha do tempo e NPCs sem ficha |
| 3 agentes | `arquivista` (fim de sessão), `continuidade` (contradições) e `guardiao-regras` (dúvida de regra, com fonte) |
| Referências | Regras (`01_Sistema/`), Disciplinas com Rituais e Cerimônias (`03_Disciplinas/`), ferramentas do narrador (`10_Ferramentas_do_Narrador/`) e a Perdição, a Compulsão e as Disciplinas de cada clã (`02_Clas/`) foram conferidas com o V5 Core e os suplementos V5 e trazem a página. O lore de clãs, seitas e cenário foi conferido ponto a ponto: cada arquivo termina com uma tabela que separa o que é V5 (com página), o que vem de edições antigas, o que é texto de fã e o que é história real |

## Requisitos

- Claude Code (terminal, app de desktop ou extensão de IDE).
- **Python 3.10 ou mais novo.** Só a biblioteca padrão é necessária para jogar.
  - Windows: instale pelo python.org ou pela Microsoft Store e marque "Add python.exe to PATH".
  - macOS e Linux: se o seu comando for `python3`, ponha `python3` na opção "Comando do Python" do plugin.
- Opcional: `pymupdf` (e Tesseract, para OCR) se quiser indexar os seus próprios PDFs.

## Instalação

No terminal:

```bash
claude plugin marketplace add eduardopasouza/vtm-v5-solo
```

```bash
claude plugin install vtm@vtm-v5-solo
```

Ou, dentro do Claude Code, use `/plugin`, adicione o marketplace `eduardopasouza/vtm-v5-solo` e instale o plugin `vtm`.

Ao ativar, o Claude Code pede as opções do plugin. Só a primeira importa para começar:

| Opção | O que colocar |
|---|---|
| Pasta das campanhas | Uma pasta **sua**, vazia, em qualquer lugar (ex.: `Documentos/vtm-campanhas`). Tudo que é seu fica nela. Nunca use a pasta do plugin |
| Campanha ativa | Pode deixar vazio. Com uma campanha só, ela é usada sozinha; com várias, o narrador pergunta qual jogar |
| Pasta do acervo de PDFs | Opcional. Veja "Seus livros" abaixo |
| Pasta dos resumos | Opcional. Resumos seus dos livros, se tiver |
| Mostrar dados individuais | Mostra cada dado rolado. Padrão: sim |
| Comando do Python | Padrão: `python` |

Para mudar depois: `/plugin`, plugin `vtm`, configurar opções. Reinicie o Claude Code depois de mudar.

## Como jogar

Abra o Claude Code na sua pasta de campanhas e fale em linguagem natural:

1. **"Quero criar um jogo de VtM."** A sessão zero define cidade, época, tom e clã, monta o cenário e cria a ficha com você, passo a passo.
2. **"Quero jogar VtM"** ou **"continuar a campanha de vampiro"**. O narrador lê o estado, resume onde parou e apresenta a cena com opções. Você pode sempre propor outra ação.
3. **"Encerrar a sessão."** O narrador faz o teste de Remorso se houver Manchas, calcula o XP e atualiza os arquivos.
4. **"Revisar a campanha de VtM."** Entre sessões: agendas dos NPCs, objetivos, auditoria.

As skills só disparam quando o pedido fala de VtM, vampiro ou da campanha.

### Várias campanhas ao mesmo tempo

Cada personagem tem a sua subpasta, e as campanhas são independentes. Para alternar entre elas:

- Deixe **Campanha ativa** vazia.
- Abra **uma conversa por campanha** e diga qual quer jogar: "quero jogar VtM com o Edward". Sem nome, o narrador lista as campanhas e pergunta.
- Cada rolagem vai para o `rolagens.jsonl` da campanha certa, porque o narrador passa o nome dela ao motor de dados.
- Ao abrir o Claude Code na pasta de campanhas, o resumo inicial mostra uma linha de cada campanha. Aberto dentro da pasta de um personagem, mostra só aquela.

## O que é seu e onde fica

```
<sua pasta de campanhas>/
├── preferencias.md        (opcional) seu tom, formato e limites de conteúdo
├── regras_da_casa.md      (opcional) suas regras da casa
└── <Nome do personagem>/
    ├── estado.json        números: Fome, Humanidade, dano, XP, noite
    ├── contexto.md, personagem.md, objetivos.md, timeline.md
    ├── direcao.md         segredos do narrador (não leia, se quiser surpresa)
    ├── rolagens.jsonl     registro de toda rolagem
    ├── npcs/, cenario/
    └── partidas/<Partida>/<História>/<Aventura>/sessao_NN.md
```

- **Preferências:** copie `09_Preferencias/01_Preferencias_de_Jogo.md` do plugin para `preferencias.md` na sua pasta e edite. A sua cópia vale no lugar do padrão.
- **Regras da casa:** o padrão do plugin tem uma (RC-1: XP mais rápido para jogo solo). Um `regras_da_casa.md` seu substitui o padrão inteiro. Para jogar só pelo livro, crie o arquivo com a linha "Nenhuma regra da casa".
- A pasta do plugin é trocada a cada atualização. Não guarde nada nela.

## Seus livros (opcional)

Sem PDFs o plugin funciona: o narrador usa as referências que vêm com ele e diz "não sei" quando elas não cobrem. Se você tem os PDFs dos livros que comprou, pode indexá-los para o narrador buscar e citar livro e página:

```bash
python -m pip install pymupdf
```

```bash
python <pasta do plugin>/scripts/acervo.py indexar --raiz "<pasta dos seus PDFs>"
```

- O índice fica só na sua máquina (`%LOCALAPPDATA%/vtm-v5/acervo.sqlite` no Windows, `~/.local/share/vtm-v5/` nos demais), nunca no repositório.
- O livro básico em inglês é reconhecido como "Core" se o arquivo se chamar `Vampire the Masquerade.pdf` ou tiver "Core" e "V5"/"5th Edition" no nome. O Core tem prioridade na busca.
- Aponte também a opção "Pasta do acervo de PDFs" para a mesma pasta.

## Fonte das regras

Ordem de prioridade: suas regras da casa > V5 Core (inglês) > suplementos V5 > referências do plugin > edições antigas (só lore). O narrador não inventa regra: sem fonte, diz que não sabe e propõe decidir com você.

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| As ferramentas de dados não aparecem | O comando da opção "Comando do Python" não existe no terminal. Veja "Requisitos" |
| Erro no início de toda sessão | Mesmo motivo: o resumo da campanha usa o mesmo comando |
| O narrador pergunta onde ficam as campanhas | A opção "Pasta das campanhas" está vazia |
| Mudei uma opção e nada mudou | Reinicie o Claude Code |

## Desenvolvimento

```bash
python -m pytest tests
```

```bash
claude --plugin-dir .
```

Com `--plugin-dir` as opções do plugin não são preenchidas; para testar a configuração, instale pelo marketplace. Regras para contribuir: nenhuma regra sem página do livro, nenhum caminho de máquina ou dado pessoal nos arquivos do plugin, testes sem simulação.

## Avisos

- Jogo de horror para adultos: violência, sangue e temas maduros. Registre seus limites em `preferencias.md`.
- Projeto de fã, sem fins comerciais. Não distribua livros, PDFs ou trechos deles junto com o plugin.

## Licença

- **Código** (pastas `scripts/`, `tests/`, `hooks/`, `skills/`, `agents/` e os manifestos em `.claude-plugin/`): licença MIT, no arquivo `LICENSE`.
- **Material de referência** (pastas numeradas `01_` a `10_`): conteúdo de fã sobre o World of Darkness, publicado nos termos do Dark Pack Agreement. A licença MIT **não** cobre esse material nem dá direito algum sobre marcas, cenário e regras da Paradox Interactive AB.
- **Logo Dark Pack** (`assets/darkpack_logo.png`): da Paradox Interactive AB, usado conforme o Dark Pack Agreement.
