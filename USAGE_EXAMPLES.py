#!/usr/bin/env python3
"""
Example Usage: How to Use the Generated QA Dataset for RAG vs LoRA Evaluation

This script demonstrates various ways to load and use the generated QA dataset
for evaluating RAG and LoRA models.
"""

import json
import os
from typing import List, Dict
from collections import defaultdict


def example_1_load_dataset():
    """Example 1: Load the generated dataset."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Load Dataset")
    print("="*70)
    
    dataset_path = "data/processed/synthetic_qa.json"
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    print(f"✓ Loaded dataset with {len(dataset['qa_pairs'])} QA pairs")
    print(f"  Metadata: {dataset['metadata']['purpose']}")
    print(f"  Focus areas: {', '.join(dataset['metadata']['focus_areas'][:3])}...")


def example_2_iterate_qa_pairs():
    """Example 2: Iterate through QA pairs and extract information."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Iterate Through QA Pairs")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    for i, pair in enumerate(dataset['qa_pairs'][:3], 1):
        print(f"\n[Pair {i}]")
        print(f"Question: {pair['question'][:80]}...")
        print(f"Source: {pair['source_file']}")
        print(f"Difficulty: {pair['difficulty']}")
        print(f"Answer length: {len(pair['answer'])} chars")


def example_3_filter_by_source():
    """Example 3: Filter QA pairs by source document."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Filter by Source Document")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    # Group by source file
    by_source = defaultdict(list)
    for pair in dataset['qa_pairs']:
        by_source[pair['source_file']].append(pair)
    
    print(f"\nQA Pairs by source document:")
    for source, pairs in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {source}: {len(pairs)} pairs")
    
    # Get all pairs about hallucinations
    print("\n\nPairs about 'hallucinations':")
    hallucination_pairs = [p for p in dataset['qa_pairs'] 
                          if 'hallucination' in p['question'].lower()]
    for pair in hallucination_pairs[:2]:
        print(f"  - {pair['question'][:60]}...")


def example_4_create_evaluation_prompt():
    """Example 4: Create evaluation prompts for models."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Create Evaluation Prompts")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    pair = dataset['qa_pairs'][0]
    
    # Create a prompt for RAG model
    rag_prompt = f"""Context: You are evaluating a RAG (Retrieval-Augmented Generation) system.

Question: {pair['question']}

Please answer the question based on retrieved documents and your knowledge.
Reference Answer: {pair['answer']}

Evaluation Criteria:
1. Does the answer address all parts of the question?
2. Is the answer grounded in the provided context?
3. Are there any factual errors or hallucinations?
"""
    
    print("RAG Evaluation Prompt Example:")
    print(rag_prompt)
    
    # Create a prompt for LoRA fine-tuned model
    lora_prompt = f"""Task: Answer the following question based on specialized domain knowledge.

Question: {pair['question']}

Expected Reference Answer: {pair['answer']}

Model Response: [TO BE FILLED BY MODEL]

Evaluation Instructions:
- Compare model response to reference answer
- Score based on correctness, completeness, and clarity
"""
    
    print("\n" + "-"*70)
    print("LoRA Fine-tuned Model Evaluation Prompt Example:")
    print(lora_prompt)


def example_5_comparative_evaluation():
    """Example 5: Set up comparative evaluation (RAG vs LoRA)."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Comparative RAG vs LoRA Evaluation")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    evaluation_setup = {
        "benchmark_name": "RAG vs LoRA Evaluation",
        "test_cases": [],
        "metrics": {
            "rouge": None,
            "bleu": None,
            "exact_match": None,
            "semantic_similarity": None
        }
    }
    
    for idx, pair in enumerate(dataset['qa_pairs'][:2], 1):
        test_case = {
            "id": f"test_{idx:03d}",
            "question": pair['question'],
            "reference_answer": pair['answer'],
            "source_document": pair['source_file'].replace('.txt', ''),
            "expected_reasoning": pair['reasoning_path'],
            "difficulty": pair['difficulty'],
            "evaluation_methods": [
                {
                    "name": "rag_system",
                    "retriever": "semantic_search",
                    "generator": "base_llm",
                    "result": None
                },
                {
                    "name": "lora_system",
                    "base_model": "same_as_rag_generator",
                    "lora_rank": 16,
                    "result": None
                }
            ]
        }
        evaluation_setup["test_cases"].append(test_case)
    
    print(json.dumps(evaluation_setup, indent=2))


def example_6_export_for_different_uses():
    """Example 6: Export dataset for different use cases."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Export for Different Use Cases")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    # For fine-tuning instruction-following
    finetuning_data = []
    for pair in dataset['qa_pairs']:
        finetuning_data.append({
            "instruction": pair['question'],
            "input": "",
            "output": pair['answer']
        })
    
    print(f"✓ Fine-tuning format: {len(finetuning_data)} examples")
    print(f"  Example: {json.dumps(finetuning_data[0], indent=2)[:200]}...")
    
    # For retrieval evaluation
    retrieval_data = []
    for pair in dataset['qa_pairs']:
        retrieval_data.append({
            "query": pair['question'],
            "positive_passages": [pair['answer']],
            "source": pair['source_file']
        })
    
    print(f"\n✓ Retrieval format: {len(retrieval_data)} queries")
    print(f"  Example: {json.dumps(retrieval_data[0], indent=2)[:200]}...")
    
    # For zero-shot evaluation
    zeroshot_data = []
    for pair in dataset['qa_pairs']:
        zeroshot_data.append({
            "task": "question_answering",
            "input": pair['question'],
            "expected_output": pair['answer'],
            "task_description": f"Answer question about {pair['source_file'].replace('.txt', '')}"
        })
    
    print(f"\n✓ Zero-shot format: {len(zeroshot_data)} test cases")


def example_7_quality_analysis():
    """Example 7: Analyze dataset quality and characteristics."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Dataset Quality Analysis")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    qa_pairs = dataset['qa_pairs']
    
    # Statistics
    question_lengths = [len(p['question']) for p in qa_pairs]
    answer_lengths = [len(p['answer']) for p in qa_pairs]
    
    print(f"\nQuestion Statistics:")
    print(f"  Total: {len(qa_pairs)}")
    print(f"  Avg length: {sum(question_lengths) / len(question_lengths):.0f} chars")
    print(f"  Min: {min(question_lengths)} chars")
    print(f"  Max: {max(question_lengths)} chars")
    
    print(f"\nAnswer Statistics:")
    print(f"  Avg length: {sum(answer_lengths) / len(answer_lengths):.0f} chars")
    print(f"  Min: {min(answer_lengths)} chars")
    print(f"  Max: {max(answer_lengths)} chars")
    
    # Question type analysis
    comparative = sum(1 for p in qa_pairs if 'differ' in p['question'].lower())
    adversarial = sum(1 for p in qa_pairs if 'incorrectly' in p['question'].lower())
    
    print(f"\nQuestion Type Distribution:")
    print(f"  Comparative: {comparative} ({comparative/len(qa_pairs)*100:.1f}%)")
    print(f"  Adversarial: {adversarial} ({adversarial/len(qa_pairs)*100:.1f}%)")
    
    # Source distribution
    sources = defaultdict(int)
    for pair in qa_pairs:
        sources[pair['source_file']] += 1
    
    print(f"\nSource Document Distribution:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} pairs")


def example_8_create_baseline_responses():
    """Example 8: Create baseline responses for comparison."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Create Baseline Responses")
    print("="*70)
    
    with open("data/processed/synthetic_qa.json", 'r') as f:
        dataset = json.load(f)
    
    baseline_results = {
        "timestamp": "2026-03-30",
        "benchmark": "rag_vs_lora_evaluation",
        "models": {
            "rag_system": {
                "retriever": "sentence-transformers/all-MiniLM-L6-v2",
                "generator": "base_llm",
                "results": []
            },
            "lora_system": {
                "base_model": "base_llm",
                "lora_params": {"rank": 16, "lora_alpha": 32},
                "results": []
            }
        }
    }
    
    for idx, pair in enumerate(dataset['qa_pairs'], 1):
        baseline_results["models"]["rag_system"]["results"].append({
            "question_id": f"q_{idx:03d}",
            "question": pair['question'],
            "reference_answer": pair['answer'],
            "model_response": "[TO BE FILLED]",
            "scores": {
                "rouge": None,
                "bleu": None,
                "semantic_similarity": None
            }
        })
        
        baseline_results["models"]["lora_system"]["results"].append({
            "question_id": f"q_{idx:03d}",
            "question": pair['question'],
            "reference_answer": pair['answer'],
            "model_response": "[TO BE FILLED]",
            "scores": {
                "rouge": None,
                "bleu": None,
                "semantic_similarity": None
            }
        })
    
    print(f"✓ Created baseline evaluation structure")
    print(f"  RAG system: {len(baseline_results['models']['rag_system']['results'])} test cases")
    print(f"  LoRA system: {len(baseline_results['models']['lora_system']['results'])} test cases")
    
    print(f"\nBaseline structure saved as dict:")
    print(f"  Keys: {list(baseline_results.keys())}")
    print(f"  Model keys: {list(baseline_results['models'].keys())}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("QA DATASET USAGE EXAMPLES")
    print("="*70)
    print("Demonstrating how to use the generated synthetic QA dataset")
    print("for RAG vs LoRA model evaluation")
    
    examples = [
        example_1_load_dataset,
        example_2_iterate_qa_pairs,
        example_3_filter_by_source,
        example_4_create_evaluation_prompt,
        example_5_comparative_evaluation,
        example_6_export_for_different_uses,
        example_7_quality_analysis,
        example_8_create_baseline_responses
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {example_func.__name__}: {str(e)}")
    
    print("\n" + "="*70)
    print("✓ All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()
