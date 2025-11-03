from __future__ import annotations
from typing import List, Dict, Any, Tuple

from psycopg2.extras import Json
from pgvector.psycopg2 import register_vector
import numpy as np



class VectorStore:
    def __init__(self, conn):
        self.conn = conn
        register_vector(self.conn)


    def upsert_document(self, content: str, metadata: Dict[str, Any], embedding: List[float]) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (content, metadata, embedding)
                VALUES (%s, %s, %s::vector)
                RETURNING id
                """,
                (content, Json(metadata), np.array(embedding)),
            )
            _id = cur.fetchone()[0]
            return _id

    def search(self, query_embedding: List[float], k: int = 3) -> List[Tuple[int, float, str, Dict[str, Any]]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id,
                       1 - (embedding <=> %s::vector) AS score,
                       content,
                       metadata
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (np.array(query_embedding), np.array(query_embedding), k),
            )
            rows = cur.fetchall()
            return [(r[0], float(r[1]), r[2], r[3]) for r in rows]
