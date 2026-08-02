import logging
import uuid
from typing import Any

# Setup logger
logger = logging.getLogger(__name__)

# Try to import chromadb. If not installed/failing, we will fallback to a simple mock.
try:
    import chromadb
    from chromadb.config import Settings

    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    logger.warning("chromadb not installed, falling back to mock knowledge base")


class IncidentKnowledgeBase:
    """
    Manages indexing and retrieval of resolved incidents to assist in future AI RCA.
    Uses ChromaDB for vector-based semantic search.
    """

    def __init__(self):
        self.mock_db: list[dict[str, Any]] = []
        global HAS_CHROMA
        if HAS_CHROMA:
            try:
                # In-memory ephemeral DB for demo purposes
                self.client = chromadb.Client(Settings(is_tenant_headless=True))
                self.collection = self.client.get_or_create_collection(name="resolved_incidents")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                HAS_CHROMA = False

    def index_resolved_incident(self, incident: dict[str, Any], analysis: dict[str, Any]) -> bool:
        """
        Indexes a resolved incident into the vector database.
        """
        doc_id = f"inc_{incident.get('incident_number', uuid.uuid4().hex[:8])}"

        # Build the document text for embedding
        symptoms = incident.get("description", "")
        root_cause = analysis.get("title", "")
        resolution = analysis.get("rationale", "")

        document = f"Symptoms: {symptoms}\nRoot Cause: {root_cause}\nResolution: {resolution}"

        metadata = {
            "incident_number": incident.get("incident_number", ""),
            "service": incident.get("service", ""),
            "severity": incident.get("severity", ""),
            "confidence": analysis.get("confidence", 0),
            "engineer": incident.get("owner", "System"),
        }

        if HAS_CHROMA:
            try:
                self.collection.add(documents=[document], metadatas=[metadata], ids=[doc_id])
                logger.info(f"Indexed incident {doc_id} into ChromaDB")
                return True
            except Exception as e:
                logger.error(f"Error indexing to ChromaDB: {e}")
                return False
        else:
            self.mock_db.append({"id": doc_id, "document": document, "metadata": metadata})
            logger.info(f"Indexed incident {doc_id} into mock KB")
            return True

    def search_similar_incidents(self, query: str, n_results: int = 3) -> list[dict[str, Any]]:
        """
        Searches the KB for similar past incidents.
        """
        if HAS_CHROMA:
            try:
                results = self.collection.query(query_texts=[query], n_results=n_results)

                # Format results
                similar = []
                if results["documents"] and len(results["documents"]) > 0:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if results["metadatas"] else []

                    for i in range(len(docs)):
                        similar.append({"document": docs[i], "metadata": metas[i] if i < len(metas) else {}})
                return similar
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")
                return []
        else:
            # Mock return based on basic string matching
            logger.info("Querying mock KB")
            results = []
            for item in self.mock_db:
                if any(word.lower() in item["document"].lower() for word in query.split()):
                    results.append(item)
            return results[:n_results]


# Singleton instance
kb = IncidentKnowledgeBase()
