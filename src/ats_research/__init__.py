"""ats-research (working name; repo/agent name "Ariadne" pending owner decision G1).

Honest public surface. Everything exported here exists and is importable.

Implemented:
    textutil.normalize / tokenize / content_words / sentences / ngrams
    textutil.bullets_of / detect_sections / heading_of / looks_multicolumn
    lexical.Tfidf (fit / vector / cosine / compare), jaccard, overlap_coefficient

Not implemented yet -- deliberately NOT imported, because importing names that do not
exist made `import ats_research` raise (fixed 2026-10-25, see docs/00-audit.md A-7):
    parse_resume, parse_job, Resume, Role, JobDescription      -> A1
    score, ScoreResult, lint, Finding                            -> A2
    propose, Proposal, Fact, check_support, SupportReport        -> A3
    HashingEmbedder, OpenAICompatibleEmbedder                    -> A2/A3

Known limitations of what is here are stated in each module's docstrings, and are
itemised with measurements in docs/00-audit.md section A.
"""
from . import lexical, textutil
from .lexical import Tfidf, jaccard, overlap_coefficient
from .textutil import (
    bullets_of, content_words, detect_sections, heading_of, looks_multicolumn,
    ngrams, normalize, sentences, term_frequencies, tokenize,
)

__all__ = [
    "textutil", "lexical",
    "Tfidf", "jaccard", "overlap_coefficient",
    "normalize", "tokenize", "content_words", "sentences", "ngrams",
    "bullets_of", "detect_sections", "heading_of", "looks_multicolumn",
    "term_frequencies",
]
__version__ = "0.0.1"
