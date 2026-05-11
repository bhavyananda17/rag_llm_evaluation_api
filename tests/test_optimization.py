#!/usr/bin/env python3
"""
Test Token Optimization System

Verifies that all optimization components are working correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_manager import TokenManager, estimate_benchmark_cost
from src.model_client import GeminiClient
from src.config import Config


def test_token_manager():
    """Test TokenManager functionality."""
    print("\n" + "="*70)
    print("TEST 1: Token Manager")
    print("="*70)
    
    try:
        manager = TokenManager(daily_budget=1_000_000)
        print("✓ TokenManager initialized")
        
        # Test estimation
        estimate = manager.estimate_request("What is RAG?", expected_response_length=150)
        print(f"✓ Estimated request: {estimate['total_tokens']} tokens")
        
        # Test benchmark estimation
        bench_est = manager.estimate_benchmark(num_questions=5)
        print(f"✓ Estimated benchmark: {bench_est['total_tokens']} tokens")
        
        # Test budget check
        budget = manager.check_budget(required_tokens=1000)
        print(f"✓ Budget check: {budget['remaining']} tokens remaining")
        
        # Test logging
        manager.log_request(input_tokens=100, output_tokens=50, success=True)
        print(f"✓ Logged request: {manager.session_tokens['total']} tokens in session")
        
        print("\n✓ All TokenManager tests passed!")
        return True
    
    except Exception as e:
        print(f"\n✗ TokenManager test failed: {str(e)}")
        return False


def test_cached_client():
    """Test CachedGeminiClient initialization."""
    print("\n" + "="*70)
    print("TEST 2: Cached Gemini Client")
    print("="*70)
    
    try:
        client = GeminiClient(use_cache=True)
        print(f"✓ Client initialized with model: {client.model_name}")
        
        # Test cache directory
        print(f"✓ Cache directory: {client.cache_dir}")
        
        # Test stats
        stats = client.get_stats()
        print(f"✓ Client statistics initialized")
        print(f"  - API Calls: {stats['api_calls']}")
        print(f"  - Cache Hits: {stats['cache_hits']}")
        print(f"  - Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        
        print("\n✓ All CachedGeminiClient tests passed!")
        return True
    
    except Exception as e:
        print(f"\n✗ CachedGeminiClient test failed: {str(e)}")
        return False


def test_vector_store():
    """Test vector store availability."""
    print("\n" + "="*70)
    print("TEST 3: Vector Store")
    print("="*70)
    
    try:
        from src.vector_db import VectorStore
        import json
        
        # Check if index exists
        index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        if os.path.exists(index_path):
            print(f"✓ Vector index found at {index_path}")
            
            # Load vector store
            vs = VectorStore(model_name='all-MiniLM-L6-v2')
            vs.load_index(index_path)
            print("✓ Vector store loaded")
            
            # Test retrieval
            results = vs.retrieve("What is RAG?", k=2)
            print(f"✓ Retrieved {len(results)} documents")
            
            print("\n✓ All VectorStore tests passed!")
            return True
        else:
            print(f"⚠ Vector index not found at {index_path}")
            print("  (This is expected if index hasn't been built yet)")
            return True
    
    except Exception as e:
        print(f"\n✗ VectorStore test failed: {str(e)}")
        return False


def test_qa_dataset():
    """Test QA dataset availability."""
    print("\n" + "="*70)
    print("TEST 4: QA Dataset")
    print("="*70)
    
    try:
        import json
        
        qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        if os.path.exists(qa_path):
            with open(qa_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            qa_pairs = dataset.get('qa_pairs', [])
            print(f"✓ Loaded {len(qa_pairs)} QA pairs")
            
            # Sample statistics
            if qa_pairs:
                sample = qa_pairs[0]
                print(f"✓ Sample question: {sample.get('question', '')[:50]}...")
                print(f"  Difficulty: {sample.get('difficulty', 'Unknown')}")
            
            print("\n✓ All QA Dataset tests passed!")
            return True
        else:
            print(f"✗ QA dataset not found at {qa_path}")
            return False
    
    except Exception as e:
        print(f"\n✗ QA Dataset test failed: {str(e)}")
        return False


def test_cost_estimation():
    """Test cost estimation."""
    print("\n" + "="*70)
    print("TEST 5: Cost Estimation")
    print("="*70)
    
    try:
        manager = TokenManager()
        
        # Base model estimate
        base_est = manager.estimate_benchmark(
            num_questions=5,
            avg_prompt_length=100,
            avg_response_length=150
        )
        
        print(f"✓ Base model estimate: {base_est['total_tokens']} tokens (${base_est['estimated_cost_usd']:.4f})")
        
        # RAG estimate
        rag_est = manager.estimate_benchmark(
            num_questions=5,
            avg_prompt_length=800,
            avg_response_length=200
        )
        
        print(f"✓ RAG estimate: {rag_est['total_tokens']} tokens (${rag_est['estimated_cost_usd']:.4f})")
        
        total = base_est['total_tokens'] + rag_est['total_tokens']
        total_cost = base_est['estimated_cost_usd'] + rag_est['estimated_cost_usd']
        
        print(f"✓ Combined: {total} tokens (${total_cost:.4f})")
        
        print("\n✓ All Cost Estimation tests passed!")
        return True
    
    except Exception as e:
        print(f"\n✗ Cost Estimation test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("TOKEN OPTIMIZATION SYSTEM - COMPREHENSIVE TEST")
    print("="*70)
    
    results = []
    
    results.append(("Token Manager", test_token_manager()))
    results.append(("Cached Client", test_cached_client()))
    results.append(("Vector Store", test_vector_store()))
    results.append(("QA Dataset", test_qa_dataset()))
    results.append(("Cost Estimation", test_cost_estimation()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
