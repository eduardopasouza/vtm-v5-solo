#!/usr/bin/env python3
"""CLI do motor de dados VtM V5 (regras em vtm_motor.py).

Saída: texto para o jogador, depois `---JSON---` e o resultado em JSON.
Registro: com `--campanha <pasta>` (ou a variável VTM_CAMPANHA), cada rolagem
é acrescentada a `<pasta>/rolagens.jsonl`.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_motor as m  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def _lista(txt: str) -> list[int]:
    return [int(x) for x in txt.split(",") if x.strip()] if txt else []


def _fmt_resultado(r: dict, titulo: str) -> list[str]:
    linhas = [titulo]
    if r.get("dados_normais"):
        linhas.append("   Normal: " + " ".join(f"[{d}]" for d in r["dados_normais"]))
    if r.get("dados_fome"):
        linhas.append("   Fome:   " + " ".join(f"({d})" for d in r["dados_fome"]))
    alvo = r.get("oponente") if r.get("oponente") is not None else r.get("dificuldade")
    alvo_txt = f" vs {alvo}" if alvo is not None else ""
    linhas.append(f"   {r['desfecho']} — {r['sucessos']} sucessos{alvo_txt} (margem {r['margem']:+d})")
    for o in r.get("observacoes", []):
        linhas.append(f"   · {o}")
    return linhas


def _fmt_rouse(r: dict) -> list[str]:
    linhas = [f"🎲 Rouse Check{' (2 dados, fica o maior)' if r['dois_dados'] else ''}"]
    for i, c in enumerate(r["checks"], 1):
        linhas.append(f"   {i}: {c['dados']} → {'ok' if c['sucesso'] else 'Fome +1'}")
    linhas.append(f"   Fome {r['fome_antes']} → {r['fome_depois']}")
    if "frenesi_de_fome" in r:
        linhas.append("   ⚠ Falhou com Fome 5: teste de frenesi de fome, DD 4")
    return linhas


def formatar(cmd: str, r: dict) -> str:
    if cmd in ("roll", "reroll", "tracker", "frenzy"):
        return "\n".join(_fmt_resultado(r, f"🎲 {cmd}"))
    if cmd == "rouse":
        return "\n".join(_fmt_rouse(r))
    if cmd == "surge":
        return "\n".join(_fmt_resultado(r["teste"], f"🎲 Blood Surge (+{r['bonus']} dados)")
                         + _fmt_rouse(r["rouse"]))
    if cmd == "conflict":
        out = _fmt_resultado(r["a"], "🎲 Conflito — lado A") + _fmt_resultado(r["b"], "   lado B")
        out.append(f"   Vencedor: {r['vencedor']} · dano em A: {r['dano_em_a']} · dano em B: {r['dano_em_b']}")
        return "\n".join(out)
    resumo = {k: v for k, v in r.items() if k not in ("fonte",)}
    return f"🎲 {r.get('tipo', cmd)}\n   " + json.dumps(resumo, ensure_ascii=False)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vtm_dice", description="Motor de dados VtM V5")
    p.add_argument("--campanha", default=os.environ.get("VTM_CAMPANHA"),
                   help="pasta da campanha para gravar rolagens.jsonl")
    p.add_argument("--semente", type=int, help="semente fixa (testes)")
    s = p.add_subparsers(dest="cmd", required=True)

    a = s.add_parser("roll", help="teste comum: parada total e Fome (a Fome substitui dados)")
    a.add_argument("parada", type=int); a.add_argument("fome", type=int)
    a.add_argument("dificuldade", type=int, nargs="?")
    a.add_argument("--oponente", type=int)

    a = s.add_parser("reroll", help="re-rolar até 3 dados normais com 1 FdV")
    a.add_argument("--normais", required=True); a.add_argument("--fome", default="")
    a.add_argument("--indices", required=True, help="posições (0-base) dos dados normais")
    a.add_argument("--dificuldade", type=int); a.add_argument("--oponente", type=int)

    a = s.add_parser("tracker", help="teste de Força de Vontade ou Humanidade")
    a.add_argument("valor_intacto", type=int); a.add_argument("dificuldade", type=int)

    a = s.add_parser("rouse", help="Rouse Check")
    a.add_argument("fome", type=int, nargs="?", default=0)
    a.add_argument("--bp", type=int, default=0); a.add_argument("--nivel", type=int)
    a.add_argument("--quantidade", type=int, default=1); a.add_argument("--forcado", action="store_true")

    a = s.add_parser("despertar", help="Rouse Check ao acordar")
    a.add_argument("fome", type=int); a.add_argument("--bp", type=int, default=0)

    a = s.add_parser("surge", help="Blood Surge numa parada com Atributo")
    a.add_argument("parada", type=int); a.add_argument("fome", type=int); a.add_argument("bp", type=int)
    a.add_argument("dificuldade", type=int, nargs="?"); a.add_argument("--oponente", type=int)

    a = s.add_parser("mend", help="curar dano Superficial (1 Rouse)")
    a.add_argument("dano_superficial", type=int); a.add_argument("fome", type=int); a.add_argument("bp", type=int)

    a = s.add_parser("mend-agg", help="curar 1 dano Agravado ao anoitecer (3 Rouses)")
    a.add_argument("fome", type=int); a.add_argument("bp", type=int)

    a = s.add_parser("frenzy", help="resistir ao frenesi")
    a.add_argument("fdv_intacta", type=int); a.add_argument("humanidade", type=int)
    a.add_argument("dificuldade", type=int)

    a = s.add_parser("remorse", help="teste de Remorso")
    a.add_argument("humanidade", type=int); a.add_argument("manchas", type=int)

    a = s.add_parser("conflict", help="conflito entre A e B")
    a.add_argument("parada_a", type=int); a.add_argument("fome_a", type=int); a.add_argument("parada_b", type=int)
    a.add_argument("--fome-b", type=int, default=0); a.add_argument("--dois-lados", action="store_true")
    a.add_argument("--arma-a", type=int, default=0); a.add_argument("--arma-b", type=int, default=0)

    a = s.add_parser("damage", help="dano a marcar no tracker")
    a.add_argument("dano", type=int); a.add_argument("natureza", choices=["superficial", "agravado"])
    a.add_argument("--gasto", action="store_true")

    a = s.add_parser("feed", help="alimentação")
    a.add_argument("fonte", choices=sorted(list(m.FONTES) + ["humano_arriscado"]))
    a.add_argument("fome", type=int); a.add_argument("bp", type=int)
    a.add_argument("--quantidade", type=int, default=0, help="para humano_arriscado: 1-4")
    return p


def executar(args: argparse.Namespace) -> dict:
    import random
    rng = random.Random(args.semente) if args.semente is not None else random.Random()
    c = args.cmd
    if c == "roll":
        if args.dificuldade is None and args.oponente is None:
            raise ValueError("roll precisa de dificuldade ou --oponente")
        return m.rolar(args.parada, args.fome, args.dificuldade, args.oponente, rng).como_dict()
    if c == "reroll":
        ant = m.avaliar(_lista(args.normais), _lista(args.fome), args.dificuldade, args.oponente)
        return m.rerolar_fdv(ant, _lista(args.indices), rng).como_dict()
    if c == "tracker":
        return m.rolar_tracker(args.valor_intacto, args.dificuldade, rng).como_dict()
    if c == "rouse":
        return m.rouse(args.fome, args.bp, args.nivel, args.quantidade, args.forcado, rng)
    if c == "despertar":
        return m.despertar(args.fome, args.bp, rng)
    if c == "surge":
        return m.surto_de_sangue(args.parada, args.fome, args.bp, args.dificuldade, args.oponente, rng)
    if c == "mend":
        return m.curar_superficial(args.dano_superficial, args.fome, args.bp, rng)
    if c == "mend-agg":
        return m.curar_agravado(args.fome, args.bp, rng)
    if c == "frenzy":
        return m.frenesi(args.fdv_intacta, args.humanidade, args.dificuldade, rng).como_dict()
    if c == "remorse":
        return m.remorso(args.humanidade, args.manchas, rng)
    if c == "conflict":
        return m.conflito(args.parada_a, args.fome_a, args.parada_b, args.fome_b,
                          args.dois_lados, args.arma_a, args.arma_b, rng)
    if c == "damage":
        return m.aplicar_dano(args.dano, args.natureza, por_gasto=args.gasto)
    if c == "feed":
        return m.alimentar(args.fonte, args.fome, args.bp, args.quantidade)
    raise SystemExit(f"Comando desconhecido: {c}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    args = parser().parse_args(argv)
    try:
        resultado = executar(args)
    except ValueError as e:
        print(f"Erro: {e}")
        return 2
    print(formatar(args.cmd, resultado))
    m.registrar(args.campanha, " ".join(argv), resultado)
    print(f"\n---JSON---\n{json.dumps(resultado, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
