"""
Document loader that indexes both CSV and PDF content into vector store.
Handles:
- CSV bid tabulation data (structured)
- PDF plan sets (unstructured text, OCR)
"""

import logging
from pathlib import Path
from typing import Optional
from src.data.loaders import DataLoader
from src.data.pdf_parser import PDFParser
from src.vectorstore.storage import SQLiteVectorStore
from src.vectorstore.embeddings import EmbeddingClient, MockEmbeddingClient

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and index both CSV and PDF documents into vector store."""
    
    def __init__(self, vector_store: SQLiteVectorStore, use_mock_embeddings: bool = False):
        self.vector_store = vector_store
        self.use_mock_embeddings = use_mock_embeddings
        
        # Initialize embedding client
        try:
            self.embedding_client = EmbeddingClient() if not use_mock_embeddings else MockEmbeddingClient()
        except Exception as e:
            logger.warning(f"Using MockEmbeddingClient: {e}")
            self.embedding_client = MockEmbeddingClient()
    
    def load_and_index_csv(self, csv_path: str) -> int:
        """Load CSV bid data and index into vector store."""
        logger.info(f"Loading CSV: {csv_path}")
        
        try:
            projects = DataLoader.load(csv_path)
            count = 0
            
            for project in projects:
                for item in project.items:
                    # Create searchable document from bid item
                    doc_id = f"csv_{project.proj_id}_{item.item_no}"
                    text = f"{item.item_desc} - {item.unit} @ ${item.unit_price:.2f}"
                    
                    try:
                        embedding = self.embedding_client.embed_text(text)
                        self.vector_store.insert(
                            doc_id=doc_id,
                            text=text,
                            embedding=embedding,
                            metadata={
                                "source": "csv",
                                "proj_id": project.proj_id,
                                "item_no": item.item_no,
                                "item_desc": item.item_desc,
                                "unit_price": item.unit_price,
                            }
                        )
                        count += 1
                    except Exception as e:
                        logger.debug(f"Failed to index item {doc_id}: {e}")
            
            logger.info(f"Indexed {count} bid items from CSV")
            return count
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return 0
    
    def load_and_index_pdf(self, pdf_path: str, chunk_size: int = 500) -> int:
        """Load PDF and index text chunks into vector store."""
        logger.info(f"Loading PDF: {pdf_path}")
        
        try:
            parser = PDFParser(verbose=True)
            text = parser._extract_text(pdf_path)
            
            if not text or not text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return 0
            
            # Split into chunks
            pdf_filename = Path(pdf_path).stem
            chunks = self._chunk_text(text, chunk_size=chunk_size)
            count = 0
            
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                doc_id = f"pdf_{pdf_filename}_chunk_{i}"
                
                try:
                    embedding = self.embedding_client.embed_text(chunk)
                    self.vector_store.insert(
                        doc_id=doc_id,
                        text=chunk,
                        embedding=embedding,
                        metadata={
                            "source": "pdf",
                            "pdf_file": pdf_filename,
                            "chunk_index": i,
                        }
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to index chunk {doc_id}: {e}")
            
            logger.info(f"Indexed {count} chunks from PDF {pdf_filename}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            return 0
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks for better semantic search."""
        chunks = []
        sentences = text.split(". ")
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def load_all_documents(self, data_dir: str = "data") -> dict:
        """Load all CSV and PDF files from a directory."""
        data_path = Path(data_dir)
        results = {"csv": 0, "pdf": 0, "errors": []}
        
        # Load all CSVs
        for csv_file in data_path.glob("*.csv"):
            try:
                count = self.load_and_index_csv(str(csv_file))
                results["csv"] += count
            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
                results["errors"].append(str(csv_file))
        
        # Load all PDFs
        for pdf_file in data_path.glob("*.pdf"):
            try:
                count = self.load_and_index_pdf(str(pdf_file))
                results["pdf"] += count
            except Exception as e:
                logger.error(f"Error loading {pdf_file}: {e}")
                results["errors"].append(str(pdf_file))
        
        return results
