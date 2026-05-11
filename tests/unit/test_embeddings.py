#!/usr/bin/env python3
"""Test which embeddings are being used"""

import os
from dotenv import load_dotenv

load_dotenv(".env")

openai_key = os.getenv("OPENAI_API_KEY")
print("=" * 80)
print("🔍 EMBEDDINGS CHECK")
print("=" * 80)

if openai_key:
    print("\n✅ OPENAI_API_KEY is configured")
    print(f"   Key starts with: {openai_key[:20]}...")
    print("\n🎯 System will use: REAL OpenAI embeddings")
    print("   Model: text-embedding-3-small")
    print("   Cost: ~$0.02 per 1M tokens")
else:
    print("\n❌ OPENAI_API_KEY not configured")
    print("\n🎯 System will use: MOCK embeddings (local)")
    print("   Cost: FREE (no API calls)")

print("\n" + "=" * 80)

# Test DocumentLoader decision
from src.data.document_loader import DocumentLoader
from src.vectorstore.storage import SQLiteVectorStore
import tempfile

print("\n📊 Testing DocumentLoader initialization...\n")

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
    db_path = f.name

vector_store = SQLiteVectorStore(db_path=db_path)

# With real key
print("🔄 Creating DocumentLoader with API key available...")
use_mock = not bool(openai_key)
doc_loader = DocumentLoader(vector_store=vector_store, use_mock_embeddings=use_mock)

if use_mock:
    print("   ❌ Using: MOCK embeddings")
    print("   Embedding client type:", type(doc_loader.embedding_client).__name__)
else:
    print("   ✅ Using: REAL OpenAI embeddings")
    print("   Embedding client type:", type(doc_loader.embedding_client).__name__)

print("\n" + "=" * 80)
print("✅ Test complete\n")

# Cleanup
import shutil
os.remove(db_path)
