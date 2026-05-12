import logging
from pathlib import Path
from src.data.indexers.base import DocumentIndexer
from src.data.parsers import PDFParser
from src.vectorstore.storage import VectorStore
from src.vectorstore.embeddings import EmbeddingClient

logger = logging.getLogger(__name__)


class PDFIndexer(DocumentIndexer):
    """Index PDF documents into vector store with text chunking."""

    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        """
        Initialize PDF indexer.

        Args:
            vector_store: VectorStore instance for storing embeddings
            embedding_client: EmbeddingClient instance for generating embeddings
        """
        self.vector_store = vector_store
        self.embedding_client = embedding_client

    def load_and_index(self, pdf_path: str, chunk_size: int = 500) -> int:
        """Load PDF and index text chunks into vector store."""
        logger.info(f"Loading PDF: {pdf_path}")

        try:
            parser = PDFParser(verbose=True)
            text = parser._extract_text(pdf_path)

            if not text or not text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return 0

            pdf_filename = Path(pdf_path).stem
            chunks = self._chunk_text(text, chunk_size=chunk_size)

            # Collect all documents before embedding (batch processing)
            documents = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                doc_id = f"pdf_{pdf_filename}_chunk_{i}"
                documents.append({
                    "doc_id": doc_id,
                    "text": chunk,
                    "metadata": {
                        "source": "pdf",
                        "pdf_file": pdf_filename,
                        "chunk_index": i,
                    }
                })

            if not documents:
                logger.info(f"No chunks to index from PDF {pdf_filename}")
                return 0

            # Batch embed all chunks at once (1000 chunks per API call)
            texts = [doc["text"] for doc in documents]
            logger.info(f"Embedding {len(texts)} chunks (batch size: 1000)...")
            embeddings = self.embedding_client.batch_embed(texts, batch_size=1000)

            # Insert all chunks into vector store
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
                    logger.debug(f"Failed to index chunk {doc['doc_id']}: {e}")

            logger.info(f"Indexed {count}/{len(documents)} chunks from PDF {pdf_filename}")
            return count

        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            return 0

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500) -> list[str]:
        """Split text into chunks for better semantic search."""
        chunks = []
        sentences = text.split(". ")

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
