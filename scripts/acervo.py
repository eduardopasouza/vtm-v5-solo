#!/usr/bin/env python3
"""CLI do índice do acervo (regras em vtm_acervo.py).

  acervo.py indexar [--raiz PASTA] [--ocr] [--so TRECHO_DO_NOME]
  acervo.py buscar "Blood Surge" [--linha VtM] [--edicao core|v5|classica] [--idioma en|pt] [--limite 8] [--json]
  acervo.py status

A raiz vem de --raiz ou da variável VTM_PASTA_ACERVO (o userConfig
`pasta_acervo` do plugin). O índice fica em %LOCALAPPDATA%/vtm-v5/acervo.sqlite
(ou VTM_INDICE).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vtm_acervo as a  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="acervo")
    p.add_argument("--indice", help="caminho do SQLite (padrão: %%LOCALAPPDATA%%/vtm-v5/acervo.sqlite)")
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("indexar")
    x.add_argument("--raiz", default=os.environ.get("VTM_PASTA_ACERVO"))
    x.add_argument("--ocr", action="store_true", help="OCR nas páginas sem texto (exige Tesseract)")
    x.add_argument("--so", help="só PDFs cujo nome contém este trecho")
    x = s.add_parser("buscar")
    x.add_argument("consulta")
    x.add_argument("--linha"); x.add_argument("--edicao"); x.add_argument("--idioma")
    x.add_argument("--limite", type=int, default=8); x.add_argument("--json", action="store_true")
    s.add_parser("status")
    args = p.parse_args(argv)

    con = a.conectar(args.indice)
    if args.cmd == "indexar":
        if not args.raiz or not Path(args.raiz).is_dir():
            print("Erro: informe --raiz ou VTM_PASTA_ACERVO com a pasta do acervo")
            return 2
        st = a.indexar(args.raiz, con, ocr=args.ocr, so=args.so)
        print(json.dumps(st, ensure_ascii=False, indent=1))
        return 0 if not st["erros"] else 1
    if args.cmd == "buscar":
        res = a.buscar(con, args.consulta, args.linha, args.edicao, args.idioma, args.limite)
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        elif not res:
            print("Nada encontrado no acervo indexado.")
        else:
            for r in res:
                print(f"- {r['citacao']} [{r['linha']}/{r['edicao']}/{r['idioma']}]\n    {r['trecho']}")
        return 0
    if args.cmd == "status":
        print(json.dumps(a.status(con), ensure_ascii=False, indent=1))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
