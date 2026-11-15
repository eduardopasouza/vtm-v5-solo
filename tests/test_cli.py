"""Teste de ponta a ponta do CLI (subprocesso, semente fixa)."""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "scripts" / "vtm_dice.py"


def rodar(*args, cwd=None):
    p = subprocess.run([sys.executable, str(CLI), *args], capture_output=True,
                       text=True, encoding="utf-8", cwd=cwd)
    return p.returncode, p.stdout


def json_de(saida):
    return json.loads(saida.split("---JSON---", 1)[1])


def test_roll_fome_substitui(tmp_path):
    code, out = rodar("--semente", "7", "roll", "5", "2", "3", cwd=tmp_path)
    assert code == 0
    r = json_de(out)
    assert len(r["dados_normais"]) == 3 and len(r["dados_fome"]) == 2


def test_todos_os_comandos_rodam(tmp_path):
    casos = [
        ["rouse", "2", "--bp", "3", "--nivel", "1"],
        ["despertar", "1"],
        ["surge", "4", "1", "2", "3"],
        ["mend", "3", "1", "2"],
        ["mend-agg", "1", "1"],
        ["frenzy", "4", "7", "3"],
        ["remorse", "6", "2"],
        ["tracker", "3", "2"],
        ["conflict", "5", "1", "4", "--dois-lados", "--arma-a", "2"],
        ["damage", "5", "superficial"],
        ["feed", "humano_seguro", "3", "1"],
        ["reroll", "--normais", "2,3,4,8", "--fome", "1", "--indices", "0,1", "--dificuldade", "3"],
    ]
    for c in casos:
        code, out = rodar("--semente", "1", *c, cwd=tmp_path)
        assert code == 0, (c, out)
        json_de(out)


def test_erro_de_regra_sai_com_codigo_2(tmp_path):
    code, out = rodar("rouse", "5", cwd=tmp_path)
    assert code == 2 and "Fome 5" in out
    code, out = rodar("roll", "5", "1", cwd=tmp_path)
    assert code == 2 and "dificuldade" in out


def test_registro_na_campanha(tmp_path):
    code, _ = rodar("--campanha", str(tmp_path), "--semente", "3", "remorse", "7", "1")
    assert code == 0
    linhas = (tmp_path / "rolagens.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 1 and json.loads(linhas[0])["resultado"]["tipo"] == "REMORSO"
