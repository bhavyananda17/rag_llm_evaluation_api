#!/usr/bin/env python3
"""
Generate Mock Benchmark Results

Creates realistic synthetic results for Base and RAG benchmarks
when API quota is exhausted or API key is unavailable.

This allows full pipeline testing and analysis without API calls.
"""

import json
import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def generate_mock_base_results() -> Dict:
    """
    Generate mock base model benchmark results.
    
    Returns:
        Dictionary with benchmark metadata and results
    """
    # Load real QA dataset
    qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    with open(qa_path, 'r', encoding='utf-8') as f:
        qa_dataset = json.load(f)
    
    qa_pairs = qa_dataset.get('qa_pairs', [])
    
    # Base model response templates (realistic but generic)
    base_templates = [
        "Self-attention and cross-attention are both key components of transformer architectures, but they differ in their input mechanisms and computational roles. Self-attention operates within a single sequence, enabling the model to capture dependencies between elements. Cross-attention, on the other hand, involves two different sequences and is essential for tasks like sequence-to-sequence translation.",
        "LoRA (Low-Rank Adaptation) significantly reduces memory requirements during fine-tuning by introducing trainable low-rank matrices instead of updating all model parameters. This approach maintains model quality while dramatically reducing the computational overhead, making it feasible to fine-tune large models on consumer hardware.",
        "Hallucinations in language models manifest as both intrinsic and extrinsic types. Intrinsic hallucinations occur when models generate text that contradicts their training data or known facts. Extrinsic hallucinations involve generating plausible-sounding but entirely fictional information.",
        "RAG systems improve language model accuracy by retrieving relevant contextual information from a knowledge base before generating responses. This external memory mechanism helps ground model outputs in factual information, reducing hallucinations and improving factual accuracy.",
        "Positional encodings in transformers serve to inject information about token positions into the model, since the transformer architecture itself is position-agnostic. These encodings enable the model to understand token order and relative positions.",
    ]
    
    results = []
    start_time = datetime.now() - timedelta(hours=1)
    
    for idx, qa_pair in enumerate(qa_pairs, 1):
        # Create somewhat realistic response (template + variation)
        template_idx = (idx - 1) % len(base_templates)
        response = base_templates[template_idx]
        
        # Add slight variation based on question
        question = qa_pair.get('question', '')
        if 'difference' in question.lower():
            response = f"The key differences are: First, {response}"
        elif 'how' in question.lower():
            response = f"The mechanism works as follows: {response}"
        elif 'what' in question.lower():
            response = f"{response}"
        
        result = {
            'id': f"base_q_{idx:03d}",
            'question': question,
            'ground_truth': qa_pair.get('answer', ''),
            'base_model_response': response,
            'source_file': qa_pair.get('source_file', ''),
            'difficulty': qa_pair.get('difficulty', 'Medium'),
            'reasoning_path': qa_pair.get('reasoning_path', ''),
            'timestamp': (start_time + timedelta(seconds=idx*2)).isoformat(),
            'success': True,
            'response_length': len(response),
            'model': 'gemini-1.5-flash (mock)'
        }
        results.append(result)
    
    # Calculate metrics
    success_count = len(results)
    total = len(results)
    
    output_data = {
        "metadata": {
            "benchmark_type": "Base Model Evaluation (Mock)",
            "model": "gemini-1.5-flash (mock)",
            "dataset": "synthetic_qa.json",
            "total_questions": len(qa_pairs),
            "questions_evaluated": success_count,
            "questions_failed": 0,
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(seconds=len(results)*2)).isoformat(),
            "duration_seconds": len(results) * 2,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "note": "Mock data generated for demonstration purposes"
        },
        "results": results,
        "errors": []
    }
    
    return output_data


def generate_mock_rag_results() -> Dict:
    """
    Generate mock RAG benchmark results.
    
    Returns:
        Dictionary with benchmark metadata and results
    """
    # Load real QA dataset
    qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    with open(qa_path, 'r', encoding='utf-8') as f:
        qa_dataset = json.load(f)
    
    qa_pairs = qa_dataset.get('qa_pairs', [])
    
    # RAG response templates (more accurate with context)
    rag_templates = [
        "Based on the provided context, self-attention operates within a single sequence where queries, keys, and values originate from the same source. This enables the model to capture contextual relationships within the sequence. Cross-attention, conversely, involves separate key and value sources from a different sequence, making it essential for encoder-decoder architectures and multi-modal tasks. The fundamental difference lies in the input sources and their computational implications for capturing inter-sequence dependencies.",
        "According to the context, LoRA (Low-Rank Adaptation) reduces memory requirements by introducing trainable low-rank decomposition matrices (A and B) that approximate the weight updates, rather than training the full weight matrix. This approach constrains the update to a lower-dimensional space, typically reducing trainable parameters by 99% while maintaining model quality. The efficiency gains come from storing and computing smaller matrices instead of full parameter sets.",
        "The context distinguishes intrinsic hallucinations, where models contradict their training data or generate factually incorrect information, from extrinsic hallucinations, which involve generating plausible-sounding but entirely fabricated information without basis in training data. Both types reflect the model's tendency to prioritize fluency over factuality.",
        "From the provided context, RAG systems improve language model accuracy through a retrieve-then-generate pipeline. The retrieval component fetches relevant documents from a knowledge base based on the input query, and the generation component produces responses conditioned on both the query and retrieved context. This architecture grounds model outputs in external knowledge, significantly reducing hallucinations and improving factual consistency.",
        "The context explains that positional encodings in transformers provide explicit information about token positions, as the transformer's self-attention mechanism is inherently position-agnostic. Encodings can be either absolute (based on token position) or relative (based on token distances), with sinusoidal encodings being the most common approach for capturing position information.",
    ]
    
    results = []
    start_time = datetime.now() - timedelta(hours=2)
    
    # Possible source files for mock retrieval
    source_files = [
        'attention_mechanism.txt',
        'transformer_architecture.txt',
        'lora_finetuning.txt',
        'llm_hallucinations.txt',
        'rag_systems.txt'
    ]
    
    for idx, qa_pair in enumerate(qa_pairs, 1):
        template_idx = (idx - 1) % len(rag_templates)
        response = rag_templates[template_idx]
        
        # Simulate retrieved context
        retrieved_sources = random.sample(source_files, k=random.randint(2, 3))
        retrieved_similarities = [round(random.uniform(0.7, 0.95), 3) for _ in retrieved_sources]
        avg_similarity = sum(retrieved_similarities) / len(retrieved_similarities)
        
        result = {
            'id': f"rag_q_{idx:03d}",
            'question': qa_pair.get('question', ''),
            'ground_truth': qa_pair.get('answer', ''),
            'rag_response': response,
            'retrieved_context_count': len(retrieved_sources),
            'retrieved_sources': retrieved_sources,
            'avg_retrieval_score': round(avg_similarity, 4),
            'source_file': qa_pair.get('source_file', ''),
            'difficulty': qa_pair.get('difficulty', 'Medium'),
            'reasoning_path': qa_pair.get('reasoning_path', ''),
            'timestamp': (start_time + timedelta(seconds=idx*3)).isoformat(),
            'success': True,
            'response_length': len(response),
            'model': 'gemini-1.5-flash (mock) + FAISS retrieval',
            'retrieval_metrics': {
                'similarities': retrieved_similarities,
                'retrieval_time_ms': round(random.uniform(10, 50), 2)
            }
        }
        results.append(result)
    
    success_count = len(results)
    total = len(results)
    
    # Calculate retrieval statistics
    total_similarities = []
    for result in results:
        total_similarities.extend(result['retrieval_metrics']['similarities'])
    
    avg_all_similarities = sum(total_similarities) / len(total_similarities) if total_similarities else 0
    
    output_data = {
        "metadata": {
            "benchmark_type": "RAG Model Evaluation (Mock)",
            "model": "gemini-1.5-flash (mock) + FAISS",
            "dataset": "synthetic_qa.json",
            "vector_store": "all-MiniLM-L6-v2 embeddings",
            "total_questions": len(qa_pairs),
            "questions_evaluated": success_count,
            "questions_failed": 0,
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": (start_time + timedelta(seconds=len(results)*3)).isoformat(),
            "duration_seconds": len(results) * 3,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "note": "Mock data generated for demonstration purposes"
        },
        "retrieval_statistics": {
            'total_retrievals': success_count,
            'successful_retrievals': success_count,
            'failed_retrievals': 0,
            'avg_similarity': round(avg_all_similarities, 4),
            'avg_context_chunks_per_question': 2.5
        },
        "results": results,
        "errors": []
    }
    
    return output_data


def main():
    """Generate and save mock benchmark results."""
    
    print("\n" + "="*70)
    print("GENERATING MOCK BENCHMARK RESULTS")
    print("="*70)
    
    # Create results directory
    results_dir = os.path.join(Config.BASE_DIR, "data/results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate Base Model Results
    print("\n📊 Generating Base Model benchmark results...")
    base_results = generate_mock_base_results()
    base_path = os.path.join(results_dir, "base_model_results.json")
    
    with open(base_path, 'w', encoding='utf-8') as f:
        json.dump(base_results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Base Model results saved: {base_path}")
    print(f"  - Questions evaluated: {base_results['metadata']['questions_evaluated']}")
    print(f"  - Success rate: {base_results['metadata']['success_rate']:.1f}%")
    
    # Generate RAG Results
    print("\n📊 Generating RAG Model benchmark results...")
    rag_results = generate_mock_rag_results()
    rag_path = os.path.join(results_dir, "rag_model_results.json")
    
    with open(rag_path, 'w', encoding='utf-8') as f:
        json.dump(rag_results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ RAG Model results saved: {rag_path}")
    print(f"  - Questions evaluated: {rag_results['metadata']['questions_evaluated']}")
    print(f"  - Success rate: {rag_results['metadata']['success_rate']:.1f}%")
    print(f"  - Avg retrieval similarity: {rag_results['retrieval_statistics']['avg_similarity']:.4f}")
    
    print("\n" + "="*70)
    print("✓ Mock benchmark results generated successfully!")
    print("="*70 + "\n")
    
    return {
        'base_results_path': base_path,
        'rag_results_path': rag_path,
        'base_results': base_results,
        'rag_results': rag_results
    }


if __name__ == "__main__":
    main()
