"""Sobe o servidor MCP real por stdio e chama ferramentas (sem mock)."""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

mcp = pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

SERVIDOR = Path(__file__).resolve().parents[1] / "scripts" / "vtm_mcp.py"


async def _chamar(env, chamadas):
    params = StdioServerParameters(command=sys.executable, args=[str(SERVIDOR)], env=env)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            nomes = {t.name for t in (await s.list_tools()).tools}
            saidas = []
            for nome, args in chamadas:
                res = await s.call_tool(nome, args)
                txt = res.content[0].text
                erro = getattr(res, "is_error", getattr(res, "isError", False))
                saidas.append({"erro_ferramenta": txt} if erro else json.loads(txt))
            return nomes, saidas


def test_servidor_lista_e_rola(tmp_path):
    camp = tmp_path / "Teste"
    camp.mkdir()
    env = dict(os.environ, VTM_PASTA_CAMPANHAS=str(tmp_path), VTM_CAMPANHA_ATIVA="Teste")
    nomes, (rolagem, rouse, auditoria) = asyncio.run(_chamar(env, [
        ("rolar", {"parada": 5, "fome": 2, "dificuldade": 3}),
        ("rouse", {"fome_atual": 1, "bp": 1}),
        ("auditar_campanha", {}),
    ]))
    assert auditoria["campanha"] == "Teste"
    assert any(a["codigo"] == "ESTADO" for a in auditoria["achados"])
    assert {"rolar", "rouse", "frenesi", "remorso", "alimentar", "conflito"} <= nomes
    assert len(rolagem["dados_normais"]) == 3 and len(rolagem["dados_fome"]) == 2
    assert rouse["tipo"] == "ROUSE"
    linhas = (camp / "rolagens.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 2


def test_buscar_acervo_pelo_servidor(tmp_path):
    fitz = pytest.importorskip("fitz")
    sys.path.insert(0, str(SERVIDOR.parent))
    import vtm_acervo as acervo
    raiz = tmp_path / "acervo" / "Vampiro a Máscara"
    raiz.mkdir(parents=True)
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "1\nIntro " * 10)
    doc.new_page().insert_text((72, 72), "2\nRouse Check: roll one die and hope.\n" + "texto " * 20)
    doc.save(raiz / "Vampire the Masquerade.pdf")
    indice = tmp_path / "idx.sqlite"
    acervo.indexar(tmp_path / "acervo", acervo.conectar(indice), aviso=None)
    env = dict(os.environ, VTM_INDICE=str(indice))
    _, (r,) = asyncio.run(_chamar(env, [("buscar_acervo", {"consulta": '"Rouse Check"'})]))
    assert r["resultados"][0]["pagina"] == 2


def test_servidor_duas_campanhas_em_paralelo(tmp_path):
    for nome in ("Helena", "Antônio"):
        (tmp_path / nome).mkdir()
    env = dict(os.environ, VTM_PASTA_CAMPANHAS=str(tmp_path), VTM_CAMPANHA_ATIVA="")
    _, (lista, a, e, sem) = asyncio.run(_chamar(env, [
        ("listar_campanhas", {}),
        ("rolar", {"parada": 4, "fome": 1, "dificuldade": 2, "campanha": "Antônio"}),
        ("rouse", {"fome_atual": 1, "bp": 1, "campanha": "Helena"}),
        ("rolar", {"parada": 4, "fome": 1, "dificuldade": 2}),
    ]))
    assert lista == {"campanhas": ["Antônio", "Helena"], "padrao": None}
    assert a["campanha"] == "Antônio" and e["campanha"] == "Helena"
    assert sem["registrado_em"] is None and "aviso" in sem
    for nome in ("Helena", "Antônio"):
        assert len((tmp_path / nome / "rolagens.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_sem_campanha_nao_grava(tmp_path):
    env = dict(os.environ, VTM_PASTA_CAMPANHAS="${user_config.pasta_campanhas}", VTM_CAMPANHA_ATIVA="")
    _, (r,) = asyncio.run(_chamar(env, [("remorso", {"humanidade": 7, "manchas": 1})]))
    assert r["registrado_em"] is None


def test_recusa_chega_ao_cliente_com_a_mensagem(tmp_path):
    """No pacote `mcp`, o texto do erro de regra precisa chegar ao narrador."""
    camp = tmp_path / "Teste"
    camp.mkdir()
    modelo = Path(__file__).resolve().parents[1] / "08_Templates" / "07_estado.json"
    estado = json.loads(modelo.read_text(encoding="utf-8"))
    estado["personagem"]["fome"] = 3
    (camp / "estado.json").write_text(json.dumps(estado), encoding="utf-8")
    env = dict(os.environ, VTM_PASTA_CAMPANHAS=str(tmp_path), VTM_CAMPANHA_ATIVA="Teste")
    nomes, (recusada, certa, lote) = asyncio.run(_chamar(env, [
        ("rolar", {"parada": 6, "fome": 2, "dificuldade": 3}),
        ("rolar", {"parada": 6, "dificuldade": 3}),
        ("rouse", {"quantidade": 10}),
    ]))
    assert {"parada", "chance", "montagem", "ler_estado"} <= nomes
    assert "Fome informada (2) difere do estado.json (3)" in recusada["erro_ferramenta"]
    assert len(certa["dados_fome"]) == 3 and certa["estado"]["fome"] == 3
    assert "montagem" in lote["erro_ferramenta"]
