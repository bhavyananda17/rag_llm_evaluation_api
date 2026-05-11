#!/usr/bin/env python3
"""Simple RAG test."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.vector_db import VectorStore

print("Loading vector store...")
vs = VectorStore()

index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
vs.load_index(index_path)
print(f"✓ Index loaded")

# Test retrieval
query = "What is the difference between self-attention and cross-attention?"
print(f"\nQuery: {query}\n")

results = vs.retrieve(query, k=3)

print(f"Retrieved {len(results)} results:\n")
for result in results:
    print(f"[{result['rank']}] {result['source_file']}")
    print(f"    Score: {result['similarity_score']:.4f}")
    print(f"    Text: {result['chunk_text'][:100]}...\n")

print("✓ Test complete")
