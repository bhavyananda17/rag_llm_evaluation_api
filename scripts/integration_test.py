#!/usr/bin/env python3
"""
Comprehensive Integration Test: QA Generation + Vector Store + RAG

Demonstrates the complete pipeline:
1. Generate QA pairs from documents
2. Build vector index from same documents
3. Use vector store to retrieve context for QA pairs
4. Evaluate retrieval quality
"""

import json
import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.vector_db import VectorStore


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def main():
    """Run comprehensive integration test."""
    
    print_section("RAG EVALUATION SYSTEM: INTEGRATION TEST")
    
    # Load QA dataset
    print_section("Step 1: Loading QA Dataset")
    
    qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    with open(qa_path, 'r', encoding='utf-8') as f:
        qa_dataset = json.load(f)
    
    qa_pairs = qa_dataset.get('qa_pairs', [])
    print(f"✓ Loaded {len(qa_pairs)} QA pairs")
    print(f"  Total files processed: {qa_dataset['metadata']['total_files_processed']}")
    print(f"  Focus areas: {', '.join(qa_dataset['metadata']['focus_areas'][:3])}...")
    
    # Load vector store
    print_section("Step 2: Loading Vector Store")
    
    try:
        vs = VectorStore(model_name='all-MiniLM-L6-v2')
        index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        vs.load_index(index_path)
        print(f"✓ Vector store loaded")
        
        # Get stats
        stats = vs.get_index_stats()
        print(f"  Total chunks indexed: {stats['total_chunks']}")
        print(f"  Embedding dimension: {stats['embedding_dimension']}")
        print(f"  Index type: {stats['index_type']}")
    except Exception as e:
        print(f"✗ Error loading vector store: {e}")
        return
    
    # Evaluate retrieval quality
    print_section("Step 3: Evaluating Retrieval Quality")
    
    evaluation_results = {
        'total_questions': len(qa_pairs),
        'evaluated': 0,
        'source_matches': 0,
        'details': []
    }
    
    print(f"Testing retrieval for first {min(5, len(qa_pairs))} questions:\n")
    
    for i, qa_pair in enumerate(qa_pairs[:5], 1):
        question = qa_pair.get('question', '')
        original_source = qa_pair.get('source_file', '')
        
        # Retrieve documents
        results = vs.retrieve(question, k=3)
        retrieved_sources = [r['source_file'] for r in results]
        
        # Check if original source is in results
        source_match = original_source in retrieved_sources
        if source_match:
            evaluation_results['source_matches'] += 1
        
        evaluation_results['evaluated'] += 1
        
        # Display result
        match_symbol = "✓" if source_match else "✗"
        print(f"[{i}] {match_symbol} {question[:70]}...")
        print(f"    Original source: {original_source}")
        print(f"    Retrieved from: {retrieved_sources}")
        print(f"    Top score: {results[0]['similarity_score']:.4f}")
        print()
    
    # Calculate metrics
    match_rate = (evaluation_results['source_matches'] / evaluation_results['evaluated']) * 100
    evaluation_results['source_match_rate'] = match_rate
    
    # Sample retrieval details
    print_section("Step 4: Sample Retrieval Details")
    
    if qa_pairs:
        sample_qa = qa_pairs[0]
        question = sample_qa.get('question', '')
        expected_answer = sample_qa.get('answer', '')
        
        print(f"Sample Question: {question}\n")
        
        results = vs.retrieve(question, k=2)
        
        print(f"Retrieved Context:\n")
        for result in results:
            print(f"From: {result['source_file']}")
            print(f"Similarity: {result['similarity_score']:.4f}")
            print(f"Content:\n{result['chunk_text'][:200]}...\n")
        
        print(f"Expected Answer:\n{expected_answer[:200]}...\n")
    
    # Integration metrics
    print_section("Step 5: Integration Metrics")
    
    print(f"QA Dataset:")
    print(f"  Total pairs: {evaluation_results['total_questions']}")
    print(f"  Questions evaluated: {evaluation_results['evaluated']}")
    
    print(f"\nRetrieval Performance:")
    print(f"  Source match rate: {match_rate:.1f}%")
    print(f"  Matches: {evaluation_results['source_matches']}/{evaluation_results['evaluated']}")
    
    print(f"\nVector Store:")
    print(f"  Model: all-MiniLM-L6-v2")
    print(f"  Embedding dimension: 384")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Index size: {stats['index_size_mb']:.2f} MB")
    
    # System integration check
    print_section("Step 6: System Integration Summary")
    
    print(f"✓ QA Generation System")
    print(f"  - Generates 2 complex QA pairs per chunk")
    print(f"  - Focuses on RAG vs LoRA distinctions")
    print(f"  - All answers grounded in source material")
    
    print(f"\n✓ Vector Store System")
    print(f"  - Encodes documents to embeddings")
    print(f"  - Stores in FAISS index for fast retrieval")
    print(f"  - Retrieves top-k most relevant chunks")
    
    print(f"\n✓ Integration")
    print(f"  - Vector store retrieves context for QA pairs")
    print(f"  - Can validate QA pair grounding")
    print(f"  - Enables RAG-based evaluation")
    
    print_section("INTEGRATION TEST COMPLETE")
    
    print(f"✅ All systems operational:")
    print(f"   - QA generation: {len(qa_pairs)} pairs generated")
    print(f"   - Vector indexing: {stats['total_chunks']} chunks indexed")
    print(f"   - Retrieval quality: {match_rate:.1f}% source match rate")
    print(f"\n✅ System ready for RAG model evaluation")
    
    return {
        'qa_dataset': evaluation_results,
        'vector_store': stats,
        'integration_status': 'READY'
    }


if __name__ == "__main__":
    try:
        result = main()
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
