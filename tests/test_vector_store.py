#!/usr/bin/env python3
"""Debug script for vector store testing."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.vector_db import VectorStore

print("Starting vector store test...")

try:
    print("Step 1: Initializing Vector Store")
    vs = VectorStore(model_name='all-MiniLM-L6-v2')
    print("✓ Vector Store initialized")
    
    print("\nStep 2: Adding documents from data/raw")
    input_dir = os.path.join(Config.BASE_DIR, "data/raw")
    print(f"Input directory: {input_dir}")
    print(f"Exists: {os.path.exists(input_dir)}")
    
    # List files
    txt_files = list(Path(input_dir).glob("*.txt"))
    print(f"Found {len(txt_files)} txt files")
    for f in txt_files:
        print(f"  - {f.name}")
    
    print("\nBuilding index...")
    stats = vs.add_documents(input_dir, chunk_size=500, chunk_overlap=100)
    print(f"✓ Index built with {stats['total_chunks']} chunks from {stats['total_files']} files")
    
    print("\nStep 3: Testing retrieval")
    query = "attention mechanism"
    results = vs.retrieve(query, k=3)
    print(f"✓ Retrieved {len(results)} results for query: '{query}'")
    
    for result in results:
        print(f"  Rank {result['rank']}: {result['source_file']} (score: {result['similarity_score']:.4f})")
    
    print("\nStep 4: Saving index")
    output_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
    vs.save_index(output_path)
    print(f"✓ Index saved to {output_path}")
    
    print("\n✓ All tests passed!")

except Exception as e:
    import traceback
    print(f"✗ Error: {str(e)}")
    traceback.print_exc()
