#!/usr/bin/env python3
"""
Optimized Benchmark Runner: Token-efficient evaluation system.

Features:
- Smart sampling (evaluates representative subset)
- Response caching
- Token budget tracking
- Batch processing with progress tracking
- Real-time cost monitoring
"""

import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm
from src.config import Config
from src.vector_db import VectorStore
from src.model_client import GeminiClient
from src.token_manager import TokenManager


class OptimizedBenchmark:
    """Token-efficient benchmark runner."""
    
    def __init__(self, use_cache: bool = True, sample_size: Optional[int] = None):
        """
        Initialize optimized benchmark.
        
        Args:
            use_cache: Enable response caching
            sample_size: Number of questions to evaluate (None = smart sampling)
        """
        print("="*70)
        print("OPTIMIZED BENCHMARK INITIALIZATION")
        print("="*70)
        
        # Initialize components
        print("\n1. Loading QA Dataset...")
        qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        with open(qa_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        self.qa_pairs = self.dataset.get('qa_pairs', [])
        print(f"   ✓ Loaded {len(self.qa_pairs)} QA pairs")
        
        # Determine sample size
        if sample_size is None:
            # Smart sampling: use all if < 20, else use 50% or 10 (whichever is larger)
            self.sample_size = min(len(self.qa_pairs), max(10, len(self.qa_pairs) // 2))
        else:
            self.sample_size = min(sample_size, len(self.qa_pairs))
        
        print(f"   Will evaluate: {self.sample_size}/{len(self.qa_pairs)} questions")
        
        # Initialize clients
        print("\n2. Initializing API Client...")
        self.client = GeminiClient(use_cache=use_cache)
        print(f"   ✓ Using model: {self.client.model_name}")
        
        print("\n3. Initializing Token Manager...")
        self.token_manager = TokenManager()
        print("   ✓ Token manager ready")
        
        # Initialize vector store (for RAG only)
        self.vector_store = None
        index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        if os.path.exists(index_path):
            print("\n4. Loading Vector Store...")
            self.vector_store = VectorStore(model_name='all-MiniLM-L6-v2')
            self.vector_store.load_index(index_path)
            print("   ✓ Vector store loaded")
        
        # Results storage
        self.results_base = []
        self.results_rag = []
        self.errors = []
    
    def _optimize_prompt(self, text: str, max_length: int = 500) -> str:
        """
        Optimize prompt to reduce token count.
        
        Strategies:
        - Truncate verbose instructions
        - Remove redundant context
        - Use concise formatting
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _estimate_total_cost(self, benchmark_type: str = "base") -> Dict:
        """Estimate cost before running."""
        if benchmark_type == "base":
            return self.token_manager.estimate_benchmark(
                num_questions=self.sample_size,
                avg_prompt_length=100,
                avg_response_length=150
            )
        else:  # RAG
            return self.token_manager.estimate_benchmark(
                num_questions=self.sample_size,
                avg_prompt_length=800,
                avg_response_length=200
            )
    
    def run_base_benchmark(self, dry_run: bool = False) -> List[Dict]:
        """
        Run optimized base model benchmark.
        
        Args:
            dry_run: Estimate cost without running
            
        Returns:
            List of results
        """
        print("\n" + "="*70)
        print("BASE MODEL BENCHMARK (Optimized)")
        print("="*70)
        
        # Cost estimation
        estimate = self._estimate_total_cost("base")
        print(f"\nEstimated Cost:")
        print(f"  Questions: {estimate['num_questions']}")
        print(f"  Tokens: {estimate['total_tokens']:,}")
        print(f"  Cost: ${estimate['estimated_cost_usd']:.4f}")
        print(f"  Within Budget: {'✓' if estimate['within_daily_budget'] else '✗'}")
        
        if dry_run:
            print("\n(Dry run mode - not executing)")
            return []
        
        # Check budget before proceeding
        if not estimate['within_daily_budget']:
            print("\n⚠ Warning: Estimated cost exceeds daily budget!")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return []
        
        print(f"\nEvaluating {self.sample_size} questions...")
        
        sampled_pairs = self.qa_pairs[:self.sample_size]
        
        for idx, qa_pair in enumerate(tqdm(
            sampled_pairs,
            desc="Base Benchmark",
            unit="q",
            colour='cyan'
        )):
            try:
                question = qa_pair.get('question', '')
                ground_truth = qa_pair.get('answer', '')
                
                # Optimize prompt
                prompt = self._optimize_prompt(
                    f"Answer this question: {question}",
                    max_length=200
                )
                
                # Generate response
                response = self.client.generate(prompt)
                
                # Store result
                self.results_base.append({
                    'id': f"base_q_{idx + 1:03d}",
                    'question': question,
                    'ground_truth': ground_truth[:200],
                    'response': response[:500],
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(0.5)  # Rate limiting
            
            except Exception as e:
                self.errors.append({
                    'id': f"base_q_{idx + 1:03d}",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return self.results_base
    
    def run_rag_benchmark(self, dry_run: bool = False) -> List[Dict]:
        """
        Run optimized RAG benchmark.
        
        Args:
            dry_run: Estimate cost without running
            
        Returns:
            List of results
        """
        if not self.vector_store:
            print("✗ Vector store not available for RAG benchmark")
            return []
        
        print("\n" + "="*70)
        print("RAG MODEL BENCHMARK (Optimized)")
        print("="*70)
        
        # Cost estimation
        estimate = self._estimate_total_cost("rag")
        print(f"\nEstimated Cost:")
        print(f"  Questions: {estimate['num_questions']}")
        print(f"  Tokens: {estimate['total_tokens']:,}")
        print(f"  Cost: ${estimate['estimated_cost_usd']:.4f}")
        print(f"  Within Budget: {'✓' if estimate['within_daily_budget'] else '✗'}")
        
        if dry_run:
            print("\n(Dry run mode - not executing)")
            return []
        
        # Check budget
        if not estimate['within_daily_budget']:
            print("\n⚠ Warning: Estimated cost exceeds daily budget!")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return []
        
        print(f"\nEvaluating {self.sample_size} questions with RAG...")
        
        sampled_pairs = self.qa_pairs[:self.sample_size]
        
        for idx, qa_pair in enumerate(tqdm(
            sampled_pairs,
            desc="RAG Benchmark",
            unit="q",
            colour='green'
        )):
            try:
                question = qa_pair.get('question', '')
                ground_truth = qa_pair.get('answer', '')
                
                # Retrieve context
                retrieved = self.vector_store.retrieve(question, k=2)
                
                # Format context (optimized)
                context_parts = []
                for chunk in retrieved:
                    context_parts.append(chunk.get('chunk_text', '')[:200])
                context = " ".join(context_parts)
                
                # Construct prompt (token-optimized)
                prompt = self._optimize_prompt(
                    f"Context: {context}\n\nQuestion: {question}\n\nAnswer:",
                    max_length=600
                )
                
                # Generate response
                response = self.client.generate(prompt)
                
                # Store result
                self.results_rag.append({
                    'id': f"rag_q_{idx + 1:03d}",
                    'question': question,
                    'ground_truth': ground_truth[:200],
                    'retrieved_count': len(retrieved),
                    'response': response[:500],
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(0.5)  # Rate limiting
            
            except Exception as e:
                self.errors.append({
                    'id': f"rag_q_{idx + 1:03d}",
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return self.results_rag
    
    def save_results(self, output_dir: str = None) -> Dict:
        """Save results to JSON files."""
        if output_dir is None:
            output_dir = os.path.join(Config.BASE_DIR, "data/results")
        os.makedirs(output_dir, exist_ok=True)
        
        files_saved = {}
        
        if self.results_base:
            base_file = os.path.join(output_dir, "optimized_base_results.json")
            with open(base_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'benchmark_type': 'Base Model (Optimized)',
                        'timestamp': datetime.now().isoformat(),
                        'sample_size': len(self.results_base),
                        'total_available': len(self.qa_pairs)
                    },
                    'results': self.results_base,
                    'errors': [e for e in self.errors if 'base' in e['id']]
                }, f, indent=2, ensure_ascii=False)
            files_saved['base'] = base_file
        
        if self.results_rag:
            rag_file = os.path.join(output_dir, "optimized_rag_results.json")
            with open(rag_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'benchmark_type': 'RAG Model (Optimized)',
                        'timestamp': datetime.now().isoformat(),
                        'sample_size': len(self.results_rag),
                        'total_available': len(self.qa_pairs)
                    },
                    'results': self.results_rag,
                    'errors': [e for e in self.errors if 'rag' in e['id']]
                }, f, indent=2, ensure_ascii=False)
            files_saved['rag'] = rag_file
        
        return files_saved
    
    def print_summary(self) -> None:
        """Print execution summary."""
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        
        if self.results_base:
            print(f"\nBase Model Results:")
            print(f"  Evaluated: {len(self.results_base)} questions")
        
        if self.results_rag:
            print(f"\nRAG Model Results:")
            print(f"  Evaluated: {len(self.results_rag)} questions")
        
        print(f"\nTotal Errors: {len(self.errors)}")
        
        self.client.print_stats()


def main():
    """Main execution."""
    
    print("\n" + "="*70)
    print("OPTIMIZED BENCHMARK RUNNER")
    print("="*70)
    
    # Initialize
    benchmark = OptimizedBenchmark(use_cache=True, sample_size=10)
    
    # Run benchmarks (with dry run first)
    print("\n" + "="*70)
    print("PHASE 1: COST ESTIMATION")
    print("="*70)
    
    benchmark.run_base_benchmark(dry_run=True)
    benchmark.run_rag_benchmark(dry_run=True)
    
    # Ask user if they want to proceed
    print("\n" + "="*70)
    print("Ready to execute benchmarks")
    print("="*70)
    response = input("Proceed with execution? (y/n): ")
    
    if response.lower() == 'y':
        print("\nExecuting benchmarks...")
        benchmark.run_base_benchmark(dry_run=False)
        benchmark.run_rag_benchmark(dry_run=False)
        
        # Save results
        files = benchmark.save_results()
        print(f"\n✓ Results saved:")
        for key, path in files.items():
            print(f"  - {key}: {path}")
        
        # Print summary
        benchmark.print_summary()
    else:
        print("\nBenchmarks cancelled.")


if __name__ == "__main__":
    main()
