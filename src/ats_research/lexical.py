"""TF-IDF with cosine similarity, in plain Python.

This is the layer almost every ATS and every "match rate" product starts from. The
sources that document it in real systems are catalogued in `.work/lanes/scoring.md`
(arXiv 2503.17438 survey, sbert.net docs, IJCOPE implementation paper); `docs/` does not
exist yet, so this line points at the primary artifact rather than a doc that was never
written (AGENT_CONTRACT C2 -- no dead references).

IDF is computed over the corpus you hand it. Two-document comparison is a degenerate
case: every term present in both gets idf = ln(3/3)+1 = 1 and every term in one gets the
same larger weight, so the ranking carries no market information. A background corpus is
what makes IDF mean anything. There is no `idf_from_background` helper and no corpus
shipped in this repo yet -- supplying one is increment A2 (docs/00-audit.md C-9).
"""
from __future__ import annotations

import math
from collections import Counter

from .textutil import content_words


def default_idf(n_docs: int, df: int) -> float:
    """Standard smoothed inverse document frequency."""
    return math.log((1 + n_docs) / (1 + df)) + 1.0


class Tfidf:
    """Vectorizer + comparison over a background corpus."""

    def __init__(self, background: list[str] | None = None, stop: set[str] | None = None,
                 sublinear_tf: bool = True):
        self.stop = stop or set()
        self.sublinear_tf = sublinear_tf
        self.df: Counter = Counter()
        self.n_docs = 0
        if background:
            self.fit(background)

    def fit(self, documents: list[str]) -> "Tfidf":
        self.df = Counter()
        for doc in documents:
            seen = set(content_words(doc, self.stop))
            for t in seen:
                self.df[t] += 1
        self.n_docs = len(documents)
        return self

    def idf(self, term: str) -> float:
        if self.n_docs == 0:
            return 1.0
        return default_idf(self.n_docs, self.df.get(term, 0))

    def vector(self, text: str) -> dict[str, float]:
        counts = Counter(content_words(text, self.stop))
        vec: dict[str, float] = {}
        for term, tf in counts.items():
            w = (math.log(tf) + 1.0) if self.sublinear_tf else float(tf)
            vec[term] = w * self.idf(term)
        return _l2(vec)

    def cosine(self, a: dict[str, float], b: dict[str, float]) -> float:
        return _cosine(a, b)

    def compare(self, text_a: str, text_b: str, top: int = 20) -> dict:
        """Cosine similarity plus the term-level evidence that produced it."""
        va, vb = self.vector(text_a), self.vector(text_b)
        shared = set(va) & set(vb)
        contrib = sorted(((t, va[t] * vb[t]) for t in shared), key=lambda kv: -kv[1])
        only_b = sorted(set(vb) - set(va), key=lambda t: -self.idf(t) * vb[t])
        return {
            "cosine": _cosine(va, vb),
            "shared_terms": [t for t, _ in contrib[:top]],
            "contributions": {t: round(c, 4) for t, c in contrib[:top]},
            "missing_from_a": only_b[:top],
            "terms_a": len(va),
            "terms_b": len(vb),
        }


def _l2(vec: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vec.values()))
    if norm == 0:
        return {}
    return {k: v / norm for k, v in vec.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) > len(b):
        a, b = b, a
    return max(0.0, min(1.0, sum(w * b[t] for t, w in a.items() if t in b)))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def overlap_coefficient(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))
