"""Servidor MCP do plugin vtm — camada fina sobre vtm_motor.

Expõe as rolagens como ferramentas para o narrador e os agentes, sem dar
acesso ao terminal. O servidor guarda estado: lê Fome, Potência, Humanidade,
Manchas e trackers de `estado.json`, recusa a chamada que informar um número
diferente do estado e grava ali o que cada rolagem muda (Fome, dano, Força de
Vontade gasta, Humanidade). Campanha sem `estado.json` segue como antes, com os
números informados na chamada. Cada rolagem também vai para `rolagens.jsonl`
do jogo em uso: o informado no parâmetro
`campanha` da ferramenta, senão VTM_CAMPANHA_ATIVA, senão a única subpasta de
VTM_PASTA_CAMPANHAS. Assim várias campanhas rodam em paralelo, cada sessão
passando o nome da sua.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_motor as m  # noqa: E402
import vtm_campanha as camp  # noqa: E402
import vtm_estado as est  # noqa: E402

class _MiniMCP:
    """Servidor MCP mínimo por stdio (JSON-RPC, uma mensagem por linha), só com
    a biblioteca padrão. Usado quando o pacote `mcp` não está instalado, para o
    plugin funcionar só com o Python. Cobre initialize, ping, tools/list e
    tools/call."""

    _TIPOS = {"int": "integer", "str": "string", "bool": "boolean", "float": "number"}

    def __init__(self, nome: str):
        self.nome = nome
        self.ferramentas: dict[str, tuple] = {}

    def _esquema_tipo(self, anotacao: str) -> dict:
        partes = [p.strip() for p in str(anotacao).split("|")]
        base = next((p for p in partes if p != "None"), "str")
        if base.startswith("list["):
            return {"type": "array", "items": {"type": self._TIPOS.get(base[5:-1], "string")}}
        return {"type": self._TIPOS.get(base, "string")}

    def tool(self):
        import inspect

        def registrar(fn):
            props, obrigatorios = {}, []
            for nome, p in inspect.signature(fn).parameters.items():
                props[nome] = self._esquema_tipo(p.annotation)
                if p.default is inspect.Parameter.empty:
                    obrigatorios.append(nome)
            esquema = {"type": "object", "properties": props, "required": obrigatorios}
            self.ferramentas[fn.__name__] = (fn, (fn.__doc__ or "").strip(), esquema)
            return fn
        return registrar

    def _responder(self, msg: dict) -> dict | None:
        import json
        metodo, ident = msg.get("method"), msg.get("id")
        if ident is None:  # notificação: sem resposta
            return None
        if metodo == "initialize":
            versao = (msg.get("params") or {}).get("protocolVersion") or "2024-11-05"
            res = {"protocolVersion": versao, "capabilities": {"tools": {}},
                   "serverInfo": {"name": self.nome, "version": "1"}}
        elif metodo == "ping":
            res = {}
        elif metodo == "tools/list":
            res = {"tools": [{"name": n, "description": d, "inputSchema": e}
                             for n, (_, d, e) in self.ferramentas.items()]}
        elif metodo == "tools/call":
            params = msg.get("params") or {}
            nome = params.get("name")
            if nome not in self.ferramentas:
                return {"jsonrpc": "2.0", "id": ident,
                        "error": {"code": -32602, "message": f"ferramenta desconhecida: {nome}"}}
            try:
                saida = self.ferramentas[nome][0](**(params.get("arguments") or {}))
                res = {"content": [{"type": "text", "text": json.dumps(saida, ensure_ascii=False)}],
                       "isError": False}
            except Exception as ex:  # erro de regra (ex.: Fome 5) volta como erro da ferramenta
                res = {"content": [{"type": "text", "text": f"Erro: {ex}"}], "isError": True}
        else:
            return {"jsonrpc": "2.0", "id": ident,
                    "error": {"code": -32601, "message": f"método não suportado: {metodo}"}}
        return {"jsonrpc": "2.0", "id": ident, "result": res}

    def run(self) -> None:
        import json
        for bruto in sys.stdin.buffer:
            linha = bruto.decode("utf-8", errors="replace").strip()
            if not linha:
                continue
            try:
                msg = json.loads(linha)
            except json.JSONDecodeError:
                continue
            resp = self._responder(msg) if isinstance(msg, dict) else None
            if resp is not None:
                sys.stdout.buffer.write((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
                sys.stdout.buffer.flush()


def _criar_servidor():
    """Servidor do pacote `mcp` quando ele existe (`MCPServer` no mcp 2.x,
    `FastMCP` no 1.x); senão, o servidor mínimo embutido.
    VTM_MCP_MINIMO=1 força o servidor mínimo (usado nos testes)."""
    if os.environ.get("VTM_MCP_MINIMO", "").strip() != "1":
        try:  # mcp 2.x: FastMCP passou a se chamar MCPServer
            from mcp.server.mcpserver import MCPServer
            return MCPServer("vtm")
        except ImportError:
            pass
        try:  # mcp 1.x (ainda instalado em algumas máquinas)
            from mcp.server.fastmcp import FastMCP
            return FastMCP("vtm")
        except ImportError:
            pass
    return _MiniMCP("vtm")


mcp = _criar_servidor()


def _classe_erro():
    """Erro que o pacote `mcp` repassa ao modelo com o texto. No mcp 2.x, uma
    exceção comum chega só como "Error executing tool"; a recusa por Fome
    divergente (e qualquer erro de regra) precisa chegar inteira."""
    for modulo in ("mcp.server.mcpserver.exceptions", "mcp.server.fastmcp.exceptions"):
        try:
            return __import__(modulo, fromlist=["ToolError"]).ToolError
        except (ImportError, AttributeError):
            continue
    return ValueError


_ErroFerramenta = _classe_erro()


def _ferramenta(fn):
    """Registra a ferramenta; erro de regra (ValueError) vira erro da ferramenta
    com a mensagem, sem derrubar o servidor."""
    import functools

    @functools.wraps(fn)
    def embrulho(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as ex:
            if isinstance(mcp, _MiniMCP):
                raise
            raise _ErroFerramenta(str(ex)) from None

    return mcp.tool()(embrulho)


def _base_campanhas() -> str:
    return os.environ.get("VTM_PASTA_CAMPANHAS", "").strip()


def _pasta_campanha(campanha: str | None = None) -> Path | None:
    """Campanha em uso: a pedida na chamada (`campanha`), senão a configurada,
    senão a única subpasta da pasta de campanhas."""
    return camp.pasta_ativa(_base_campanhas(), os.environ.get("VTM_CAMPANHA_ATIVA", "").strip(),
                            campanha)


def _nomes_campanhas() -> list[str]:
    return [p.name for p in camp.listar_jogos(_base_campanhas())]


def _reg(cmd: str, resultado: dict, campanha: str | None = None) -> dict:
    pasta = _pasta_campanha(campanha)
    arq = m.registrar(pasta, cmd, resultado)
    resultado = dict(resultado)
    resultado["registrado_em"] = str(arq) if arq else None
    if arq:
        resultado["campanha"] = pasta.name
    elif campanha and campanha.strip():
        resultado["aviso"] = (f"campanha '{campanha}' não encontrada; rolagem não registrada. "
                              f"Campanhas: {', '.join(_nomes_campanhas()) or 'nenhuma'}")
    elif len(_nomes_campanhas()) > 1:
        resultado["aviso"] = ("há mais de uma campanha e nenhuma fixada; informe `campanha` "
                              "para registrar a rolagem no jogo certo")
    return resultado


@_ferramenta
def listar_campanhas() -> dict:
    """Lista as campanhas (subpastas de jogo) da pasta de campanhas e diz qual é a
    padrão. Com mais de uma, o narrador pergunta ao jogador qual jogar e passa o
    nome em `campanha` em todas as ferramentas de dados daquela sessão."""
    padrao = _pasta_campanha()
    return {"campanhas": _nomes_campanhas(), "padrao": padrao.name if padrao else None}


def _ctx(campanha: str | None, npc: bool = False) -> tuple[Path | None, dict | None]:
    """Pasta e estado da campanha. Rolagem de NPC não lê nem grava estado."""
    pasta = _pasta_campanha(campanha)
    return pasta, (None if npc else est.carregar(pasta))


def _fim(cmd: str, resultado: dict, campanha: str | None, pasta: Path | None,
         estado: dict | None, gravar: bool = False) -> dict:
    """Grava o estado (se mudou), registra a rolagem e devolve os números atuais."""
    if estado is not None and gravar:
        est.gravar(pasta, estado)
    out = _reg(cmd, resultado, campanha)
    if estado is not None:
        out["estado"] = est.resumo(estado)
        out["estado_gravado"] = gravar
    return out


def _p(estado: dict) -> dict:
    return estado["personagem"]


@_ferramenta
def ler_estado(campanha: str | None = None) -> dict:
    """Números atuais do personagem em estado.json (Fome, Potência, Humanidade,
    Manchas, Saúde, Força de Vontade). Usar antes de citar qualquer número."""
    pasta, estado = _ctx(campanha)
    if estado is None:
        return {"erro": "campanha sem estado.json (ou não encontrada): os números vêm do contexto.md"}
    return {"campanha": pasta.name, "sessao": estado["sessao"], "tempo": estado["tempo"],
            "estado": est.resumo(estado)}


@_ferramenta
def parada(atributo: str, habilidade: str | None = None, disciplina: str | None = None,
           bonus: int = 0, campanha: str | None = None) -> dict:
    """Soma uma parada pela ficha (personagem.md ou ficha.json), em vez de
    calcular de cabeça. `habilidade` aceita também um segundo Atributo;
    `bonus` pode ser negativo. Devolve o total e as partes."""
    pasta, estado = _ctx(campanha)
    if pasta is None:
        raise ValueError("campanha não encontrada: informe `campanha`")
    out = est.parada(pasta, atributo, habilidade, disciplina, bonus)
    if estado is not None:
        out["fome"] = _p(estado)["fome"]
    return out


@_ferramenta
def chance(parada: int, dificuldade: int, fome: int | None = None,
           campanha: str | None = None, npc: bool = False) -> dict:
    """Chance de vitória de um teste (percentual exato, arredondado), mais as de
    crítico confuso e falha bestial. Usar na linha de cada opção: "~Z%". Sem
    `fome`, usa a do estado.json. Não rola nada e não registra."""
    _, estado = _ctx(campanha, npc)
    return m.chance(parada, est.valor(estado, "fome", fome, 0 if npc else None), dificuldade)


@_ferramenta
def rolar(parada: int, fome: int | None = None, dificuldade: int | None = None,
          oponente: int | None = None, campanha: str | None = None, npc: bool = False) -> dict:
    """Teste comum de VtM V5. `parada` é o total (Atributo + Habilidade + bônus);
    a Fome substitui dados normais. Informe `dificuldade` ou `oponente` (sucessos).
    Não informe `fome`: ela vem do estado.json; se informar um valor diferente
    do estado, a chamada é recusada. Para rolar a parada de um NPC, `npc=true`
    (Fome 0 se não informada; não mexe no estado).
    `campanha` (em todas as ferramentas) = nome da pasta do jogo; obrigatório na
    prática quando há mais de uma campanha."""
    pasta, estado = _ctx(campanha, npc)
    f = est.valor(estado, "fome", fome, 0 if npc else None)
    return _fim(f"rolar {parada} {f} {dificuldade} {oponente}" + (" npc" if npc else ""),
                m.rolar(parada, f, dificuldade, oponente).como_dict(), campanha, pasta, estado)


@_ferramenta
def rerolar_fdv(normais: list[int], fome: list[int], indices: list[int],
                dificuldade: int | None = None, oponente: int | None = None,
                campanha: str | None = None, npc: bool = False) -> dict:
    """Gasta 1 Força de Vontade para re-rolar até 3 dados normais (índices 0-base)
    de um teste de Atributo ou Habilidade. Dados de Fome nunca são re-rolados.
    Proibido em testes de Força de Vontade, Humanidade, frenesi e Rouse.
    Marca 1 Superficial na Força de Vontade do estado.json. Só chamar depois
    que o jogador escolheu gastar."""
    pasta, estado = _ctx(campanha, npc)
    ant = m.avaliar(normais, fome, dificuldade, oponente)
    res = m.rerolar_fdv(ant, indices).como_dict()
    if estado is not None:
        notas = est.marcar_dano(_p(estado)["forca_vontade"], 1, "superficial")
        res["observacoes"] = res.get("observacoes", []) + notas
    return _fim("rerolar_fdv", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def teste_tracker(valor_intacto: int, dificuldade: int,
                  campanha: str | None = None) -> dict:
    """Teste de Força de Vontade ou Humanidade: sem Fome, sem re-rolagem, mínimo 1 dado."""
    return _reg("teste_tracker", m.rolar_tracker(valor_intacto, dificuldade).como_dict(), campanha)


@_ferramenta
def rouse(fome_atual: int | None = None, bp: int | None = None,
          nivel_disciplina: int | None = None, quantidade: int = 1, forcado: bool = False,
          noites_intercaladas: bool | None = None, campanha: str | None = None) -> dict:
    """Rouse Check. Com nível de Disciplina dentro do limite da Potência, rola 2
    dados. Fome e Potência vêm do estado.json, e a Fome nova é gravada lá.
    `quantidade` > 1 só vale para Rouses seguidos da mesma cena e exige
    `noites_intercaladas=false`; despertares de noites diferentes vão por
    `montagem`."""
    if quantidade < 1:
        raise ValueError("quantidade deve ser 1 ou mais")
    if quantidade > 1 and noites_intercaladas is not False:
        raise ValueError("Vários Rouses de uma vez só valem dentro da mesma cena: confirme com "
                         "noites_intercaladas=false. Para despertares de noites diferentes, com "
                         "alimentações no meio, use a ferramenta `montagem`.")
    pasta, estado = _ctx(campanha)
    f = est.valor(estado, "fome", fome_atual)
    res = m.rouse(f, est.valor(estado, "potencia_sangue", bp, 0), nivel_disciplina, quantidade, forcado)
    if estado is not None:
        _p(estado)["fome"] = res["fome_depois"]
    return _fim("rouse", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def despertar(fome_atual: int | None = None, bp: int | None = None,
              campanha: str | None = None) -> dict:
    """Rouse Check ao acordar (uma noite); com Fome 5, falha leva a torpor.
    Lê e grava a Fome no estado.json. Várias noites: `montagem`."""
    pasta, estado = _ctx(campanha)
    res = m.despertar(est.valor(estado, "fome", fome_atual), est.valor(estado, "potencia_sangue", bp, 0))
    if estado is not None:
        _p(estado)["fome"] = res["fome_depois"]
    return _fim("despertar", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def montagem(noites: int, eventos: list[str] | None = None, parar_com_fome: int = 5,
             campanha: str | None = None) -> dict:
    """Várias noites resumidas: um Rouse de despertar por noite e, depois dele,
    as alimentações daquela noite, na ordem. `eventos`: lista de "noite:fonte"
    (ex.: "2:humano_seguro") ou "noite:humano_arriscado:N"; noite 1 = o próximo
    despertar. Para sozinha em torpor ou quando a Fome chega a `parar_com_fome`
    com noites por vir: aí a decisão volta ao jogador. Parte da Fome do
    estado.json e grava a Fome final. Não rola caça nem testes de risco: esses
    seguem um a um, pelo contrato de resposta."""
    pasta, estado = _ctx(campanha)
    if estado is None:
        raise ValueError("montagem precisa do estado.json da campanha (Fome e Potência de partida)")
    res = m.montagem(_p(estado)["fome"], _p(estado)["potencia_sangue"], noites, eventos, parar_com_fome)
    _p(estado)["fome"] = res["fome_depois"]
    return _fim(f"montagem {noites}", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def surto_de_sangue(parada: int, fome_atual: int | None = None, bp: int | None = None,
                    dificuldade: int | None = None, oponente: int | None = None,
                    campanha: str | None = None) -> dict:
    """Blood Surge: soma dados pela Potência a uma parada com Atributo e cobra um
    Rouse. Fome e Potência vêm do estado.json; a Fome nova é gravada."""
    pasta, estado = _ctx(campanha)
    res = m.surto_de_sangue(parada, est.valor(estado, "fome", fome_atual),
                            est.valor(estado, "potencia_sangue", bp), dificuldade, oponente)
    if estado is not None:
        _p(estado)["fome"] = res["rouse"]["fome_depois"]
    return _fim("surto_de_sangue", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def curar(dano_superficial: int | None = None, fome_atual: int | None = None,
          bp: int | None = None, campanha: str | None = None) -> dict:
    """Cura dano Superficial de Saúde com um Rouse (quantidade pela Potência).
    Com estado.json, lê o dano e a Fome de lá e grava os dois."""
    pasta, estado = _ctx(campanha)
    if estado is not None:
        atual = _p(estado)["saude"]["superficial"]
        if dano_superficial is not None and dano_superficial != atual:
            raise est.Divergencia(f"Dano Superficial informado ({dano_superficial}) difere do estado.json "
                                  f"({atual}). Nada foi rolado. Repita a chamada sem esse parâmetro.")
        dano_superficial = atual
        if atual == 0:
            raise ValueError("Não há dano Superficial de Saúde para curar")
    elif dano_superficial is None:
        raise ValueError("informe dano_superficial: a campanha não tem estado.json")
    res = m.curar_superficial(dano_superficial, est.valor(estado, "fome", fome_atual),
                              est.valor(estado, "potencia_sangue", bp))
    if estado is not None:
        _p(estado)["saude"]["superficial"] = res["dano_restante"]
        _p(estado)["fome"] = res["rouse"]["fome_depois"]
    return _fim("curar", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def curar_agravado(fome_atual: int | None = None, bp: int | None = None,
                   campanha: str | None = None) -> dict:
    """Ao anoitecer: três Rouses para curar 1 de dano Agravado. Lê e grava a
    Fome e a Saúde no estado.json."""
    pasta, estado = _ctx(campanha)
    if estado is not None and _p(estado)["saude"]["agravado"] == 0:
        raise ValueError("Não há dano Agravado de Saúde para curar")
    res = m.curar_agravado(est.valor(estado, "fome", fome_atual), est.valor(estado, "potencia_sangue", bp))
    if estado is not None:
        _p(estado)["fome"] = res["fome_depois"]
        _p(estado)["saude"]["agravado"] -= res["curado"]
    return _fim("curar_agravado", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def frenesi(dificuldade: int, fdv_intacta: int | None = None, humanidade: int | None = None,
            campanha: str | None = None) -> dict:
    """Resistir ao frenesi: Força de Vontade intacta + Humanidade/3. Os dois
    números vêm do estado.json."""
    pasta, estado = _ctx(campanha)
    res = m.frenesi(est.fdv_intacta(estado, fdv_intacta), est.valor(estado, "humanidade", humanidade),
                    dificuldade).como_dict()
    return _fim("frenesi", res, campanha, pasta, estado)


@_ferramenta
def remorso(humanidade: int | None = None, manchas: int | None = None,
            campanha: str | None = None) -> dict:
    """Teste de Remorso ao fim da sessão: dados = 10 - Humanidade - Manchas
    (mínimo 1). Lê do estado.json e grava a Humanidade nova e Manchas 0."""
    pasta, estado = _ctx(campanha)
    res = m.remorso(est.valor(estado, "humanidade", humanidade), est.valor(estado, "manchas", manchas))
    if estado is not None:
        _p(estado)["humanidade"] = res["humanidade_depois"]
        _p(estado)["manchas"] = res["manchas_depois"]
    return _fim("remorso", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def conflito(parada_a: int, parada_b: int, fome_a: int | None = None, fome_b: int = 0,
             dois_lados: bool = False, arma_a: int = 0, arma_b: int = 0,
             campanha: str | None = None, npc: bool = False) -> dict:
    """Conflito: o vencedor causa margem + arma; em dois lados, empate dá 1 de
    dano a cada um. O lado A é o personagem (Fome do estado.json); o B, o
    adversário. `npc=true` quando os dois lados são NPCs. O dano não é marcado
    aqui: use `aplicar_dano` com `alvo`."""
    pasta, estado = _ctx(campanha, npc)
    res = m.conflito(parada_a, est.valor(estado, "fome", fome_a, 0 if npc else None), parada_b, fome_b,
                     dois_lados, arma_a, arma_b)
    return _fim("conflito", res, campanha, pasta, estado)


@_ferramenta
def aplicar_dano(dano: int, natureza: str, por_gasto: bool = False, alvo: str | None = None,
                 campanha: str | None = None) -> dict:
    """Quanto marcar no tracker: Superficial é dividido por 2 (para cima), salvo
    gasto. Com `alvo` = "saude" ou "forca_vontade", marca o dano no personagem
    (estado.json), convertendo Superficial em Agravado se o tracker já estiver
    cheio. Sem `alvo`, só calcula (dano em NPC)."""
    res = m.aplicar_dano(dano, natureza, por_gasto=por_gasto)
    if alvo is None:
        return res
    if alvo not in ("saude", "forca_vontade"):
        raise ValueError("alvo deve ser 'saude' ou 'forca_vontade'")
    pasta, estado = _ctx(campanha)
    if estado is None:
        raise ValueError("para marcar o dano é preciso o estado.json da campanha")
    res["alvo"] = alvo
    res["notas"] = est.marcar_dano(_p(estado)[alvo], res["marcado"], res["natureza"])
    return _fim(f"aplicar_dano {alvo}", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def alimentar(fonte: str, fome_atual: int | None = None, bp: int | None = None,
              quantidade_arriscada: int = 0, campanha: str | None = None) -> dict:
    """Alimentação. Fontes: animais_pequenos, animal_medio, animal_grande, bolsa,
    gole_humano, humano_seguro, humano_arriscado (1-4), humano_drenar_e_matar.
    Fome e Potência vêm do estado.json; a Fome nova é gravada."""
    pasta, estado = _ctx(campanha)
    res = m.alimentar(fonte, est.valor(estado, "fome", fome_atual),
                      est.valor(estado, "potencia_sangue", bp), quantidade_arriscada)
    if estado is not None:
        _p(estado)["fome"] = res["fome_depois"]
    return _fim("alimentar", res, campanha, pasta, estado, gravar=True)


@_ferramenta
def auditar_campanha(campanha: str | None = None) -> dict:
    """Audita uma campanha (só leitura): estado.json, números divergentes entre
    estado e .md, Potência x tabela do Core, sessões fora da linha do tempo,
    rodapés defasados e NPCs sem ficha. `campanha` = nome da pasta do jogo;
    vazio = a configurada ou a única."""
    pasta = _pasta_campanha(campanha)
    if pasta is None:
        nomes = _nomes_campanhas()
        if campanha and campanha.strip():
            return {"erro": f"campanha '{campanha}' não encontrada", "campanhas": nomes}
        if len(nomes) > 1:
            return {"erro": "há mais de uma campanha: informe `campanha`", "campanhas": nomes}
        return {"erro": "campanha ativa não encontrada: configure pasta_campanhas (e campanha_ativa, "
                        "se quiser uma padrão) nas opções do plugin"}
    achados = camp.auditar(pasta)
    return {"campanha": pasta.name, "achados": camp.achados_como_dict(achados),
            "erros": sum(a.nivel == "erro" for a in achados)}


@_ferramenta
def buscar_acervo(consulta: str, linha: str | None = None, edicao: str | None = None,
                  idioma: str | None = None, limite: int = 8) -> dict:
    """Busca no índice local dos livros (V5 Core primeiro, depois suplementos V5,
    depois edições antigas). Devolve livro, página impressa e trecho curto para
    citar. Frase exata entre aspas. Filtros: linha (VtM, VtDA, WtA, MtA, HtR),
    edicao (core, v5, classica), idioma (en, pt). Sem resultado = não citar."""
    import vtm_acervo as acervo
    caminho = acervo.indice_padrao()
    if not caminho.exists():
        return {"erro": f"índice do acervo não encontrado em {caminho}. O acervo é opcional: sem ele, "
                        "use os arquivos 01_Sistema a 10_Ferramentas do plugin (trazem a página do Core). "
                        "Para criar o índice a partir dos seus PDFs: python scripts/acervo.py indexar --raiz <pasta>"}
    con = acervo.conectar(caminho)
    try:
        return {"consulta": consulta, "resultados": acervo.buscar(con, consulta, linha, edicao, idioma, limite)}
    finally:
        con.close()


@_ferramenta
def tabela_potencia(bp: int) -> dict:
    """Linha da tabela de Potência de Sangue (Core p. 216)."""
    from dataclasses import asdict
    return {"bp": bp, **asdict(m.potencia(bp)), "fonte": "Core p. 216"}


if __name__ == "__main__":
    mcp.run()
