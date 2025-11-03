from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class RetrievalResult:
    doc_id: int
    score: float
    content: str

def simple_precision_at_k(results: List[RetrievalResult], relevant_ids: List[int], k: int = 3) -> float:
    got = [r.doc_id for r in results[:k]]
    hits = sum(1 for x in got if x in relevant_ids)
    return hits / float(k)
