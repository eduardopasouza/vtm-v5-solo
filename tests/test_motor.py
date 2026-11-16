"""Testes do núcleo de regras com dados escolhidos (Core = V5 Core Rulebook,
página impressa)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import vtm_motor as m  # noqa: E402


class Dados:
    """Substitui random.Random: devolve a sequência dada, em ordem."""

    def __init__(self, *valores):
        self.valores = list(valores)

    def randint(self, a, b):
        assert a == 1 and b == 10
        return self.valores.pop(0)


# --- avaliação básica (Core p. 120-122, 207) --------------------------------

def test_sucesso_simples():
    r = m.avaliar([6, 7, 2], [], dificuldade=2)
    assert (r.sucessos, r.tipo, r.margem) == (2, "SUCESSO", 0)


def test_par_de_dez_vale_quatro():
    r = m.avaliar([10, 10, 3], [], dificuldade=3)
    assert r.sucessos == 4 and r.tipo == "CRITICO" and r.criticos == 1


def test_tres_dez_valem_cinco_quatro_dez_valem_oito():
    assert m.avaliar([10, 10, 10], []).sucessos == 5
    assert m.avaliar([10, 10, 10, 10], []).sucessos == 8


def test_critico_confuso_com_dez_na_fome():
    r = m.avaliar([10, 4], [10], dificuldade=3)
    assert r.tipo == "CRITICO_CONFUSO"


def test_dez_na_fome_sem_par_nao_e_confuso():
    r = m.avaliar([7, 4], [10], dificuldade=2)
    assert r.tipo == "SUCESSO"


def test_falha_bestial():
    # Exemplo da Core p. 206: parada 4, Fome 2, DD 3, um sucesso, 1 na Fome.
    r = m.avaliar([6, 3], [1, 4], dificuldade=3)
    assert r.tipo == "FALHA_BESTIAL" and not r.vitoria


def test_um_na_fome_com_vitoria_nao_e_bestial():
    r = m.avaliar([6, 7], [1], dificuldade=2)
    assert r.tipo == "SUCESSO"


def test_falha_total_e_vitoria_com_custo():
    assert m.avaliar([2, 3], [], dificuldade=1).tipo == "FALHA_TOTAL"
    r = m.avaliar([6, 3], [], dificuldade=3)
    assert r.tipo == "FALHA" and r.observacoes


def test_sem_alvo_nao_vira_sucesso():
    r = m.avaliar([2, 3], [1])
    assert r.tipo == "SEM_ALVO" and not r.vitoria


def test_agente_vence_empate_em_disputa():
    r = m.avaliar([6, 7], [], oponente=2)
    assert r.vitoria and r.margem == 0


# --- parada com Fome (Core p. 205) ------------------------------------------

def test_fome_substitui_dados_normais():
    r = m.rolar(6, 2, 3, rng=Dados(1, 2, 3, 4, 5, 6))
    assert len(r.dados_normais) == 4 and len(r.dados_fome) == 2


def test_parada_menor_que_fome_vira_toda_fome():
    assert m.dividir_parada(2, 4) == (0, 2)


# --- Força de Vontade (Core p. 122-123) --------------------------------------

def test_rerolagem_fdv_so_normais_ate_tres():
    r = m.avaliar([2, 3, 4, 8], [1], dificuldade=3)
    novo = m.rerolar_fdv(r, [0, 1, 2], rng=Dados(6, 7, 9))
    assert novo.dados_normais == [6, 7, 9, 8]
    assert novo.dados_fome == [1]
    assert novo.tipo == "SUCESSO"
    with pytest.raises(ValueError):
        m.rerolar_fdv(r, [0, 1, 2, 3])
    with pytest.raises(ValueError):
        m.rerolar_fdv(r, [4])  # índice do dado de Fome


def test_teste_de_tracker_nao_rerola_e_tem_minimo_um():
    r = m.rolar_tracker(0, 2, rng=Dados(7))
    assert len(r.dados_normais) == 1
    with pytest.raises(ValueError):
        m.rerolar_fdv(r, [0])


# --- Rouse (Core p. 211, 216) ------------------------------------------------

def test_rouse_falha_sobe_fome():
    out = m.rouse(2, rng=Dados(5))
    assert out["fome_depois"] == 3


def test_rouse_dois_dados_pela_potencia():
    # Potência 3: poderes até nível 2 rolam dois dados.
    out = m.rouse(2, bp=3, nivel_disciplina=2, rng=Dados(3, 8))
    assert out["dois_dados"] and out["fome_depois"] == 2
    out = m.rouse(2, bp=3, nivel_disciplina=3, rng=Dados(3))
    assert not out["dois_dados"] and out["fome_depois"] == 3


def test_rouse_com_fome_cinco():
    with pytest.raises(ValueError):
        m.rouse(5, rng=Dados(7))
    out = m.rouse(5, forcado=True, rng=Dados(2))
    assert out["fome_depois"] == 5 and out["frenesi_de_fome"]["dificuldade"] == 4


def test_despertar_com_fome_cinco_vira_torpor():
    assert m.despertar(5, rng=Dados(3))["torpor"]
    assert not m.despertar(4, rng=Dados(3))["torpor"]


# --- Potência, surto e cura (Core p. 216-219) -------------------------------

def test_tabela_potencia_pontos_de_referencia():
    assert m.potencia(1).surto == 1 and m.potencia(1).severidade_perdicao == 1
    assert m.potencia(5).cura_superficial == 3 and m.potencia(5).rouse_dois_dados_ate == 3
    assert m.potencia(10).bonus_disciplina == 5
    # Células de alimentação compartilhadas no Core p. 216: 6-7 e 8-9.
    assert m.potencia(7).sacia_menos_humano == m.potencia(6).sacia_menos_humano == 2
    assert m.potencia(9).sacia_menos_humano == m.potencia(8).sacia_menos_humano == 2
    assert m.potencia(9).fome_minima_sem_matar == 3
    with pytest.raises(ValueError):
        m.potencia(11)


def test_surto_soma_dados_e_cobra_rouse():
    # Potência 3 soma 2 dados: parada 3 vira 5 (Fome 1). Depois o Rouse.
    out = m.surto_de_sangue(3, 1, 3, dificuldade=2, rng=Dados(6, 6, 2, 2, 4, 9))
    assert out["bonus"] == 2
    assert len(out["teste"]["dados_normais"]) == 4
    assert out["rouse"]["fome_depois"] == 1


def test_surto_com_fome_cinco_nao_rola():
    with pytest.raises(ValueError):
        m.surto_de_sangue(3, 5, 1, dificuldade=2, rng=Dados())


def test_cura_superficial_pela_potencia():
    out = m.curar_superficial(5, 1, 2, rng=Dados(7))
    assert out["curado"] == 2 and out["dano_restante"] == 3


def test_cura_agravada_tres_rouses_e_torpor():
    out = m.curar_agravado(2, 1, rng=Dados(7, 3, 8))
    assert out["curado"] == 1 and out["fome_depois"] == 3
    out = m.curar_agravado(5, 1, rng=Dados(2, 7, 7))
    assert out["torpor"] and out["curado"] == 0


# --- Frenesi e Remorso (Core p. 219, 239) ------------------------------------

def test_frenesi_soma_terco_da_humanidade():
    # FdV 4 intacta + Humanidade 7 // 3 = 2 -> 6 dados.
    r = m.frenesi(4, 7, 3, rng=Dados(6, 6, 6, 1, 1, 1))
    assert r.extra["parada"] == 6 and r.vitoria
    assert "gasta o turno" in r.desfecho


def test_frenesi_critico_nao_perde_turno():
    r = m.frenesi(3, 3, 3, rng=Dados(10, 10, 1, 1))
    assert r.desfecho == "Frenesi resistido sem perder o turno"


def test_remorso_caixas_vazias_e_minimo():
    # Core p. 239: Humanidade 6 com 2 Manchas rola 2 dados.
    out = m.remorso(6, 2, rng=Dados(3, 7))
    assert len(out["dados"]) == 2 and out["humanidade_depois"] == 6
    out = m.remorso(7, 3, rng=Dados(4))
    assert len(out["dados"]) == 1 and out["humanidade_depois"] == 6
    assert out["manchas_depois"] == 0


# --- Conflito e dano (Core p. 124-126) ---------------------------------------

def test_conflito_margem_mais_arma():
    out = m.conflito(3, 0, 2, arma_a=2, rng=Dados(6, 7, 8, 6, 1))
    assert out["vencedor"] == "A" and out["dano_em_b"] == 4


def test_conflito_dois_lados_empate():
    out = m.conflito(2, 0, 2, dois_lados=True, rng=Dados(6, 1, 7, 2))
    assert out["vencedor"] == "EMPATE" and out["dano_em_a"] == 1 and out["dano_em_b"] == 1


def test_lado_b_classificado_contra_a():
    # A: 2 sucessos. B (vampiro, Fome 1): 1 sucesso com 1 na Fome -> falha bestial de B.
    out = m.conflito(2, 0, 2, fome_b=1, rng=Dados(6, 7, 6, 1))
    assert out["b"]["tipo"] == "FALHA_BESTIAL" and out["b"]["margem"] == -1
    # Empate em conflito de um lado: A vence, B não.
    out = m.conflito(1, 0, 1, rng=Dados(6, 6))
    assert out["a"]["vitoria"] and not out["b"]["vitoria"]


def test_defesa_pura_nao_causa_dano():
    out = m.conflito(2, 0, 3, rng=Dados(1, 1, 6, 6, 6))
    assert out["vencedor"] == "B" and out["dano_em_a"] == 0


def test_dano_superficial_dividido_arredonda_para_cima():
    assert m.aplicar_dano(5, "superficial")["marcado"] == 3
    assert m.aplicar_dano(5, "agravado")["marcado"] == 5
    assert m.aplicar_dano(1, "superficial", por_gasto=True)["marcado"] == 1


# --- Alimentação (Core p. 211-212, 216) --------------------------------------

def test_alimentacao_humano_seguro_e_piso():
    out = m.alimentar("humano_seguro", 3, 1)
    assert out["fome_depois"] == 1
    out = m.alimentar("humano_seguro", 2, 1)
    assert out["fome_depois"] == 1  # não desce abaixo de 1 sem matar


def test_so_matar_chega_a_zero():
    assert m.alimentar("humano_drenar_e_matar", 4, 1)["fome_depois"] == 0


def test_animal_nao_sacia_acima_de_potencia_dois():
    assert m.alimentar("animal_grande", 4, 3)["fome_depois"] == 4
    assert m.alimentar("animal_grande", 4, 1)["fome_depois"] == 2


def test_penalidade_humana_pela_potencia():
    # Potência 4 sacia 1 a menos por humano: gole seguro de 2 vira 1.
    assert m.alimentar("humano_seguro", 4, 4)["fome_depois"] == 3


def test_registro_jsonl(tmp_path):
    arq = m.registrar(tmp_path, "roll 5 1 3", {"tipo": "SUCESSO"})
    assert arq.exists() and "roll 5 1 3" in arq.read_text(encoding="utf-8")
    assert m.registrar(None, "x", {}) is None
