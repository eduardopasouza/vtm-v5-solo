#!/usr/bin/env python3
"""
VtM V5 Dice Roller — Vampire: The Masquerade 5th Edition
Rolagem real de dados para campanhas solo.
"""

import random
import sys
import json
import io

# Fix Windows cp1252 encoding — force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def roll_dice(pool_normal: int, pool_fome: int, dificuldade: int) -> dict:
    """Rola dados VtM V5 com pool normal + dados de Fome."""
    dados_normais = [random.randint(1, 10) for _ in range(pool_normal)]
    dados_fome = [random.randint(1, 10) for _ in range(pool_fome)]
    todos = dados_normais + dados_fome

    sucessos = sum(1 for d in todos if d >= 6)

    # Críticos: pares de 10s geram +2 sucessos extras cada par
    tens_normais = sum(1 for d in dados_normais if d == 10)
    tens_fome = sum(1 for d in dados_fome if d == 10)
    total_tens = tens_normais + tens_fome
    pares_criticos = total_tens // 2
    sucessos += pares_criticos * 2  # cada par de 10s = 4 sucessos (2 já contados + 2 extras)

    # Determinar tipo de resultado
    margem = sucessos - dificuldade
    falha = sucessos < dificuldade
    tem_critico = pares_criticos > 0
    tem_1_fome = any(d == 1 for d in dados_fome)
    tem_10_fome = any(d == 10 for d in dados_fome)

    if falha and tem_1_fome:
        tipo = "FALHA_BESTIAL"
        simbolo = "🩸"
        descricao = "Falha Bestial — A Besta se manifesta"
    elif falha:
        tipo = "FALHA"
        simbolo = "✗"
        descricao = "Falha"
    elif tem_critico and tem_10_fome:
        tipo = "CRITICO_CONFUSO"
        simbolo = "⚠"
        descricao = "Crítico Confuso — Sucesso com consequências bestiais"
    elif tem_critico:
        tipo = "CRITICO"
        simbolo = "✦"
        descricao = "Crítico!"
    else:
        tipo = "SUCESSO"
        simbolo = "✓"
        descricao = "Sucesso"

    return {
        "dados_normais": dados_normais,
        "dados_fome": dados_fome,
        "sucessos": sucessos,
        "dificuldade": dificuldade,
        "margem": margem,
        "pares_criticos": pares_criticos,
        "tipo": tipo,
        "simbolo": simbolo,
        "descricao": descricao,
        "pool_total": pool_normal + pool_fome,
    }


def rouse_check(quantidade: int = 1) -> dict:
    """Rouse Check — cada dado que resulta em 1-5 aumenta Fome em 1."""
    resultados = []
    fome_ganha = 0
    for _ in range(quantidade):
        dado = random.randint(1, 10)
        falhou = dado <= 5
        if falhou:
            fome_ganha += 1
        resultados.append({"dado": dado, "falhou": falhou})

    return {
        "tipo": "ROUSE_CHECK",
        "resultados": resultados,
        "fome_ganha": fome_ganha,
        "quantidade": quantidade,
        "descricao": f"Rouse Check: +{fome_ganha} Fome" if fome_ganha > 0 else "Rouse Check: Fome estável",
    }


def teste_remorso(humanidade_desmarcada: int) -> dict:
    """Teste de Remorso — rola dados = marcações vazias de Humanidade."""
    if humanidade_desmarcada <= 0:
        return {
            "tipo": "REMORSO",
            "dados": [],
            "sucessos": 0,
            "resultado": "DEGENERAÇÃO",
            "descricao": "Sem dados para rolar — Humanidade cai automaticamente",
        }

    dados = [random.randint(1, 10) for _ in range(humanidade_desmarcada)]
    sucessos = sum(1 for d in dados if d >= 6)

    if sucessos > 0:
        resultado = "REMORSO"
        descricao = "Remorso sentido — Humanidade preservada, Manchas removidas"
    else:
        resultado = "DEGENERAÇÃO"
        descricao = "Sem remorso — Humanidade cai em 1 ponto"

    return {
        "tipo": "REMORSO",
        "dados": dados,
        "sucessos": sucessos,
        "resultado": resultado,
        "descricao": descricao,
    }


def teste_frenesi(pool: int, dificuldade: int = 3) -> dict:
    """Teste de Frenesi — pool de Compostura + Determinação."""
    dados = [random.randint(1, 10) for _ in range(pool)]
    sucessos = sum(1 for d in dados if d >= 6)

    if sucessos >= dificuldade:
        resultado = "RESISTIDO"
        descricao = f"Frenesi resistido ({sucessos} sucessos vs DD {dificuldade})"
    else:
        resultado = "FRENESI"
        descricao = f"FRENESI! A Besta assume o controle ({sucessos} vs DD {dificuldade})"

    return {
        "tipo": "FRENESI",
        "dados": dados,
        "sucessos": sucessos,
        "dificuldade": dificuldade,
        "resultado": resultado,
        "descricao": descricao,
    }


def formatar_resultado(resultado: dict) -> str:
    """Formata o resultado para exibição."""
    linhas = []

    if resultado["tipo"] == "ROUSE_CHECK":
        linhas.append(f"🎲 Rouse Check ({resultado['quantidade']}x)")
        for i, r in enumerate(resultado["resultados"], 1):
            status = "✗ Fome +1" if r["falhou"] else "✓ OK"
            linhas.append(f"   Dado {i}: [{r['dado']}] → {status}")
        linhas.append(f"   Resultado: {resultado['descricao']}")

    elif resultado["tipo"] == "REMORSO":
        linhas.append("🎲 Teste de Remorso")
        if resultado["dados"]:
            linhas.append(f"   Dados: {resultado['dados']}")
            linhas.append(f"   Sucessos: {resultado['sucessos']}")
        linhas.append(f"   Resultado: {resultado['descricao']}")

    elif resultado["tipo"] == "FRENESI":
        linhas.append("🎲 Teste de Frenesi")
        linhas.append(f"   Pool: {len(resultado['dados'])} | DD: {resultado['dificuldade']}")
        linhas.append(f"   Dados: {resultado['dados']}")
        linhas.append(f"   Resultado: {resultado['descricao']}")

    else:  # Rolagem padrão
        r = resultado
        linhas.append(f"🎲 Rolagem | Pool: {r['pool_total']} (Normal: {len(r['dados_normais'])} + Fome: {len(r['dados_fome'])}) | DD: {r['dificuldade']}")

        normais_str = " ".join(f"[{d}]" for d in r["dados_normais"])
        fome_str = " ".join(f"({d})" for d in r["dados_fome"])
        linhas.append(f"   Normal: {normais_str}")
        if r["dados_fome"]:
            linhas.append(f"   Fome:   {fome_str}")

        linhas.append(f"   {r['simbolo']} {r['descricao']} — {r['sucessos']} sucessos (margem: {r['margem']:+d})")

    return "\n".join(linhas)


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python vtm_dice.py roll <normais> <fome> <dificuldade>")
        print("  python vtm_dice.py rouse [quantidade]")
        print("  python vtm_dice.py remorse <humanidade_desmarcada>")
        print("  python vtm_dice.py frenzy <pool> [dificuldade]")
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando == "roll":
        if len(sys.argv) < 5:
            print("Erro: roll requer <normais> <fome> <dificuldade>")
            sys.exit(1)
        normais = int(sys.argv[2])
        fome = int(sys.argv[3])
        dificuldade = int(sys.argv[4])
        resultado = roll_dice(normais, fome, dificuldade)

    elif comando == "rouse":
        qtd = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        resultado = rouse_check(qtd)

    elif comando == "remorse":
        if len(sys.argv) < 3:
            print("Erro: remorse requer <humanidade_desmarcada>")
            sys.exit(1)
        humanidade = int(sys.argv[2])
        resultado = teste_remorso(humanidade)

    elif comando == "frenzy":
        if len(sys.argv) < 3:
            print("Erro: frenzy requer <pool> [dificuldade]")
            sys.exit(1)
        pool = int(sys.argv[2])
        dif = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        resultado = teste_frenesi(pool, dif)

    else:
        print(f"Comando desconhecido: {comando}")
        sys.exit(1)

    # Output formatado para humano
    print(formatar_resultado(resultado))

    # Output JSON para processamento
    print(f"\n---JSON---\n{json.dumps(resultado, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
