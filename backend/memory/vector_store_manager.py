import chromadb
from chromadb.config import Settings
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages the persistent ChromaDB vector store for the CNS.
    """

    def __init__(self, persistence_path: str = "./data/chroma_db"):
        self.persistence_path = persistence_path

        # Ensure the data directory exists
        os.makedirs(persistence_path, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(path=persistence_path)
            logger.info(f"Connected to ChromaDB at {persistence_path}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    def get_collection(self, name: str):
        """Gets or creates a collection by name."""
        return self.client.get_or_create_collection(name=name)

    def add_memory(
        self,
        collection_name: str,
        document: str,
        metadata: Dict[str, Any],
        id: str = None,
    ):
        """
        Adds a memory (document) to the specified collection.
        If id is not provided, one will be generated based on timestamp.
        """
        collection = self.get_collection(collection_name)

        if id is None:
            id = f"{collection_name}_{datetime.now().timestamp()}"

        try:
            collection.add(documents=[document], metadatas=[metadata], ids=[id])
            logger.info(f"Added memory to '{collection_name}' with ID: {id}")
            return id
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return None

    def search_memory(
        self, collection_name: str, query: str, n_results: int = 3
    ) -> Dict[str, Any]:
        """
        Semantically searches the memory for the given query.
        """
        collection = self.get_collection(collection_name)

        try:
            results = collection.query(query_texts=[query], n_results=n_results)
            return results
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return {}

    def delete_memory(self, collection_name: str, id: str):
        """
        Deletes a specific memory by ID.
        """
        collection = self.get_collection(collection_name)
        try:
            collection.delete(ids=[id])
            logger.info(f"Deleted memory ID: {id} from '{collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")


if __name__ == "__main__":
    # Test execution
    vs = VectorStoreManager()

    # Add a sample memory
    test_id = vs.add_memory(
        collection_name="test_memories",
        document="The user prefers using 'pathlib' over 'os.path' for file operations.",
        metadata={"category": "preference", "timestamp": str(datetime.now())},
    )

    # Search for it
    logger.info("Searching for 'file path preference'...")
    results = vs.search_memory(
        "test_memories", "What does the user prefer for file paths?"
    )
    logger.info(f"Results: {results}")

    # Cleanup
    if test_id:
        vs.delete_memory("test_memories", test_id)
