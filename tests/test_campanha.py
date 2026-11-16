"""Testes da memória da campanha com uma campanha fictícia criada no teste."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import vtm_campanha as c  # noqa: E402
import campanha as cli  # noqa: E402

TEMPLATE = RAIZ / "08_Templates" / "07_estado.json"


def estado_base(**mudancas):
    e = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    e["campanha"] = "Mara Voss"
    e["personagem"]["nome"] = "Mara Voss"
    e["sessao"] = 2
    for k, v in mudancas.items():
        e["personagem"][k] = v
    return e


def montar(tmp_path, estado=None, contexto_fome=2, ficha_fome=2, timeline_sessoes=(1, 2),
           rodape_ficha=2, ficha_extra=""):
    camp = tmp_path / "Mara Voss"
    (camp / "npcs").mkdir(parents=True)
    hist = camp / "partidas" / "P" / "H" / "A"
    hist.mkdir(parents=True)
    for n in (1, 2):
        (hist / f"sessao_{n:02d}.md").write_text(f"# Sessão {n}\n", encoding="utf-8")
    (camp / "contexto.md").write_text(
        "# Contexto\n\n## Estado Actual\n\n| Campo | Valor |\n|---|---|\n"
        f"| **Fome** | {contexto_fome} |\n| **Humanidade** | 7 |\n\n"
        "## Proximos passos\n1. Caçar no porto\n2. Falar com Iris\n\n"
        "## Relacoes Activas\n\n| NPC | Atitude |\n|---|---|\n| Iris | Aliada |\n| Bram | Rival |\n\n"
        "*Atualizado — Sessão 2*\n", encoding="utf-8")
    (camp / "personagem.md").write_text(
        f"# Mara\n\n| **Fome** | {ficha_fome} |\n| **Potência de Sangue** | 1 |\n{ficha_extra}\n"
        f"*Atualizado — Sessão {rodape_ficha}*\n", encoding="utf-8")
    (camp / "timeline.md").write_text(
        "# Linha do tempo\n" + "".join(f"- Sessão {n}: algo\n" for n in timeline_sessoes)
        + "\n*Sessão 2*\n", encoding="utf-8")
    (camp / "npcs" / "iris_kell.md").write_text("# Iris Kell\n", encoding="utf-8")
    (camp / "npcs" / "indice.md").write_text("# Índice\n- Iris Kell\n", encoding="utf-8")
    (camp / "direcao.md").write_text("# SEGREDO: Iris é a traidora\n", encoding="utf-8")
    if estado is not None:
        (camp / "estado.json").write_text(json.dumps(estado), encoding="utf-8")
    return camp


def codigos(achados):
    return sorted(a.codigo for a in achados)


# --- schema --------------------------------------------------------------------

def test_template_e_valido():
    assert c.validar_estado(json.loads(TEMPLATE.read_text(encoding="utf-8"))) == []


def test_validacao_aponta_erros():
    e = estado_base(fome=7)
    e["personagem"]["saude"] = {"max": 5, "superficial": 4, "agravado": 3}
    e["personagem"]["humanidade"], e["personagem"]["manchas"] = 8, 4
    erros = c.validar_estado(e)
    assert any("fome" in x for x in erros)
    assert any("dano maior" in x for x in erros)
    assert any("Degeneração" in x for x in erros)


# --- auditoria -----------------------------------------------------------------

def test_campanha_limpa_sem_estado_so_avisa_ausencia(tmp_path):
    camp = montar(tmp_path)
    achados = c.auditar(camp)
    assert [a for a in achados if a.nivel == "erro"] == []
    assert "ESTADO" in codigos(achados)


def test_divergencia_entre_contexto_e_ficha(tmp_path):
    camp = montar(tmp_path, ficha_fome=4)
    assert "NUMERO_DIVERGENTE" in codigos(c.auditar(camp))


def test_estado_prevalece_e_md_duplicado_e_aviso(tmp_path):
    camp = montar(tmp_path, estado=estado_base(fome=3))
    achados = c.auditar(camp)
    div = [a for a in achados if a.codigo == "NUMERO_DIVERGENTE"]
    assert len(div) == 2  # contexto e ficha dizem 2, estado diz 3
    camp2 = montar(tmp_path / "b", estado=estado_base(fome=2))
    assert "NUMERO_DUPLICADO" in codigos(c.auditar(camp2))


def test_sessao_fora_da_timeline_e_rodape(tmp_path):
    camp = montar(tmp_path, timeline_sessoes=(1,), rodape_ficha=1)
    cods = codigos(c.auditar(camp))
    assert "TIMELINE" in cods and "RODAPE" in cods


def test_timeline_com_coluna_de_sessao():
    linhas = ["| Data | Sessão | Evento |", "|---|---|---|", "| Nov | 8 | algo |",
              "| Nov | **9** | outro |", "", "| Evento | Sessão | Local |", "|---|---|---|",
              "| x | 13 | Tooley |", "- Sessão 2: texto"]
    assert c.sessoes_citadas(linhas) == {2, 8, 9, 13}


def test_estado_atrasado(tmp_path):
    e = estado_base()
    e["sessao"] = 1
    camp = montar(tmp_path, estado=e)
    assert any(a.codigo == "ESTADO" and "Sessão 1" in a.mensagem for a in c.auditar(camp))


def test_npc_sem_ficha(tmp_path):
    camp = montar(tmp_path)
    sem = [a for a in c.auditar(camp) if a.codigo == "NPC_SEM_FICHA"]
    assert [a.mensagem.split()[0] for a in sem] == ["Bram"]


def test_potencia_contra_tabela_do_core(tmp_path):
    camp = montar(tmp_path, ficha_extra="- BP 1: Surge +3, Bane 1\n")
    pot = [a for a in c.auditar(camp) if a.codigo == "POTENCIA_TABELA"]
    assert len(pot) == 1 and "Surge 3" in pot[0].mensagem


# --- resumo e hook -------------------------------------------------------------

def test_resumo_usa_estado_e_nao_le_direcao(tmp_path):
    camp = montar(tmp_path, estado=estado_base(fome=3))
    txt = c.resumo(camp)
    assert "Fome 3" in txt and "Caçar no porto" in txt
    assert "SEGREDO" not in txt and "traidora" not in txt
    assert len(txt.splitlines()) <= 15


def test_hook_so_dentro_da_pasta(tmp_path):
    camp = montar(tmp_path, estado=estado_base())
    env = {"CLAUDE_PLUGIN_OPTION_PASTA_CAMPANHAS": str(tmp_path),
           "CLAUDE_PLUGIN_OPTION_CAMPANHA_ATIVA": "Mara Voss"}
    dentro = cli.modo_hook(json.dumps({"cwd": str(camp)}), env)
    assert json.loads(dentro)["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    pai = cli.modo_hook(json.dumps({"cwd": str(tmp_path.parent)}), env)
    assert pai == ""  # pasta mãe comum (ex.: C:\dev) não recebe
    (tmp_path.parent / ".claude-plugin").mkdir(exist_ok=True)
    (tmp_path.parent / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
    pai = cli.modo_hook(json.dumps({"cwd": str(tmp_path.parent)}), env)
    assert pai  # pasta mãe que é o repositório do plugin
    avo = cli.modo_hook(json.dumps({"cwd": str(tmp_path.parent.parent)}), env)
    assert avo == ""  # mais acima (ex.: C:\dev) não recebe
    fora = tmp_path.parent / "outro_projeto"
    fora.mkdir(exist_ok=True)
    assert cli.modo_hook(json.dumps({"cwd": str(fora)}), env) == ""
    assert cli.modo_hook("{}", env) == ""
    assert cli.modo_hook("não é json", env) == ""
    com_bom = "\ufeff" + json.dumps({"cwd": str(camp)})
    assert cli.modo_hook(com_bom, env)


# --- várias campanhas em paralelo -------------------------------------------------

def montar_duas(tmp_path):
    a = montar(tmp_path, estado=estado_base(fome=3))
    b = tmp_path / "Outro Jogo"
    b.mkdir()
    e = estado_base(fome=1)
    e["campanha"] = e["personagem"]["nome"] = "Outro Jogo"
    (b / "estado.json").write_text(json.dumps(e), encoding="utf-8")
    (tmp_path / "_resumos").mkdir()
    return a, b


def test_pasta_ativa_com_campanha_explicita(tmp_path):
    a, b = montar_duas(tmp_path)
    assert [p.name for p in c.listar_jogos(str(tmp_path))] == ["Mara Voss", "Outro Jogo"]
    assert c.pasta_ativa(str(tmp_path), "") is None  # duas e nenhuma fixada
    assert c.pasta_ativa(str(tmp_path), "Mara Voss") == a
    assert c.pasta_ativa(str(tmp_path), "Mara Voss", "Outro Jogo") == b  # chamada vence a configuração
    assert c.pasta_ativa(str(tmp_path), "Mara Voss", "Nao Existe") is None  # não cai na configurada
    for ruim in ("..", "../x", "Mara Voss/npcs", "_resumos", ".git", "${user_config.x}"):
        assert c.pasta_jogo(str(tmp_path), ruim) is None


def test_hook_com_duas_campanhas_lista_as_duas(tmp_path):
    a, b = montar_duas(tmp_path)
    env = {"CLAUDE_PLUGIN_OPTION_PASTA_CAMPANHAS": str(tmp_path),
           "CLAUDE_PLUGIN_OPTION_CAMPANHA_ATIVA": ""}
    txt = json.loads(cli.modo_hook(json.dumps({"cwd": str(tmp_path)}), env))["hookSpecificOutput"]["additionalContext"]
    assert "Mara Voss" in txt and "Outro Jogo" in txt and "campanha" in txt
    assert "SEGREDO" not in txt and "_resumos" not in txt
    # aberta dentro da pasta de um jogo: só ele
    txt = json.loads(cli.modo_hook(json.dumps({"cwd": str(b)}), env))["hookSpecificOutput"]["additionalContext"]
    assert "Outro Jogo" in txt and "Mara Voss" not in txt


def test_cli_auditar_codigo_de_saida(tmp_path):
    camp = montar(tmp_path, ficha_fome=4)
    p = subprocess.run([sys.executable, str(RAIZ / "scripts" / "campanha.py"), "auditar", str(camp), "--json"],
                       capture_output=True, text=True, encoding="utf-8")
    assert p.returncode == 1
    assert any(a["codigo"] == "NUMERO_DIVERGENTE" for a in json.loads(p.stdout))
