import logging
from src.data.indexers.base import DocumentIndexer
from src.data.parsers import CSVParser
from src.vectorstore.storage import VectorStore
from src.vectorstore.embeddings import EmbeddingClient

logger = logging.getLogger(__name__)


class CSVIndexer(DocumentIndexer):
    """Index CSV bid tabulation data into vector store."""

    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        """
        Initialize CSV indexer.

        Args:
            vector_store: VectorStore instance for storing embeddings
            embedding_client: EmbeddingClient instance for generating embeddings
        """
        self.vector_store = vector_store
        self.embedding_client = embedding_client

    def load_and_index(self, csv_path: str) -> int:
        """Load CSV bid data and index into vector store."""
        logger.info(f"Loading CSV: {csv_path}")

        try:
            projects = CSVParser().parse(csv_path)

            # Collect all documents before embedding (batch processing)
            documents = []
            for project in projects:
                for item in project.items:
                    doc_id = f"csv_{project.proj_id}_{item.item_no}"
                    text = f"{item.item_desc} - {item.unit} @ ${item.unit_price:.2f}"

                    documents.append({
                        "doc_id": doc_id,
                        "text": text,
                        "metadata": {
                            "source": "csv",
                            "proj_id": project.proj_id,
                            "item_no": item.item_no,
                            "item_desc": item.item_desc,
                            "unit_price": item.unit_price,
                        }
                    })

            if not documents:
                logger.info("No documents to index from CSV")
                return 0

            # Batch embed all texts at once (1000 texts per API call)
            texts = [doc["text"] for doc in documents]
            logger.info(f"Embedding {len(texts)} items (batch size: 1000)...")
            embeddings = self.embedding_client.batch_embed(texts, batch_size=1000)

            # Insert all documents into vector store
            count = 0
            for doc, embedding in zip(documents, embeddings):
                try:
                    self.vector_store.insert(
                        doc_id=doc["doc_id"],
                        text=doc["text"],
                        embedding=embedding,
                        metadata=doc["metadata"]
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to index item {doc['doc_id']}: {e}")

            logger.info(f"Indexed {count}/{len(documents)} bid items from CSV")
            return count

        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return 0
