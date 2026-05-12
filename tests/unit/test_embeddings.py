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

# Test DocumentLoader with factory
from src.data.document_loader import DocumentLoader
from src.data.indexers import IndexersFactory
from src.vectorstore.storage import MockVectorStore
from src.vectorstore.embeddings import OpenAIEmbeddingClient, MockEmbeddingClient

print("\n📊 Testing DocumentLoader initialization...\n")

vector_store = MockVectorStore()

# Determine which embedding client to use
print("🔄 Creating DocumentLoader with factory...")
if openai_key:
    print("   ✅ Using: REAL OpenAI embeddings")
    embedding_client = OpenAIEmbeddingClient()
    embedding_type = "OpenAI"
else:
    print("   ❌ Using: MOCK embeddings")
    embedding_client = MockEmbeddingClient()
    embedding_type = "Mock"

indexers_factory = IndexersFactory(vector_store=vector_store, embedding_client=embedding_client)
doc_loader = DocumentLoader(indexers_factory=indexers_factory)

print(f"   Embedding client type: {type(embedding_client).__name__}")

print("\n" + "=" * 80)
print("✅ Test complete\n")
