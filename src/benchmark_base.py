#!/usr/bin/env python3
"""
Base Model Benchmark Script

This script evaluates the base LLM (Gemini) on the synthetic QA dataset
without providing any additional context (retrieval or fine-tuning).
Results are saved for later comparison with RAG and LoRA approaches.
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm
from src.config import Config
from src.model_client import GeminiClient


class BaseModelBenchmark:
    """Benchmark the base model on QA dataset without additional context."""
    
    def __init__(self):
        """Initialize benchmark with Gemini client and QA dataset."""
        print("="*70)
        print("BASE MODEL BENCHMARK INITIALIZATION")
        print("="*70)
        
        # Initialize client
        print("\nInitializing Gemini Client...")
        self.client = GeminiClient()
        print("✓ Gemini Client initialized")
        
        # Load QA dataset
        qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        print(f"Loading QA dataset from {qa_path}...")
        
        if not os.path.exists(qa_path):
            raise ValueError(f"QA dataset not found at {qa_path}")
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        
        self.qa_pairs = self.dataset.get('qa_pairs', [])
        print(f"✓ Loaded {len(self.qa_pairs)} QA pairs")
        
        # Initialize results storage
        self.results = []
        self.errors = []
        
        # Metadata
        self.start_time = None
        self.end_time = None
    
    def run_benchmark(self, num_samples: int = None, rate_limit_delay: float = 2.0) -> List[Dict]:
        """
        Run benchmark on QA dataset.
        
        Args:
            num_samples: Number of QA pairs to benchmark (None = all)
            rate_limit_delay: Seconds to wait between API calls
            
        Returns:
            List of result dictionaries
        """
        if num_samples is None:
            num_samples = len(self.qa_pairs)
        
        num_samples = min(num_samples, len(self.qa_pairs))
        
        print("\n" + "="*70)
        print("BASE MODEL BENCHMARK EXECUTION")
        print("="*70)
        print(f"Evaluating {num_samples} QA pairs")
        print(f"Rate limit delay: {rate_limit_delay}s between calls")
        print(f"{'='*70}\n")
        
        self.start_time = datetime.now()
        
        # Process each QA pair
        for idx, qa_pair in enumerate(tqdm(
            self.qa_pairs[:num_samples],
            desc="Benchmarking",
            unit="question",
            colour='green'
        )):
            try:
                question = qa_pair.get('question', '')
                ground_truth = qa_pair.get('answer', '')
                source_file = qa_pair.get('source_file', '')
                difficulty = qa_pair.get('difficulty', 'Unknown')
                reasoning_path = qa_pair.get('reasoning_path', '')
                
                # Call model WITHOUT providing context
                model_response = self._call_model(question)
                
                # Store result
                result = {
                    'id': f"q_{idx + 1:03d}",
                    'question': question,
                    'ground_truth': ground_truth,
                    'base_model_response': model_response,
                    'source_file': source_file,
                    'difficulty': difficulty,
                    'reasoning_path': reasoning_path,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
                self.results.append(result)
                
                # Rate limiting
                time.sleep(rate_limit_delay)
            
            except Exception as e:
                error_record = {
                    'id': f"q_{idx + 1:03d}",
                    'question': qa_pair.get('question', 'Unknown')[:100],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.errors.append(error_record)
                
                # Still rate limit even on error
                time.sleep(rate_limit_delay)
                
                print(f"  Error on question {idx + 1}: {str(e)}")
        
        self.end_time = datetime.now()
        
        return self.results
    
    def _call_model(self, question: str) -> str:
        """
        Call the base model with just the question (no context).
        
        Args:
            question: Input question
            
        Returns:
            Model response
        """
        prompt = f"""Answer the following question based on your knowledge. 
Do not make up information - if you don't know the answer, say so.

Question: {question}"""
        
        response = self.client.generate(prompt)
        
        return response
    
    def save_results(self, output_dir: str = None) -> str:
        """
        Save benchmark results to JSON file.
        
        Args:
            output_dir: Directory to save results (default: data/results/)
            
        Returns:
            Path to saved results file
        """
        if output_dir is None:
            output_dir = os.path.join(Config.BASE_DIR, "data/results")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare output data
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        output_data = {
            "metadata": {
                "benchmark_type": "Base Model Evaluation",
                "model": "gemini-1.5-flash",
                "dataset": "synthetic_qa.json",
                "total_questions": len(self.qa_pairs),
                "questions_evaluated": len(self.results),
                "questions_failed": len(self.errors),
                "timestamp": datetime.now().isoformat(),
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": duration,
                "success_rate": (len(self.results) / (len(self.results) + len(self.errors)) * 100) if (len(self.results) + len(self.errors)) > 0 else 0
            },
            "results": self.results,
            "errors": self.errors
        }
        
        # Save to JSON
        output_path = os.path.join(output_dir, "base_model_results.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✓ Results saved to: {output_path}")
        print(f"{'='*70}\n")
        
        return output_path
    
    def print_summary(self) -> None:
        """Print benchmark summary statistics."""
        if not self.results and not self.errors:
            print("No results to summarize")
            return
        
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        success_count = len(self.results)
        error_count = len(self.errors)
        total = success_count + error_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print("BASE MODEL BENCHMARK SUMMARY")
        print("="*70)
        print(f"Questions evaluated: {success_count}")
        print(f"Failed evaluations: {error_count}")
        print(f"Total: {total}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Avg time per question: {duration / success_count:.1f}s" if success_count > 0 else "N/A")
        print(f"{'='*70}\n")
    
    def print_sample_results(self, num_samples: int = 3) -> None:
        """
        Print sample results for review.
        
        Args:
            num_samples: Number of results to print
        """
        if not self.results:
            print("No results to display")
            return
        
        print("\n" + "="*70)
        print(f"SAMPLE BASE MODEL RESPONSES (First {min(num_samples, len(self.results))})")
        print("="*70)
        
        for result in self.results[:num_samples]:
            print(f"\n[{result['id']}] {result['source_file']} - {result['difficulty']}")
            print(f"Question:\n{result['question']}\n")
            print(f"Ground Truth:\n{result['ground_truth'][:200]}...\n")
            print(f"Base Model Response:\n{result['base_model_response'][:200]}...\n")
            print("-" * 70)


def main():
    """Main execution function."""
    
    try:
        # Initialize benchmark
        benchmark = BaseModelBenchmark()
        
        # Run benchmark (using all QA pairs)
        results = benchmark.run_benchmark(
            num_samples=None,  # Use all available QA pairs
            rate_limit_delay=2.0
        )
        
        # Print summary
        benchmark.print_summary()
        
        # Print sample results
        benchmark.print_sample_results(num_samples=2)
        
        # Save results
        output_path = benchmark.save_results()
        
        print(f"✓ Benchmark complete!")
        print(f"Results saved to: {output_path}")
        
    except Exception as e:
        print(f"✗ Benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
