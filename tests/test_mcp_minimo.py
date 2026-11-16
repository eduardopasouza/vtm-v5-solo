"""Servidor MCP mínimo (sem o pacote `mcp`): fala JSON-RPC por stdio direto,
sem cliente de terceiros, para valer também numa máquina só com o Python."""

import json
import os
import subprocess
import sys
from pathlib import Path

SERVIDOR = Path(__file__).resolve().parents[1] / "scripts" / "vtm_mcp.py"


def _conversar(env, mensagens):
    entrada = "".join(json.dumps(m) + "\n" for m in mensagens).encode("utf-8")
    p = subprocess.run([sys.executable, str(SERVIDOR)], input=entrada, capture_output=True,
                       env=dict(os.environ, VTM_MCP_MINIMO="1", **env), timeout=30)
    return [json.loads(x) for x in p.stdout.decode("utf-8").splitlines() if x.strip()]


def _chamada(ident, nome, args):
    return {"jsonrpc": "2.0", "id": ident, "method": "tools/call",
            "params": {"name": nome, "arguments": args}}


INICIO = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "teste", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
]


def test_minimo_lista_rola_e_registra(tmp_path):
    camp = tmp_path / "Unica"
    camp.mkdir()
    # Sem campanha_ativa: a única subpasta vira a campanha ativa.
    env = {"VTM_PASTA_CAMPANHAS": str(tmp_path), "VTM_CAMPANHA_ATIVA": ""}
    r = _conversar(env, INICIO + [
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        _chamada(3, "rolar", {"parada": 5, "fome": 2, "dificuldade": 3}),
        _chamada(4, "rerolar_fdv", {"normais": [2, 3, 8], "fome": [4], "indices": [0, 1], "dificuldade": 2}),
        _chamada(5, "rouse", {"fome_atual": 5}),
        {"jsonrpc": "2.0", "id": 6, "method": "nao/existe"},
    ])
    assert [x["id"] for x in r] == [1, 2, 3, 4, 5, 6]  # a notificação não tem resposta
    assert r[0]["result"]["protocolVersion"] == "2025-06-18"
    ferramentas = {t["name"]: t for t in r[1]["result"]["tools"]}
    assert {"rolar", "rouse", "frenesi", "remorso", "alimentar", "conflito",
            "auditar_campanha", "buscar_acervo"} <= set(ferramentas)
    esquema = ferramentas["rerolar_fdv"]["inputSchema"]
    assert esquema["properties"]["normais"] == {"type": "array", "items": {"type": "integer"}}
    assert esquema["required"] == ["normais", "fome", "indices"]
    rolagem = json.loads(r[2]["result"]["content"][0]["text"])
    assert len(rolagem["dados_normais"]) == 3 and len(rolagem["dados_fome"]) == 2
    assert rolagem["registrado_em"]
    assert json.loads(r[3]["result"]["content"][0]["text"])["extra"]["rerolados"] == [0, 1]
    assert r[4]["result"]["isError"] is True  # Fome 5: erro de regra, não queda do servidor
    assert r[5]["error"]["code"] == -32601
    assert len((camp / "rolagens.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_minimo_sem_configuracao(tmp_path):
    env = {"VTM_PASTA_CAMPANHAS": "${user_config.pasta_campanhas}", "VTM_CAMPANHA_ATIVA": "",
           "VTM_INDICE": str(tmp_path / "nao_existe.sqlite")}
    r = _conversar(env, INICIO + [
        _chamada(2, "remorso", {"humanidade": 7, "manchas": 1}),
        _chamada(3, "auditar_campanha", {}),
        _chamada(4, "buscar_acervo", {"consulta": "Rouse"}),
    ])
    assert json.loads(r[1]["result"]["content"][0]["text"])["registrado_em"] is None
    assert "erro" in json.loads(r[2]["result"]["content"][0]["text"])
    assert "opcional" in json.loads(r[3]["result"]["content"][0]["text"])["erro"]
