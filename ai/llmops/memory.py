import os
import logging
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)

class AgentLongTermMemory:
    """Long-term memory for Mock Interview Agents using Qdrant Vector Database."""

    def __init__(self, collection_name: str = "candidate_profiles", vector_size: int = 1536):
        self.collection_name = collection_name
        self.vector_size = vector_size
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        try:
            self.client = QdrantClient(url=qdrant_url)
            self._ensure_collection()
            self.enabled = True
            logger.info("AgentLongTermMemory enabled and connected to Qdrant.")
        except Exception as e:
            self.enabled = False
            logger.warning(f"AgentLongTermMemory disabled (Qdrant connection failed): {e}")

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def save_memory(self, point_id: str, vector: list[float], payload: dict[str, Any]):
        """Save candidate profile or interaction memory to Vector DB."""
        if not self.enabled:
            return
            
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Qdrant save error: {e}")

    def search_memory(self, query_vector: list[float], limit: int = 3) -> list[dict[str, Any]]:
        """Retrieve relevant past interactions or profile data."""
        if not self.enabled:
            return []
            
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [hit.payload for hit in results]
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []
