#!/usr/bin/env python3
"""
Build Vector Index for RAG Document Retrieval

This script automatically scans data/raw/, builds a FAISS index from
all transformer and RAG documents, and saves the index for later retrieval.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.vector_db import VectorStore


def main():
    """Main execution function."""
    
    print("\n" + "="*70)
    print("FAISS INDEX BUILDER FOR RAG RETRIEVAL")
    print("="*70)
    
    # Initialize vector store
    print("\nInitializing Vector Store...")
    try:
        vector_store = VectorStore(
            model_name='all-MiniLM-L6-v2',
            use_gpu=False
        )
    except Exception as e:
        print(f"✗ Error initializing Vector Store: {str(e)}")
        print("  Make sure sentence-transformers and faiss-cpu are installed")
        return
    
    # Build index from raw documents
    input_dir = os.path.join(Config.BASE_DIR, "data/raw")
    
    try:
        stats = vector_store.add_documents(
            directory_path=input_dir,
            chunk_size=500,
            chunk_overlap=100
        )
    except Exception as e:
        print(f"✗ Error building index: {str(e)}")
        return
    
    # Save index
    output_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
    
    try:
        vector_store.save_index(output_path)
    except Exception as e:
        print(f"✗ Error saving index: {str(e)}")
        return
    
    # Print summary
    print("\n" + "="*70)
    print("INDEX BUILD SUMMARY")
    print("="*70)
    print(f"Files processed: {stats['total_files']}")
    print(f"Total chunks created: {stats['total_chunks']}")
    print(f"Chunk size: 500 tokens with 100-token overlap")
    print(f"Model: all-MiniLM-L6-v2")
    print(f"Index location: {output_path}")
    
    print(f"\nFile-by-file breakdown:")
    for file_info in stats['files_processed']:
        print(f"  • {file_info['file']:35} → {file_info['chunks']:3} chunks")
    
    print(f"\n{'='*70}")
    print(f"✓ Index building complete!")
    print(f"{'='*70}\n")
    
    # Test retrieval
    print("Testing index retrieval...")
    test_query = "What is the relationship between attention mechanisms and transformer performance?"
    
    try:
        results = vector_store.retrieve(test_query, k=3)
        
        print(f"\nTest Query: {test_query}\n")
        print(f"Top {len(results)} Results:")
        print("="*70)
        
        for result in results:
            print(f"\n[Rank {result['rank']}] Source: {result['source_file']}")
            print(f"Similarity Score: {result['similarity_score']:.4f}")
            print(f"Content (first 150 chars):\n{result['chunk_text'][:150]}...\n")
    
    except Exception as e:
        print(f"✗ Error testing retrieval: {str(e)}")


if __name__ == "__main__":
    main()
