"""Testes do índice do acervo com PDFs reais gerados no teste (PyMuPDF)."""

import sys
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import vtm_acervo as a  # noqa: E402


def pdf(caminho: Path, paginas: list[str]):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for texto in paginas:
        pg = doc.new_page()
        pg.insert_text((72, 72), texto, fontsize=10)
    doc.save(caminho)


def montar_acervo(raiz: Path):
    filler = "\n".join(["texto de preenchimento para a pagina ter conteudo"] * 3)
    pdf(raiz / "Vampiro a Máscara" / "Vampire the Masquerade.pdf", [
        "1\nIntro\n" + filler,
        "2\nBlood Surge adds dice to a pool.\n" + filler,
        "3\nRouse Check: roll one die.\n" + filler,
    ])
    pdf(raiz / "Vampiro a Máscara" / "Vampire The Masquerade 5.0 - Camarilla.pdf", [
        "10\nBlood Surge in the court.\n" + filler,
    ])
    pdf(raiz / "Vampiro a Máscara" / "Vampiro a Máscara - Livro de Clã - Ventrue - Biblioteca Élfica.pdf", [
        "5\nOs Ventrue e a Perdição do clã. Surto de Sangue.\n" + filler,
    ])
    pdf(raiz / "Vampiro o Réquiem" / "Vampiro o Réquiem - Módulo Básico.pdf", [
        "1\nBlood Surge no Réquiem não deve entrar.\n" + filler,
    ])


@pytest.fixture
def acervo(tmp_path):
    raiz = tmp_path / "acervo"
    montar_acervo(raiz)
    con = a.conectar(tmp_path / "idx" / "acervo.sqlite")
    st = a.indexar(raiz, con, aviso=None)
    return raiz, con, st


def test_classificacao(tmp_path):
    raiz = tmp_path
    assert a.classificar(raiz / "Vampiro a Máscara" / "Vampire the Masquerade.pdf", raiz).edicao == "core"
    l = a.classificar(raiz / "Vampiro a Máscara" / "Vampire The Masquerade 5.0 - Anarch.pdf", raiz)
    assert (l.edicao, l.idioma) == ("v5", "en")
    l = a.classificar(raiz / "Lobisomem o Apocalipse" / "Lobisomem o Apocalipse - Fianna - Biblioteca Élfica.pdf", raiz)
    assert (l.linha, l.edicao, l.idioma, l.titulo) == ("WtA", "classica", "pt", "Lobisomem o Apocalipse - Fianna")
    assert a.classificar(raiz / "Mago o Despertar" / "x.pdf", raiz) is None  # CofD fora (P9)


def test_classificacao_fora_do_layout_do_autor(tmp_path):
    """PDFs de outro jogador: sem as pastas por linha e com outros nomes de arquivo."""
    raiz = tmp_path
    l = a.classificar(raiz / "Vampire The Masquerade 5th Edition Core Rulebook.pdf", raiz)
    assert (l.edicao, l.linha, l.idioma) == ("core", "VtM", "en")
    assert a.classificar(raiz / "livros" / "VtM V5 Corebook.pdf", raiz).edicao == "core"
    assert a.classificar(raiz / "VtM V5 - Players Guide.pdf", raiz).edicao == "v5"
    assert a.classificar(raiz / "V5 Companion.pdf", raiz).edicao == "v5"
    assert a.classificar(raiz / "Vampiro a Mascara 3a Edicao.pdf", raiz).edicao == "classica"


def test_pagina_impressa():
    assert a.pagina_impressa("VA M P I R E S\n2 0 5\nHunger", 207) == 205
    assert a.pagina_impressa("Tabela\n7\n", 300) is None  # longe demais da página do PDF
    assert a.pagina_impressa("sem numero", 3) is None


def test_indexa_e_exclui_cofd(acervo):
    _, con, st = acervo
    assert st["novos"] == 3 and st["fora"] == 1
    assert a.status(con)["livros"] == 3


def test_busca_prioriza_core_e_cita_pagina(acervo):
    _, con, _ = acervo
    res = a.buscar(con, "Blood Surge")
    assert res[0]["livro"] == "Vampire the Masquerade" and res[0]["pagina"] == 2
    assert res[1]["edicao"] == "v5"
    assert all("Réquiem" not in r["livro"] for r in res)
    assert "«Blood»" in res[0]["trecho"]


def test_busca_sem_acento_e_filtros(acervo):
    _, con, _ = acervo
    res = a.buscar(con, "perdicao", idioma="pt")
    assert res and res[0]["linha"] == "VtM" and res[0]["edicao"] == "classica"
    assert a.buscar(con, "Blood Surge", edicao="classica") == []
    assert a.buscar(con, "") == []


def test_frase_exata(acervo):
    _, con, _ = acervo
    assert a.buscar(con, '"Rouse Check"')[0]["pagina"] == 3
    assert a.buscar(con, '"Check Rouse"') == []


@pytest.mark.skipif(a.tessdata() is None, reason="Tesseract não instalado")
def test_ocr_em_pagina_de_imagem(tmp_path):
    # Página com texto só como imagem: sem OCR não indexa; com OCR, a busca acha.
    fonte = fitz.open()
    fonte.new_page().insert_text((72, 120), "Taumaturgia Tremere sangue ritual\nda capela de Viena", fontsize=28)
    img = fonte[0].get_pixmap(dpi=200)
    raiz = tmp_path / "acervo" / "Vampiro a Máscara"
    raiz.mkdir(parents=True)
    doc = fitz.open()
    doc.new_page().insert_image(fitz.Rect(0, 0, 612, 792), pixmap=img)
    doc.save(raiz / "Vampiro a Máscara - Livro de Clã - Teste.pdf")
    con = a.conectar(tmp_path / "idx.sqlite")
    a.indexar(tmp_path / "acervo", con, aviso=None)
    assert a.buscar(con, "Taumaturgia") == []
    st = a.indexar(tmp_path / "acervo", con, ocr=True, aviso=None)
    assert st["atualizados"] == 1
    assert a.buscar(con, "Taumaturgia")


def test_reindexacao_incremental(acervo):
    raiz, con, _ = acervo
    st = a.indexar(raiz, con, aviso=None)
    assert st["pulados"] == 3 and st["novos"] == 0
