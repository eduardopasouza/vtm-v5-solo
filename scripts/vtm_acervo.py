"""Índice local do acervo de PDFs (frente 8).

O texto extraído dos livros é conteúdo de terceiros: o índice fica numa pasta
local do usuário (padrão `%LOCALAPPDATA%/vtm-v5/acervo.sqlite`, ou a variável
VTM_INDICE), nunca no repositório. A busca devolve livro, página e um trecho
curto, para o narrador citar a fonte.

Prioridade das fontes (decisão P6): V5 Core > suplementos V5 > edições antigas.
O Crônicas das Trevas (CofD) fica fora do índice (P9).
"""

from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

# Pastas do acervo -> linha. None = fora do índice (CofD, P9).
LINHAS = {
    "vampiro a máscara": "VtM",
    "vampiro a idade das trevas": "VtDA",
    "lobisomem o apocalipse": "WtA",
    "mago a ascensão": "MtA",
    "hunter_ the reckoning": "HtR",
    "vampiro o réquiem": None,
    "mago o despertar": None,
    "lobisomem os destituídos": None,
}

_V5 = re.compile(r"(5\.0|\bV5\b|VtM V5|5th Edition|5e\b|Vampire the Masquerade\.pdf$)", re.IGNORECASE)
_INGLES = re.compile(r"(Vampire|Masquerade|Clanbook|Companion|Hunter|Reckoning|Cults of)", re.IGNORECASE)
_CORE_V5 = "vampire the masquerade.pdf"
# Outros nomes comuns do livro básico V5 em inglês: "... 5th Edition Core Rulebook",
# "V5 Core", "VtM V5 Corebook". Suplementos não têm "core" no nome.
def eh_core_v5(nome: str) -> bool:
    n = nome.lower()
    if n == _CORE_V5:
        return True
    return bool("core" in n and re.search(r"vampire|vtm|masquerade", n)
                and re.search(r"5th|\bv5\b|5e\b|5\.0", n)
                and not re.search(r"companion|player", n))

PRIORIDADE = {"core": 1, "v5": 2, "classica": 4}


def indice_padrao() -> Path:
    env = os.environ.get("VTM_INDICE", "").strip()
    if env and "${" not in env:
        return Path(env)
    base = os.environ.get("LOCALAPPDATA") or str(
        Path.home() / ("AppData/Local" if os.name == "nt" else ".local/share"))
    return Path(base) / "vtm-v5" / "acervo.sqlite"


@dataclass
class Livro:
    arquivo: str
    titulo: str
    linha: str
    edicao: str      # "core", "v5" ou "classica"
    idioma: str      # "en" ou "pt"


def classificar(caminho: Path, raiz: Path) -> Livro | None:
    """Classifica um PDF pela pasta e pelo nome. None = fora do índice."""
    rel = caminho.relative_to(raiz)
    pasta = rel.parts[0].lower() if len(rel.parts) > 1 else ""
    if pasta in LINHAS:
        linha = LINHAS[pasta]
        if linha is None:
            return None
    else:
        linha = "outro"
    nome = caminho.name
    titulo = re.sub(r"\s*-\s*Biblioteca Élfica", "", caminho.stem).strip(" -_")
    if eh_core_v5(nome):
        edicao = "core"
        if linha == "outro":
            linha = "VtM"
    elif linha in ("VtM", "outro") and _V5.search(nome) and re.search(r"vampire|vtm|masquerade", nome, re.I) or "companion" in nome.lower() or "cults of the blood gods" in nome.lower():
        edicao = "v5"
    else:
        edicao = "classica"
    idioma = "en" if _INGLES.search(nome) and not re.search(r"Vampiro|Lobisomem|Mago", nome) else "pt"
    return Livro(str(rel).replace("\\", "/"), titulo, linha, edicao, idioma)


# --------------------------------------------------------------------------
# Página impressa
# --------------------------------------------------------------------------

_NUM_PAGINA = re.compile(r"^\d(?:\s?\d){0,3}$")


def pagina_impressa(texto: str, pagina_pdf: int) -> int | None:
    """Procura o número de página impresso nas primeiras e últimas linhas do
    texto extraído (ex.: "2 0 5" no V5 Core). Aceita só números próximos da
    página do PDF, para não confundir com valores de tabela."""
    linhas = [x.strip() for x in texto.splitlines() if x.strip()]
    candidatos = linhas[:4] + linhas[-4:]
    for c in candidatos:
        if _NUM_PAGINA.match(c):
            n = int(c.replace(" ", ""))
            if 0 < n and abs(pagina_pdf - n) <= 40:
                return n
    return None


# --------------------------------------------------------------------------
# Banco
# --------------------------------------------------------------------------

ESQUEMA = """
CREATE TABLE IF NOT EXISTS livros (
  id INTEGER PRIMARY KEY,
  arquivo TEXT UNIQUE NOT NULL,
  titulo TEXT NOT NULL,
  linha TEXT NOT NULL,
  edicao TEXT NOT NULL,
  idioma TEXT NOT NULL,
  prioridade INTEGER NOT NULL,
  total_paginas INTEGER NOT NULL,
  paginas_sem_texto INTEGER NOT NULL,
  ocr INTEGER NOT NULL DEFAULT 0,
  tamanho INTEGER NOT NULL,
  mtime REAL NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS paginas USING fts5(
  texto,
  livro_id UNINDEXED,
  pagina_pdf UNINDEXED,
  pagina_impressa UNINDEXED,
  tokenize = 'unicode61 remove_diacritics 2'
);
"""


def conectar(caminho: Path | str | None = None) -> sqlite3.Connection:
    caminho = Path(caminho) if caminho else indice_padrao()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
    con.executescript(ESQUEMA)
    return con


def tessdata() -> str | None:
    """Pasta dos modelos do Tesseract: TESSDATA_PREFIX ou a instalação padrão do Windows."""
    env = os.environ.get("TESSDATA_PREFIX")
    if env and Path(env).is_dir():
        return env
    padrao = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tessdata"
    return str(padrao) if padrao.is_dir() else None


def _texto_pagina(pagina, ocr: bool, idioma: str) -> tuple[str, bool]:
    texto = pagina.get_text()
    if len(texto.strip()) >= 40 or not ocr:
        return texto, False
    try:
        tp = pagina.get_textpage_ocr(language="por+eng" if idioma == "pt" else "eng", dpi=200, full=True,
                                     tessdata=tessdata())
        return pagina.get_text(textpage=tp), True
    except Exception:
        return texto, False


def indexar(raiz: str | Path, con: sqlite3.Connection, ocr: bool = False,
            so: str | None = None, aviso=print) -> dict:
    """Indexa (ou reindexa os alterados) os PDFs de `raiz`. Incremental: pula
    livros com mesmo tamanho e data, salvo se `ocr` pedir páginas sem texto."""
    import fitz  # PyMuPDF

    raiz = Path(raiz)
    stats = {"novos": 0, "atualizados": 0, "pulados": 0, "fora": 0, "paginas": 0, "erros": []}
    for pdf in sorted(raiz.rglob("*.pdf")):
        if so and so.lower() not in pdf.name.lower():
            continue
        livro = classificar(pdf, raiz)
        if livro is None:
            stats["fora"] += 1
            continue
        st = pdf.stat()
        linha_db = con.execute("SELECT id, tamanho, mtime, paginas_sem_texto, ocr FROM livros WHERE arquivo=?",
                               (livro.arquivo,)).fetchone()
        if linha_db and linha_db[1] == st.st_size and abs(linha_db[2] - st.st_mtime) < 1 \
                and not (ocr and linha_db[3] > 0 and not linha_db[4]):
            stats["pulados"] += 1
            continue
        try:
            doc = fitz.open(pdf)
        except Exception as e:  # PDF corrompido
            stats["erros"].append(f"{livro.arquivo}: {e}")
            continue
        if linha_db:
            con.execute("DELETE FROM paginas WHERE livro_id=?", (linha_db[0],))
            con.execute("DELETE FROM livros WHERE id=?", (linha_db[0],))
        cur = con.execute(
            "INSERT INTO livros (arquivo, titulo, linha, edicao, idioma, prioridade, total_paginas, "
            "paginas_sem_texto, ocr, tamanho, mtime) VALUES (?,?,?,?,?,?,?,0,0,?,?)",
            (livro.arquivo, livro.titulo, livro.linha, livro.edicao, livro.idioma,
             PRIORIDADE[livro.edicao], doc.page_count, st.st_size, st.st_mtime))
        livro_id = cur.lastrowid
        sem_texto, usou_ocr = 0, False
        for i, pagina in enumerate(doc, 1):
            texto, foi_ocr = _texto_pagina(pagina, ocr, livro.idioma)
            usou_ocr |= foi_ocr
            if len(texto.strip()) < 40:
                sem_texto += 1
                continue
            con.execute("INSERT INTO paginas (texto, livro_id, pagina_pdf, pagina_impressa) VALUES (?,?,?,?)",
                        (texto, livro_id, i, pagina_impressa(texto, i)))
            stats["paginas"] += 1
        con.execute("UPDATE livros SET paginas_sem_texto=?, ocr=? WHERE id=?", (sem_texto, int(usou_ocr), livro_id))
        con.commit()
        stats["atualizados" if linha_db else "novos"] += 1
        if aviso:
            aviso(f"  {livro.arquivo}: {doc.page_count} p., {sem_texto} sem texto")
    return stats


# --------------------------------------------------------------------------
# Busca
# --------------------------------------------------------------------------


def consulta_fts(consulta: str) -> str:
    """Converte texto livre em consulta FTS5. Entre aspas = frase exata;
    senão, todos os termos (E)."""
    consulta = consulta.strip()
    if '"' in consulta:
        frases = re.findall(r'"([^"]+)"', consulta)
        resto = re.sub(r'"[^"]+"', " ", consulta)
        partes = [f'"{f}"' for f in frases] + [f'"{t}"' for t in re.findall(r"\w+", resto)]
    else:
        partes = [f'"{t}"' for t in re.findall(r"\w+", consulta)]
    return " AND ".join(partes)


def buscar(con: sqlite3.Connection, consulta: str, linha: str | None = None,
           edicao: str | None = None, idioma: str | None = None, limite: int = 8) -> list[dict]:
    q = consulta_fts(consulta)
    if not q:
        return []
    filtros, args = [], [q]
    for campo, valor in (("l.linha", linha), ("l.edicao", edicao), ("l.idioma", idioma)):
        if valor:
            filtros.append(f"{campo} = ?")
            args.append(valor)
    where = (" AND " + " AND ".join(filtros)) if filtros else ""
    args.append(max(1, min(limite, 30)))
    sql = f"""
      SELECT l.titulo, l.linha, l.edicao, l.idioma, paginas.pagina_pdf, paginas.pagina_impressa,
             snippet(paginas, 0, '«', '»', ' … ', 24) AS trecho, bm25(paginas) AS score
      FROM paginas JOIN livros l ON l.id = paginas.livro_id
      WHERE paginas MATCH ?{where}
      ORDER BY l.prioridade, score
      LIMIT ?"""
    out = []
    for titulo, ln, ed, idi, pdf, imp, trecho, score in con.execute(sql, args):
        out.append({"livro": titulo, "linha": ln, "edicao": ed, "idioma": idi,
                    "pagina": imp, "pagina_pdf": pdf,
                    "citacao": f"{titulo}, p. {imp}" if imp else f"{titulo}, p. {pdf} do PDF",
                    "trecho": re.sub(r"\s+", " ", trecho).strip()})
    return out


def status(con: sqlite3.Connection) -> dict:
    livros = con.execute("SELECT COUNT(*), COALESCE(SUM(total_paginas),0), COALESCE(SUM(paginas_sem_texto),0), "
                         "COALESCE(SUM(ocr),0) FROM livros").fetchone()
    por_linha = dict(con.execute("SELECT linha || '/' || edicao, COUNT(*) FROM livros GROUP BY 1").fetchall())
    sem_texto = [r[0] for r in con.execute(
        "SELECT titulo FROM livros WHERE paginas_sem_texto * 2 > total_paginas ORDER BY titulo")]
    return {"livros": livros[0], "paginas": livros[1], "paginas_sem_texto": livros[2],
            "livros_com_ocr": livros[3], "por_linha": por_linha, "livros_majoritariamente_sem_texto": sem_texto}
