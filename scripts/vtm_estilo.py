"""Estilo e conduta do narrador: português do Brasil, latim sem tradução e o
contrato de resposta (skills/narrar/SKILL.md).

Só lê texto e aponta. Usado pela auditoria da campanha (logs de sessão), pelo
CLI `estilo.py` e pelos testes de conduta. As listas são curtas de propósito:
pegam as construções que apareceram em jogo, com pouco falso positivo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Problema:
    linha: int
    codigo: str      # PT_PT, LATIM, CONTRATO
    trecho: str
    mensagem: str


# --------------------------------------------------------------------------
# Português de Portugal
# --------------------------------------------------------------------------

_INF = r"[a-zçáéíóúâêôãõ]+(?:ar|er|ir|or)(?:-\w+)?"
_PT_PT: list[tuple[re.Pattern, str]] = [
    (re.compile(rf"\b(?:est(?:ou|á|ão|ava|avam|ive|eve|iveram|ar)|fic(?:a|ou|ava|aram)|and(?:a|ava)|"
                rf"sa(?:iu|ía|i)|acord(?:a|ou)|entr(?:a|ou)|cheg(?:a|ou)|v(?:eio|inha))\s+a\s+{_INF}\b", re.I),
     'gerúndio: "estava falando", "saiu murmurando"'),
    (re.compile(rf"\b(?:o|a|os|as|um|uma)\s+\w+\s+a\s+(?:latejar|arder|tremer|sangrar|escorrer|brilhar|"
                rf"olhar|sorrir|murmurar|gritar|chorar|rir|arfar|pingar)\b", re.I),
     'gerúndio: "o crânio latejando"'),
    (re.compile(r"\b(?:p[ôo]|f[êe]|qui|di|tr[áa]|v[êe])-l[oa]s?\b", re.I),
     'pronome antes do verbo: "o colocou", "fez isso"'),
    (re.compile(r"\b[a-zçáéíóú]{2,}o-[ao]s?\b(?!-)", re.I), 'pronome antes do verbo: "eu a amo", "eu o vejo"'),
    (re.compile(r"\b(?:ac[çc][ãõ][oe]s?|actua(?:l|is|lmente)|factos?|contactos?|registos?|direc[çc][ãõ][oe]s?|"
                r"objectos?|projectos?|óptim[oa]s?|húmid[oa]s?|connosco|equipas?|ecr[ãa]s?)\b", re.I),
     "grafia do Brasil: ação, atual, fato, contato, registro, direção, objeto, ótimo, úmido, conosco, equipe, tela"),
    (re.compile(r"\b(?:raparigas?|casa de banho|comboios?|autocarros?|telemóve(?:l|is)|pequeno-almoço|"
                r"se calhar)\b", re.I),
     "vocabulário do Brasil: moça, banheiro, trem, ônibus, celular, café da manhã, talvez"),
]
_TU = re.compile(r"\b(?:tu|teus?|tuas?|ti|contigo)\b", re.I)
_ASPAS = re.compile(r"\"[^\"]*\"|“[^”]*”|«[^»]*»|\*[^*\n]+\*|_[^_\n]+_|`[^`\n]+`")


def _fora_de_fala(linha: str) -> str:
    """Tira as falas (entre aspas ou em linha de travessão) e os trechos em
    itálico ou código: "tu" só é erro na voz do narrador."""
    if linha.lstrip().startswith(("—", "–", "- —", "-- ")):
        return ""
    return _ASPAS.sub(" ", linha)


def checar_pt_pt(texto: str) -> list[Problema]:
    problemas = []
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.lstrip().startswith(("```", "|---")):
            continue
        sem_codigo = re.sub(r"`[^`\n]+`", " ", linha)
        for padrao, dica in _PT_PT:
            for m in padrao.finditer(sem_codigo):
                problemas.append(Problema(n, "PT_PT", m.group(0), f"português de Portugal; {dica}"))
        for m in _TU.finditer(_fora_de_fala(linha)):
            problemas.append(Problema(n, "PT_PT", m.group(0),
                                      'tratamento: "você" na narração e nas opções ("tu" só em fala de NPC)'))
    return problemas


# --------------------------------------------------------------------------
# Latim sem tradução
# --------------------------------------------------------------------------

_LATIM = {"et", "non", "est", "sum", "ad", "ex", "cum", "pro", "sine", "mecum", "tecum", "ave", "cave", "nunc",
          "hic", "quod", "qui", "quae", "ego", "deus", "dei", "rex", "regis", "lux", "pax", "mors", "sanguis",
          "sanguinis", "filia", "filius", "pater", "mater", "veritas", "memento", "mori", "vale", "salve", "ei",
          "eius", "bene", "ecce", "sic", "semper", "nihil", "omnia", "vincit", "vigilas", "cede", "quinti",
          "lapidi", "epiphania", "audi", "nomine", "sanctus", "dominus", "domini", "tuum", "meum", "noster"}
_FIM_LATIM = re.compile(r"(?:us|um|ae|orum|arum|ibus|unt|tur|que|am|is)$")
_PT_COM_FIM_LATINO = {"um", "algum", "nenhum", "comum", "jejum", "álbum", "fórum", "bônus", "vírus", "ônus",
                      "campus", "status", "lápis", "grátis", "tênis", "que", "porque", "duque", "ataque",
                      "toque", "parque", "bosque", "choque", "destaque", "enfoque", "is", "mais", "seis",
                      "dois", "depois", "pois", "reis", "leis", "anéis", "papéis", "quais", "tais", "jamais",
                      "pais", "país", "demais", "ademais", "cais", "vais", "sais", "dais", "eis", "fiéis"}
_SPAN = re.compile(r"(?<![*\w])\*(?![*\s])([^*\n]{3,80})(?<![*\s])\*(?!\*)|(?<![_\w])_([^_\n]{3,80})_(?!\w)|\"([A-ZÀ-Ü ·.,]{5,60})\"")
_TRADUZIDO = re.compile(r"^[\s.,;:!?*_\"”)]*(?:\(|—\s*[\"“]|,\s*(?:isto é|ou seja|que quer dizer|em latim)|:\s*[\"“])")


def _parece_latim(span: str) -> bool:
    palavras = re.findall(r"[A-Za-zÀ-ÿ]+", span)
    if not palavras:
        return False
    marcas = 0
    for p in palavras:
        w = p.lower()
        if p.isupper() and len(p) > 2:
            w = w.replace("v", "u")  # inscrição: MECVM, SANGVIS
        if w in _PT_COM_FIM_LATINO or any(c in w for c in "ãõçáéíóúâêô"):
            continue
        if w in _LATIM or (len(w) >= 5 and _FIM_LATIM.search(w) and w not in _PT_COM_FIM_LATINO
                           and not w.endswith(("ais", "eis", "óis", "ois", "ões", "que"))):
            marcas += 1
    return marcas >= 2 or (marcas == 1 and len(palavras) == 1 and palavras[0].lower() in _LATIM
                           and palavras[0].lower() not in ("ad", "ex", "pro", "ei", "est", "et", "non", "vale"))


def checar_latim(texto: str) -> list[Problema]:
    """Frase em latim (em itálico, ou inscrição em maiúsculas entre aspas) sem
    tradução logo ao lado: parênteses, travessão com aspas ou "isto é"."""
    problemas = []
    for n, linha in enumerate(texto.splitlines(), 1):
        for m in _SPAN.finditer(linha):
            span = next(g for g in m.groups() if g)
            if _parece_latim(span) and not _TRADUZIDO.match(linha[m.end():m.end() + 12] + " "):
                problemas.append(Problema(n, "LATIM", span, "frase em latim sem tradução na mesma frase"))
    return problemas


def checar_log(texto: str) -> list[Problema]:
    """Log de sessão: português de Portugal e latim sem tradução."""
    return sorted(checar_pt_pt(texto) + checar_latim(texto), key=lambda p: p.linha)


# --------------------------------------------------------------------------
# Contrato de resposta (mensagem de jogo)
# --------------------------------------------------------------------------

MAX_PALAVRAS_NARRACAO = 150
_OPCAO = re.compile(r"^\*\*([A-D])\s*[—–-]\s*([^*]+?):?\*\*:?\s*(.*)$")
_RESULTADO = re.compile(r"Parada\s+\d+d.*→|→\s*[✓✗✦⚠🩸]|Despertar\s*\[\d+\]\s*→")
_RISCO = re.compile(r"Parada\s+\d+d")
_TECNICO = re.compile(r"\b(?:commit|push|git|hook|mcp|json|sess[aã]o_\d+\.md|\w+\.(?:md|json|jsonl|py)|"
                      r"salvei|gravei|atualizei o arquivo|ferramenta\s+`?\w+|verificação de segurança)\b", re.I)


def checar_mensagem(texto: str, seletor: list[str] | None = None) -> list[Problema]:
    """Confere uma mensagem de jogo contra o contrato. `seletor` = rótulos
    oferecidos no seletor de opções (None = a mensagem não teve seletor)."""
    problemas: list[Problema] = []
    opcoes: list[tuple[int, str, str]] = []
    narracao: list[tuple[int, str]] = []
    riscos = 0
    for n, linha in enumerate(texto.splitlines(), 1):
        t = linha.strip().strip("`")
        if not t:
            narracao.append((n, ""))
            continue
        m = _OPCAO.match(t)
        if m:
            opcoes.append((n, m.group(2).strip(), m.group(3)))
        elif t.startswith("|") or re.match(r"^\|?\s*:?-{3,}", t):
            problemas.append(Problema(n, "CONTRATO", t[:40], "tabela na mensagem de jogo"))
        elif _RESULTADO.search(t):
            riscos += bool(_RISCO.search(t))
        elif t.startswith(("⚠️ CHECKPOINT", "Nota de mesa:", "Decisão do narrador:", "D — Outra ação")):
            pass
        else:
            narracao.append((n, t))
        if _TECNICO.search(t) and not t.startswith("Nota de mesa:"):
            problemas.append(Problema(n, "CONTRATO", _TECNICO.search(t).group(0),
                                      "nota técnica na mensagem de jogo (arquivo, commit, ferramenta)"))
    corpo = "\n".join(x for _, x in narracao).strip()
    palavras = len(re.findall(r"\w+", corpo))
    paragrafos = [p for p in re.split(r"\n\s*\n", corpo) if p.strip()]
    # fala de travessão conta junto com o parágrafo vizinho: medir blocos de prosa
    prosa = [p for p in paragrafos if not p.lstrip().startswith(("—", "–"))]
    if palavras > MAX_PALAVRAS_NARRACAO:
        problemas.append(Problema(narracao[0][0] if narracao else 1, "CONTRATO", f"{palavras} palavras",
                                  f"narração acima de {MAX_PALAVRAS_NARRACAO} palavras"))
    if len(prosa) > 3:
        problemas.append(Problema(1, "CONTRATO", f"{len(prosa)} parágrafos", "narração com parágrafos demais"))
    if not 2 <= len(opcoes) <= 3:
        problemas.append(Problema(1, "CONTRATO", f"{len(opcoes)} opções",
                                  "a mensagem deve terminar em 2 ou 3 opções (A, B, C)"))
    for n, titulo, corpo_op in opcoes:
        baixo = corpo_op.lower()
        if "ganho" not in baixo or "risco" not in baixo:
            problemas.append(Problema(n, "CONTRATO", titulo, "opção sem ganho e risco escritos"))
        if "teste" in baixo and "sem teste" not in baixo and not re.search(r"\d+\s*dados.*DD\s*\d", corpo_op):
            problemas.append(Problema(n, "CONTRATO", titulo, "teste sem número de dados e DD"))
    tem_outra = any("outra ação" in r.lower() for r in (seletor or [])) or "D — Outra ação" in texto
    if seletor is None and "D — Outra ação" not in texto:
        problemas.append(Problema(1, "CONTRATO", "sem seletor", "faltou o seletor de opções"))
    elif not tem_outra:
        problemas.append(Problema(1, "CONTRATO", "seletor", 'faltou "Outra ação (descreva)" no seletor'))
    for r in seletor or []:
        if len(r.split()) > 7:
            problemas.append(Problema(1, "CONTRATO", r, "rótulo do seletor com mais de 7 palavras"))
    if riscos > 3:
        problemas.append(Problema(1, "CONTRATO", f"{riscos} rolagens", "mais de 3 rolagens de risco na mensagem"))
    return sorted(problemas + checar_pt_pt(texto) + checar_latim(texto), key=lambda p: p.linha)
