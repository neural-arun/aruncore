import os
import json
from typing import Optional, Dict, Any
from backend.app.services.rag_service import RAGService


class ActiveLearningService:
    def __init__(self, tenant_id: str = "arun"):
        self.tenant_id = tenant_id
        self.rag_service = RAGService(tenant_id=tenant_id)

    def process_incoming_owner_reply(self, session_id: str, question: str, answer: str) -> bool:
        """Processes owner's Telegram/WhatsApp answer, ingests into active_learning.json & ChromaDB."""
        print(f"[ACTIVE_LEARNING] Processing owner answer for session '{session_id}': Q: '{question}' ➔ A: '{answer}'")
        
        # Ingest into vector store
        success = self.rag_service.add_knowledge_entry(question, answer)
        return success
