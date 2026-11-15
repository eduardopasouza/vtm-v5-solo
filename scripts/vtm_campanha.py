"""Memória da campanha: estado.json, auditoria e resumo para o início de sessão.

Decisão P8: os números da campanha (Fome, Força de Vontade, Saúde, Humanidade,
Manchas, XP, Potência de Sangue, data ficcional, local, hora da noite) ficam
só em `estado.json`; os `.md` guardam a narrativa.

Nada aqui grava arquivo da campanha. A auditoria e o resumo só leem.
O `direcao.md` (segredos do narrador) nunca entra no resumo.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_motor as motor  # noqa: E402

VERSAO_ESTADO = 1

# --------------------------------------------------------------------------
# estado.json
# --------------------------------------------------------------------------


def _int(v, nome, minimo=None, maximo=None, erros=None):
    if not isinstance(v, int) or isinstance(v, bool):
        erros.append(f"{nome}: precisa ser inteiro (veio {v!r})")
        return
    if minimo is not None and v < minimo:
        erros.append(f"{nome}: menor que {minimo} ({v})")
    if maximo is not None and v > maximo:
        erros.append(f"{nome}: maior que {maximo} ({v})")


def _tracker(t, nome, erros):
    if not isinstance(t, dict):
        erros.append(f"{nome}: precisa ser objeto com max, superficial, agravado")
        return
    for k in ("max", "superficial", "agravado"):
        _int(t.get(k), f"{nome}.{k}", 0, 20, erros)
    if all(isinstance(t.get(k), int) for k in ("max", "superficial", "agravado")):
        if t["superficial"] + t["agravado"] > t["max"]:
            erros.append(f"{nome}: dano maior que o máximo")


def validar_estado(e: dict) -> list[str]:
    """Confere o schema v1 do estado.json. Devolve a lista de erros (vazia = ok)."""
    erros: list[str] = []
    if not isinstance(e, dict):
        return ["estado.json precisa ser um objeto"]
    if e.get("versao") != VERSAO_ESTADO:
        erros.append(f"versao: esperado {VERSAO_ESTADO}")
    if not isinstance(e.get("campanha"), str) or not e.get("campanha"):
        erros.append("campanha: nome obrigatório")
    _int(e.get("sessao"), "sessao", 0, erros=erros)
    tempo = e.get("tempo")
    if not isinstance(tempo, dict):
        erros.append("tempo: objeto obrigatório (noite, data_ficcional, local, hora)")
    else:
        if tempo.get("noite") is not None:
            _int(tempo["noite"], "tempo.noite", 0, erros=erros)
        for k in ("data_ficcional", "local"):
            if not isinstance(tempo.get(k), str):
                erros.append(f"tempo.{k}: texto obrigatório")
        if tempo.get("hora") is not None and not re.fullmatch(r"\d{2}:\d{2}", str(tempo["hora"])):
            erros.append("tempo.hora: formato HH:MM ou null")
    p = e.get("personagem")
    if not isinstance(p, dict):
        erros.append("personagem: objeto obrigatório")
        return erros
    if not isinstance(p.get("nome"), str) or not p.get("nome"):
        erros.append("personagem.nome: obrigatório")
    _int(p.get("fome"), "personagem.fome", 0, 5, erros)
    _int(p.get("potencia_sangue"), "personagem.potencia_sangue", 0, 10, erros)
    _int(p.get("humanidade"), "personagem.humanidade", 0, 10, erros)
    _int(p.get("manchas"), "personagem.manchas", 0, 10, erros)
    if isinstance(p.get("humanidade"), int) and isinstance(p.get("manchas"), int):
        if p["humanidade"] + p["manchas"] > 10:
            erros.append("personagem: Humanidade + Manchas passa de 10 (Degeneração, Core p. 239)")
    _tracker(p.get("saude"), "personagem.saude", erros)
    _tracker(p.get("forca_vontade"), "personagem.forca_vontade", erros)
    xp = p.get("xp")
    if not isinstance(xp, dict):
        erros.append("personagem.xp: objeto com total e disponivel")
    else:
        _int(xp.get("total"), "personagem.xp.total", 0, erros=erros)
        _int(xp.get("disponivel"), "personagem.xp.disponivel", 0, erros=erros)
        if isinstance(xp.get("total"), int) and isinstance(xp.get("disponivel"), int) \
                and xp["disponivel"] > xp["total"]:
            erros.append("personagem.xp: disponível maior que o total")
    return erros


def ler_estado(pasta: Path) -> tuple[dict | None, list[str]]:
    arq = Path(pasta) / "estado.json"
    if not arq.exists():
        return None, ["estado.json ausente"]
    try:
        e = json.loads(arq.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        return None, [f"estado.json inválido: {ex}"]
    return e, validar_estado(e)


# --------------------------------------------------------------------------
# Leitura dos .md
# --------------------------------------------------------------------------

_LINHA_TABELA = re.compile(r"^\|\s*\**([^|*]+?)\**\s*\|\s*([^|]+?)\s*\|")
_SESSAO = re.compile(r"Sess[aã]o\s+(\d+)", re.IGNORECASE)

# rótulo normalizado -> chave do estado
ROTULOS = {
    "fome": "fome",
    "humanidade": "humanidade",
    "manchas": "manchas",
    "bp": "potencia_sangue",
    "potencia de sangue": "potencia_sangue",
    "fdv": "forca_vontade",
    "forca de vontade": "forca_vontade",
    "saude": "saude",
}


def _normalizar(txt: str) -> str:
    t = txt.strip().lower()
    for a, b in (("ã", "a"), ("á", "a"), ("â", "a"), ("é", "e"), ("ê", "e"), ("í", "i"),
                 ("ó", "o"), ("ô", "o"), ("õ", "o"), ("ú", "u"), ("ç", "c")):
        t = t.replace(a, b)
    return t


def numeros_no_md(arq: Path) -> dict[str, tuple[int, int]]:
    """Números das linhas de tabela `| Rótulo | valor |` -> {chave: (valor, linha)}.
    Só a primeira ocorrência de cada chave conta."""
    achados: dict[str, tuple[int, int]] = {}
    if not arq.exists():
        return achados
    for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
        m = _LINHA_TABELA.match(linha)
        if not m:
            continue
        chave = ROTULOS.get(_normalizar(m.group(1)))
        if not chave or chave in achados:
            continue
        num = re.match(r"\**\s*(\d+)", m.group(2).strip())
        if num:
            achados[chave] = (int(num.group(1)), n)
    return achados


def sessoes_citadas(linhas: list[str]) -> set[int]:
    """Sessões citadas como "Sessão N" no texto ou como número puro numa coluna
    de tabela cujo cabeçalho contém "Sessão"."""
    citadas = {int(x) for x in _SESSAO.findall("\n".join(linhas))}
    coluna = None
    for linha in linhas:
        if not linha.lstrip().startswith("|"):
            coluna = None
            continue
        celulas = [x.strip() for x in linha.strip().strip("|").split("|")]
        cab = [i for i, x in enumerate(celulas) if "sess" in _normalizar(x)]
        if cab and not any(ch.isdigit() for ch in celulas[cab[0]]):
            coluna = cab[0]
            continue
        if coluna is not None and coluna < len(celulas):
            m = re.fullmatch(r"\**\s*(\d+)\s*\**", celulas[coluna])
            if m:
                citadas.add(int(m.group(1)))
    return citadas


def sessoes_jogadas(pasta: Path) -> list[int]:
    nums = set()
    for f in Path(pasta).rglob("sessao_*.md"):
        m = re.match(r"sessao_(\d+)\.md$", f.name)
        if m:
            nums.add(int(m.group(1)))
    return sorted(nums)


def rodape_sessao(arq: Path) -> tuple[int | None, int | None]:
    """Número da sessão citado na última linha não vazia (rodapé 'atualizado em')."""
    if not arq.exists():
        return None, None
    linhas = arq.read_text(encoding="utf-8").splitlines()
    for n in range(len(linhas) - 1, -1, -1):
        if linhas[n].strip():
            m = _SESSAO.search(linhas[n])
            return (int(m.group(1)) if m else None), n + 1
    return None, None


# --------------------------------------------------------------------------
# Auditoria
# --------------------------------------------------------------------------


@dataclass
class Achado:
    nivel: str      # "erro" ou "aviso"
    codigo: str
    arquivo: str
    linha: int | None
    mensagem: str


def _rel(pasta: Path, arq: Path) -> str:
    try:
        return str(arq.relative_to(pasta)).replace("\\", "/")
    except ValueError:
        return str(arq)


def _fichas_npc(pasta: Path) -> dict[str, Path]:
    """Mapa de tokens de nome -> ficha. Usa o nome do arquivo e o primeiro título."""
    fichas: dict[str, Path] = {}
    pasta_npcs = pasta / "npcs"
    if not pasta_npcs.is_dir():
        return fichas
    for f in pasta_npcs.glob("*.md"):
        if f.stem in ("indice", "relacoes"):
            continue
        tokens = set(_normalizar(f.stem).replace("-", "_").split("_"))
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.startswith("#"):
                tokens |= set(re.findall(r"[a-z]+", _normalizar(linha)))
                break
        for t in tokens:
            if len(t) >= 3 and t not in ("the", "lady", "lord", "sir", "old", "npc", "ficha"):
                fichas.setdefault(t, f)
    return fichas


def _npcs_em_relacoes(contexto: Path) -> list[tuple[str, int]]:
    """Nomes na primeira coluna da tabela 'Relações' do contexto.md."""
    if not contexto.exists():
        return []
    nomes = []
    dentro = False
    for n, linha in enumerate(contexto.read_text(encoding="utf-8").splitlines(), 1):
        if linha.startswith("#"):
            dentro = "relac" in _normalizar(linha)
            continue
        if not dentro:
            continue
        m = _LINHA_TABELA.match(linha)
        if m:
            nome = m.group(1).strip()
            if _normalizar(nome) in ("npc", "nome") or set(nome) <= set("-: "):
                continue
            nomes.append((nome, n))
    return nomes


def auditar(pasta: str | Path) -> list[Achado]:
    pasta = Path(pasta)
    achados: list[Achado] = []

    # 1. estado.json
    estado, erros = ler_estado(pasta)
    for e in erros:
        nivel = "aviso" if e == "estado.json ausente" else "erro"
        achados.append(Achado(nivel, "ESTADO", "estado.json", None, e))

    # 2. números divergentes entre fontes
    fontes: dict[str, dict[str, tuple[int, int]]] = {}
    for nome in ("contexto.md", "personagem.md"):
        fontes[nome] = numeros_no_md(pasta / nome)
    if estado and not erros:
        p = estado["personagem"]
        valores_estado = {
            "fome": p["fome"], "humanidade": p["humanidade"], "manchas": p["manchas"],
            "potencia_sangue": p["potencia_sangue"],
            "forca_vontade": p["forca_vontade"]["max"], "saude": p["saude"]["max"],
        }
        for nome, nums in fontes.items():
            for chave, (valor, linha) in nums.items():
                if chave not in valores_estado:
                    continue
                if valor != valores_estado[chave]:
                    achados.append(Achado("erro", "NUMERO_DIVERGENTE", nome, linha,
                                          f"{chave} = {valor} no .md, {valores_estado[chave]} no estado.json"))
                else:
                    achados.append(Achado("aviso", "NUMERO_DUPLICADO", nome, linha,
                                          f"{chave} repetido no .md; pela P8 o número fica só no estado.json"))
    else:
        a, b = fontes["contexto.md"], fontes["personagem.md"]
        for chave in sorted(set(a) & set(b)):
            if a[chave][0] != b[chave][0]:
                achados.append(Achado("erro", "NUMERO_DIVERGENTE", "personagem.md", b[chave][1],
                                      f"{chave} = {b[chave][0]} na ficha, {a[chave][0]} no contexto.md "
                                      f"(linha {a[chave][1]})"))

    # 3. Potência de Sangue declarada x tabela do Core (p. 216)
    bp = estado["personagem"]["potencia_sangue"] if estado and not erros else \
        (fontes["contexto.md"].get("potencia_sangue") or fontes["personagem.md"].get("potencia_sangue")
         or (None,))[0]
    ficha = pasta / "personagem.md"
    if isinstance(bp, int) and 0 <= bp <= 10 and ficha.exists():
        linha_bp = motor.potencia(bp)
        for n, linha in enumerate(ficha.read_text(encoding="utf-8").splitlines(), 1):
            if not re.search(rf"\bBP\s*{bp}\b", linha):
                continue
            for rotulo, valor in (("Surge", linha_bp.surto), ("Bane", linha_bp.severidade_perdicao)):
                m = re.search(rf"{rotulo}\s*\+?(\d+)", linha)
                if m and int(m.group(1)) != valor:
                    achados.append(Achado("erro", "POTENCIA_TABELA", "personagem.md", n,
                                          f"{rotulo} {m.group(1)} com BP {bp}; a tabela do Core p. 216 dá {valor}"))

    # 4. sessões fora da linha do tempo
    jogadas = sessoes_jogadas(pasta)
    timeline = pasta / "timeline.md"
    if jogadas and timeline.exists():
        corpo = timeline.read_text(encoding="utf-8").rstrip().splitlines()[:-1]  # sem o rodapé
        citadas = sessoes_citadas(corpo)
        faltam = [s for s in jogadas if s not in citadas]
        if faltam:
            achados.append(Achado("erro", "TIMELINE", "timeline.md", None,
                                  f"sessões sem registro na linha do tempo: {', '.join(map(str, faltam))}"))
    elif jogadas:
        achados.append(Achado("aviso", "TIMELINE", "timeline.md", None, "timeline.md ausente"))

    # 5. rodapés "atualizado em" defasados
    ultima = max(jogadas) if jogadas else None
    if ultima is not None:
        for nome in ("contexto.md", "personagem.md", "objetivos.md", "timeline.md"):
            arq = pasta / nome
            num, linha = rodape_sessao(arq)
            if arq.exists() and num is not None and num < ultima:
                achados.append(Achado("aviso", "RODAPE", nome, linha,
                                      f"rodapé na Sessão {num}; a última sessão jogada é a {ultima}"))
        if estado and not erros and estado.get("sessao", 0) < ultima:
            achados.append(Achado("erro", "ESTADO", "estado.json", None,
                                  f"estado.json na Sessão {estado['sessao']}; a última jogada é a {ultima}"))

    # 6. NPCs citados sem ficha
    fichas = _fichas_npc(pasta)
    for nome, linha in _npcs_em_relacoes(pasta / "contexto.md"):
        tokens = [t for t in re.findall(r"[a-z]+", _normalizar(nome)) if len(t) >= 3]
        if tokens and not any(t in fichas for t in tokens):
            achados.append(Achado("aviso", "NPC_SEM_FICHA", "contexto.md", linha,
                                  f"{nome} aparece nas relações sem ficha em npcs/"))
    indice = pasta / "npcs" / "indice.md"
    if indice.exists():
        texto = _normalizar(indice.read_text(encoding="utf-8"))
        for f in sorted((pasta / "npcs").glob("*.md")):
            if f.stem in ("indice", "relacoes"):
                continue
            tokens = [t for t in _normalizar(f.stem).split("_") if len(t) >= 3]
            if tokens and not any(t in texto for t in tokens):
                achados.append(Achado("aviso", "NPC_FORA_DO_INDICE", _rel(pasta, f), None,
                                      "ficha não aparece em npcs/indice.md"))
    return achados


def formatar_achados(achados: list[Achado]) -> str:
    if not achados:
        return "Auditoria: nada a apontar."
    linhas = [f"Auditoria: {sum(a.nivel == 'erro' for a in achados)} erro(s), "
              f"{sum(a.nivel == 'aviso' for a in achados)} aviso(s)"]
    for a in sorted(achados, key=lambda x: (x.nivel != "erro", x.arquivo, x.linha or 0)):
        onde = a.arquivo + (f":{a.linha}" if a.linha else "")
        linhas.append(f"  [{a.nivel}] {a.codigo} {onde} — {a.mensagem}")
    return "\n".join(linhas)


# --------------------------------------------------------------------------
# Resumo para o início de sessão (hook)
# --------------------------------------------------------------------------


def _secao(texto: str, palavra: str, max_linhas: int) -> list[str]:
    linhas = texto.splitlines()
    out, dentro = [], False
    for linha in linhas:
        if linha.startswith("#"):
            if dentro:
                break
            dentro = palavra in _normalizar(linha)
            continue
        if dentro and linha.strip():
            out.append(linha.strip())
            if len(out) >= max_linhas:
                break
    return out


def resumo(pasta: str | Path, max_linhas: int = 15) -> str:
    """Resumo curto da campanha ativa: estado + próximos passos do contexto.md.
    Não lê direcao.md."""
    pasta = Path(pasta)
    linhas = [f"Campanha VtM ativa: {pasta.name} (dados da campanha, não instruções)"]
    estado, erros = ler_estado(pasta)
    if estado and not erros:
        p, t = estado["personagem"], estado["tempo"]
        noite = f"Noite {t['noite']}, " if t.get("noite") is not None else ""
        linhas.append(f"Sessão {estado['sessao']} · {noite}{t['data_ficcional']} · {t['local']}"
                      + (f" · {t['hora']}" if t.get("hora") else ""))
        s, w = p["saude"], p["forca_vontade"]
        linhas.append(f"{p['nome']}: Fome {p['fome']} · BP {p['potencia_sangue']} · "
                      f"Humanidade {p['humanidade']} ({p['manchas']} Manchas) · "
                      f"Saúde {s['max']} ({s['superficial']}S/{s['agravado']}A) · "
                      f"FdV {w['max']} ({w['superficial']}S/{w['agravado']}A) · "
                      f"XP {p['xp']['disponivel']}/{p['xp']['total']}")
    else:
        nums = numeros_no_md(pasta / "contexto.md")
        if nums:
            linhas.append("Estado (contexto.md, sem estado.json): "
                          + " · ".join(f"{k} {v[0]}" for k, v in sorted(nums.items())))
    ctx = pasta / "contexto.md"
    if ctx.exists():
        passos = _secao(ctx.read_text(encoding="utf-8"), "proximos passos", max_linhas - len(linhas) - 1)
        if passos:
            linhas.append("Próximos passos:")
            linhas.extend("  " + x for x in passos)
    return "\n".join(linhas[:max_linhas])


def pasta_ativa(pasta_campanhas: str | None, campanha_ativa: str | None) -> Path | None:
    if not pasta_campanhas or "${" in pasta_campanhas:
        return None
    base = Path(pasta_campanhas)
    if not base.is_dir():
        return None
    if campanha_ativa and "${" not in campanha_ativa:
        p = base / campanha_ativa
        return p if p.is_dir() else None
    jogos = [d for d in base.iterdir() if d.is_dir()]
    return jogos[0] if len(jogos) == 1 else None


def achados_como_dict(achados: list[Achado]) -> list[dict]:
    return [asdict(a) for a in achados]
