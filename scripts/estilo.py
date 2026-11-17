#!/usr/bin/env python3
"""CLI de estilo e conduta do narrador (regras em vtm_estilo.py).

  estilo.py checar <arquivo.md> [...]          português de Portugal e latim sem tradução (logs de sessão)
  estilo.py mensagem <arquivo> [--seletor "A|B|Outra ação (descreva)"]
                                               confere uma mensagem de jogo contra o contrato de resposta

Sai com código 1 se achar algum problema.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_estilo as e  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="estilo")
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("checar"); a.add_argument("arquivos", nargs="+")
    a = s.add_parser("mensagem"); a.add_argument("arquivo"); a.add_argument("--seletor")
    args = p.parse_args(argv)
    total = 0
    for nome in (args.arquivos if args.cmd == "checar" else [args.arquivo]):
        arq = Path(nome)
        if not arq.is_file():
            print(f"Erro: arquivo não encontrado: {arq}")
            return 2
        texto = arq.read_text(encoding="utf-8")
        if args.cmd == "checar":
            problemas = e.checar_log(texto)
        else:
            rotulos = [x.strip() for x in args.seletor.split("|")] if args.seletor else None
            problemas = e.checar_mensagem(texto, rotulos)
        for pr in problemas:
            print(f"{arq.name}:{pr.linha} [{pr.codigo}] {pr.trecho} — {pr.mensagem}")
        total += len(problemas)
    print(f"{total} problema(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
