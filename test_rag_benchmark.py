#!/usr/bin/env python3
"""Test the RAG benchmark script with minimal samples."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.benchmark_rag import RAGBenchmark

print("Testing RAG Benchmark Script...\n")

try:
    # Initialize benchmark
    benchmark = RAGBenchmark()
    
    # Test format_context function
    print("\nTesting context formatting...")
    test_chunks = [
        {
            'source_file': 'test.txt',
            'similarity_score': 0.95,
            'chunk_text': 'This is test content for retrieval.'
        }
    ]
    formatted = benchmark.format_context(test_chunks)
    print(f"Formatted context:\n{formatted}")
    
    # Test augmented prompt construction
    print("\nTesting augmented prompt construction...")
    test_question = "What is attention?"
    augmented = benchmark.construct_augmented_prompt(test_question, formatted)
    print(f"Augmented prompt (first 300 chars):\n{augmented[:300]}...")
    
    # Run benchmark on 1 sample to test
    print("\nRunning RAG benchmark on 1 sample...")
    results = benchmark.run_benchmark(num_samples=1, rate_limit_delay=1.0)
    
    if results:
        print(f"✓ Got {len(results)} result(s)")
        print(f"  Retrieved context count: {results[0]['retrieved_context_count']}")
        print(f"  Retrieved sources: {results[0]['retrieved_sources']}")
        print(f"  Avg retrieval score: {results[0]['avg_retrieval_score']:.4f}")
    
    # Print summary
    benchmark.print_summary()
    
    # Save results
    output_path = benchmark.save_results()
    
    print(f"✓ RAG Benchmark test successful!")
    print(f"Results saved to: {output_path}")
    
except Exception as e:
    print(f"✗ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
