#!/usr/bin/env python3
"""Quick test - just index CSV and search"""

import sys
from pathlib import Path

# Add project root to path so imports work from scripts/
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(".env")

import tempfile
from src.data.loaders import DataLoader
from src.data.document_loader import DocumentLoader
from src.vectorstore.storage import SQLiteVectorStore
from src.vectorstore.retrieval import HybridRetriever
from src.vectorstore.embeddings import MockEmbeddingClient

print("=" * 80)
print("⚡ QUICK TEST - CSV Only (PDFs skip for speed)")
print("=" * 80)

# Load CSV only
with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
    db_path = f.name

vector_store = SQLiteVectorStore(db_path=db_path)
doc_loader = DocumentLoader(vector_store=vector_store, use_mock_embeddings=True)

print("\n📊 Indexing CSV...")
csv_count = doc_loader.load_and_index_csv("data/sample_bid_tabulation.csv")
print(f"✅ Indexed {csv_count} bid items")

print("\n🔍 Testing search...")
embedding_client = MockEmbeddingClient()
retriever = HybridRetriever(
    vector_store=vector_store,
    embedding_client=embedding_client,
    semantic_weight=0.7,
    keyword_weight=0.3
)

# Test search
results = retriever.search(query="MOBILIZATION pavement", limit=5)
print(f"\nSearch results for 'MOBILIZATION pavement':")
for i, (doc_id, score, metadata) in enumerate(results, 1):
    doc = vector_store.get_by_id(doc_id)
    if doc:
        print(f"{i}. [{metadata.get('source')}] (score: {score:.2f})")
        print(f"   {doc.get('text', '')[:100]}...")

import os
os.remove(db_path)
print("\n✅ Test complete")
