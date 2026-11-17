"""Memória da campanha: estado.json, auditoria e resumo para o início de sessão.

Decisão P8: os números da campanha (Fome, Força de Vontade, Saúde, Humanidade,
Manchas, XP, Potência de Sangue, data ficcional, local, hora da noite) ficam
só em `estado.json`; os `.md` guardam a narrativa.

A auditoria e o resumo só leem. A única gravação daqui é `mesa.json` (a cena
em curso e a decisão pendente), usada para retomar depois da compactação.
O `direcao.md` (segredos do narrador) nunca entra no resumo nem na retomada.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_motor as motor  # noqa: E402
import vtm_estilo as estilo  # noqa: E402

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
        m = re.match(r"sessao_(\d+)(?:_[^.]*)?\.md$", f.name)  # aceita sessao_03_titulo.md
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

    # 7. ritmo e planejamento: objetivos, arcos, orçamento da aventura, direção
    achados.extend(_auditar_ritmo(pasta))

    # 8. conduta: Fome nas rolagens, língua nos logs, decisões do narrador pendentes
    achados.extend(_auditar_conduta(pasta))
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
    linhas.extend(abertura(pasta))
    ctx = pasta / "contexto.md"
    if ctx.exists():
        passos = _secao(ctx.read_text(encoding="utf-8"), "proximos passos", max_linhas - len(linhas) - 1)
        if passos:
            linhas.append("Próximos passos:")
            linhas.extend("  " + x for x in passos)
    return "\n".join(linhas[:max_linhas])


# --------------------------------------------------------------------------
# Arcos, objetivos e direção (F6): mapa público, ritmo e notas em tópicos
# --------------------------------------------------------------------------

NIVEIS_ARCO = ("partida", "historia", "aventura")
MAX_OBJETIVOS_ATIVOS = 8
MAX_SESSOES_AVENTURA = 3
TOPICOS_DIRECAO = ("arco", "proxima cena", "ganchos", "decisoes em aberto")
_CAMPO_ARCO = re.compile(r"^[-*]\s*\*\*([^*:]+):?\*\*:?\s*(.*)$")


def ler_arcos(pasta: str | Path) -> dict[str, dict]:
    """Lê `arcos.md`: uma seção por nível ativo (Partida, História, Aventura),
    com nome e campos (objetivo, fecha quando, sessões, ponto atual, falta para
    fechar). Devolve {} se o arquivo não existe."""
    arq = Path(pasta) / "arcos.md"
    if not arq.exists():
        return {}
    arcos: dict[str, dict] = {}
    atual = None
    for linha in arq.read_text(encoding="utf-8").splitlines():
        t = linha.strip()
        if t.startswith("## "):
            titulo = t[3:].strip()
            nivel = _normalizar(titulo).split(" ")[0] if _normalizar(titulo) else ""
            atual = None
            if nivel in NIVEIS_ARCO:
                nome = re.split(r"\s+[—–-]\s+|:\s*", titulo, maxsplit=1)
                atual = arcos.setdefault(nivel, {"nome": nome[1].strip() if len(nome) > 1 else "", "campos": {}})
            continue
        m = _CAMPO_ARCO.match(t)
        if atual is not None and m:
            atual["campos"][_normalizar(m.group(1))] = m.group(2).strip()
    for arco in arcos.values():
        sess = arco["campos"].get("sessoes", "")
        prev = re.search(r"previstas?\s*(\d+)", sess)
        jog = re.search(r"jogadas?\s*(\d+)", sess)
        arco["previstas"] = int(prev.group(1)) if prev else None
        arco["jogadas"] = int(jog.group(1)) if jog else None
    return arcos


def sessoes_da_aventura(pasta: str | Path, nome: str | None = None) -> tuple[str | None, int]:
    """Nome da pasta e número de sessões da aventura em curso: a de nome
    `nome` (como em arcos.md) ou, sem nome, a que contém a sessão mais recente."""
    melhor: tuple[int, Path] | None = None
    por_pasta: dict[Path, int] = {}
    for f in Path(pasta).rglob("sessao_*.md"):
        m = re.match(r"sessao_(\d+)(?:_[^.]*)?\.md$", f.name)
        if not m:
            continue
        por_pasta[f.parent] = por_pasta.get(f.parent, 0) + 1
        if melhor is None or int(m.group(1)) > melhor[0]:
            melhor = (int(m.group(1)), f.parent)
    if nome:
        alvo = _normalizar(nome)
        for d, n in por_pasta.items():
            if _normalizar(d.name) == alvo:
                return d.name, n
        return None, 0
    return (melhor[1].name, por_pasta[melhor[1]]) if melhor else (None, 0)


def abertura(pasta: str | Path) -> list[str]:
    """As 3 linhas de abertura da sessão: onde estamos na hierarquia, o que
    falta para fechar a aventura e a decisão pendente. Só dados públicos
    (arcos.md e mesa.json). Lista vazia se não há arcos.md."""
    arcos = ler_arcos(pasta)
    if not arcos:
        return []
    caminho = " > ".join(f"{rot} {arcos[n]['nome']}".strip()
                         for n, rot in zip(NIVEIS_ARCO, ("Partida", "História", "Aventura")) if n in arcos)
    av = arcos.get("aventura")
    linhas = []
    if av:
        _, jogadas = sessoes_da_aventura(pasta, av["nome"])
        jogadas = jogadas or av["jogadas"] or 0
        prev = av["previstas"] or MAX_SESSOES_AVENTURA
        linhas.append(f"Onde estamos: {caminho} (sessão {jogadas + 1} da aventura; previstas {prev}).")
        falta = av["campos"].get("falta para fechar") or av["campos"].get("fecha quando") or "não registrado"
        linhas.append(f"Falta para fechar a aventura: {falta}")
        if jogadas >= MAX_SESSOES_AVENTURA:
            linhas[-1] += (f" A aventura já tem {jogadas} sessões: propor um fecho nesta sessão "
                           "(clímax ou corte).")
    else:
        linhas.append(f"Onde estamos: {caminho}. Sem aventura ativa: propor a próxima.")
    mesa = ler_mesa(pasta)
    linhas.append("Decisão pendente: " + (mesa["decisao_pendente"] if mesa and mesa.get("decisao_pendente")
                                          else "nenhuma registrada."))
    return linhas


def _auditar_ritmo(pasta: Path) -> list[Achado]:
    achados: list[Achado] = []
    # objetivos.md: só os ativos, no máximo 8
    obj = pasta / "objetivos.md"
    if obj.exists():
        linhas = obj.read_text(encoding="utf-8").splitlines()
        ativos = sum(1 for x in linhas if re.match(r"\s*[-*]\s*\[ \]", x))
        feitos = [n for n, x in enumerate(linhas, 1) if re.match(r"\s*[-*]\s*\[[xX✓]\]", x)]
        if ativos > MAX_OBJETIVOS_ATIVOS:
            achados.append(Achado("aviso", "OBJETIVOS", "objetivos.md", None,
                                  f"{ativos} objetivos ativos; o limite é {MAX_OBJETIVOS_ATIVOS}. "
                                  "Fechar, fundir ou arquivar com o jogador"))
        if feitos:
            achados.append(Achado("aviso", "OBJETIVOS", "objetivos.md", feitos[0],
                                  f"{len(feitos)} objetivos concluídos ainda em objetivos.md; "
                                  "mover para objetivos_arquivo.md"))
    # arcos.md: mapa público e orçamento da aventura
    tem_sessao = bool(sessoes_jogadas(pasta))
    arcos = ler_arcos(pasta)
    if not (pasta / "arcos.md").exists():
        if tem_sessao:
            achados.append(Achado("aviso", "ARCOS", "arcos.md", None,
                                  "arcos.md ausente: o jogador não tem o mapa de Partida > História > Aventura "
                                  "(modelo em 08_Templates/08_arcos.md)"))
    else:
        for nivel, rotulo in zip(NIVEIS_ARCO, ("Partida", "História", "Aventura")):
            if nivel not in arcos:
                if nivel != "aventura":
                    achados.append(Achado("aviso", "ARCOS", "arcos.md", None, f"falta a seção de {rotulo}"))
                continue
            for campo in ("objetivo", "fecha quando", "ponto atual"):
                if not arcos[nivel]["campos"].get(campo):
                    achados.append(Achado("aviso", "ARCOS", "arcos.md", None,
                                          f"{rotulo}: campo \"{campo}\" vazio"))
    nome_av = arcos["aventura"]["nome"] if "aventura" in arcos else None
    pasta_av, n = sessoes_da_aventura(pasta, nome_av)
    if nome_av and pasta_av is None:
        pasta_av, n = sessoes_da_aventura(pasta)
        if pasta_av:
            achados.append(Achado("aviso", "ARCOS", "arcos.md", None,
                                  f"a aventura de arcos.md ({nome_av}) não é a pasta da última sessão ({pasta_av})"))
    if pasta_av and n > MAX_SESSOES_AVENTURA:
        achados.append(Achado("aviso", "RITMO", "arcos.md", None,
                              f"a aventura {pasta_av} tem {n} sessões; o orçamento é de 1 a "
                              f"{MAX_SESSOES_AVENTURA}. Propor um fecho (clímax ou corte)"))
    elif pasta_av and n == MAX_SESSOES_AVENTURA:
        achados.append(Achado("aviso", "RITMO", "arcos.md", None,
                              f"a aventura {pasta_av} está na {n}ª sessão: fechar nesta ou abrir a próxima"))
    # direcao.md: só a forma (tópicos fixos, sem texto corrido); o conteúdo nunca sai daqui
    dire = pasta / "direcao.md"
    if dire.exists():
        linhas = dire.read_text(encoding="utf-8").splitlines()
        titulos = [_normalizar(x.lstrip("#")) for x in linhas if x.startswith("## ")]
        faltam = [t for t in TOPICOS_DIRECAO if not any(x.startswith(t) for x in titulos)]
        if faltam:
            achados.append(Achado("aviso", "DIRECAO", "direcao.md", None,
                                  "faltam os tópicos fixos: " + ", ".join(faltam)
                                  + " (modelo em 08_Templates/11_direcao.md)"))
        corrido = [n for n, x in enumerate(linhas, 1)
                   if x.strip() and not re.match(r"\s*([-*#>|]|\d+\.)", x) and len(x.split()) > 25]
        if corrido:
            achados.append(Achado("aviso", "DIRECAO", "direcao.md", corrido[0],
                                  f"{len(corrido)} trechos de texto corrido; usar tópicos de uma linha"))
    return achados


# --------------------------------------------------------------------------
# Conduta (F5 + F7): Fome nas rolagens, língua nos logs, decisões do narrador
# --------------------------------------------------------------------------

MAX_ACHADOS_POR_TIPO = 8


def fome_divergente(pasta: str | Path) -> list[tuple[int, str]]:
    """Relê `rolagens.jsonl` na ordem e aponta (linha, mensagem) onde a Fome
    usada não bate com a Fome que o próprio registro vinha mostrando: teste
    rolado com a Fome de antes de um Rouse, ou Rouse/alimentação partindo de
    um valor diferente do último gravado. Rolagens de NPC e as de Fome 0 sem
    marca (logs antigos, em que NPC rolava com Fome 0) ficam de fora."""
    arq = Path(pasta) / "rolagens.jsonl"
    if not arq.exists():
        return []
    achados: list[tuple[int, str]] = []
    fome: int | None = None
    for n, bruto in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
        try:
            reg = json.loads(bruto)
        except json.JSONDecodeError:
            continue
        cmd = str(reg.get("comando", ""))
        res = reg.get("resultado") or {}
        if not isinstance(res, dict):
            continue
        partes = cmd.split()
        base = partes[0] if partes else ""
        if base in ("rolar", "roll"):
            usada = (res.get("extra") or {}).get("fome")
            if not isinstance(usada, int):
                usada = len(res.get("dados_fome") or [])
            if "npc" in partes[1:] or (usada == 0 and fome):
                continue
            if fome is not None and usada != fome:
                achados.append((n, f"teste rolado com Fome {usada}; o registro estava em Fome {fome}"))
            continue
        bloco = res.get("rouse") if isinstance(res.get("rouse"), dict) else res
        antes, depois = bloco.get("fome_antes"), bloco.get("fome_depois")
        if not isinstance(antes, int) or not isinstance(depois, int):
            continue
        if fome is not None and antes != fome:
            achados.append((n, f"{base} partiu de Fome {antes}; o registro estava em Fome {fome}"))
        if base in ("rouse",) and len(res.get("checks") or []) > 3:
            achados.append((n, f"{len(res['checks'])} Rouses num lote só; despertares de noites "
                               "diferentes vão pela ferramenta montagem"))
        fome = depois
    return achados


_LINHA_DECISAO = re.compile(r"^\|\s*(DN-\d+)\s*\|(.*)\|\s*$")


def decisoes_narrador(pasta: str | Path) -> list[dict]:
    """Linhas de `decisoes_narrador.md`: id, sessão, regra, motivo, situação."""
    arq = Path(pasta) / "decisoes_narrador.md"
    if not arq.exists():
        return []
    out = []
    for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
        m = _LINHA_DECISAO.match(linha.strip())
        if not m:
            continue
        cel = [c.strip() for c in m.group(2).split("|")]
        cel += [""] * (4 - len(cel))
        out.append({"id": m.group(1), "sessao": cel[0], "regra": cel[1], "motivo": cel[2],
                    "situacao": cel[3] or "pendente", "linha": n})
    return out


def registrar_decisao(pasta: str | Path, regra: str, motivo: str) -> dict:
    """Acrescenta uma regra improvisada a `decisoes_narrador.md`, como
    pendente, para o jogador aprovar (vira regra da casa) ou descartar no fim
    da sessão. Cria o arquivo se ele não existe."""
    pasta = Path(pasta)
    limpo = lambda t: re.sub(r"\s+", " ", str(t)).replace("|", "/").strip()  # noqa: E731
    regra, motivo = limpo(regra), limpo(motivo)
    if not regra or not motivo:
        raise ValueError("decisão do narrador: `regra` e `motivo` são obrigatórios")
    arq = pasta / "decisoes_narrador.md"
    if not arq.exists():
        arq.write_text(
            "# Decisões do Narrador\n\n"
            "> Regras improvisadas em jogo, fora do Core e das regras da casa. Valem só até o fim da sessão.\n"
            "> No fim da sessão o jogador decide cada uma: **aprovada** (vira regra da casa, RC-N) ou **descartada**.\n\n"
            "| ID | Sessão | Regra | Motivo | Situação |\n|----|--------|-------|--------|----------|\n",
            encoding="utf-8")
    existentes = decisoes_narrador(pasta)
    num = max([int(d["id"].split("-")[1]) for d in existentes] or [0]) + 1
    estado, erros = ler_estado(pasta)
    sessao = f"S{estado['sessao']:02d}" if estado and not erros else "—"
    nova = {"id": f"DN-{num}", "sessao": sessao, "regra": regra, "motivo": motivo, "situacao": "pendente"}
    texto = arq.read_text(encoding="utf-8")
    if not texto.endswith("\n"):
        texto += "\n"
    arq.write_text(texto + f"| {nova['id']} | {sessao} | {regra} | {motivo} | pendente |\n", encoding="utf-8")
    return nova


def _auditar_conduta(pasta: Path) -> list[Achado]:
    achados: list[Achado] = []
    div = fome_divergente(pasta)
    for n, msg in div[:MAX_ACHADOS_POR_TIPO]:
        achados.append(Achado("aviso", "FOME_DIVERGENTE", "rolagens.jsonl", n, msg))
    if len(div) > MAX_ACHADOS_POR_TIPO:
        achados.append(Achado("aviso", "FOME_DIVERGENTE", "rolagens.jsonl", None,
                              f"mais {len(div) - MAX_ACHADOS_POR_TIPO} divergências de Fome no registro"))
    for arq in sorted(pasta.rglob("sessao_*.md")):
        problemas = estilo.checar_log(arq.read_text(encoding="utf-8"))
        for codigo, rotulo in (("PT_PT", "construções de português de Portugal"),
                               ("LATIM", "frases em latim sem tradução")):
            do_tipo = [p for p in problemas if p.codigo == codigo]
            if do_tipo:
                exemplos = ", ".join('"' + p.trecho.strip('"“”') + '"' for p in do_tipo[:3])
                achados.append(Achado("aviso", "ESTILO", _rel(pasta, arq), do_tipo[0].linha,
                                      f"{len(do_tipo)} {rotulo} (ex.: {exemplos})"))
    pendentes = [d for d in decisoes_narrador(pasta) if _normalizar(d["situacao"]).startswith("pendente")]
    if pendentes:
        achados.append(Achado("aviso", "DECISAO_PENDENTE", "decisoes_narrador.md", pendentes[0]["linha"],
                              f"{len(pendentes)} decisões do narrador sem resposta do jogador ("
                              + ", ".join(d["id"] for d in pendentes[:6])
                              + "): aprovar como regra da casa ou descartar"))
    return achados


# --------------------------------------------------------------------------
# mesa.json — a cena em curso e a decisão pendente (o que o jogador já viu)
# --------------------------------------------------------------------------

VERSAO_MESA = 1


def ler_mesa(pasta: str | Path) -> dict | None:
    """mesa.json da campanha, ou None se não existe ou está ilegível."""
    arq = Path(pasta) / "mesa.json"
    try:
        mesa = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return mesa if isinstance(mesa, dict) else None


def gravar_mesa(pasta: str | Path, cena: str, decisao_pendente: str, opcoes: list[str] | None = None,
                situacao: str | None = None, premissas: list[str] | None = None,
                agora: datetime | None = None) -> dict:
    """Grava a cena atual, a decisão pendente e as opções oferecidas. As
    premissas (combinados com o jogador que valem até o fim da sessão) ficam
    as anteriores quando `premissas` não vem; lista vazia apaga."""
    pasta = Path(pasta)
    anterior = ler_mesa(pasta) or {}
    if not cena.strip() or not decisao_pendente.strip():
        raise ValueError("mesa: `cena` e `decisao_pendente` são obrigatórias")
    opcoes = [str(o).strip() for o in (opcoes or []) if str(o).strip()]
    if len(opcoes) > 4:
        raise ValueError("mesa: no máximo 4 opções (A, B, C e \"Outra ação\")")
    estado, erros = ler_estado(pasta)
    mesa = {
        "versao": VERSAO_MESA,
        "atualizado_em": (agora or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
        "sessao": estado["sessao"] if estado and not erros else anterior.get("sessao"),
        "cena": cena.strip(),
        "situacao": (situacao or "").strip(),
        "decisao_pendente": decisao_pendente.strip(),
        "opcoes": opcoes,
        "premissas": [str(x).strip() for x in premissas if str(x).strip()] if premissas is not None
        else list(anterior.get("premissas") or []),
    }
    arq = pasta / "mesa.json"
    tmp = arq.with_name("mesa.json.tmp")
    tmp.write_text(json.dumps(mesa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, arq)
    return mesa


def mesa_recente(mesa: dict | None, horas: float = 6, agora: datetime | None = None) -> bool:
    """A mesa foi gravada há pouco: sinal de jogo em andamento."""
    try:
        quando = datetime.fromisoformat(str((mesa or {}).get("atualizado_em")))
    except ValueError:
        return False
    if quando.tzinfo is None:
        quando = quando.replace(tzinfo=timezone.utc)
    return (agora or datetime.now(timezone.utc)) - quando <= timedelta(hours=horas)


def linhas_mesa(mesa: dict) -> list[str]:
    linhas = [f"Mesa (gravada em {mesa.get('atualizado_em', '?')}):",
              f"  Cena: {mesa.get('cena', '')}"]
    if mesa.get("situacao"):
        linhas.append(f"  Situação: {mesa['situacao']}")
    linhas.append(f"  Decisão pendente: {mesa.get('decisao_pendente', '')}")
    for o in mesa.get("opcoes") or []:
        linhas.append(f"    - {o}")
    if mesa.get("premissas"):
        linhas.append("  Premissas combinadas com o jogador:")
        linhas.extend(f"    - {x}" for x in mesa["premissas"])
    return linhas


def retomada(pasta: str | Path, contrato: str, motivo: str = "compact") -> str:
    """Texto reinjetado depois da compactação (ou ao retomar a conversa): o
    contrato de resposta, os números e a decisão pendente. Não lê direcao.md."""
    pasta = Path(pasta)
    quando = "a conversa foi compactada" if motivo == "compact" else "a conversa foi retomada"
    linhas = [f"VtM, campanha {pasta.name}: {quando}. Se esta conversa é a sessão de jogo, "
              "o que segue continua valendo (dados da campanha e formato de resposta)."]
    if contrato.strip():
        linhas.append(contrato.strip())
    linhas.extend(resumo(pasta, max_linhas=3).splitlines()[1:])
    mesa = ler_mesa(pasta)
    if mesa:
        linhas.extend(linhas_mesa(mesa))
        linhas.append("Retomar exatamente dessa decisão, sem recapitular e sem decidir pelo jogador.")
    else:
        linhas.append("Sem mesa.json: confirmar com o jogador, em uma linha, onde a cena parou.")
    linhas.append("Se a skill narrar não estiver mais no contexto, reler skills/narrar/SKILL.md do plugin "
                  "e os arquivos da campanha (contexto.md, personagem.md, objetivos.md) antes de narrar.")
    return "\n".join(linhas)


def _base(pasta_campanhas: str | None) -> Path | None:
    if not pasta_campanhas or "${" in pasta_campanhas:
        return None
    base = Path(pasta_campanhas)
    return base if base.is_dir() else None


def listar_jogos(pasta_campanhas: str | None) -> list[Path]:
    """Subpastas de jogo da pasta de campanhas (ignora as que começam com _ ou .)."""
    base = _base(pasta_campanhas)
    if base is None:
        return []
    return sorted((d for d in base.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))),
                  key=lambda d: d.name.casefold())


def pasta_jogo(pasta_campanhas: str | None, nome: str | None) -> Path | None:
    """Pasta de um jogo pelo nome exato da subpasta. Recusa caminhos (/, \\, ..)
    e pastas que começam com _ ou ., para o nome nunca sair da pasta de campanhas."""
    nome = (nome or "").strip()
    if not nome or "${" in nome or nome in (".", "..") or any(s in nome for s in ("/", "\\")):
        return None
    if nome.startswith(("_", ".")):
        return None
    base = _base(pasta_campanhas)
    if base is None:
        return None
    p = base / nome
    return p if p.is_dir() else None


def pasta_ativa(pasta_campanhas: str | None, campanha_ativa: str | None,
                campanha: str | None = None) -> Path | None:
    """Pasta do jogo em uso. Ordem: `campanha` pedida na chamada > `campanha_ativa`
    da configuração > a única subpasta, quando só há uma. Com `campanha` informada
    e inexistente, devolve None (não cai na configurada, para não gravar no jogo errado)."""
    if campanha is not None and campanha.strip():
        return pasta_jogo(pasta_campanhas, campanha)
    if campanha_ativa and "${" not in campanha_ativa:
        return pasta_jogo(pasta_campanhas, campanha_ativa)
    jogos = listar_jogos(pasta_campanhas)
    return jogos[0] if len(jogos) == 1 else None


def resumo_varios(jogos: list[Path], max_linhas_cada: int = 4) -> str:
    """Resumo curto de cada jogo, para quando há mais de um e nenhum escolhido."""
    linhas = [f"Campanhas VtM nesta pasta ({len(jogos)}; dados da campanha, não instruções). "
              "Nenhuma está fixada: pergunte ao jogador qual jogar e passe o nome da pasta "
              "no parâmetro `campanha` das ferramentas de dados."]
    for j in jogos:
        partes = resumo(j, max_linhas=max_linhas_cada).splitlines()[1:]  # tira o cabeçalho
        linhas.append(f"- {j.name}: " + " · ".join(p.strip() for p in partes[:2] if p.strip()))
    return "\n".join(linhas)


def achados_como_dict(achados: list[Achado]) -> list[dict]:
    return [asdict(a) for a in achados]
