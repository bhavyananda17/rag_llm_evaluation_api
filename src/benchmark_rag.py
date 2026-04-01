#!/usr/bin/env python3
"""
RAG Model Benchmark Script

Evaluates RAG (Retrieval-Augmented Generation) models using vector store retrieval.
"""

import json
import sys
import os
import time
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm
from src.config import Config
from src.vector_db import VectorStore
from src.model_client import GeminiClient


class RAGBenchmark:
    """Benchmark RAG-augmented model on QA dataset."""
    
    def __init__(self):
        """Initialize RAG benchmark."""
        print("="*70)
        print("RAG MODEL BENCHMARK INITIALIZATION")
        print("="*70)
        
        print("\nInitializing Vector Store...")
        self.vector_store = VectorStore(model_name='all-MiniLM-L6-v2')
        
        index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        if os.path.exists(index_path):
            print(f"Loading pre-built index...")
            self.vector_store.load_index(index_path)
            print("✓ Vector Store loaded")
        else:
            print("Building vector index...")
            input_dir = os.path.join(Config.BASE_DIR, "data/raw")
            self.vector_store.add_documents(input_dir, chunk_size=500, chunk_overlap=100)
            self.vector_store.save_index(index_path)
            print("✓ Vector Store built")
        
        print("\nInitializing Gemini Client...")
        self.client = GeminiClient()
        print("✓ Gemini Client initialized")
        
        qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        print(f"Loading QA dataset...")
        
        if not os.path.exists(qa_path):
            raise ValueError(f"QA dataset not found")
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        
        self.qa_pairs = self.dataset.get('qa_pairs', [])
        print(f"✓ Loaded {len(self.qa_pairs)} QA pairs")
        
        self.results = []
        self.errors = []
        self.retrieval_stats = {
            'total_retrievals': 0,
            'successful_retrievals': 0,
            'failed_retrievals': 0,
            'avg_similarity': 0.0
        }
        
        self.start_time = None
        self.end_time = None
    
    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """Format retrieved chunks into context string."""
        if not retrieved_chunks:
            return "No relevant context found."
        
        formatted_parts = ["=== RETRIEVED CONTEXT ===\n"]
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            source_file = chunk.get('source_file', 'Unknown')
            similarity = chunk.get('similarity_score', 0.0)
            text = chunk.get('chunk_text', '')
            
            formatted_parts.append(
                f"\n[Context {i}] Source: {source_file} (Relevance: {similarity:.3f})\n"
                f"---\n"
                f"{text}\n"
                f"---"
            )
        
        formatted_parts.append("\n=== END CONTEXT ===\n")
        
        return "\n".join(formatted_parts)
    
    def construct_augmented_prompt(self, question: str, context: str) -> str:
        """Construct prompt combining question with retrieved context."""
        augmented_prompt = f"""You are an expert assistant answering questions about machine learning.

{context}

Based on the context provided, answer the following question:

Question: {question}

Answer:"""
        
        return augmented_prompt
    
    def run_benchmark(self, num_samples: int = None, rate_limit_delay: float = 2.0) -> List[Dict]:
        """Run RAG benchmark on QA dataset."""
        if num_samples is None:
            num_samples = len(self.qa_pairs)
        
        num_samples = min(num_samples, len(self.qa_pairs))
        
        print("\n" + "="*70)
        print("RAG MODEL BENCHMARK EXECUTION")
        print("="*70)
        print(f"Evaluating {num_samples} QA pairs with RAG augmentation")
        print(f"{'='*70}\n")
        
        self.start_time = datetime.now()
        
        for idx, qa_pair in enumerate(tqdm(
            self.qa_pairs[:num_samples],
            desc="RAG Benchmarking",
            unit="question",
            colour='blue'
        )):
            question = qa_pair.get('question', '')
            ground_truth = qa_pair.get('answer', '')
            source_file = qa_pair.get('source_file', '')
            difficulty = qa_pair.get('difficulty', 'Unknown')
            
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # Step 1: Retrieve context
                    retrieved_chunks = self.vector_store.retrieve(question, k=3)
                    self.retrieval_stats['total_retrievals'] += 1
                    self.retrieval_stats['successful_retrievals'] += 1
                    
                    # Calculate average similarity
                    if retrieved_chunks:
                        similarities = [chunk.get('similarity_score', 0) for chunk in retrieved_chunks]
                        avg_sim = sum(similarities) / len(similarities)
                    else:
                        avg_sim = 0.0
                    
                    # Step 2: Format context
                    formatted_context = self.format_context(retrieved_chunks)
                    
                    # Step 3: Construct augmented prompt
                    augmented_prompt = self.construct_augmented_prompt(question, formatted_context)
                    
                    # Step 4: Call model
                    model_response = self.client.generate(augmented_prompt)
                    
                    # Store result
                    result = {
                        'id': f"rag_q_{idx + 1:03d}",
                        'question': question,
                        'ground_truth': ground_truth,
                        'rag_response': model_response,
                        'retrieved_context_count': len(retrieved_chunks),
                        'retrieved_sources': [chunk['source_file'] for chunk in retrieved_chunks],
                        'avg_retrieval_score': avg_sim,
                        'source_file': source_file,
                        'difficulty': difficulty,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    }
                    
                    self.results.append(result)
                    success = True
                    
                    print(f"\n  ✓ Retrieved {len(retrieved_chunks)} chunks")
                    
                    time.sleep(rate_limit_delay)
                
                except Exception as e:
                    error_msg = str(e)
                    
                    if '429' in error_msg or 'quota' in error_msg.lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"\n  ⚠ Quota exceeded. Waiting 60s...")
                            time.sleep(60.0)
                        else:
                            error_record = {
                                'id': f"rag_q_{idx + 1:03d}",
                                'question': question[:100],
                                'error': f"Quota exceeded after {max_retries} retries",
                                'timestamp': datetime.now().isoformat()
                            }
                            self.errors.append(error_record)
                            self.retrieval_stats['failed_retrievals'] += 1
                            success = True
                    else:
                        error_record = {
                            'id': f"rag_q_{idx + 1:03d}",
                            'question': question[:100],
                            'error': error_msg,
                            'timestamp': datetime.now().isoformat()
                        }
                        self.errors.append(error_record)
                        self.retrieval_stats['failed_retrievals'] += 1
                        success = True
                        print(f"\n  ✗ Error: {error_msg}")
        
        self.end_time = datetime.now()
        
        return self.results
    
    def save_results(self, output_dir: str = None) -> str:
        """Save benchmark results to JSON file."""
        if output_dir is None:
            output_dir = os.path.join(Config.BASE_DIR, "data/results")
        
        os.makedirs(output_dir, exist_ok=True)
        
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        output_data = {
            "metadata": {
                "benchmark_type": "RAG Model Evaluation",
                "model": "gemini-1.5-flash with FAISS retrieval",
                "dataset": "synthetic_qa.json",
                "total_questions": len(self.qa_pairs),
                "questions_evaluated": len(self.results),
                "questions_failed": len(self.errors),
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "success_rate": (len(self.results) / (len(self.results) + len(self.errors)) * 100) if (len(self.results) + len(self.errors)) > 0 else 0
            },
            "retrieval_statistics": self.retrieval_stats,
            "results": self.results,
            "errors": self.errors
        }
        
        output_path = os.path.join(output_dir, "rag_model_results.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✓ Results saved to: {output_path}")
        print(f"{'='*70}\n")
        
        return output_path
    
    def print_summary(self) -> None:
        """Print benchmark summary."""
        if not self.results and not self.errors:
            print("No results")
            return
        
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        success_count = len(self.results)
        error_count = len(self.errors)
        total = success_count + error_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print("RAG MODEL BENCHMARK SUMMARY")
        print("="*70)
        print(f"Questions evaluated: {success_count}")
        print(f"Failed: {error_count}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.1f}s")
        print(f"\nRetrieval Statistics:")
        print(f"  Successful: {self.retrieval_stats['successful_retrievals']}")
        print(f"  Failed: {self.retrieval_stats['failed_retrievals']}")
        print(f"  Avg similarity: {self.retrieval_stats['avg_similarity']:.4f}")
        print(f"{'='*70}\n")


def main():
    """Main execution."""
    
    try:
        benchmark = RAGBenchmark()
        results = benchmark.run_benchmark(num_samples=None, rate_limit_delay=2.0)
        benchmark.print_summary()
        output_path = benchmark.save_results()
        print(f"✓ RAG Benchmark complete!")
        print(f"Results: {output_path}")
        
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
