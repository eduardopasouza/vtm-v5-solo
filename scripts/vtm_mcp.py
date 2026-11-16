"""Servidor MCP do plugin vtm — camada fina sobre vtm_motor.

Expõe as rolagens como ferramentas para o narrador e os agentes, sem dar
acesso ao terminal. Não edita arquivos da campanha; só acrescenta cada
rolagem a `rolagens.jsonl` da campanha ativa quando as variáveis
VTM_PASTA_CAMPANHAS e VTM_CAMPANHA_ATIVA apontam para uma pasta existente.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_motor as m  # noqa: E402
import vtm_campanha as camp  # noqa: E402

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


def _pasta_campanha() -> Path | None:
    """Campanha ativa: a configurada, ou a única subpasta da pasta de campanhas."""
    return camp.pasta_ativa(os.environ.get("VTM_PASTA_CAMPANHAS", "").strip(),
                            os.environ.get("VTM_CAMPANHA_ATIVA", "").strip())


def _reg(cmd: str, resultado: dict) -> dict:
    arq = m.registrar(_pasta_campanha(), cmd, resultado)
    resultado = dict(resultado)
    resultado["registrado_em"] = str(arq) if arq else None
    return resultado


@mcp.tool()
def rolar(parada: int, fome: int, dificuldade: int | None = None, oponente: int | None = None) -> dict:
    """Teste comum de VtM V5. `parada` é o total (Atributo + Habilidade + bônus);
    a Fome substitui dados normais. Informe `dificuldade` ou `oponente` (sucessos)."""
    return _reg(f"rolar {parada} {fome} {dificuldade} {oponente}",
                m.rolar(parada, fome, dificuldade, oponente).como_dict())


@mcp.tool()
def rerolar_fdv(normais: list[int], fome: list[int], indices: list[int],
                dificuldade: int | None = None, oponente: int | None = None) -> dict:
    """Gasta 1 Força de Vontade para re-rolar até 3 dados normais (índices 0-base)
    de um teste de Atributo ou Habilidade. Dados de Fome nunca são re-rolados.
    Proibido em testes de Força de Vontade, Humanidade, frenesi e Rouse."""
    ant = m.avaliar(normais, fome, dificuldade, oponente)
    return _reg("rerolar_fdv", m.rerolar_fdv(ant, indices).como_dict())


@mcp.tool()
def teste_tracker(valor_intacto: int, dificuldade: int) -> dict:
    """Teste de Força de Vontade ou Humanidade: sem Fome, sem re-rolagem, mínimo 1 dado."""
    return _reg("teste_tracker", m.rolar_tracker(valor_intacto, dificuldade).como_dict())


@mcp.tool()
def rouse(fome_atual: int, bp: int = 0, nivel_disciplina: int | None = None,
          quantidade: int = 1, forcado: bool = False) -> dict:
    """Rouse Check. Com nível de Disciplina dentro do limite da Potência, rola 2 dados."""
    return _reg("rouse", m.rouse(fome_atual, bp, nivel_disciplina, quantidade, forcado))


@mcp.tool()
def despertar(fome_atual: int, bp: int = 0) -> dict:
    """Rouse Check ao acordar; com Fome 5, falha leva a torpor."""
    return _reg("despertar", m.despertar(fome_atual, bp))


@mcp.tool()
def surto_de_sangue(parada: int, fome_atual: int, bp: int,
                    dificuldade: int | None = None, oponente: int | None = None) -> dict:
    """Blood Surge: soma dados pela Potência a uma parada com Atributo e cobra um Rouse."""
    return _reg("surto_de_sangue", m.surto_de_sangue(parada, fome_atual, bp, dificuldade, oponente))


@mcp.tool()
def curar(dano_superficial: int, fome_atual: int, bp: int) -> dict:
    """Cura dano Superficial de Saúde com um Rouse (quantidade pela Potência)."""
    return _reg("curar", m.curar_superficial(dano_superficial, fome_atual, bp))


@mcp.tool()
def curar_agravado(fome_atual: int, bp: int) -> dict:
    """Ao anoitecer: três Rouses para curar 1 de dano Agravado."""
    return _reg("curar_agravado", m.curar_agravado(fome_atual, bp))


@mcp.tool()
def frenesi(fdv_intacta: int, humanidade: int, dificuldade: int) -> dict:
    """Resistir ao frenesi: Força de Vontade intacta + Humanidade/3."""
    return _reg("frenesi", m.frenesi(fdv_intacta, humanidade, dificuldade).como_dict())


@mcp.tool()
def remorso(humanidade: int, manchas: int) -> dict:
    """Teste de Remorso ao fim da sessão: dados = 10 - Humanidade - Manchas (mínimo 1)."""
    return _reg("remorso", m.remorso(humanidade, manchas))


@mcp.tool()
def conflito(parada_a: int, fome_a: int, parada_b: int, fome_b: int = 0,
             dois_lados: bool = False, arma_a: int = 0, arma_b: int = 0) -> dict:
    """Conflito: o vencedor causa margem + arma; em dois lados, empate dá 1 de dano a cada um."""
    return _reg("conflito", m.conflito(parada_a, fome_a, parada_b, fome_b, dois_lados, arma_a, arma_b))


@mcp.tool()
def aplicar_dano(dano: int, natureza: str, por_gasto: bool = False) -> dict:
    """Quanto marcar no tracker: Superficial é dividido por 2 (para cima), salvo gasto."""
    return m.aplicar_dano(dano, natureza, por_gasto=por_gasto)


@mcp.tool()
def alimentar(fonte: str, fome_atual: int, bp: int, quantidade_arriscada: int = 0) -> dict:
    """Alimentação. Fontes: animais_pequenos, animal_medio, animal_grande, bolsa,
    gole_humano, humano_seguro, humano_arriscado (1-4), humano_drenar_e_matar."""
    return _reg("alimentar", m.alimentar(fonte, fome_atual, bp, quantidade_arriscada))


@mcp.tool()
def auditar_campanha() -> dict:
    """Audita a campanha ativa (só leitura): estado.json, números divergentes entre
    estado e .md, Potência x tabela do Core, sessões fora da linha do tempo,
    rodapés defasados e NPCs sem ficha."""
    pasta = _pasta_campanha()
    if pasta is None:
        return {"erro": "campanha ativa não encontrada: configure pasta_campanhas (e campanha_ativa, "
                        "se houver mais de uma) nas opções do plugin"}
    achados = camp.auditar(pasta)
    return {"campanha": pasta.name, "achados": camp.achados_como_dict(achados),
            "erros": sum(a.nivel == "erro" for a in achados)}


@mcp.tool()
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


@mcp.tool()
def tabela_potencia(bp: int) -> dict:
    """Linha da tabela de Potência de Sangue (Core p. 216)."""
    from dataclasses import asdict
    return {"bp": bp, **asdict(m.potencia(bp)), "fonte": "Core p. 216"}


if __name__ == "__main__":
    mcp.run()
