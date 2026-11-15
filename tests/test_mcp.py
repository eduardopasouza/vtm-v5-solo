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
                saidas.append(json.loads(res.content[0].text))
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


def test_sem_campanha_nao_grava(tmp_path):
    env = dict(os.environ, VTM_PASTA_CAMPANHAS="${user_config.pasta_campanhas}", VTM_CAMPANHA_ATIVA="")
    _, (r,) = asyncio.run(_chamar(env, [("remorso", {"humanidade": 7, "manchas": 1})]))
    assert r["registrado_em"] is None
