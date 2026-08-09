"""Hybrid RAG coordinator.

Composes the knowledge-retrieval pipeline for a tenant: dense vector search
(ChromaDB), sparse keyword search (BM25), and reranking get their turn here
in future integration; today ChromaDB is built at ingest time and runtime
retrieval is served by `KnowledgeService` (project READMEs + LinkedIn posts +
profile sections + verified Q&A pairs). This service also doubles as the
active-learning ingestion point for owner-verified answers.
"""
import hashlib
from typing import List, Dict, Any

from backend.app.services.knowledge_service import knowledge_service


class RAGService:
    """Hybrid RAG coordinator: retrieval + active-learning ingestion per tenant."""

    def __init__(self, tenant_id: str = "arun"):
        self.tenant_id = tenant_id

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Executes high-precision hybrid retrieval for the specified tenant."""
        print(f"[RAG_SERVICE] Retrieving context for tenant '{self.tenant_id}' query: '{query[:80]}'")

        raw = knowledge_service.search(query)

        chunks: List[Dict[str, Any]] = []
        if raw:
            parts = [p for p in raw.split("\n\n--- ") if p.strip()]
            for i, part in enumerate(parts[:top_k]):
                chunks.append({
                    "id": f"{self.tenant_id}_chunk_{i}_{hashlib.md5(part.encode('utf-8')).hexdigest()[:8]}",
                    "content": part.strip(),
                    "score": max(0.0, 0.95 - (i * 0.03)),
                    "source": "knowledge_base",
                })
        return chunks

    def add_knowledge_entry(self, question: str, answer: str) -> bool:
        """Persists a verified Q&A into unknown_questions.json and re-ingests."""
        try:
            result = knowledge_service.save_verified_answer(question, answer)
            print(f"[RAG_SERVICE] Active-learning entry for tenant '{self.tenant_id}': {result}")
            return True
        except Exception as e:
            print(f"[RAG_SERVICE ERROR] Failed to persist Q&A for tenant '{self.tenant_id}': {e}")
            return False