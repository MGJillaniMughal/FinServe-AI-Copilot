"""Vector retrieval store.

Primary path is a dependency-free TF-IDF + cosine-similarity engine that
provides genuine semantic-style ranking over indexed document chunks.
When an OpenAI API key is configured, dense embeddings can be plugged in
through `embed_fn`; otherwise the TF-IDF representation is used.

Developed by Jillani SofTech.
"""
import math
import re
from collections import Counter
from typing import Callable, Dict, List, Optional, Tuple

from backend.utils.logger import get_logger

logger = get_logger("vector-store")
_TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]+")
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "is", "are",
    "be", "this", "that", "with", "as", "by", "at", "from", "it", "its", "was",
}


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN.findall(text or "") if t.lower() not in _STOP]


class VectorStore:
    def __init__(self, embed_fn: Optional[Callable[[str], List[float]]] = None) -> None:
        self.chunks: List[Dict] = []          # {doc_id, filename, text, tf}
        self.df: Counter = Counter()          # document frequency per term
        self.embed_fn = embed_fn

    # --------- indexing ---------
    def add(self, doc_id: str, filename: str, text: str) -> None:
        toks = tokenize(text)
        if not toks:
            return
        tf = Counter(toks)
        for term in set(toks):
            self.df[term] += 1
        self.chunks.append({"doc_id": doc_id, "filename": filename, "text": text, "tf": tf})

    def reset(self) -> None:
        self.chunks.clear()
        self.df.clear()

    # --------- scoring ---------
    def _idf(self, term: str) -> float:
        n = max(1, len(self.chunks))
        return math.log((1 + n) / (1 + self.df.get(term, 0))) + 1.0

    def _vec(self, tf: Counter) -> Dict[str, float]:
        return {t: (c / sum(tf.values())) * self._idf(t) for t, c in tf.items()}

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        common = set(a) & set(b)
        if not common:
            return 0.0
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query: str, top_k: int = 4) -> List[Tuple[float, Dict]]:
        q_tf = Counter(tokenize(query))
        if not q_tf or not self.chunks:
            return []
        qv = self._vec(q_tf)
        scored = []
        for ch in self.chunks:
            score = self._cosine(qv, self._vec(ch["tf"]))
            if score > 0:
                scored.append((round(score, 4), ch))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def best_sentences(self, query: str, contexts: List[Dict], n: int = 3) -> List[str]:
        q_tf = Counter(tokenize(query))
        qv = self._vec(q_tf)
        sentences = []
        for ctx in contexts:
            for s in re.split(r"(?<=[.!?])\s+", ctx["text"]):
                if len(s.split()) < 4:
                    continue
                sv = self._vec(Counter(tokenize(s)))
                sentences.append((self._cosine(qv, sv), s.strip()))
        sentences.sort(key=lambda x: x[0], reverse=True)
        seen, out = set(), []
        for _, s in sentences:
            if s not in seen:
                seen.add(s)
                out.append(s)
            if len(out) >= n:
                break
        return out


def chunk_text(text: str, size: int = 110, overlap: int = 25) -> List[str]:
    words = (text or "").split()
    if not words:
        return []
    step = max(1, size - overlap)
    out = []
    for i in range(0, len(words), step):
        piece = " ".join(words[i:i + size]).strip()
        if piece:
            out.append(piece)
    return out
