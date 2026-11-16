"""Estado da campanha para o motor de dados.

Lê e grava `estado.json` (fonte única dos números), confere os parâmetros que
o narrador informa contra o estado, marca dano nos trackers e lê a ficha
(`ficha.json` ou `personagem.md`) para somar paradas. As regras de dados ficam
em vtm_motor.py; o schema do estado, em vtm_campanha.py.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_campanha as camp  # noqa: E402


class Divergencia(ValueError):
    """O valor informado na chamada não bate com o estado.json."""


ROTULOS = {"fome": "Fome", "potencia_sangue": "Potência de Sangue",
           "humanidade": "Humanidade", "manchas": "Manchas"}

# --------------------------------------------------------------------------
# estado.json
# --------------------------------------------------------------------------


def carregar(pasta: Path | None) -> dict | None:
    """Estado válido da campanha, ou None se não há pasta ou estado.json
    (campanha antiga: o motor segue sem estado). Estado com erro é recusado:
    rolar em cima de número errado é pior do que parar."""
    if pasta is None:
        return None
    estado, erros = camp.ler_estado(Path(pasta))
    if estado is None:
        if erros == ["estado.json ausente"]:
            return None
        raise ValueError(erros[0])
    if erros:
        raise ValueError("estado.json com erro (" + "; ".join(erros) + "). Corrija o arquivo antes de rolar.")
    return estado


def gravar(pasta: Path, estado: dict) -> None:
    """Grava o estado inteiro, de forma atômica, depois de validar."""
    erros = camp.validar_estado(estado)
    if erros:
        raise ValueError("estado.json ficaria inválido: " + "; ".join(erros))
    arq = Path(pasta) / "estado.json"
    tmp = arq.with_name("estado.json.tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, arq)


def valor(estado: dict | None, chave: str, informado: int | None, padrao: int | None = None) -> int:
    """Número a usar na rolagem. Com estado: o do estado; se a chamada informar
    outro, recusa (Divergencia). Sem estado: o informado, senão `padrao`."""
    rotulo = ROTULOS[chave]
    if estado is None:
        if informado is not None:
            return informado
        if padrao is not None:
            return padrao
        raise ValueError(f"informe {rotulo}: a campanha não tem estado.json")
    atual = estado["personagem"][chave]
    if informado is not None and informado != atual:
        raise Divergencia(
            f"{rotulo} informada ({informado}) difere do estado.json ({atual}). Nada foi rolado. "
            f"Repita a chamada sem esse parâmetro; se o errado for o estado.json, corrija o arquivo antes.")
    return atual


def intacto(tracker: dict) -> int:
    return tracker["max"] - tracker["superficial"] - tracker["agravado"]


def fdv_intacta(estado: dict | None, informado: int | None) -> int:
    if estado is None:
        if informado is None:
            raise ValueError("informe a Força de Vontade intacta: a campanha não tem estado.json")
        return informado
    atual = intacto(estado["personagem"]["forca_vontade"])
    if informado is not None and informado != atual:
        raise Divergencia(f"Força de Vontade intacta informada ({informado}) difere do estado.json ({atual}). "
                          "Nada foi rolado. Repita a chamada sem esse parâmetro.")
    return atual


def marcar_dano(tracker: dict, quantidade: int, natureza: str) -> list[str]:
    """Marca dano já calculado (depois de dividir o Superficial) num tracker.
    Com o tracker cheio, cada ponto converte 1 Superficial em Agravado
    (Core p. 126-127). Devolve as notas de condição."""
    for _ in range(max(0, quantidade)):
        if intacto(tracker) > 0:
            tracker["superficial" if natureza == "superficial" else "agravado"] += 1
        elif tracker["superficial"] > 0:
            tracker["superficial"] -= 1
            tracker["agravado"] += 1
    notas = []
    if tracker["agravado"] >= tracker["max"]:
        notas.append("Tracker todo em Agravado (Core p. 126-127)")
    elif intacto(tracker) == 0:
        notas.append("Tracker cheio: Prejudicado, -2 dados nas paradas afetadas (Core p. 126)")
    return notas


def resumo(estado: dict) -> dict:
    """Números atuais, para o narrador não citar de memória."""
    p = estado["personagem"]
    s, f = p["saude"], p["forca_vontade"]
    return {"fome": p["fome"], "potencia_sangue": p["potencia_sangue"],
            "humanidade": p["humanidade"], "manchas": p["manchas"],
            "saude": f"{intacto(s)} de {s['max']} ({s['superficial']} Superficial, {s['agravado']} Agravado)",
            "forca_vontade": f"{intacto(f)} de {f['max']} ({f['superficial']} Superficial, {f['agravado']} Agravado)"}


# --------------------------------------------------------------------------
# Ficha: ficha.json ou personagem.md
# --------------------------------------------------------------------------

ATRIBUTOS = ("forca", "destreza", "vigor", "carisma", "manipulacao", "compostura",
             "inteligencia", "raciocinio", "determinacao")
_SECOES = {"atributos": "atributos", "habilidades": "habilidades", "disciplinas": "disciplinas"}
_PONTOS = "●•"


def _norm(txt: str) -> str:
    sem = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", sem.lower()).strip()


def _nivel(txt: str) -> int | None:
    txt = txt.strip().strip("*").strip()
    if re.fullmatch(r"\d{1,2}", txt):
        return int(txt)
    if txt and all(c in _PONTOS + "○ " for c in txt) and any(c in _PONTOS for c in txt):
        return sum(c in _PONTOS for c in txt)
    return None


def _ler_md(texto: str) -> dict[str, dict[str, tuple[str, int]]]:
    ficha = {s: {} for s in _SECOES.values()}
    secao = None
    for linha in texto.splitlines():
        t = linha.strip()
        if t.startswith("## "):
            secao = _SECOES.get(_norm(t[3:]).split(" ")[0] if _norm(t[3:]) else "")
            continue
        if secao is None or not t:
            continue
        pares: list[tuple[str, int]] = []
        if t.startswith("|"):
            celulas = [c.strip() for c in t.strip("|").split("|")]
            i = 0
            while i + 1 < len(celulas):
                n = _nivel(celulas[i + 1])
                if n is not None and _nivel(celulas[i]) is None and celulas[i]:
                    pares.append((celulas[i].strip("* "), n))
                    i += 2
                else:
                    i += 1
        elif t.startswith("#") and secao == "disciplinas":
            mt = re.match(r"#+\s*([^●•(\d]+?)\s*([●•]+|\d+)", t)
            if mt:
                pares.append((mt.group(1), _nivel(mt.group(2)) or 0))
        elif t[0] in "-*":
            mt = re.match(r"[-*]\s*\**([^:*●•\d|(]+?)\**\s*:?\**\s*([●•]+|\d{1,2})(?!\d)", t)
            if mt:
                pares.append((mt.group(1), _nivel(mt.group(2)) or 0))
        for nome, n in pares:
            if secao == "atributos" and _norm(nome) not in ATRIBUTOS:
                continue  # cabeçalho de coluna (Físicos, Sociais, Mentais)
            ficha[secao].setdefault(_norm(nome), (nome.strip(), n))
    return ficha


def ler_ficha(pasta: Path) -> dict[str, dict[str, tuple[str, int]]]:
    """Atributos, Habilidades e Disciplinas da ficha. `ficha.json` (objeto com
    as chaves atributos, habilidades e disciplinas, cada uma nome -> nível) vale
    por cima de `personagem.md`."""
    pasta = Path(pasta)
    arq_json = pasta / "ficha.json"
    if arq_json.exists():
        bruto = json.loads(arq_json.read_text(encoding="utf-8"))
        return {s: {_norm(k): (k, int(v)) for k, v in (bruto.get(s) or {}).items()}
                for s in _SECOES.values()}
    arq = pasta / "personagem.md"
    if not arq.exists():
        raise ValueError("ficha não encontrada: a campanha não tem personagem.md nem ficha.json")
    return _ler_md(arq.read_text(encoding="utf-8"))


def _buscar(ficha: dict, nome: str, secoes: tuple[str, ...]) -> tuple[str, int] | None:
    chave = _norm(nome)
    for s in secoes:
        if chave in ficha[s]:
            return ficha[s][chave]
    return None


def parada(pasta: Path, atributo: str, habilidade: str | None = None,
           disciplina: str | None = None, bonus: int = 0) -> dict:
    """Soma a parada pela ficha. `habilidade` também aceita um segundo Atributo
    (ex.: Compostura + Determinação). Habilidade que não está na ficha vale 0
    (Core p. 119), com aviso, porque também pode ser nome digitado errado."""
    ficha = ler_ficha(pasta)
    if not ficha["atributos"]:
        raise ValueError("não achei a seção de Atributos na ficha; confira personagem.md")
    partes, avisos = [], []
    a = _buscar(ficha, atributo, ("atributos",))
    if a is None:
        raise ValueError(f"Atributo '{atributo}' não está na ficha. Atributos: "
                         + ", ".join(v[0] for v in ficha["atributos"].values()))
    partes.append({"nome": a[0], "valor": a[1]})
    if habilidade:
        h = _buscar(ficha, habilidade, ("habilidades", "atributos"))
        if h is None:
            avisos.append(f"'{habilidade}' não está na ficha: contei 0. Habilidades na ficha: "
                          + ", ".join(v[0] for v in ficha["habilidades"].values()))
            h = (habilidade, 0)
        partes.append({"nome": h[0], "valor": h[1]})
    if disciplina:
        d = _buscar(ficha, disciplina, ("disciplinas",))
        if d is None:
            raise ValueError(f"Disciplina '{disciplina}' não está na ficha. Disciplinas: "
                             + (", ".join(v[0] for v in ficha["disciplinas"].values()) or "nenhuma"))
        partes.append({"nome": d[0], "valor": d[1]})
    if bonus:
        partes.append({"nome": "bônus" if bonus > 0 else "penalidade", "valor": bonus})
    total = max(0, sum(p["valor"] for p in partes))
    out = {"tipo": "PARADA", "parada": total, "partes": partes,
           "texto": " + ".join(f"{p['nome']} {p['valor']}" for p in partes) + f" = {total}"}
    if avisos:
        out["avisos"] = avisos
    return out
