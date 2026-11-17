"""Conduta do narrador (F5 + F7): português de Portugal, latim sem tradução,
contrato de resposta, Fome divergente nas rolagens e decisões do narrador."""

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import vtm_campanha as c  # noqa: E402
import vtm_estilo as e  # noqa: E402


def _cods(problemas):
    return [(p.codigo, p.trecho) for p in problemas]


# ---------------------------------------------------------------- língua


def test_pt_pt_pega_as_construcoes_vistas_em_jogo():
    texto = ("Ele estava a falar quando ela saiu a murmurar.\n"
             "Saiu de lá com o crânio a latejar.\n"
             "Decidiu pô-lo na mesa. Amo-a, disse.\n"
             "A acção actual é um facto; o contacto ficou no registo.\n"
             "A rapariga foi à casa de banho.\n"
             "Tu sentes o frio nos teus ossos.\n")
    trechos = [t.lower() for _, t in _cods(e.checar_pt_pt(texto))]
    for esperado in ("estava a falar", "saiu a murmurar", "o crânio a latejar", "pô-lo", "amo-a",
                     "acção", "actual", "facto", "contacto", "registo", "rapariga", "casa de banho", "tu", "teus"):
        assert esperado in trechos, esperado


def test_pt_br_limpo_nao_gera_falso_positivo():
    texto = ("Ele estava falando quando ela saiu murmurando. Você sente o frio.\n"
             "Ela começou a falar e passou a usar o anel. De fato, o contato registrou a ação atual.\n"
             "Chegou a hora. Ele veio a pé e ficou a noite toda. Foi um ataque, e depois mais dois.\n"
             "O arquivo `objectos.md` e a tabela de **Fome** ficam como estão.\n")
    assert e.checar_pt_pt(texto) == []


def test_tu_so_vale_em_fala_de_npc():
    assert e.checar_pt_pt('— Tu não és bem-vinda aqui — diz o ancião.\n') == []
    assert e.checar_pt_pt('O ancião diz: "Tu não és bem-vinda aqui."\n') == []
    assert _cods(e.checar_pt_pt("O ancião olha para ti.\n")) == [("PT_PT", "ti")]


def test_latim_precisa_de_traducao_ao_lado():
    sem = e.checar_latim('Ele murmura *Bene vigilas, Valeri* e some.\nNa parede: "SANGVIS QVINTI LAPIDI"\n')
    assert [p.codigo for p in sem] == ["LATIM", "LATIM"]
    com = ('Ele murmura *Bene vigilas, Valeri* ("Vigias bem, Valério") e some.\n'
           'Na parede: "SANGVIS QVINTI LAPIDI" ("o sangue do Quinto, à pedra").\n'
           "Ela é *muito* cuidadosa com os **dados** e com o *Elysium*.\n")
    assert e.checar_latim(com) == []


# ---------------------------------------------------------------- contrato


def _exemplos_da_skill():
    """Blocos de exemplo de skills/narrar/SKILL.md, na ordem: (rótulo, texto)."""
    texto = (RAIZ / "skills" / "narrar" / "SKILL.md").read_text(encoding="utf-8")
    return re.findall(r"^(Ruim|Bom)[^\n]*:\n```\n(.*?)\n```", texto, flags=re.S | re.M)


def _separar_seletor(bloco):
    m = re.search(r"^\[Seletor: (.+)\]$", bloco, flags=re.M)
    rotulos = [r.strip() for r in m.group(1).split("|")] if m else None
    return re.sub(r"^\[Seletor: .+\]$", "", bloco, flags=re.M), rotulos


def test_exemplos_bons_da_skill_cumprem_o_contrato():
    bons = [b for rotulo, b in _exemplos_da_skill() if rotulo == "Bom"]
    assert len(bons) == 3
    for bloco in bons:
        texto, rotulos = _separar_seletor(bloco)
        assert e.checar_mensagem(texto, rotulos) == [], bloco[:60]


def test_exemplos_ruins_da_skill_sao_reprovados():
    ruins = [b for rotulo, b in _exemplos_da_skill() if rotulo == "Ruim"]
    assert len(ruins) == 3
    for bloco in ruins:
        assert e.checar_mensagem(bloco, None), bloco[:60]
    msgs = " ".join(p.mensagem for p in e.checar_mensagem(ruins[0], None))
    assert "português de Portugal" in msgs and "nota técnica" in msgs and "seletor" in msgs


def test_contrato_narracao_longa_tabela_e_seletor():
    base = ("O salão está frio.\n\n"
            "**A — Entrar:** ganho: ver quem está lá · risco: ser vista · teste: Destreza + Furtividade, 5 dados, DD 3, ~51%\n"
            "**B — Esperar:** ganho: ouvir a conversa · risco: perder a hora · sem teste\n")
    ok = ["Entrar", "Esperar", "Outra ação (descreva)"]
    assert e.checar_mensagem(base, ok) == []
    assert "seletor" in e.checar_mensagem(base, None)[0].mensagem
    assert "Outra ação" in e.checar_mensagem(base, ["Entrar", "Esperar"])[0].mensagem
    assert any("7 palavras" in p.mensagem for p in
               e.checar_mensagem(base, ["Entrar pela porta dos fundos sem ser vista hoje", "Outra ação (descreva)"]))
    longa = "palavra " * 160 + "\n\n" + base
    assert any("150 palavras" in p.mensagem for p in e.checar_mensagem(longa, ok))
    assert any("tabela" in p.mensagem for p in e.checar_mensagem("| Fome | 2 |\n|---|---|\n" + base, ok))
    sem_risco = base.replace("ganho: ouvir a conversa · risco: perder a hora · ", "")
    assert any("ganho e risco" in p.mensagem for p in e.checar_mensagem(sem_risco, ok))
    sem_dados = base.replace(", 5 dados, DD 3, ~51%", "")
    assert any("dados e DD" in p.mensagem for p in e.checar_mensagem(sem_dados, ok))
    quatro = "\n".join(f"Parada 5d (4N+1F) | DD 2 | [6][7][2][3] | (4) → ✓ Sucesso" for _ in range(4))
    assert any("mais de 3 rolagens" in p.mensagem for p in e.checar_mensagem(quatro + "\n\n" + base, ok))
    com_dn = "Decisão do narrador: ajudar o aliado dá +1 dado nesta cena.\n\n" + base
    assert e.checar_mensagem(com_dn, ok) == []


def test_cli_estilo(tmp_path):
    arq = tmp_path / "sessao_01.md"
    arq.write_text("Ela estava a falar.\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "estilo.py"), "checar", str(arq)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1 and "estava a falar" in r.stdout and "1 problema(s)" in r.stdout
    arq.write_text("Ela estava falando.\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "estilo.py"), "checar", str(arq)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0


# ---------------------------------------------------------------- auditoria de conduta


def _reg(cmd, **res):
    return json.dumps({"quando": "2026-01-01T00:00:00+00:00", "comando": cmd, "resultado": res}, ensure_ascii=False)


def _campanha(tmp_path):
    pasta = tmp_path / "Jogo"
    (pasta / "partidas" / "P" / "H" / "A").mkdir(parents=True)
    (pasta / "estado.json").write_text((RAIZ / "08_Templates" / "07_estado.json").read_text(encoding="utf-8"),
                                       encoding="utf-8")
    return pasta


def test_fome_divergente_no_registro(tmp_path):
    pasta = _campanha(tmp_path)
    linhas = [
        _reg("rouse", tipo="ROUSE", fome_antes=1, fome_depois=2, checks=[{"dados": [3], "sucesso": False}]),
        _reg("rolar 7 2 3 None", dados_fome=[4, 5], extra={"parada": 7, "fome": 2}),          # certo
        _reg("rouse", tipo="ROUSE", fome_antes=2, fome_depois=3, checks=[{"dados": [2], "sucesso": False}]),
        _reg("rolar 7 2 3 None", dados_fome=[4, 5], extra={"parada": 7, "fome": 2}),          # Fome de antes do Rouse
        _reg("rolar 5 0 2 None npc", dados_fome=[], extra={"parada": 5, "fome": 0}),          # NPC: ignora
        _reg("rolar 5 0 2 None", dados_fome=[], extra={"parada": 5, "fome": 0}),              # log antigo de NPC
        _reg("alimentar", tipo="ALIMENTACAO", fome_antes=3, fome_depois=1),
        _reg("surto_de_sangue", tipo="SURTO", rouse={"fome_antes": 1, "fome_depois": 2}),
        _reg("rouse", tipo="ROUSE", fome_antes=0, fome_depois=4,
             checks=[{"dados": [1], "sucesso": False}] * 10),                                 # lote partindo de 0
        "linha quebrada",
    ]
    (pasta / "rolagens.jsonl").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    div = c.fome_divergente(pasta)
    assert [n for n, _ in div] == [4, 9, 9]
    assert "Fome 2; o registro estava em Fome 3" in div[0][1]
    assert "partiu de Fome 0" in div[1][1] and "10 Rouses num lote" in div[2][1]
    achados = [a for a in c.auditar(pasta) if a.codigo == "FOME_DIVERGENTE"]
    assert len(achados) == 3 and all(a.nivel == "aviso" for a in achados)


def test_auditoria_aponta_estilo_nos_logs(tmp_path):
    pasta = _campanha(tmp_path)
    log = pasta / "partidas" / "P" / "H" / "A" / "sessao_01.md"
    log.write_text("# Sessão 1\nEla estava a falar. Ele disse *Bene vigilas, Valeri* e saiu.\n", encoding="utf-8")
    estilo = [a for a in c.auditar(pasta) if a.codigo == "ESTILO"]
    assert len(estilo) == 2 and estilo[0].arquivo.endswith("sessao_01.md")
    assert "estava a falar" in estilo[0].mensagem and "latim" in estilo[1].mensagem
    log.write_text("# Sessão 1\nEla estava falando.\n", encoding="utf-8")
    assert not [a for a in c.auditar(pasta) if a.codigo == "ESTILO"]


def test_decisoes_do_narrador_registro_e_pendencia(tmp_path):
    pasta = _campanha(tmp_path)
    assert c.decisoes_narrador(pasta) == []
    d1 = c.registrar_decisao(pasta, "Falhar ao resistir custa 1 de Força de Vontade", "o Core não cobre | busquei")
    d2 = c.registrar_decisao(pasta, "Ajuda do aliado dá +1 dado", "sem regra no Core para este caso")
    assert (d1["id"], d2["id"], d1["sessao"]) == ("DN-1", "DN-2", "S00")
    lidas = c.decisoes_narrador(pasta)
    assert [d["situacao"] for d in lidas] == ["pendente", "pendente"] and "/" in lidas[0]["motivo"]
    pend = [a for a in c.auditar(pasta) if a.codigo == "DECISAO_PENDENTE"]
    assert len(pend) == 1 and "2 decisões" in pend[0].mensagem and "DN-1, DN-2" in pend[0].mensagem
    arq = pasta / "decisoes_narrador.md"
    arq.write_text(arq.read_text(encoding="utf-8").replace("| pendente |", "| aprovada (RC-3) |", 1)
                   .replace("| pendente |", "| descartada |", 1), encoding="utf-8")
    assert not [a for a in c.auditar(pasta) if a.codigo == "DECISAO_PENDENTE"]
    assert c.registrar_decisao(pasta, "Outra", "motivo")["id"] == "DN-3"
    import pytest
    with pytest.raises(ValueError, match="obrigatórios"):
        c.registrar_decisao(pasta, "", "x")
    # o modelo do plugin é lido pelo mesmo leitor
    modelo = (RAIZ / "08_Templates" / "13_decisoes_narrador.md").read_text(encoding="utf-8")
    arq.write_text(modelo, encoding="utf-8")
    assert [d["situacao"] for d in c.decisoes_narrador(pasta)] == ["pendente", "aprovada (RC-3)", "descartada"]
