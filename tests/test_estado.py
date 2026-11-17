"""Motor com estado (F1): estado.json lido e gravado pelo servidor MCP, recusa
de número divergente, parada pela ficha, chance e montagem."""

import json
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import vtm_estado as est  # noqa: E402
import vtm_motor as m  # noqa: E402

SERVIDOR = RAIZ / "scripts" / "vtm_mcp.py"

FICHA = """# Personagem de Teste

## Atributos

| Físicos | • | Sociais | • | Mentais | • |
|---------|---|---------|---|---------|---|
| Força | 2 | Carisma | 3 | Inteligência | 2 |
| Destreza | 3 | Manipulação | 4 | Raciocínio | 3 |
| Vigor | 2 | Compostura | 3 | Determinação | 2 |

## Habilidades

| Habilidade | Valor | Especialidade |
|------------|-------|---------------|
| Persuasão | 3 | Negociação |
| Intuição | 2 | — |

- **Briga:** 1
- Furtividade ●●

## Disciplinas

### Presença ●● (Clã)
| Nível | Poder | Efeito |
|-------|-------|--------|
| 1 | Fascinar | texto |

- Auspícios 1

## Vantagens
| Vantagem | Valor |
|----------|-------|
| Recursos | 3 |
"""


def _estado(fome=2, bp=1, **extra):
    e = json.loads((RAIZ / "08_Templates" / "07_estado.json").read_text(encoding="utf-8"))
    e["personagem"].update({"fome": fome, "potencia_sangue": bp})
    e["personagem"].update(extra)
    return e


def _campanha(tmp_path, nome="Teste", **kw):
    pasta = tmp_path / nome
    pasta.mkdir()
    (pasta / "estado.json").write_text(json.dumps(_estado(**kw)), encoding="utf-8")
    (pasta / "personagem.md").write_text(FICHA, encoding="utf-8")
    return pasta


def _ler(pasta):
    return json.loads((pasta / "estado.json").read_text(encoding="utf-8"))["personagem"]


# ---------------------------------------------------------------- unidade


def test_valor_usa_o_estado_e_recusa_divergencia():
    e = _estado(fome=3)
    assert est.valor(e, "fome", None) == 3
    assert est.valor(e, "fome", 3) == 3
    with pytest.raises(est.Divergencia, match=r"informada \(2\) difere do estado.json \(3\)"):
        est.valor(e, "fome", 2)


def test_valor_sem_estado_usa_o_informado():
    assert est.valor(None, "fome", 2) == 2
    assert est.valor(None, "potencia_sangue", None, padrao=0) == 0
    with pytest.raises(ValueError, match="informe Fome"):
        est.valor(None, "fome", None)


def test_estado_invalido_e_recusado(tmp_path):
    pasta = _campanha(tmp_path)
    (pasta / "estado.json").write_text(json.dumps(_estado(fome=9)), encoding="utf-8")
    with pytest.raises(ValueError, match="estado.json com erro"):
        est.carregar(pasta)
    assert est.carregar(tmp_path / "nao_existe") is None


def test_gravar_valida_e_preserva_campos(tmp_path):
    pasta = _campanha(tmp_path)
    e = est.carregar(pasta)
    e["personagem"]["fome"] = 4
    est.gravar(pasta, e)
    salvo = json.loads((pasta / "estado.json").read_text(encoding="utf-8"))
    assert salvo["personagem"]["fome"] == 4 and salvo["tempo"] == e["tempo"]
    e["personagem"]["fome"] = 6
    with pytest.raises(ValueError, match="inválido"):
        est.gravar(pasta, e)
    assert _ler(pasta)["fome"] == 4  # o arquivo bom não foi trocado


def test_marcar_dano_converte_com_tracker_cheio():
    t = {"max": 3, "superficial": 2, "agravado": 0}
    assert est.marcar_dano(t, 1, "superficial") == \
        ["Tracker cheio: Prejudicado, -2 dados nas paradas afetadas (Core p. 126)"]
    assert t == {"max": 3, "superficial": 3, "agravado": 0}
    est.marcar_dano(t, 2, "superficial")  # cheio: cada ponto vira Agravado
    assert t == {"max": 3, "superficial": 1, "agravado": 2}
    notas = est.marcar_dano(t, 5, "agravado")
    assert t == {"max": 3, "superficial": 0, "agravado": 3} and "Agravado" in notas[0]


def test_ficha_md_nos_dois_formatos():
    f = est._ler_md(FICHA)
    assert len(f["atributos"]) == 9 and f["atributos"]["manipulacao"] == ("Manipulação", 4)
    assert "fisicos" not in f["atributos"]
    assert {k: v[1] for k, v in f["habilidades"].items()} == \
        {"persuasao": 3, "intuicao": 2, "briga": 1, "furtividade": 2}
    assert {k: v[1] for k, v in f["disciplinas"].items()} == {"presenca": 2, "auspicios": 1}


def test_parada_soma_pela_ficha(tmp_path):
    pasta = _campanha(tmp_path)
    r = est.parada(pasta, "manipulacao", "Persuasão", "presença", 1)
    assert r["parada"] == 10 and r["texto"] == "Manipulação 4 + Persuasão 3 + Presença 2 + bônus 1 = 10"
    assert est.parada(pasta, "Compostura", "Determinação")["parada"] == 5  # dois Atributos
    sem = est.parada(pasta, "Destreza", "Condução")
    assert sem["parada"] == 3 and "contei 0" in sem["avisos"][0]
    with pytest.raises(ValueError, match="Atributo 'Sorte'"):
        est.parada(pasta, "Sorte")
    with pytest.raises(ValueError, match="Disciplina"):
        est.parada(pasta, "Força", disciplina="Potência")


def test_parada_prefere_ficha_json(tmp_path):
    pasta = _campanha(tmp_path)
    (pasta / "ficha.json").write_text(json.dumps(
        {"atributos": {"Força": 5}, "habilidades": {"Briga": 4}, "disciplinas": {}}), encoding="utf-8")
    assert est.parada(pasta, "força", "briga")["parada"] == 9


def test_chance_confere_com_simulacao():
    c = m.chance(7, 2, 4)
    assert (c["dados_normais"], c["dados_fome"], c["texto"]) == (5, 2, f"~{c['vitoria']}%")
    rng = random.Random(7)
    n = 20000
    rol = [m.rolar(7, 2, 4, rng=rng) for _ in range(n)]
    for chave, tipo in (("critico_confuso", "CRITICO_CONFUSO"), ("falha_bestial", "FALHA_BESTIAL")):
        assert abs(c[chave] - 100 * sum(r.tipo == tipo for r in rol) / n) <= 2
    assert abs(c["vitoria"] - 100 * sum(r.vitoria for r in rol) / n) <= 2


def test_chance_valores_conhecidos():
    assert m.chance(1, 0, 1)["vitoria"] == 50
    assert m.chance(2, 0, 4)["vitoria"] == 1  # só o par de 10
    assert m.chance(6, 0, 3)["vitoria"] == 67
    assert m.chance(5, 0, 2)["falha_bestial"] == 0
    assert m.chance(1, 1, 1)["falha_bestial"] == 10


def test_montagem_intercala_alimentacao():
    # Dados fixos: todos os despertares falham (Fome +1 por noite).
    class Falha(random.Random):
        def randint(self, a, b):
            return 1
    r = m.montagem(2, 1, 4, ["2:humano_seguro", "3:gole_humano"], rng=Falha())
    assert [(n["fome_ao_acordar"], n["fome_ao_fim"]) for n in r["noites"]] == \
        [(3, 3), (4, 2), (3, 2), (3, 3)]
    assert r["fome_depois"] == 3 and "interrompida" not in r


def test_montagem_para_na_fome_limite_e_no_torpor():
    class Falha(random.Random):
        def randint(self, a, b):
            return 1
    r = m.montagem(2, 1, 10, parar_com_fome=4, rng=Falha())
    assert r["noites_feitas"] == 2 and r["fome_depois"] == 4 and "faltam 8 noites" in r["interrompida"]
    r = m.montagem(5, 1, 3, parar_com_fome=6, rng=Falha())
    assert r["noites_feitas"] == 1 and "torpor" in r["interrompida"]
    with pytest.raises(ValueError, match="evento inválido"):
        m.montagem(1, 1, 3, ["caçar"])
    with pytest.raises(ValueError, match="noite deve ficar"):
        m.montagem(1, 1, 3, ["4:bolsa"])


# ---------------------------------------------------------------- servidor


def _conversar(tmp_path, chamadas):
    msgs = [{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}}]
    msgs += [{"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": n, "arguments": a}}
             for i, (n, a) in enumerate(chamadas, 1)]
    entrada = "".join(json.dumps(x) + "\n" for x in msgs).encode("utf-8")
    env = dict(os.environ, VTM_MCP_MINIMO="1", VTM_PASTA_CAMPANHAS=str(tmp_path), VTM_CAMPANHA_ATIVA="")
    p = subprocess.run([sys.executable, str(SERVIDOR)], input=entrada, capture_output=True, env=env, timeout=30)
    saidas = []
    for linha in p.stdout.decode("utf-8").splitlines()[1:]:
        res = json.loads(linha)["result"]
        txt = res["content"][0]["text"]
        saidas.append({"erro_ferramenta": txt} if res["isError"] else json.loads(txt))
    return saidas


def test_servidor_le_a_fome_do_estado_e_recusa_divergente(tmp_path):
    pasta = _campanha(tmp_path, fome=3)
    sem, igual, errada, npc = _conversar(tmp_path, [
        ("rolar", {"parada": 7, "dificuldade": 3}),
        ("rolar", {"parada": 7, "fome": 3, "dificuldade": 3}),
        ("rolar", {"parada": 7, "fome": 2, "dificuldade": 3}),
        ("rolar", {"parada": 5, "dificuldade": 2, "npc": True}),
    ])
    for r in (sem, igual):
        assert len(r["dados_fome"]) == 3 and len(r["dados_normais"]) == 4
        assert r["estado"]["fome"] == 3
    assert "Fome informada (2) difere do estado.json (3)" in errada["erro_ferramenta"]
    assert npc["dados_fome"] == [] and "estado" not in npc
    # a rolagem recusada não entra no registro
    assert len((pasta / "rolagens.jsonl").read_text(encoding="utf-8").splitlines()) == 3


def test_servidor_grava_fome_dano_e_forca_de_vontade(tmp_path):
    pasta = _campanha(tmp_path, fome=4)
    comer, rer, dano, soh_calculo, lido = _conversar(tmp_path, [
        ("alimentar", {"fonte": "humano_seguro"}),
        ("rerolar_fdv", {"normais": [2, 3, 8], "fome": [4, 5], "indices": [0, 1], "dificuldade": 2}),
        ("aplicar_dano", {"dano": 3, "natureza": "superficial", "alvo": "saude"}),
        ("aplicar_dano", {"dano": 3, "natureza": "superficial"}),
        ("ler_estado", {}),
    ])
    assert (comer["fome_antes"], comer["fome_depois"]) == (4, 2) and comer["estado_gravado"] is True
    assert dano["marcado"] == 2 and soh_calculo == {**soh_calculo, "marcado": 2} and "alvo" not in soh_calculo
    p = _ler(pasta)
    assert p["fome"] == 2
    assert p["forca_vontade"]["superficial"] == 1 and p["saude"]["superficial"] == 2
    assert lido["estado"]["fome"] == 2 and lido["estado"]["forca_vontade"].startswith("4 de 5")


def test_servidor_rouse_em_lote_exige_confirmacao_e_grava(tmp_path):
    pasta = _campanha(tmp_path, fome=0)
    recusado, lote, um = _conversar(tmp_path, [
        ("rouse", {"quantidade": 10}),
        ("rouse", {"quantidade": 2, "noites_intercaladas": False}),
        ("rouse", {}),
    ])
    assert "montagem" in recusado["erro_ferramenta"]
    assert lote["fome_antes"] == 0 and len(lote["checks"]) == 2
    assert um["fome_antes"] == lote["fome_depois"]  # a segunda chamada parte da Fome gravada
    assert _ler(pasta)["fome"] == um["fome_depois"]


def test_servidor_montagem_remorso_e_frenesi(tmp_path):
    pasta = _campanha(tmp_path, fome=1, manchas=2)
    mont, rem, fren, div = _conversar(tmp_path, [
        ("montagem", {"noites": 3, "eventos": ["2:humano_seguro"], "parar_com_fome": 6}),
        ("remorso", {}),
        ("frenesi", {"dificuldade": 3}),
        ("frenesi", {"dificuldade": 3, "humanidade": 9}),
    ])
    assert mont["noites_feitas"] == 3 and mont["fome_antes"] == 1
    assert [len(n["alimentacoes"]) for n in mont["noites"]] == [0, 1, 0]
    p = _ler(pasta)
    assert p["fome"] == mont["fome_depois"] and p["manchas"] == 0
    assert p["humanidade"] == rem["humanidade_depois"]
    assert fren["extra"]["parada"] == 5 + p["humanidade"] // 3  # FdV intacta 5 do modelo
    assert "Humanidade informada (9)" in div["erro_ferramenta"]


def test_servidor_parada_e_chance(tmp_path):
    _campanha(tmp_path, fome=2)
    par, ch, ch_npc = _conversar(tmp_path, [
        ("parada", {"atributo": "Manipulação", "habilidade": "Persuasão"}),
        ("chance", {"parada": 7, "dificuldade": 4}),
        ("chance", {"parada": 7, "dificuldade": 4, "npc": True}),
    ])
    assert par["parada"] == 7 and par["fome"] == 2
    assert ch["dados_fome"] == 2 and ch["texto"] == f"~{ch['vitoria']}%"
    assert ch_npc["dados_fome"] == 0 and ch_npc["falha_bestial"] == 0


def test_servidor_sem_estado_segue_como_antes(tmp_path):
    (tmp_path / "Antiga").mkdir()
    com, sem, mont = _conversar(tmp_path, [
        ("rolar", {"parada": 5, "fome": 2, "dificuldade": 3}),
        ("rolar", {"parada": 5, "dificuldade": 3}),
        ("montagem", {"noites": 2}),
    ])
    assert len(com["dados_fome"]) == 2 and "estado" not in com
    assert "informe Fome" in sem["erro_ferramenta"]
    assert "estado.json" in mont["erro_ferramenta"]


def test_servidor_registra_a_mesa(tmp_path):
    pasta = _campanha(tmp_path)
    reg, lido, ruim = _conversar(tmp_path, [
        ("registrar_mesa", {"cena": "Gabinete do Xerife", "decisao_pendente": "Como responder?",
                            "opcoes": ["A — Mostrar o que apurou", "B — Ler o Xerife"]}),
        ("ler_estado", {}),
        ("registrar_mesa", {"cena": "", "decisao_pendente": "x"}),
    ])
    assert reg["mesa"]["decisao_pendente"] == "Como responder?"
    assert lido["mesa"]["opcoes"] == ["A — Mostrar o que apurou", "B — Ler o Xerife"]
    assert "obrigatórias" in ruim["erro_ferramenta"]
    assert json.loads((pasta / "mesa.json").read_text(encoding="utf-8"))["cena"] == "Gabinete do Xerife"


def test_servidor_registra_decisao_do_narrador(tmp_path):
    pasta = _campanha(tmp_path)
    d1, d2, ruim = _conversar(tmp_path, [
        ("registrar_decisao", {"regra": "Ajuda do aliado dá +1 dado", "motivo": "o Core não cobre este caso"}),
        ("registrar_decisao", {"regra": "Correr no telhado pede Destreza + Atletismo DD 3", "motivo": "sem tabela"}),
        ("registrar_decisao", {"regra": "x", "motivo": ""}),
    ])
    assert d1["decisao"]["id"] == "DN-1" and d2["pendentes"] == ["DN-1", "DN-2"]
    assert d1["mostrar_ao_jogador"] == "Decisão do narrador: Ajuda do aliado dá +1 dado (DN-1)"
    assert "obrigatórios" in ruim["erro_ferramenta"]
    assert "| DN-2 |" in (pasta / "decisoes_narrador.md").read_text(encoding="utf-8")
