"""Command-line entry point: `ariadne`.

Scope discipline: this CLI exposes only what the package actually does today — text
normalisation, tokenisation, section detection, and a TF-IDF comparison with term-level
evidence. It deliberately has no "score my CV" command, because Ariadne does not yet
produce a score and a CLI flag that pretends otherwise would be a stub (AGENT_CONTRACT
C7.7) and, worse, a user-facing claim (C8).

Exit codes: 0 success, 1 usage/data error, 2 internal error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .lexical import Tfidf
from .textutil import detect_sections, looks_multicolumn, normalize, tokenize

# CLI-level stop list. NOT a claim about what an ATS filters: it exists so that `compare` does not
# answer with "the / is / and". Any real stop list is corpus-dependent and belongs to A1.
_STOP = set("""a an and are as at be been but by for from has have he her his i if in into is it its
of on or our she that the their them then there these they this to was we were what when which who
will with you your""".split())


def _read(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    return p.read_text(encoding="utf-8", errors="replace")


def cmd_inspect(args: argparse.Namespace) -> int:
    raw = _read(args.file)
    text = normalize(raw)
    sections = detect_sections(text)
    out = {
        "file": args.file,
        "characters": len(text),
        "tokens": len(tokenize(text)),
        "sections": {k: len(v.splitlines()) for k, v in sections.items()},
        "heads": sorted(sections),
        "looks_multicolumn": looks_multicolumn(raw),
        "note": (
            "looks_multicolumn is a heuristic over tabs / runs of 4+ spaces in the RAW text; "
            "normalize() collapses both, so this number is only meaningful on raw extraction. "
            "See src/ariadne_ats/textutil.py (P3 in docs/00-audit.md)."
        ),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    a, b = _read(args.a), _read(args.b)
    tf = Tfidf(stop=_STOP)
    result = tf.compare(normalize(a), normalize(b), top=args.top)
    result["note"] = (
        "Document similarity only: cosine over TF-IDF terms. No background corpus is shipped, so "
        "IDF carries no market signal in the two-document case (docs/00-audit.md P7). This is not "
        "a score, an ATS verdict, or a prediction."
    )
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ariadne",
        description="Ariadne — transparent, dependency-free measurement of how a parser reads a CV.",
    )
    p.add_argument("--version", action="version", version=f"ariadne {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    i = sub.add_parser("inspect", help="normalise a document and report tokens and sections")
    i.add_argument("file")
    i.set_defaults(func=cmd_inspect)

    c = sub.add_parser("compare", help="TF-IDF cosine similarity between two documents, with evidence")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--top", type=int, default=20)
    c.set_defaults(func=cmd_compare)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FileNotFoundError as e:
        print(f"ariadne: no such file: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001 - visible failure, never a silent exit 0 (C7.7)
        print(f"ariadne: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
