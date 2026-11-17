#!/usr/bin/env python3
"""CLI da memória da campanha (regras em vtm_campanha.py).

  campanha.py auditar <pasta_da_campanha> [--json]
  campanha.py validar <pasta_da_campanha>
  campanha.py resumo  <pasta_da_campanha>
  campanha.py hook    # SessionStart: lê o JSON do hook no stdin

O modo `hook` usa CLAUDE_PLUGIN_OPTION_PASTA_CAMPANHAS e
CLAUDE_PLUGIN_OPTION_CAMPANHA_ATIVA (exportadas pelo Claude Code aos hooks de
plugin). Na abertura, só injeta o resumo quando a sessão abre dentro da pasta
de campanhas ou no repositório do plugin logo acima dela. Depois de uma
compactação ou retomada (`source` = compact ou resume), injeta o contrato de
resposta, os números e a decisão pendente (`mesa.json`); fora da pasta de
campanhas, só se a mesa foi gravada nas últimas horas (jogo em andamento).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_campanha as c  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def _dentro(a: Path, b: Path) -> bool:
    try:
        a.resolve().relative_to(b.resolve())
        return True
    except ValueError:
        return False


def modo_hook(stdin_txt: str, env: dict) -> str:
    stdin_txt = stdin_txt.lstrip("\ufeff")
    try:
        dados = json.loads(stdin_txt) if stdin_txt.strip() else {}
    except json.JSONDecodeError:
        return ""
    if not dados.get("cwd"):
        return ""
    cwd = Path(dados["cwd"]).resolve()
    base_txt = env.get("CLAUDE_PLUGIN_OPTION_PASTA_CAMPANHAS", "")
    jogos = c.listar_jogos(base_txt)
    if not jogos:
        return ""
    base = Path(base_txt).resolve()
    # Dentro da pasta de campanhas, ou na pasta logo acima dela quando essa é o
    # repositório do plugin (tem .claude-plugin/plugin.json). Outras pastas
    # (ex.: C:\dev, mesmo sendo mãe da pasta de campanhas) não recebem o resumo.
    eh_repo_plugin = cwd == base.parent and (cwd / ".claude-plugin" / "plugin.json").is_file()
    na_pasta = _dentro(cwd, base) or eh_repo_plugin
    # Sessão aberta dentro da pasta de um jogo: esse jogo, qualquer que seja a configuração.
    proprio = next((j for j in jogos if _dentro(cwd, j)), None)
    pasta = proprio or c.pasta_ativa(base_txt, env.get("CLAUDE_PLUGIN_OPTION_CAMPANHA_ATIVA", ""))

    if dados.get("source") in ("compact", "resume"):
        # Sem campanha fixada: o jogo em andamento é o da mesa gravada por último.
        if pasta is None:
            recentes = [j for j in jogos if c.mesa_recente(c.ler_mesa(j))]
            pasta = max(recentes, key=lambda j: c.ler_mesa(j)["atualizado_em"]) if recentes else None
        if pasta is None or not (na_pasta or c.mesa_recente(c.ler_mesa(pasta))):
            return ""
        texto = c.retomada(pasta, _contrato_curto(), dados["source"])
    elif not na_pasta:
        return ""
    elif pasta is not None:
        texto = c.resumo(pasta)
        mesa = c.ler_mesa(pasta)
        if mesa and "Decisão pendente:" not in texto:
            texto += "\n" + "\n".join(c.linhas_mesa(mesa))
    elif len(jogos) > 1:
        texto = c.resumo_varios(jogos)
    else:
        return ""
    return json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                              "additionalContext": texto}},
                      ensure_ascii=False)


def _contrato_curto() -> str:
    arq = Path(__file__).resolve().parents[1] / "skills" / "narrar" / "contrato_curto.md"
    try:
        return arq.read_text(encoding="utf-8")
    except OSError:
        return ""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="campanha")
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("auditar"); a.add_argument("pasta"); a.add_argument("--json", action="store_true")
    a = s.add_parser("validar"); a.add_argument("pasta")
    a = s.add_parser("resumo"); a.add_argument("pasta")
    s.add_parser("hook")
    args = p.parse_args(argv)

    if args.cmd == "hook":
        try:
            out = modo_hook(sys.stdin.read(), dict(os.environ))
        except Exception:  # o hook nunca deve travar o início da sessão
            out = ""
        if out:
            print(out)
        return 0

    pasta = Path(args.pasta)
    if not pasta.is_dir():
        print(f"Erro: pasta não encontrada: {pasta}")
        return 2
    if args.cmd == "auditar":
        achados = c.auditar(pasta)
        if args.json:
            print(json.dumps(c.achados_como_dict(achados), ensure_ascii=False, indent=2))
        else:
            print(c.formatar_achados(achados))
        return 1 if any(a.nivel == "erro" for a in achados) else 0
    if args.cmd == "validar":
        _, erros = c.ler_estado(pasta)
        print("estado.json ok" if not erros else "\n".join(erros))
        return 0 if not erros else 1
    if args.cmd == "resumo":
        print(c.resumo(pasta))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
