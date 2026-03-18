import os
from pinecone import Pinecone, ServerlessSpec
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class PineconeManager:
    """
    Modular client to handle Vector Database operations via Pinecone API.
    Used for AI memory and Semantic Search.
    Adheres to Rule 5 (Modular Integrity) and Rule 12 (Tenant Isolation).
    """

    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "g777-memory")
        self.pc = None
        self.index = None
        
        if self.api_key:
            try:
                self.pc = Pinecone(api_key=self.api_key)
                self._ensure_index_exists()
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {str(e)}")
        else:
            logger.warning("PINECONE_API_KEY not set. Vector DB operations will be disabled.")

    def _ensure_index_exists(self):
        """Creates the index if it doesn't exist (using free tier serverless logic)"""
        if self.index_name not in [index.name for index in self.pc.list_indexes()]:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=768, # Default dimension for many fast embedding models
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region=self.environment)
            )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def upsert_vectors(self, tenant_id: str, vectors: list):
        """
        Upsert vectors with Rule 12: Tenant Isolation requirement.
        Every vector MUST have metadata containing the tenant_id binding.
        """
        if not self.index:
            return False
            
        # Ensure Tenant Isolation (Rule 12)
        isolated_vectors = []
        for vec in vectors:
            # vec format: {"id": "str", "values": [floats], "metadata": {dict}}
            if "metadata" not in vec:
                vec["metadata"] = {}
            vec["metadata"]["tenant_id"] = tenant_id  # Force binding
            isolated_vectors.append(vec)
            
        try:
            self.index.upsert(vectors=isolated_vectors)
            return True
        except Exception as e:
            logger.error(f"Pinecone Upsert Error: {str(e)}")
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def query_vectors(self, tenant_id: str, query_vector: list, top_k: int = 5):
        """
        Query vectors strictly filtered by Tenant ID.
        """
        if not self.index:
            return {"matches": []}
            
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter={"tenant_id": {"$eq": tenant_id}} # CRITICAL: Rule 12 isolate
            )
            return results
        except Exception as e:
            logger.error(f"Pinecone Query Error: {str(e)}")
            raise e

# Singleton instance
pinecone_manager = PineconeManager()
