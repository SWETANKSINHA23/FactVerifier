"""
In-memory vector store — drop-in replacement for the Endee HTTP client.
Uses numpy cosine similarity so no external service is required.
Data persists for the lifetime of the Render process (lost on restart).
"""
import numpy as np
import json
import uuid
from typing import List, Dict, Any


# ── Module-level singleton so all agents share the same store ──────────────
class _VectorStore:
    def __init__(self):
        self.vectors: List[np.ndarray] = []
        self.payloads: List[Dict[str, Any]] = []

    def insert(self, vector: List[float], payload: Dict[str, Any]):
        self.vectors.append(np.array(vector, dtype=np.float32))
        self.payloads.append(payload)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.vectors:
            return []

        q = np.array(query_vector, dtype=np.float32)
        q_norm = q / (np.linalg.norm(q) + 1e-9)

        scores = [
            float(np.dot(q_norm, v / (np.linalg.norm(v) + 1e-9)))
            for v in self.vectors
        ]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [{"score": scores[i], "payload": self.payloads[i]} for i in top_indices]

    def count(self) -> int:
        return len(self.vectors)


_STORE = _VectorStore()  # shared across all agent instances


# ── Public client — same interface as the old Endee HTTP client ────────────
class EndeeClient:
    """Wraps the in-memory store with the same API the agents already use."""

    def __init__(self):
        self._store = _STORE

    # kept for compatibility — nothing to create in memory
    def ensure_index_exists(self):
        pass

    def insert(self, vector: List[float], payload: Dict[str, Any]):
        self._store.insert(vector, payload)
        return {"status": "success"}

    def search(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        return self._store.search(vector, top_k)

    def count(self) -> int:
        return self._store.count()
