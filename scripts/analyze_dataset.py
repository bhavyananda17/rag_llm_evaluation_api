#!/usr/bin/env python3
"""
Analysis and Evaluation Script for Generated QA Dataset

This script demonstrates how to:
1. Load the generated synthetic QA dataset
2. Analyze dataset statistics and composition
3. Export data in various formats for model evaluation
4. Generate evaluation metrics
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


class QADatasetAnalyzer:
    """Analyze and evaluate generated QA dataset."""
    
    def __init__(self, dataset_path: str):
        """Initialize analyzer with dataset."""
        self.dataset_path = dataset_path
        self.dataset = None
        self.qa_pairs = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load dataset from JSON file."""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        self.qa_pairs = self.dataset.get('qa_pairs', [])
        print(f"✓ Loaded {len(self.qa_pairs)} QA pairs from dataset")
    
    def print_summary(self):
        """Print high-level dataset summary."""
        metadata = self.dataset.get('metadata', {})
        stats = self.dataset.get('statistics', {})
        
        print("\n" + "="*70)
        print("DATASET SUMMARY")
        print("="*70)
        print(f"Version: {metadata.get('version', 'N/A')}")
        print(f"Purpose: {metadata.get('purpose', 'N/A')}")
        print(f"Total QA Pairs: {len(self.qa_pairs)}")
        print(f"Files Processed: {stats.get('total_files', 0)}")
        print(f"Chunks Processed: {stats.get('total_chunks', 0)}")
        print(f"Generation Method: {metadata.get('generation_method', 'N/A')}")
        
        print(f"\nFocus Areas:")
        for area in metadata.get('focus_areas', []):
            print(f"  • {area}")
    
    def print_file_breakdown(self):
        """Print breakdown by source file."""
        stats = self.dataset.get('statistics', {})
        files_processed = stats.get('files_processed', [])
        
        print("\n" + "="*70)
        print("FILE PROCESSING BREAKDOWN")
        print("="*70)
        
        for file_info in files_processed:
            file_name = file_info.get('file', 'Unknown')
            chunks = file_info.get('chunks', 0)
            qa_pairs = file_info.get('qa_pairs', 0)
            print(f"{file_name:30} | Chunks: {chunks:2} | QA Pairs: {qa_pairs:2}")
    
    def print_question_analysis(self):
        """Analyze and print question statistics."""
        print("\n" + "="*70)
        print("QUESTION ANALYSIS")
        print("="*70)
        
        # Extract question characteristics
        question_lengths = []
        question_word_counts = []
        question_types = defaultdict(int)
        
        for pair in self.qa_pairs:
            question = pair.get('question', '')
            question_lengths.append(len(question))
            question_word_counts.append(len(question.split()))
            
            # Classify question type
            if 'differ' in question.lower() or 'difference' in question.lower():
                question_types['Comparative'] += 1
            elif 'incorrectly' in question.lower() or 'misconception' in question.lower():
                question_types['Adversarial'] += 1
            else:
                question_types['Other'] += 1
        
        # Print statistics
        print(f"Total Questions: {len(self.qa_pairs)}")
        print(f"\nQuestion Length (characters):")
        print(f"  Min: {min(question_lengths)}")
        print(f"  Max: {max(question_lengths)}")
        print(f"  Avg: {sum(question_lengths) / len(question_lengths):.1f}")
        
        print(f"\nQuestion Length (words):")
        print(f"  Min: {min(question_word_counts)}")
        print(f"  Max: {max(question_word_counts)}")
        print(f"  Avg: {sum(question_word_counts) / len(question_word_counts):.1f}")
        
        print(f"\nQuestion Type Distribution:")
        for q_type, count in sorted(question_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.qa_pairs)) * 100
            print(f"  {q_type}: {count} ({percentage:.1f}%)")
    
    def print_answer_analysis(self):
        """Analyze and print answer statistics."""
        print("\n" + "="*70)
        print("ANSWER ANALYSIS")
        print("="*70)
        
        answer_lengths = []
        answer_word_counts = []
        
        for pair in self.qa_pairs:
            answer = pair.get('answer', '')
            answer_lengths.append(len(answer))
            answer_word_counts.append(len(answer.split()))
        
        print(f"Total Answers: {len(self.qa_pairs)}")
        print(f"\nAnswer Length (characters):")
        print(f"  Min: {min(answer_lengths)}")
        print(f"  Max: {max(answer_lengths)}")
        print(f"  Avg: {sum(answer_lengths) / len(answer_lengths):.1f}")
        
        print(f"\nAnswer Length (words):")
        print(f"  Min: {min(answer_word_counts)}")
        print(f"  Max: {max(answer_word_counts)}")
        print(f"  Avg: {sum(answer_word_counts) / len(answer_word_counts):.1f}")
    
    def print_difficulty_distribution(self):
        """Print difficulty distribution."""
        print("\n" + "="*70)
        print("DIFFICULTY DISTRIBUTION")
        print("="*70)
        
        difficulties = Counter(pair.get('difficulty', 'Unknown') for pair in self.qa_pairs)
        
        for difficulty in ['Easy', 'Medium', 'Hard']:
            count = difficulties.get(difficulty, 0)
            percentage = (count / len(self.qa_pairs)) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {difficulty:8} | {bar:20} | {count:2} ({percentage:5.1f}%)")
    
    def print_source_file_distribution(self):
        """Print QA pair distribution by source file."""
        print("\n" + "="*70)
        print("QA PAIR DISTRIBUTION BY SOURCE FILE")
        print("="*70)
        
        source_distribution = Counter(pair.get('source_file', 'Unknown') for pair in self.qa_pairs)
        
        total = len(self.qa_pairs)
        for source, count in sorted(source_distribution.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {source:30} | {bar:20} | {count:2} ({percentage:5.1f}%)")
    
    def export_for_evaluation(self, output_dir: str = "exports"):
        """Export dataset in various formats for model evaluation."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export 1: Simple Q&A pairs (CSV format)
        csv_file = os.path.join(output_dir, "qa_pairs.csv")
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("question_id,source_file,question,answer,difficulty\n")
            for idx, pair in enumerate(self.qa_pairs, 1):
                question = pair.get('question', '').replace('"', '""')
                answer = pair.get('answer', '').replace('"', '""')
                source = pair.get('source_file', '')
                difficulty = pair.get('difficulty', '')
                f.write(f'{idx},"{source}","{question}","{answer}","{difficulty}"\n')
        print(f"✓ Exported to {csv_file}")
        
        # Export 2: Evaluation format (JSON with metadata)
        eval_file = os.path.join(output_dir, "evaluation_format.json")
        eval_data = {
            "metadata": self.dataset.get('metadata', {}),
            "evaluation_set": [
                {
                    "id": f"qa_{idx:03d}",
                    "question": pair.get('question', ''),
                    "reference_answer": pair.get('answer', ''),
                    "source_file": pair.get('source_file', ''),
                    "difficulty": pair.get('difficulty', 'Hard'),
                    "reasoning_path": pair.get('reasoning_path', '')
                }
                for idx, pair in enumerate(self.qa_pairs, 1)
            ]
        }
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(eval_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported to {eval_file}")
        
        # Export 3: RAG benchmark format
        rag_file = os.path.join(output_dir, "rag_benchmark.json")
        rag_data = {
            "benchmark_name": "RAG vs LoRA Evaluation Set",
            "questions": [
                {
                    "id": f"q_{idx:03d}",
                    "query": pair.get('question', ''),
                    "expected_answer": pair.get('answer', ''),
                    "source_document": pair.get('source_file', '').replace('.txt', ''),
                    "complexity": pair.get('difficulty', 'Hard'),
                    "metrics": {
                        "rouge_score": None,  # To be filled after evaluation
                        "bleu_score": None,
                        "exact_match": None
                    }
                }
                for idx, pair in enumerate(self.qa_pairs, 1)
            ]
        }
        with open(rag_file, 'w', encoding='utf-8') as f:
            json.dump(rag_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported to {rag_file}")
    
    def print_sample_qa_pairs(self, num_samples: int = 3):
        """Print sample QA pairs for review."""
        print("\n" + "="*70)
        print(f"SAMPLE QA PAIRS (First {num_samples})")
        print("="*70)
        
        for idx, pair in enumerate(self.qa_pairs[:num_samples], 1):
            print(f"\n[QA Pair {idx}]")
            print(f"Source: {pair.get('source_file', 'Unknown')}")
            print(f"Difficulty: {pair.get('difficulty', 'Unknown')}")
            print(f"\nQuestion:\n{pair.get('question', 'N/A')}")
            print(f"\nAnswer:\n{pair.get('answer', 'N/A')[:200]}...")
            print(f"\nReasoning Path:\n{pair.get('reasoning_path', 'N/A')}")
            print("-" * 70)


def main():
    """Main execution."""
    dataset_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    
    if not os.path.exists(dataset_path):
        print(f"✗ Dataset not found at {dataset_path}")
        print("Please run src/generate_data.py first to generate the dataset.")
        return
    
    # Initialize analyzer
    analyzer = QADatasetAnalyzer(dataset_path)
    
    # Print comprehensive analysis
    analyzer.print_summary()
    analyzer.print_file_breakdown()
    analyzer.print_question_analysis()
    analyzer.print_answer_analysis()
    analyzer.print_difficulty_distribution()
    analyzer.print_source_file_distribution()
    analyzer.print_sample_qa_pairs(num_samples=2)
    
    # Export for evaluation
    print("\n" + "="*70)
    print("EXPORTING FOR EVALUATION")
    print("="*70)
    analyzer.export_for_evaluation(output_dir="data/exports")
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
