"""Núcleo de regras do VtM V5 — rolagens e mecânicas.

Fonte canônica (decisão P6): Vampire: The Masquerade 5th Edition Core Rulebook,
citado como "Core p. N" pelo número de página impresso. As regras abaixo são
paráfrases; o texto do livro não é reproduzido aqui.

Todas as funções recebem um `random.Random` (ou dados já rolados) para que os
testes usem resultados escolhidos. Nada aqui grava arquivo; o registro de
rolagens fica em `registrar()`.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

SUCESSO_MIN = 6  # Core p. 120: cada dado com 6 ou mais é um sucesso.

# --------------------------------------------------------------------------
# Tabela de Potência de Sangue — Core p. 216
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class LinhaPotencia:
    surto: int              # dados somados pelo Blood Surge
    cura_superficial: int   # dano Superficial curado por Rouse Check
    bonus_disciplina: int   # dados somados a paradas de Disciplina
    rouse_dois_dados_ate: int  # nível máximo de poder com Rouse de 2 dados (0 = nenhum)
    severidade_perdicao: int
    animal_bolsa: str       # "integral", "metade" ou "nada"
    sacia_menos_humano: int  # Fome a menos saciada por alimentação em humano
    fome_minima_sem_matar: int  # piso de Fome sem drenar e matar um humano


# Linha 7: na tabela impressa as células de penalidade de alimentação das
# linhas 6-7 e 8-9 aparecem mescladas; o texto da Core p. 211 ("acima de
# Potência 7, não reduz a Fome abaixo de 3 sem matar") confirma que a linha 7
# fica com o piso 2. [a verificar contra a errata]
POTENCIA = {
    0: LinhaPotencia(0, 1, 0, 0, 0, "integral", 0, 1),
    1: LinhaPotencia(1, 1, 0, 1, 1, "integral", 0, 1),
    2: LinhaPotencia(1, 2, 1, 1, 1, "metade", 0, 1),
    3: LinhaPotencia(2, 2, 1, 2, 2, "nada", 0, 1),
    4: LinhaPotencia(2, 3, 2, 2, 2, "nada", 1, 1),
    5: LinhaPotencia(3, 3, 2, 3, 3, "nada", 1, 2),
    6: LinhaPotencia(3, 3, 3, 3, 3, "nada", 2, 2),
    7: LinhaPotencia(4, 3, 3, 4, 4, "nada", 2, 2),
    8: LinhaPotencia(4, 4, 4, 4, 4, "nada", 2, 3),
    9: LinhaPotencia(5, 4, 4, 5, 5, "nada", 3, 3),
    10: LinhaPotencia(5, 5, 5, 5, 5, "nada", 3, 3),
}


def potencia(bp: int) -> LinhaPotencia:
    if bp not in POTENCIA:
        raise ValueError(f"Potência de Sangue fora de 0-10: {bp}")
    return POTENCIA[bp]


# --------------------------------------------------------------------------
# Avaliação de uma parada
# --------------------------------------------------------------------------


@dataclass
class Resultado:
    tipo: str
    dados_normais: list[int]
    dados_fome: list[int] = field(default_factory=list)
    sucessos: int = 0
    dificuldade: int | None = None
    oponente: int | None = None
    margem: int = 0
    criticos: int = 0
    vitoria: bool = False
    desfecho: str = ""
    observacoes: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    def como_dict(self) -> dict:
        return asdict(self)


def contar_sucessos(dados: list[int]) -> tuple[int, int]:
    """Sucessos e pares de 10. Core p. 120-121: 6+ é sucesso; cada par de 10
    vale quatro sucessos no total (dois a mais que os dois 10)."""
    base = sum(1 for d in dados if d >= SUCESSO_MIN)
    pares = sum(1 for d in dados if d == 10) // 2
    return base + 2 * pares, pares


def avaliar(normais: list[int], fome: list[int] | None = None,
            dificuldade: int | None = None, oponente: int | None = None) -> Resultado:
    """Classifica uma parada já rolada.

    - Vitória: sucessos >= dificuldade, ou >= sucessos do oponente (o agente
      vence empates) — Core p. 120 e 123.
    - Crítico: vitória com ao menos um par de 10 — Core p. 120.
    - Crítico confuso: crítico com ao menos um 10 num dado de Fome — Core p. 207.
    - Falha bestial: falha com ao menos um 1 num dado de Fome — Core p. 207.
    - Falha total: nenhum sucesso — Core p. 122.
    - Vitória com custo: falha com algum sucesso; o Narrador pode oferecer — Core p. 121.
    """
    fome = list(fome or [])
    todos = list(normais) + fome
    sucessos, pares = contar_sucessos(todos)
    alvo = dificuldade if oponente is None else oponente
    if alvo is None:
        # Sem DD nem oponente não há vitória nem falha a decidir.
        r = Resultado(tipo="SEM_ALVO", dados_normais=list(normais), dados_fome=fome,
                      sucessos=sucessos, margem=sucessos, criticos=pares,
                      desfecho=f"{sucessos} sucessos (sem dificuldade definida)")
        r.observacoes.append("Defina dificuldade ou oponente para classificar o resultado")
        return r
    vitoria = sucessos >= alvo
    margem = sucessos - alvo

    if vitoria:
        if pares and 10 in fome:
            tipo, desfecho = "CRITICO_CONFUSO", "Crítico confuso — vence, mas a Besta age"
        elif pares:
            tipo, desfecho = "CRITICO", "Crítico"
        else:
            tipo, desfecho = "SUCESSO", "Sucesso"
    else:
        if 1 in fome:
            tipo, desfecho = "FALHA_BESTIAL", "Falha bestial — a Besta se manifesta"
        elif sucessos == 0:
            tipo, desfecho = "FALHA_TOTAL", "Falha total"
        else:
            tipo, desfecho = "FALHA", "Falha"

    r = Resultado(tipo=tipo, dados_normais=list(normais), dados_fome=fome,
                  sucessos=sucessos, dificuldade=dificuldade, oponente=oponente,
                  margem=margem, criticos=pares, vitoria=vitoria, desfecho=desfecho)
    if not vitoria and sucessos > 0:
        r.observacoes.append("Vitória com custo possível (Core p. 121)")
    return r


def _d10(rng: random.Random, n: int) -> list[int]:
    return [rng.randint(1, 10) for _ in range(n)]


def dividir_parada(parada: int, fome: int) -> tuple[int, int]:
    """Core p. 205: dados de Fome substituem dados normais um a um; se a
    parada for menor que a Fome, rola-se só dados de Fome."""
    parada = max(0, parada)
    n_fome = min(max(0, fome), parada)
    return parada - n_fome, n_fome


def rolar(parada: int, fome: int, dificuldade: int | None = None,
          oponente: int | None = None, rng: random.Random | None = None) -> Resultado:
    """Teste comum de Atributo + Habilidade com Fome."""
    rng = rng or random.Random()
    n_norm, n_fome = dividir_parada(parada, fome)
    r = avaliar(_d10(rng, n_norm), _d10(rng, n_fome), dificuldade, oponente)
    r.extra["parada"] = parada
    r.extra["fome"] = fome
    return r


def rerolar_fdv(anterior: Resultado, indices: list[int],
                rng: random.Random | None = None) -> Resultado:
    """Core p. 122: gastar 1 de Força de Vontade re-rola até três dados
    normais de um teste de Habilidade ou Atributo; nunca dados de Fome, nunca
    Checks nem testes de tracker. O gasto marca 1 de dano Superficial na FdV
    (Core p. 123), sem dividir pela metade (Core p. 126).

    Quem chama não deve usar esta função para testes de Força de Vontade,
    Humanidade ou frenesi, nem para Checks: resultados reconstruídos fora do
    processo perdem a marca `sem_rerolagem`."""
    if len(indices) > 3:
        raise ValueError("Força de Vontade re-rola no máximo 3 dados normais")
    if len(set(indices)) != len(indices):
        raise ValueError("Índice repetido")
    if anterior.extra.get("sem_rerolagem"):
        raise ValueError("Este teste não admite re-rolagem por Força de Vontade")
    rng = rng or random.Random()
    normais = list(anterior.dados_normais)
    for i in indices:
        if not 0 <= i < len(normais):
            raise ValueError(f"Índice fora da parada normal: {i}")
        normais[i] = rng.randint(1, 10)
    r = avaliar(normais, anterior.dados_fome, anterior.dificuldade, anterior.oponente)
    r.extra = dict(anterior.extra)
    r.extra["rerolados"] = sorted(indices)
    r.extra["custo_fdv_superficial"] = 1
    r.observacoes.append("Gasto de 1 FdV: marcar 1 Superficial na Força de Vontade (Core p. 123)")
    return r


def rolar_tracker(valor_intacto: int, dificuldade: int,
                  rng: random.Random | None = None, bonus: int = 0) -> Resultado:
    """Testes de Força de Vontade ou Humanidade — Core p. 119 e 205: a parada
    é o valor intacto do tracker (mínimo 1 dado), sem dados de Fome e sem
    re-rolagem por FdV."""
    rng = rng or random.Random()
    n = max(1, valor_intacto + bonus)
    r = avaliar(_d10(rng, n), [], dificuldade)
    r.extra["sem_rerolagem"] = True
    return r


# --------------------------------------------------------------------------
# Rouse Check — Core p. 211 e tabela p. 216
# --------------------------------------------------------------------------


def rouse(fome_atual: int, bp: int = 0, nivel_disciplina: int | None = None,
          quantidade: int = 1, forcado: bool = False,
          rng: random.Random | None = None) -> dict:
    """Cada Rouse Check rola 1 dado; 6+ mantém a Fome, falha soma 1.
    Para ativar poder de Disciplina com nível <= limite da Potência, rolam-se
    dois dados e fica o maior. Com Fome 5 não se pode despertar o sangue de
    propósito; se forçado, faz-se teste de frenesi de fome com DD 4."""
    rng = rng or random.Random()
    if fome_atual >= 5 and not forcado:
        raise ValueError("Com Fome 5 não se desperta o sangue de propósito (Core p. 211)")
    limite = potencia(bp).rouse_dois_dados_ate
    dois = nivel_disciplina is not None and 1 <= nivel_disciplina <= limite
    fome = fome_atual
    checks = []
    frenesi = False
    for _ in range(quantidade):
        dados = _d10(rng, 2 if dois else 1)
        ok = max(dados) >= SUCESSO_MIN
        if not ok:
            if fome >= 5:
                frenesi = True
            else:
                fome += 1
        checks.append({"dados": dados, "sucesso": ok})
    out = {"tipo": "ROUSE", "fome_antes": fome_atual, "fome_depois": fome,
           "dois_dados": dois, "checks": checks,
           "fonte": "Core p. 211, 216"}
    if frenesi:
        out["frenesi_de_fome"] = {"dificuldade": 4, "fonte": "Core p. 211"}
    return out


def despertar(fome_atual: int, bp: int = 0, rng: random.Random | None = None) -> dict:
    """Rouse Check ao acordar (Core p. 219). Se a falha levaria a Fome acima
    de 5, o vampiro entra em torpor em vez de testar frenesi."""
    rng = rng or random.Random()
    d = rng.randint(1, 10)
    ok = d >= SUCESSO_MIN
    out = {"tipo": "DESPERTAR", "dado": d, "sucesso": ok, "fome_antes": fome_atual,
           "fome_depois": fome_atual if ok else min(5, fome_atual + 1),
           "torpor": (not ok and fome_atual >= 5), "fonte": "Core p. 219"}
    return out


# --------------------------------------------------------------------------
# Blood Surge e cura — Core p. 218-219
# --------------------------------------------------------------------------


def surto_de_sangue(parada: int, fome_atual: int, bp: int, dificuldade: int | None = None,
                    oponente: int | None = None, rng: random.Random | None = None) -> dict:
    """Soma dados de Blood Surge (tabela p. 216) a uma parada com Atributo,
    com um Rouse Check. Vale uma rolagem; não serve para testes de FdV ou
    Humanidade (Core p. 218). A Fome do Rouse entra depois do efeito (p. 211)."""
    rng = rng or random.Random()
    if fome_atual >= 5:
        raise ValueError("Com Fome 5 não se desperta o sangue para um Blood Surge (Core p. 211)")
    bonus = potencia(bp).surto
    teste = rolar(parada + bonus, fome_atual, dificuldade, oponente, rng)
    teste.extra["surto"] = bonus
    custo = rouse(fome_atual, bp, rng=rng)
    return {"tipo": "SURTO", "bonus": bonus, "teste": teste.como_dict(), "rouse": custo,
            "fonte": "Core p. 216, 218"}


def curar_superficial(dano_superficial: int, fome_atual: int, bp: int,
                      rng: random.Random | None = None) -> dict:
    """Um Rouse Check por turno cura dano Superficial de Saúde conforme a
    Potência (Core p. 218, tabela p. 216)."""
    rng = rng or random.Random()
    cura = min(dano_superficial, potencia(bp).cura_superficial)
    custo = rouse(fome_atual, bp, rng=rng)
    return {"tipo": "CURA_SUPERFICIAL", "curado": cura,
            "dano_restante": dano_superficial - cura, "rouse": custo,
            "fonte": "Core p. 216, 218"}


def curar_agravado(fome_atual: int, bp: int, rng: random.Random | None = None) -> dict:
    """Ao anoitecer, três Rouse Checks além do de despertar curam 1 de dano
    Agravado (e um ferimento incapacitante); só 1 por noite. Se a Fome
    passaria de 5, o vampiro entra em torpor (Core p. 218-219)."""
    rng = rng or random.Random()
    fome = fome_atual
    checks = []
    torpor = False
    for _ in range(3):
        d = rng.randint(1, 10)
        ok = d >= SUCESSO_MIN
        if not ok:
            if fome >= 5:
                torpor = True
            else:
                fome += 1
        checks.append({"dados": [d], "sucesso": ok})
    return {"tipo": "CURA_AGRAVADO", "curado": 0 if torpor else 1,
            "fome_antes": fome_atual, "fome_depois": fome, "checks": checks,
            "torpor": torpor, "fonte": "Core p. 218-219"}


# --------------------------------------------------------------------------
# Frenesi e Remorso
# --------------------------------------------------------------------------


def frenesi(fdv_intacta: int, humanidade: int, dificuldade: int,
            rng: random.Random | None = None) -> Resultado:
    """Core p. 219: rola a Força de Vontade (intacta) mais um terço da
    Humanidade, arredondado para baixo, contra a DD do Narrador. Vitória
    resiste, mas gasta um turno contendo a Besta; crítico resiste sem perder
    o turno."""
    bonus = humanidade // 3
    r = rolar_tracker(fdv_intacta, dificuldade, rng, bonus=bonus)
    r.extra.update({"bonus_humanidade": bonus, "parada": max(1, fdv_intacta + bonus)})
    if r.vitoria and r.criticos:
        r.desfecho = "Frenesi resistido sem perder o turno"
    elif r.vitoria:
        r.desfecho = "Frenesi resistido — gasta o turno contendo a Besta"
    else:
        r.desfecho = "FRENESI — a Besta assume"
    r.tipo = "FRENESI_" + ("RESISTIDO" if r.vitoria else "FALHOU")
    r.observacoes.append("Core p. 219")
    return r


def remorso(humanidade: int, manchas: int, rng: random.Random | None = None) -> dict:
    """Core p. 239: rola um dado por caixa da Humanidade sem ponto e sem
    Mancha (10 - Humanidade - Manchas), mínimo 1. Um sucesso mantém a
    Humanidade; nenhum tira 1. Em ambos os casos as Manchas são apagadas."""
    rng = rng or random.Random()
    n = max(1, 10 - humanidade - manchas)
    dados = _d10(rng, n)
    sucessos = sum(1 for d in dados if d >= SUCESSO_MIN)
    mantem = sucessos > 0
    return {"tipo": "REMORSO", "dados": dados, "sucessos": sucessos,
            "humanidade_antes": humanidade,
            "humanidade_depois": humanidade if mantem else humanidade - 1,
            "manchas_depois": 0,
            "desfecho": "Remorso sentido — Humanidade mantida" if mantem
            else "Sem remorso — Humanidade -1",
            "fonte": "Core p. 239"}


# --------------------------------------------------------------------------
# Conflito e dano — Core p. 124-127
# --------------------------------------------------------------------------


def conflito(parada_a: int, fome_a: int, parada_b: int, fome_b: int = 0,
             dois_lados: bool = False, arma_a: int = 0, arma_b: int = 0,
             rng: random.Random | None = None) -> dict:
    """Disputa de conflito. Quem tiver mais sucessos vence e causa a margem
    (sucessos do vencedor menos os do perdedor) mais o bônus da arma. Num
    conflito de dois lados, empate faz os dois causarem dano com margem 1
    (Core p. 124-126). Em conflito de um lado só (defesa pura), só A causa dano.
    O lado B é tratado como PNJ e usa dados de Fome apenas se informados."""
    rng = rng or random.Random()
    a = rolar(parada_a, fome_a, rng=rng)
    b = rolar(parada_b, fome_b, rng=rng)
    a_final = avaliar(a.dados_normais, a.dados_fome, oponente=b.sucessos)
    # B só vence com mais sucessos que A (o agente vence empates, Core p. 123);
    # num conflito de dois lados o empate conta para os dois.
    alvo_b = a.sucessos if dois_lados else a.sucessos + 1
    b_final = avaliar(b.dados_normais, b.dados_fome, oponente=alvo_b)
    b_final.margem = b.sucessos - a.sucessos
    b_final.oponente = a.sucessos
    out = {"tipo": "CONFLITO", "a": a_final.como_dict(), "b": b_final.como_dict(),
           "dano_em_a": 0, "dano_em_b": 0, "fonte": "Core p. 124-126"}
    if a.sucessos > b.sucessos:
        out["dano_em_b"] = (a.sucessos - b.sucessos) + arma_a
        out["vencedor"] = "A"
    elif b.sucessos > a.sucessos:
        out["vencedor"] = "B"
        if dois_lados:
            out["dano_em_a"] = (b.sucessos - a.sucessos) + arma_b
    else:
        if dois_lados:
            out["vencedor"] = "EMPATE"
            out["dano_em_a"] = 1 + arma_b
            out["dano_em_b"] = 1 + arma_a
        else:
            # Em disputa comum o agente vence empates (Core p. 123); sem margem, sem dano.
            out["vencedor"] = "A"
    return out


def aplicar_dano(dano: int, tipo: str, alvo_vampiro: bool = True,
                 por_gasto: bool = False) -> dict:
    """Core p. 126: dano Superficial é dividido pela metade (arredondando
    para cima) antes de marcar, salvo regra em contrário; pontos gastos de
    um tracker (ex.: FdV) não são divididos."""
    tipo = tipo.lower()
    if tipo not in ("superficial", "agravado"):
        raise ValueError("tipo deve ser 'superficial' ou 'agravado'")
    if tipo == "superficial" and not por_gasto:
        marcado = math.ceil(dano / 2)
    else:
        marcado = dano
    return {"tipo": "DANO", "dano_bruto": dano, "natureza": tipo, "marcado": marcado,
            "fonte": "Core p. 126"}


# --------------------------------------------------------------------------
# Alimentação — Core p. 211-212 e tabela p. 216
# --------------------------------------------------------------------------

FONTES = {
    # fonte: (Fome saciada, é animal/bolsa?, é humano?, mata?)
    "animais_pequenos": (1, True, False, False),
    "animal_medio": (1, True, False, False),
    "animal_grande": (2, True, False, False),
    "bolsa": (1, True, False, False),
    "gole_humano": (1, False, True, False),
    "humano_seguro": (2, False, True, False),
    "humano_drenar_e_matar": (5, False, True, True),
}


def alimentar(fonte: str, fome_atual: int, bp: int, quantidade_arriscada: int = 0) -> dict:
    """Quanto de Fome uma alimentação sacia (tabela Core p. 212) depois das
    penalidades da Potência (p. 216). Só drenar e matar um humano chega a
    Fome 0; fora isso a Fome não cai abaixo do piso da Potência (p. 211, 216).
    `humano_arriscado` sacia de 1 a 4 (quantidade_arriscada) e causa dano
    Agravado igual ao saciado na vítima."""
    linha = potencia(bp)
    if fonte == "humano_arriscado":
        if not 1 <= quantidade_arriscada <= 4:
            raise ValueError("humano_arriscado precisa de quantidade_arriscada entre 1 e 4")
        base, animal, humano, mata = quantidade_arriscada, False, True, False
    elif fonte in FONTES:
        base, animal, humano, mata = FONTES[fonte]
    else:
        raise ValueError(f"Fonte desconhecida: {fonte}")

    saciado = base
    notas = []
    if animal:
        if linha.animal_bolsa == "nada":
            saciado = 0
            notas.append("Sangue animal ou de bolsa não sacia nesta Potência (Core p. 216)")
        elif linha.animal_bolsa == "metade":
            saciado = base // 2
            notas.append("Sangue animal ou de bolsa sacia metade (Core p. 216) [arredondamento a verificar]")
    if humano and not mata:
        saciado = max(0, saciado - linha.sacia_menos_humano)
    piso = 0 if mata else linha.fome_minima_sem_matar
    fome_depois = max(piso, fome_atual - saciado) if fome_atual > piso else fome_atual
    out = {"tipo": "ALIMENTACAO", "fonte_sangue": fonte, "fome_antes": fome_atual,
           "saciado": fome_atual - fome_depois, "fome_depois": fome_depois,
           "piso_sem_matar": linha.fome_minima_sem_matar, "notas": notas,
           "fonte": "Core p. 211-212, 216"}
    if fonte == "humano_arriscado":
        out["vitima"] = {"dano_agravado": quantidade_arriscada,
                         "teste": f"Vigor + Força da vítima, DD {quantidade_arriscada}, para sobreviver"}
    return out


# --------------------------------------------------------------------------
# Registro
# --------------------------------------------------------------------------


def registrar(pasta_campanha: str | Path | None, comando: str, resultado: dict) -> Path | None:
    """Acrescenta a rolagem a `rolagens.jsonl` da campanha. Sem pasta, não grava."""
    if not pasta_campanha:
        return None
    pasta = Path(pasta_campanha)
    if not pasta.is_dir():
        return None
    arq = pasta / "rolagens.jsonl"
    linha = {"quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "comando": comando, "resultado": resultado}
    with arq.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return arq
